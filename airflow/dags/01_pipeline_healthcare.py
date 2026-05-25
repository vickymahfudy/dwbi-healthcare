from datetime import datetime, timedelta
import os
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

with DAG(
    '02_healthcare_data_pipeline',
    default_args=default_args,
    description='Pipeline ETL + dbt Otomatis Beruntun',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Langkah 1: Generate Data Palsu (DE)
    task_generate_data = BashOperator(
        task_id='run_data_generator',
        bash_command='python /opt/airflow/data_generator/src/generator.py',
    )

    # Langkah 2: Ingest CSV ke Postgres (DE)
    task_ingest_data = PythonOperator(
        task_id='ingest_csv_to_database',
        python_callable=ingest_csv_to_postgres,
    )

    # Langkah 3: dbt Run - Mengeksekusi semua file SQL transformasi di folder staging/marts (Analytics Engineer)
    task_dbt_run = BashOperator(
        task_id='dbt_run_transformation',
        bash_command='cd /opt/airflow/dbt_project && dbt run --target docker_env --profiles-dir .',
    )

    # Langkah 4: dbt Test - Memvalidasi kualitas data mart (Data Quality Analyst)
    # Ini akan menguji data, misalnya: memastikan ID tidak ada yang null atau duplikat.
    task_dbt_test = BashOperator(
        task_id='dbt_data_quality_test',
        bash_command='cd /opt/airflow/dbt_project && dbt test --target docker_env --profiles-dir .',
    )

    # Menghubungkan semua task agar berjalan berurutan sekali trigger
    task_generate_data >> task_ingest_data >> task_dbt_run >> task_dbt_test