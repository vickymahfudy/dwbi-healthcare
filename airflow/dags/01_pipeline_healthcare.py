from datetime import datetime, timedelta
import os
import re
import requests
import yaml
import pandas as pd
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'kelompok_healthcare',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# --- 1. FUNGSI INGEST DATA ---
def ingest_csv_to_postgres():
    DATABASE_URI = 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow'
    engine = create_engine(DATABASE_URI)
    CSV_DIR = '/opt/airflow/data_generator/output'
    
    files_to_ingest = {
        'source_pasien.csv': 'src_pasien',
        'source_dokter.csv': 'src_dokter',
        'source_kunjungan.csv': 'src_kunjungan'
    }
    
    for file_name, table_name in files_to_ingest.items():
        file_path = os.path.join(CSV_DIR, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df.to_sql(table_name, con=engine, if_exists='replace', index=False, schema='public')
            print(f"✅ Berhasil menginjeksi {file_name} ke tabel {table_name}")

# --- 2. FUNGSI OTOMATISASI GENERATE FILE MODEL DBT ---
def auto_generate_dbt_models():
    # Menembak langsung ke branch 'faker-data' repositori dwbi-healthcare Anda (Menggunakan Raw URL)
    CONFIG_URL = "https://raw.githubusercontent.com/vickymahfudy/dwbi-healthcare/faker-data/dbt_project/dbt_manifest.yml"
    DBT_PROJECT_PATH = "/opt/airflow/dbt_project"
    
    print(f"⏳ Mengunduh master manifest YAML dari: {CONFIG_URL}")
    try:
        response = requests.get(CONFIG_URL)
        response.raise_for_status()
        file_map = yaml.safe_load(response.text)
    except Exception as e:
        raise Exception(f"❌ Gagal mengunduh file manifest dari GitHub: {e}")

    # Buat folder-folder dasar dbt di dalam Docker volume jika belum ada
    base_folders = ["models/staging", "models/dimensions", "models/marts"]
    for folder in base_folders:
        os.makedirs(os.path.join(DBT_PROJECT_PATH, folder), exist_ok=True)

    detected_sources = set()

    # Ekstraksi dan pembuatan file SQL secara otomatis sesuai manifest GitHub Anda
    for rel_path, content in file_map.items():
        full_path = os.path.join(DBT_PROJECT_PATH, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content.strip())

        # Deteksi otomatis nama tabel source mentah dari query SQL Anda
        sources = re.findall(r"source\s*\(\s*['\"](\w+)['\"]\s*,\s*['\"](\w+)['\"]\s*\)", content)
        for src_schema, src_table in sources: 
            detected_sources.add((src_schema, src_table))
        print(f"   ✅ File model dbt berhasil dibuat di container: {rel_path}")

    # Otomatis membuat file sources.yml agar dbt mengenali database Postgres Anda
    if detected_sources:
        schema_dict = {}
        for src_schema, src_table in detected_sources:
            if src_schema not in schema_dict:
                schema_dict[src_schema] = []
            schema_dict[src_schema].append(src_table)
            
        yaml_out = "version: 2\nsources:\n"
        for schema_name, tables in schema_dict.items():
            yaml_out += f"  - name: {schema_name}\n    tables:\n"
            for t in sorted(tables):
                yaml_out += f"      - name: {t}\n"
                
        with open(os.path.join(DBT_PROJECT_PATH, "models/staging/sources.yml"), "w") as f:
            f.write(yaml_out)
        print(f"✨ File sources.yml otomatis dibuat untuk schema: {list(schema_dict.keys())}")


# --- 3. DEFINISI ORKESTRASI DAG AIRFLOW ---
with DAG(
    '02_healthcare_data_pipeline',
    default_args=default_args,
    description='Pipeline ETL + dbt Otomatis Terintegrasi dengan GitHub Manifest',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Trigger Generator Data Palsu
    task_generate_data = BashOperator(
        task_id='run_data_generator',
        bash_command='python /opt/airflow/data_generator/src/generator.py',
    )

    # Task 2: Ingest File CSV ke PostgreSQL
    task_ingest_data = PythonOperator(
        task_id='ingest_csv_to_database',
        python_callable=ingest_csv_to_postgres,
    )

    # Task 3: Mengunduh manifest dari GitHub & auto-generate seluruh file model .sql dbt
    task_auto_generate_models = PythonOperator(
        task_id='auto_generate_dbt_files',
        python_callable=auto_generate_dbt_models,
    )

    # Task 4: dbt Run - Mengeksekusi hasil kompilasi model SQL menjadi Star Schema nyata
    task_dbt_run = BashOperator(
        task_id='dbt_run_transformation',
        bash_command='cd /opt/airflow/dbt_project && dbt run --target docker_env --profiles-dir .',
    )

    # Task 5: dbt Test - Memvalidasi Data Quality / integrity constraint
    task_dbt_test = BashOperator(
        task_id='dbt_data_quality_test',
        bash_command='cd /opt/airflow/dbt_project && dbt test --target docker_env --profiles-dir .',
    )

    # Definisi dependensi alur kerja (Linear Pipeline)
    task_generate_data >> task_ingest_data >> task_auto_generate_models >> task_dbt_run >> task_dbt_test