from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'kelompok_healthcare',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    '01_healthcare_data_pipeline',
    default_args=default_args,
    description='Pipeline ETL utama untuk Data Mart Rumah Sakit',
    schedule_interval=None,  # Kita set manual dulu untuk development
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Menjalankan skrip Python generator data sintetik
    task_generate_data = BashOperator(
        task_id='run_data_generator',
        bash_command='python /opt/airflow/data_generator/src/generator.py',
    )

    # Task 2: Tempat penampung (placeholder) untuk langkah Ingestion berikutnya
    task_ingest_data = BashOperator(
        task_id='ingest_to_database',
        bash_command='echo "Langkah berikutnya: Memasukkan data CSV ke PostgreSQL Staging..."',
    )

    # Mengatur urutan jalannya task
    task_generate_data >> task_ingest_data