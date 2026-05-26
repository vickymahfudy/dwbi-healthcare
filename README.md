# 🏥 Data Warehouse & Business Intelligence - Healthcare Analytics

**Departemen Ilmu Komputer dan Elektronika, Universitas Gadjah Mada**

Proyek ini merupakan implementasi lengkap Data Warehouse dan Business Intelligence untuk domain Healthcare (Rumah Sakit) menggunakan metodologi **Kimball Dimensional Modeling**. Proyek ini mencakup seluruh pipeline data dari data generation, orchestration, transformation, hingga analytics query yang siap digunakan untuk visualisasi dan decision making.

---

## Daftar Isi

- [Domain & Proses Bisnis](#-domain--proses-bisnis)
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Struktur Repositori](#-struktur-repositori)
- [Tech Stack](#-tech-stack)
- [Instalasi & Setup](#-instalasi--setup)
- [Cara Menjalankan Pipeline](#-cara-menjalankan-pipeline)
- [Data Model](#-data-model)
- [Analytics Queries](#-analytics-queries)
- [Dokumentasi dbt](#-dokumentasi-dbt)
- [Tim & Kontributor](#-tim--kontributor)

---

## Domain & Proses Bisnis

### Domain: Healthcare (Rumah Sakit)

Proyek ini mengimplementasikan Data Warehouse untuk domain **Healthcare** berdasarkan Bab 14 buku *The Data Warehouse Toolkit* oleh Ralph Kimball.

### Proses Bisnis Utama: Kunjungan Pasien (Patient Visits)

Data mart yang dibangun berfokus pada analisis **Kunjungan Pasien** yang mencakup:

- **Tren Kunjungan**: Analisis pola kunjungan berdasarkan waktu, lokasi, dan demografi
- **Analisis Finansial**: Pendapatan, biaya perawatan, metode pembayaran
- **Kinerja Dokter**: Produktivitas dan spesialisasi dokter
- **Operasional Fasilitas**: Utilisasi fasilitas, length of stay, status keluar pasien
- **Analisis Klinis**: Distribusi diagnosis, tindakan medis, penggunaan obat

---

## Arsitektur Sistem

```
┌─────────────────┐
│  Data Generator │  ← Faker/Python (10,000+ records)
│   (Python)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Source CSV    │  ← source_pasien.csv, source_dokter.csv, source_kunjungan.csv
│     Files       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Apache Airflow │  ← Orchestration & Scheduling
│   (Docker)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ← Source Tables (OLTP)
│  (src_* tables) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      dbt        │  ← Transformation (ELT)
│  Transformation │     - Staging (stg_*)
│                 │     - Dimensions (dim_*)
│                 │     - Facts (fact_*)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Warehouse │  ← Star Schema (Dimensional Model)
│  (PostgreSQL)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analytics Layer │  ← Business Intelligence Queries
│  (SQL Queries)  │
└─────────────────┘
```

---

## Struktur Repositori

```
dwbi-healthcare/
├── data_generator/              # 📊 Data Generation
│   ├── src/
│   │   └── generator.py         # Script generator data menggunakan Faker
│   ├── output/                  # Output CSV files
│   │   ├── source_pasien.csv
│   │   ├── source_dokter.csv
│   │   └── source_kunjungan.csv
│   └── Multi-disease.py         # Generator tambahan untuk diagnosis
│
├── airflow/                     # 🔄 Orchestration
│   ├── dags/
│   │   └── 01_pipeline_healthcare.py  # DAG utama pipeline
│   ├── docker-compose.yaml      # Docker setup untuk Airflow
│   ├── Dockerfile               # Custom Airflow image
│   ├── .env                     # Environment variables
│   └── logs/                    # Airflow execution logs
│
├── dbt_project/                 # 🔧 Data Transformation
│   ├── models/
│   │   ├── staging/             # Layer 1: Raw data staging
│   │   │   ├── sources.yml      # Source definitions
│   │   │   ├── stg_pasien.sql
│   │   │   ├── stg_dokter.sql
│   │   │   └── stg_kunjungan.sql
│   │   ├── dimensions/          # Layer 2: Dimension tables
│   │   │   ├── dim_pasien.sql
│   │   │   ├── dim_dokter.sql
│   │   │   ├── dim_fasilitas.sql
│   │   │   ├── dim_pembayaran.sql
│   │   │   └── dim_waktu.sql
│   │   └── marts/               # Layer 3: Fact tables
│   │       ├── fact_kunjungan.sql
│   │       └── schema.yml       # dbt tests & documentation
│   ├── dbt_project.yml          # dbt configuration
│   ├── profiles.yml             # Database connection profiles
│   ├── dbt_manifest.yml         # Auto-generation manifest
│   └── target/                  # dbt compiled artifacts & docs
│
├── analytics_queries/           # 📈 Business Intelligence Queries
│   ├── 01_total_pendapatan_per_fasilitas.sql
│   ├── 02_kinerja_dokter_per_spesialisasi.sql
│   ├── 03_distribusi_metode_pembayaran.sql
│   ├── 04_analisis_length_of_stay.sql
│   ├── 05_tren_kunjungan_bulanan.sql
│   ├── 06_status_keluar_rawat_inap.sql
│   ├── 07_breakdown_komponen_biaya.sql
│   ├── 08_kunjungan_per_kota_asal.sql
│   ├── 09_profil_demografi_pasien.sql
│   ├── 10_biaya_obat_igd_vs_rawat_jalan.sql
│   ├── 11_top_5_dokter_teraktif.sql
│   └── 12_average_ticket_size.sql
│
├── LaTeX/                       # 📄 Dokumentasi Akademik
│   └── modul/                   # Makalah & Slide Presentasi
│
├── docs/                        # 📚 Dokumentasi Teknis
├── logs/                        # 📝 Application logs
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md                    # Dokumentasi ini
```

---

## Tech Stack

### Data Generation
- **Python 3.x** - Programming language
- **Faker** - Synthetic data generation
- **Pandas** - Data manipulation

### Orchestration
- **Apache Airflow 2.10.2** - Workflow orchestration
- **Docker & Docker Compose** - Containerization
- **Celery** - Distributed task queue
- **Redis** - Message broker

### Database
- **PostgreSQL 13** - Data warehouse database
- **psycopg2** - PostgreSQL adapter for Python

### Transformation
- **dbt (Data Build Tool)** - Data transformation framework
- **SQLAlchemy** - SQL toolkit

### Analytics & Visualization
- **SQL** - Analytics queries
- **Jupyter Notebook** - Interactive analysis
- **Matplotlib & Seaborn** - Data visualization

---

## Instalasi & Setup

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/vickymahfudy/dwbi-healthcare.git
cd dwbi-healthcare
```

### 2. Setup Python Virtual Environment

```bash
# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Windows:
.\.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Airflow dengan Docker

```bash
cd airflow

# Set Airflow UID (Linux/macOS)
echo "AIRFLOW_UID=$(id -u)" > .env

# Start Airflow services
docker-compose up -d

# Tunggu hingga semua services running (±2-3 menit)
docker-compose ps
```

### 4. Akses Airflow Web UI

- URL: http://localhost:8000
- Username: `airflow`
- Password: `airflow`

### 5. Akses PostgreSQL Database

```bash
# Connection details:
Host: localhost
Port: 5050
Database: airflow
Username: airflow
Password: airflow
```

---

## Cara Menjalankan Pipeline

### Menjalankan Full Pipeline

1. **Akses Airflow UI** di http://localhost:8000

2. **Aktifkan DAG** `01_healthcare_data_pipeline`

3. **Trigger DAG** secara manual dengan klik tombol "Play"

4. **Monitor Eksekusi** - Pipeline akan menjalankan task berikut secara berurutan:

   ```
   run_data_generator 
      ↓
   ingest_csv_to_database
      ↓
   auto_generate_dbt_files
      ↓
   dbt_run_transformation
      ↓
   dbt_data_quality_test
      ↓
   dbt_generate_docs
      ↓
   dbt_serve_docs
   ```

### Detail Setiap Task

#### Task 1: `run_data_generator`
- Generate synthetic data menggunakan Faker
- Output: 3 CSV files di `data_generator/output/`
- Data: 10,000+ records untuk pasien, dokter, dan kunjungan

#### Task 2: `ingest_csv_to_database`
- Load CSV files ke PostgreSQL
- Tabel: `src_pasien`, `src_dokter`, `src_kunjungan`
- Mode: Truncate & Load (idempotent)

#### Task 3: `auto_generate_dbt_files`
- Download manifest dari GitHub
- Auto-generate dbt model files
- Create `sources.yml` otomatis

#### Task 4: `dbt_run_transformation`
- Execute dbt models
- Build staging → dimensions → facts
- Materialisasi Star Schema

#### Task 5: `dbt_data_quality_test`
- Run dbt tests
- Validasi data quality & integrity
- Check constraints & relationships

#### Task 6: `dbt_generate_docs`
- Generate dbt documentation
- Create data lineage graph
- Build catalog

#### Task 7: `dbt_serve_docs`
- Serve dbt docs di http://localhost:8081
- Interactive documentation & lineage

---

## Data Model

### Star Schema Design

#### Fact Table

**`fact_kunjungan`** - Grain: One row per patient visit
- `kunjungan_key` (PK)
- `pasien_key` (FK → dim_pasien)
- `dokter_key` (FK → dim_dokter)
- `fasilitas_key` (FK → dim_fasilitas)
- `pembayaran_key` (FK → dim_pembayaran)
- `tanggal_kunjungan_key` (FK → dim_waktu)
- `tanggal_keluar_key` (FK → dim_waktu)
- **Measures:**
  - `total_biaya`
  - `biaya_konsultasi`
  - `biaya_tindakan`
  - `biaya_obat`
  - `biaya_lab`
  - `length_of_stay`

#### Dimension Tables

**`dim_pasien`** - Patient dimension
- `pasien_key` (PK)
- `pasien_id` (Natural Key)
- `nama_pasien`
- `tanggal_lahir`
- `umur`
- `jenis_kelamin`
- `golongan_darah`
- `alamat`, `kota`, `provinsi`
- `no_telepon`

**`dim_dokter`** - Doctor dimension
- `dokter_key` (PK)
- `dokter_id` (Natural Key)
- `nama_dokter`
- `spesialisasi`
- `no_str` (Surat Tanda Registrasi)
- `tahun_lulus`
- `pengalaman_tahun`

**`dim_fasilitas`** - Facility dimension
- `fasilitas_key` (PK)
- `jenis_fasilitas` (IGD, Rawat Jalan, Rawat Inap)
- `nama_ruangan`
- `kelas_perawatan`

**`dim_pembayaran`** - Payment dimension
- `pembayaran_key` (PK)
- `metode_pembayaran` (BPJS, Asuransi Swasta, Tunai)
- `nama_asuransi`
- `no_polis`

**`dim_waktu`** - Time dimension
- `tanggal_key` (PK)
- `tanggal`
- `tahun`, `bulan`, `hari`
- `nama_bulan`, `nama_hari`
- `kuartal`, `semester`
- `is_weekend`, `is_holiday`

---

## Analytics Queries

Proyek ini menyediakan 12 analytics queries siap pakai di folder `analytics_queries/`:

1. **Total Pendapatan per Fasilitas** - Revenue analysis by facility type
2. **Kinerja Dokter per Spesialisasi** - Doctor performance metrics
3. **Distribusi Metode Pembayaran** - Payment method distribution
4. **Analisis Length of Stay** - Average stay duration analysis
5. **Tren Kunjungan Bulanan** - Monthly visit trends
6. **Status Keluar Rawat Inap** - Discharge status analysis
7. **Breakdown Komponen Biaya** - Cost component breakdown
8. **Kunjungan per Kota Asal** - Geographic distribution
9. **Profil Demografi Pasien** - Patient demographics
10. **Biaya Obat IGD vs Rawat Jalan** - Medication cost comparison
11. **Top 5 Dokter Teraktif** - Most active doctors
12. **Average Ticket Size** - Average transaction value

### Contoh Query

```sql
-- Total Pendapatan per Fasilitas
SELECT 
    f.jenis_fasilitas,
    COUNT(DISTINCT fk.kunjungan_key) as total_kunjungan,
    SUM(fk.total_biaya) as total_pendapatan,
    AVG(fk.total_biaya) as rata_rata_biaya
FROM fact_kunjungan fk
JOIN dim_fasilitas f ON fk.fasilitas_key = f.fasilitas_key
GROUP BY f.jenis_fasilitas
ORDER BY total_pendapatan DESC;
```

---

## Dokumentasi dbt

### Akses dbt Documentation

Setelah pipeline selesai running, akses dokumentasi interaktif dbt di:

**http://localhost:8081**

Dokumentasi ini mencakup:
- **Data Lineage Graph** - Visual dependency graph
- **Model Documentation** - Deskripsi setiap model
- **Column Details** - Metadata kolom & tipe data
- **Test Results** - Status data quality tests
- **Source Freshness** - Data freshness checks

### dbt Commands (Manual)

```bash
# Masuk ke container Airflow
docker exec -it airflow-webserver-1 bash

# Navigate to dbt project
cd /opt/airflow/dbt_project

# Run models
dbt run --target docker_env --profiles-dir .

# Run tests
dbt test --target docker_env --profiles-dir .

# Generate docs
dbt docs generate --target docker_env --profiles-dir .

# Serve docs
dbt docs serve --port 8081 --target docker_env --profiles-dir .
```

---

## Tim & Kontributor

### Pembagian Peran

1. **Sinta Siti Nuriah: Data Engineer (Upstream & Ingestion)**
   - Pembuatan dataset sintetik (10,000+ records)
   - Design skema source tables
   - Implementasi data ingestion

2. **Vicky Mahfudy: Workflow & Orchestration Coordinator**
   - Setup Docker environment
   - Konfigurasi Apache Airflow
   - Implementasi DAG & error handling

3. **Engelbertus Rande: Analytics Engineer (Data Modeling & dbt Developer)**
   - Design dimensional model (Star Schema)
   - Implementasi dbt transformations
   - Data quality testing

4. **Gilbert Fandiliam Mooy: BI Developer & Data Quality Analyst**
   - Perumusan business questions
   - Implementasi analytics queries
   - Data validation & performance tuning

---

## Catatan Penting

### Troubleshooting

**Port sudah digunakan:**
```bash
# Check port usage
lsof -i :8000  # Airflow
lsof -i :5050  # PostgreSQL
lsof -i :8081  # dbt docs

# Kill process
kill -9 <PID>
```

**Reset Airflow:**
```bash
cd airflow
docker-compose down -v
docker-compose up -d
```

**Reset Database:**
```bash
# Connect to PostgreSQL
docker exec -it airflow-postgres-1 psql -U airflow

# Drop tables
DROP TABLE IF EXISTS src_pasien, src_dokter, src_kunjungan CASCADE;
DROP TABLE IF EXISTS dim_pasien, dim_dokter, dim_fasilitas, dim_pembayaran, dim_waktu CASCADE;
DROP TABLE IF EXISTS fact_kunjungan CASCADE;
```

### Best Practices

- Selalu jalankan pipeline dari Airflow UI untuk tracking & logging
- Monitor logs di `airflow/logs/` untuk debugging
- Backup database sebelum eksperimen besar
- Gunakan dbt tests untuk validasi setiap perubahan model
- Review dbt docs untuk memahami data lineage

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik di Universitas Gadjah Mada.

---

## Referensi

- [The Data Warehouse Toolkit - Ralph Kimball](https://www.kimballgroup.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Kimball Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)

---

**Departemen Ilmu Komputer dan Elektronika**  
**Universitas Gadjah Mada**  
**2026**