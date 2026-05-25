from datetime import datetime, timedelta
import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'dwbi_admin',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def execute_flat_table_ddl():
    """Membaca file SQL dan HANYA mengeksekusi perintah CREATE TABLE"""
    sql_file_path = '/opt/airflow/sql/healthcare_joined_10000.sql'
    hook = PostgresHook(postgres_conn_id='postgres_default')
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    # Memotong bagian INSERT INTO bawaan (agar tabel dibuat kosong)
    sql_ddl = sql_content.split("INSERT INTO")[0] if "INSERT INTO" in sql_content else sql_content
    hook.run(sql_ddl)
    print("Skema tabel 'hospital_encounters' berhasil dibuat.")

def load_denormalized_data():
    """Memuat data CSV ke Postgres"""
    csv_file_path = '/opt/airflow/data/healthcare_joined_10000.csv'
    table_name = 'hospital_encounters'
    
    df = pd.read_csv(csv_file_path)
    df.columns = df.columns.str.lower() # Sinkronisasi nama kolom (huruf kecil)
    
    hook = PostgresHook(postgres_conn_id='postgres_default')
    hook.run(f"TRUNCATE TABLE {table_name};") # Bersihkan data lama
    
    engine = hook.get_sqlalchemy_engine()
    df.to_sql(table_name, con=engine, if_exists='append', index=False, method='multi', chunksize=1000)
    print(f"Berhasil memuat {len(df)} baris data.")

def analyze_denormalized_data():
    """Verifikasi bahwa data sudah masuk ke Postgres"""
    hook = PostgresHook(postgres_conn_id='postgres_default')
    query = "SELECT COUNT(*) as total_row_count FROM hospital_encounters;"
    df_summary = hook.get_pandas_df(query)
    print("\nVERIFIKASI DATA: \n", df_summary.to_string(index=False))

with DAG(
    'etl_denormalized_healthcare',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id='create_table', python_callable=execute_flat_table_ddl)
    t2 = PythonOperator(task_id='load_csv_data', python_callable=load_denormalized_data)
    t3 = PythonOperator(task_id='verify_data', python_callable=analyze_denormalized_data)

    t1 >> t2 >> t3