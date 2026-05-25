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

# Fungsi Python untuk membaca CSV dan memasukkannya ke PostgreSQL
def ingest_csv_to_postgres():
    # URI Koneksi ke Postgres bawaan Airflow Docker
    DATABASE_URI = 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow'
    engine = create_engine(DATABASE_URI)
    
    CSV_DIR = '/opt/airflow/data_generator/output'
    
    files_to_ingest = {
        'source_pasien.csv': 'src_pasien',
        'source_dokter.csv': 'src_dokter',
        'source_kunjungan.csv': 'src_kunjungan'
    }
    
    print("⏳ Memulai proses Ingestion ke PostgreSQL Staging...")
    
    for file_name, table_name in files_to_ingest.items():
        file_path = os.path.join(CSV_DIR, file_name)
        
        if os.path.exists(file_path):
            print(f"Mengunduh {file_name} ke tabel {table_name}...")
            df = pd.read_csv(file_path)
            
            # Perbaikan di argumen 'con'
            df.to_sql(table_name, con=engine, if_exists='replace', index=False, schema='public')
            print(f"✅ Berhasil memuat {len(df)} baris ke tabel {table_name}.")
        else:
            raise FileNotFoundError(f"File {file_name} tidak ditemukan di {CSV_DIR}!")

# Inisialisasi DAG
with DAG(
    '01_healthcare_data_pipeline',
    default_args=default_args,
    description='Pipeline ETL utama untuk Data Mart Rumah Sakit',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Menjalankan skrip Python generator data sintetik
    task_generate_data = BashOperator(
        task_id='run_data_generator',
        bash_command='python /opt/airflow/data_generator/src/generator.py',
    )

    # Task 2: Menjalankan fungsi Ingestion menggunakan PythonOperator
    task_ingest_data = PythonOperator(
        task_id='ingest_csv_to_database',
        python_callable=ingest_csv_to_postgres,
    )

    # Mengatur urutan alur data: Buat data dulu -> baru masukkan ke DB
    task_generate_data >> task_ingest_data