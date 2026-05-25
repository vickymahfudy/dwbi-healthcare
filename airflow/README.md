# Healthcare ETL Pipeline with Airflow & PostgreSQL

## 📁 Struktur Proyek

```text
explore_00/
├── dags/
│   └── dag_healthcare.py               # Script pipeline ETL Airflow
├── data/
│   └── healthcare_joined_10000.csv    # Dataset mentah rumah sakit (10.000 baris)
├── sql/
│   └── healthcare_joined_10000.sql    # DDL awal untuk pembuatan tabel
├── analytics_notebook.ipynb           # Notebook analisis & visualisasi data
├── docker-compose.yaml                # Konfigurasi Docker
└── README.md                          # Dokumentasi utama proyek
```

---

# 🛠️ Prasyarat Sistem (Prerequisites)

Sebelum menjalankan proyek, pastikan laptop Anda telah menginstal:

- Docker Desktop (Docker Engine & Docker Compose)
- Python 3.10+
- Jupyter Notebook
- Lakukan penginstalan modul ``faker pandas sqlalchemy psycopg2 psycopg2-binary`` secara global untuk python (jalankan di luar mode venv) dengan cara:

  ``` cmd\bash
  pip install faker pandas sqlalchemy psycopg2 psycopg2-binary
  ```

---

# 🚀 Langkah 1 — Menjalankan Environment Airflow & Database

Buka Terminal / CMD lalu masuk ke folder proyek:

```bash
cd explore_00
```

## 1. Menyalakan Container Docker

```bash
docker-compose up -d
```

## 2. Inisialisasi Database Internal Airflow

```bash
docker-compose run --rm webserver airflow db init
```

## 3. Membuat User Administrator Airflow

```bash
docker-compose run --rm webserver airflow users create \
    --username admin \
    --firstname Sinta \
    --lastname Admin \
    --role Admin \
    --email admin@hospital.com \
    --password admin
```

---

# 🖥️ Langkah 2 — Akses Web UI & Eksekusi Pipeline

Setelah seluruh container berstatus **healthy**, buka browser dan akses layanan berikut:

| Layanan                  | URL                   | Kredensial                 |
| ------------------------ | --------------------- | -------------------------- |
| Apache Airflow Dashboard | http://localhost:8080 | admin / admin              |
| pgAdmin 4                | http://localhost:5050 | admin@hospital.com / admin |

---

# 🔄 Menjalankan DAG di Airflow

1. Login ke Airflow Web UI.
2. Cari DAG bernama:

```text
etl_denormalized_healthcare
```

3. Aktifkan DAG dengan menggeser toggle menjadi warna biru.
4. Klik tombol **Play / Trigger DAG**.
5. Pastikan seluruh task berikut berhasil:

```text
create_table ➜ load_csv_data ➜ verify_data
```

Semua task harus berwarna **hijau tua (success)**.

---

# 🔌 Kredensial Koneksi PostgreSQL

Database PostgreSQL dapat diakses dari dua environment berbeda.

## A. Koneksi dari Dalam Docker

Digunakan oleh:
- Airflow
- pgAdmin
- Container internal lainnya

| Parameter | Value    |
| --------- | -------- |
| Host      | postgres |
| Port      | 5432     |
| Database  | airflow  |
| Username  | airflow  |
| Password  | airflow  |

---

## B. Koneksi dari Luar Docker

Digunakan oleh:
- DBeaver
- Jupyter Notebook lokal
- Python lokal

| Parameter | Value     |
| --------- | --------- |
| Host      | localhost |
| Port      | 5430      |
| Database  | airflow   |
| Username  | airflow   |
| Password  | airflow   |

---

# 📓 Langkah 3 — Analisis Data Menggunakan Jupyter Notebook

Setelah Airflow berhasil memuat 10.000 baris data ke PostgreSQL, Anda dapat mulai melakukan analisis data.

---

## 1. Install Library Python

Pastikan terlebih dahulu sudah masuk ke dalam mode venv, dapat dilihat petunjuknya pada ([../README.md](README.md)) di folder proyek utama.
---

## 2. Jalankan Jupyter Notebook

```bash
jupyter notebook
```

---

## 3. Contoh Koneksi & Query PostgreSQL

Buat file notebook baru bernama:

```text
analytics_notebook.ipynb
```

Lalu gunakan script berikut:

```python
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Koneksi ke PostgreSQL Docker
engine = create_engine(
    'postgresql+psycopg2://airflow:airflow@localhost:5430/airflow'
)

# Ambil seluruh data hasil ETL
df = pd.read_sql(
    'SELECT * FROM hospital_encounters',
    con=engine
)

print(f"Sukses memuat {len(df)} baris data.")

# Query analisis sederhana
query = """
SELECT
    age_cat,
    AVG(post_total_cost) AS rata_biaya
FROM hospital_encounters
GROUP BY age_cat
ORDER BY age_cat;
"""

df_cost = pd.read_sql(query, con=engine)

# Visualisasi
sns.barplot(
    x='age_cat',
    y='rata_biaya',
    data=df_cost,
    palette='Blues_d'
)

plt.title('Rata-rata Biaya Perawatan per Kategori Umur')
plt.xlabel('Kategori Umur')
plt.ylabel('Rata-rata Biaya')
plt.show()
```

---

# 🧹 Hard Reset Environment

Jika database mengalami masalah, data ganda, atau container corrupt, lakukan reset total:

```bash
docker-compose down -v

docker-compose up -d

docker-compose run --rm webserver airflow db init
```

Setelah hard reset, ulangi proses pembuatan user administrator Airflow.

---

# ✅ Output Pipeline

Pipeline ETL ini akan:

- Membaca file CSV healthcare
- Membuat tabel PostgreSQL otomatis
- Melakukan loading data ke database
- Memvalidasi jumlah data
- Menyediakan data siap analisis di Jupyter Notebook

---

# 📌 Teknologi yang Digunakan

- Apache Airflow
- PostgreSQL
- pgAdmin
- Docker & Docker Compose
- Pandas
- SQLAlchemy
- Matplotlib
- Seaborn
- Jupyter Notebook