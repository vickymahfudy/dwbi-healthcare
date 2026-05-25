# Proyek Data Warehouse & Business Intelligence - Bagian I

**Departemen Ilmu Komputer dan Elektronika, Universitas Gadjah Mada**

Proyek ini merupakan bagian pertama dari rangkaian tugas besar semester untuk mata kuliah Data Warehouse & Business Intelligence. Fokus utama dari proyek ini adalah menerapkan metodologi *Kimball Dimensional Modeling*, membangun pipa data (pipeline) ETL/ELT, dan menghasilkan Data Mart yang bersih serta siap digunakan untuk keperluan visualisasi pada tahap berikutnya.

---

## 🏥 Domain Terpilih: Healthcare (Rumah Sakit)

Dalam proyek ini, kami memilih domain **Healthcare (Rumah Sakit)** yang didasarkan pada Bab 14 buku *The Data Warehouse Toolkit* oleh Ralph Kimball. 

Analisis analitik pada domain ini akan berfokus pada proses bisnis **Kunjungan Pasien (Patient Admissions/Visits)**. Data mart yang dibangun bertujuan untuk membantu manajemen rumah sakit dan tenaga medis dalam memantau tren kunjungan, efisiensi tindakan medis, analisis diagnosis penyakit, serta manajemen operasional fasilitas kesehatan secara keseluruhan.

---

## 📂 Struktur Repositori

Repositori ini disusun menggunakan struktur berbasis komponen (*monorepo style*) untuk memisahkan setiap tahapan teknologi yang digunakan agar kolaborasi tim berjalan dengan rapi:

```text
dwbi-healthcare/
├── .github/
│   └── workflows/          # (Opsional) Untuk CI/CD seperti dbt-test otomatis
├── data_generator/         # Bagian Pembuatan Dataset (Tahap 3)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── generator.py    # Skrip utama menggunakan Faker/mimesis
│   │   └── schema.sql      # Skema DDL untuk tabel sumber (OLTP mentah)
│   ├── requirements.txt    # Library Python (faker, psycopg2, dll.)
│   └── README.md
├── airflow/                # Bagian Orchestration (Tahap 4)
│   ├── dags/
│   │   └── dwbi_pipeline_dag.py  # DAG Airflow untuk Ingestion & memicu dbt
│   ├── plugins/
│   ├── docker-compose.yaml # Jika tim menjalankan Airflow lewat Docker
│   └── README.md
├── dbt_project/            # Bagian Transformasi data mart (Tahap 4 & 5)
│   ├── models/
│   │   ├── staging/        # stg_* (Membaca data mentah dari source)
│   │   ├── intermediate/   # int_* (Join, pembersihan, logika bisnis)
│   │   └── marts/          # fct_* dan dim_* (Data Mart Final)
│   ├── tests/              # dbt custom tests
│   ├── dbt_project.yml     # Konfigurasi project dbt
│   ├── packages.yml        # dbt packages (misal: dbt_utils)
│   └── profiles.yml        # Konfigurasi koneksi ke DB (Postgres/DuckDB)
├── analytics_queries/      # Bagian Verifikasi & Validasi (Tahap 6)
│   ├── query_1_business_q.sql
│   ├── query_2_data_quality.sql
│   └── ...
├── docs/                   # Dokumentasi Arsitektur & Kimball Bus Matrix
│   └── bus_matrix.md
├── .gitignore              # Mengecualikan file .env, logs, dbt_modules, dll.
└── README.md               # Panduan utama cara menjalankan seluruh project

```

---

## Persiapan lingkungan kerja

1. Masuk ke dalam folder proyek utama.
2. Mempersiapkan virtual environment (venv) untuk lingkungan kerja dengan menjalankan perintah berikut:

   ```
   python -m venv .venv
   ```
3. mengaktifkan venv dengan perintah berikut:

   ```
   Windows:
   .\.venv\Scripts\activate

   Linux:
   source venv/bin/activate

   atau

   source venv/bin/activate.fish
   ```
4. Setelah itu jalankan perintah berikut untuk melalkukan instalasi modul-modul python yang akan digunakan :

   ```
   ip install -r ./requirements.txt
   ```

Catatan: untuk keluar dari venv, gunakan perintah ``deactivate``
---

## 👥 Pembagian Tugas & Tanggung Jawab (PIC)

Untuk memastikan kolaborasi berjalan lancar, tim dibagi menjadi 4 peran utama berdasarkan alur data dari hulu ke hilir:

1. **Data Engineer (Upstream & Ingestion)**

* **Tanggung Jawab:** Pembuatan dataset sintetik transaksional (min. 10.000 baris) menggunakan Python (`Faker`) yang merepresentasikan proses bisnis rumah sakit, merancang skema data mentah (*source tables*), dan mengurus proses awal pemuatan data (*ingestion*).

2. **Workflow & Orchestration Coordinator**

* **Tanggung Jawab:** Mengonfigurasi *environment* tim menggunakan Docker, menyusun arsitektur DAG di Apache Airflow untuk mengotomatisasi seluruh pipeline (*ingestion*, *staging*, hingga memicu dbt), serta menangani *error handling/retry logic*.

3. **Analytics Engineer (Data Modeling & dbt Developer)**

* **Tanggung Jawab:** Merancang *Dimensional Modeling* (*Star Schema*) termasuk menentukan *grain*, *fact table*, *dimension table*, dan strategi *Slowly Changing Dimensions* (SCD). Mengimplementasikan transformasi data berlapis menggunakan dbt (`stg_*`, `int_*`, `fct_*`, `dim_*`).

4. **BI Developer & Data Quality Analyst**

* **Tanggung Jawab:** Merumuskan pertanyaan analitik utama dari *stakeholder*, menulis query analitik SQL kompleks untuk menjawab kebutuhan bisnis, melakukan pengujian kualitas data (*data quality check*), dan menganalisis performa query (*indexing/execution plan*).

---