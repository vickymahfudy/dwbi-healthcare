import os
import random
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Inisialisasi Faker dengan lokalisasi Indonesia
fake = Faker('id_ID')

# Mengunci seed agar data yang dihasilkan selalu konsisten
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Konfigurasi Jumlah Data
TOTAL_PASIEN = 2500
TOTAL_DOKTER = 80
TOTAL_TRANSAKSI_KUNJUNGAN = 12000  # Memenuhi syarat minimal 10.000 baris

print("⏳ Memulai pembuatan dataset sintetik rumah sakit (Bahasa Indonesia & Relasional)...")

# ==========================================
# 1. GENERATE TABEL SUMBER: PASIEN (SOURCE_PASIEN)
# ==========================================
data_pasien = []
jenis_kelamin_opsi = ['Laki-laki', 'Perempuan']

for pasien_id in range(1, TOTAL_PASIEN + 1):
    jk = random.choice(jenis_kelamin_opsi)
    nama = fake.name_male() if jk == 'Laki-laki' else fake.name_female()
    
    data_pasien.append({
        'id_pasien': f'PSN-{pasien_id:05d}',
        'indeks_pasien': 1000 + pasien_id,  # Substitusi dari patIndex
        'kunci_pasien': random.randint(100000, 999999),  # Substitusi dari patient_key
        'nama_pasien': nama,
        'jenis_kelamin': jk,
        'kode_jenis_kelamin': 1 if jk == 'Laki-laki' else 2,  # Substitusi dari sexN
        'tanggal_lahir': fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
        'kategori_usia': random.choice([1, 2, 3, 4, 5, 6]),  # Substitusi dari age_cat
        'grup_usia': random.choice([1, 2, 3, 4]),  # Substitusi dari age_grpN
        'kode_wilayah': random.choice([1, 2, 3, 4]),  # Substitusi dari regionN
        'alamat': fake.street_address(),
        'kota': fake.city()
    })

df_pasien = pd.DataFrame(data_pasien)


# ==========================================
# 2. GENERATE TABEL SUMBER: DOKTER (SOURCE_DOKTER)
# ==========================================
data_dokter = []
spesialisasi_opsi = {
    'Umum': 50000, 'Anak': 150000, 'Penyakit Dalam': 200000, 
    'Bedah': 300000, 'Jantung': 350000, 'Saraf': 250000, 'Mata': 120000
}

for dokter_id in range(1, TOTAL_DOKTER + 1):
    spesialisasi = random.choice(list(spesialisasi_opsi.keys()))
    biaya_konsultasi = spesialisasi_opsi[spesialisasi]
    
    data_dokter.append({
        'id_dokter': f'DKT-{dokter_id:03d}',
        'nama_dokter': fake.name(),
        'spesialisasi': spesialisasi,
        'biaya_konsultasi': biaya_konsultasi,
        'nomor_izin_praktek': f'STR-{random.randint(100000, 999999)}'
    })

df_dokter = pd.DataFrame(data_dokter)


# ==========================================
# 3. GENERATE TABEL SUMBER: KOMORBIDITAS (SOURCE_KOMORBIDITAS)
# ==========================================
data_komorbiditas = []
# Daftar penyakit diterjemahkan/disesuaikan agar relevan sebagai nama kolom bersih
daftar_penyakit = [
    'KETERGANTUNGAN_ALKOHOL_NARKOBA', 'ASMA', 'ARITMIA_JANTUNG', 'PENYAKIT_KATUP_JANTUNG', 'CEREBROVASCULAR',
    'GINJAL_KRONIS', 'NYERI_KRONIS_FIBROMIALGIA', 'GAGAL_JANTUNG_KONGESTIF', 'PPOK', 'DEMENSIA', 'DEPRESI',
    'DIABETES', 'DISLIPIDEMIA', 'EPILEPSI_KEJANG', 'HEPATITIS', 'HIV_AIDS', 'HIPERTENSI',
    'HATI_KANDUNG_EMPEDU_PANKREAS', 'INFARK_MIOKARD_PJK', 'OSTEOARTRITIS', 'KELUMPUHAN', 'TUKAK_LAMBUNG',
    'VASKULAR_PERIFER', 'GAGAL_GINJAL', 'REUMATOLOGI', 'SKIZOFRENIA', 'GANGGUAN_TIDUR',
    'MEROKOK', 'TIROID', 'TUMOR_PADAT', 'KANKER_METASTASIS', 'LEUKEMIA_LIMFOMA', 'KANKER_LAINNYA', 'KANKER_IN_SITU'
]

for pasien in data_pasien:
    baris_komorbid = {'id_pasien': pasien['id_pasien']}
    for penyakit in daftar_penyakit:
        baris_komorbid[penyakit] = random.choices([0, 1], weights=[88, 12])[0]
        
    # Hitung total indeks komorbiditas masa lalu (pre_CCI)
    baris_komorbid['indeks_komorbiditas_pre'] = sum([v for k, v in baris_komorbid.items() if k != 'id_pasien'])
    data_komorbiditas.append(baris_komorbid)

df_komorbiditas = pd.DataFrame(data_komorbiditas)


# ==========================================
# 4. GENERATE TABEL SUMBER: MASTER PROSEDUR (SOURCE_PROSEDUR)
# ==========================================
prosedur_pool = [
    {"Kode_Prosedur": "ICD10-0DTJ", "Kategori_Prosedur": "Bedah", "Deskripsi_Prosedur": "Appendectomy (Open)", "biaya_dasar": 7500.0},
    {"Kode_Prosedur": "CPT-70450", "Kategori_Prosedur": "Radiologi", "Deskripsi_Prosedur": "CT Scan, Kepala/Otak", "biaya_dasar": 800.0},
    {"Kode_Prosedur": "CPT-93000", "Kategori_Prosedur": "Diagnostik", "Deskripsi_Prosedur": "Elektrokardiogram (EKG)", "biaya_dasar": 70.0},
    {"Kode_Prosedur": "CPT-80053", "Kategori_Prosedur": "Laboratorium", "Deskripsi_Prosedur": "Comprehensive Metabolic Panel", "biaya_dasar": 50.0},
    {"Kode_Prosedur": "CPT-71045", "Kategori_Prosedur": "Radiologi", "Deskripsi_Prosedur": "Rontgen Dada, tunggal", "biaya_dasar": 120.0}
]

data_prosedur = []
for proc in prosedur_pool:
    data_prosedur.append({
        'kode_prosedur': proc['Kode_Prosedur'],
        'kategori_prosedur': proc['Kategori_Prosedur'],
        'deskripsi_prosedur': proc['Deskripsi_Prosedur']
    })

df_prosedur = pd.DataFrame(data_prosedur)


# ==========================================
# 5. GENERATE TABEL TRANSAKSI: KUNJUNGAN (SOURCE_KUNJUNGAN)
# ==========================================
data_kunjungan = []
kelas_obat_opsi = ['*ANTIDIABETIK*', '*ANTIHIPERTENSI*', '*STATIN*', '*ANALGESIK*']
tipe_fasilitas_opsi = ['IGD', 'Rawat Jalan', 'Rawat Inap']
status_keluar_opsi = ['Sembuh', 'Dirujuk', 'Pulang Paksa', 'Meninggal']
metode_pembayaran_opsi = ['BPJS', 'Asuransi Swasta', 'Mandiri']

start_date = datetime(2025, 1, 1)

for kunjungan_id in range(1, TOTAL_TRANSAKSI_KUNJUNGAN + 1):
    pasien = random.choice(data_pasien)
    dokter = random.choice(data_dokter)
    proc = random.choice(prosedur_pool)
    
    tipe_fasilitas = random.choice(tipe_fasilitas_opsi)
    metode_pembayaran = random.choice(metode_pembayaran_opsi)
    pdc_val = round(random.uniform(0.05, 1.0), 4)
    
    # Logika Lama Rawat Inap
    if tipe_fasilitas == 'Rawat Inap':
        lama_rawat = random.randint(1, 14)
        status_keluar = random.choices(status_keluar_opsi, weights=[80, 12, 6, 2])[0]
    else:
        lama_rawat = 0
        status_keluar = 'Sembuh'

    # Biaya Masa Depan (Post-Period Cost)
    biaya_obat_post = round(random.uniform(10.0, 6000.0), 2)
    biaya_bedah_post = round(random.uniform(0.0, 15000.0), 2)
    biaya_rawat_inap_post = round(random.choice([0.0, 0.0, random.uniform(1000.0, 8000.0)]), 2)
    biaya_igd_post = round(random.choice([0.0, random.uniform(200.0, 1500.0)]), 2)
    biaya_medis_post = biaya_bedah_post + biaya_rawat_inap_post + biaya_igd_post
    
    # Biaya Masa Lalu (Pre-Period Cost)
    biaya_obat_pre = round(random.uniform(10.0, 5000.0), 2)
    biaya_bedah_pre = round(random.uniform(0.0, 12000.0), 2)
    biaya_rawat_inap_pre = round(random.choice([0.0, 0.0, random.uniform(1000.0, 7000.0)]), 2)
    biaya_igd_pre = round(random.choice([0.0, random.uniform(200.0, 1200.0)]), 2)
    biaya_medis_pre = biaya_bedah_pre + biaya_rawat_inap_pre + biaya_igd_pre

    nilai_copay = random.uniform(0.01, 100.0)
    tgl_kunjungan = start_date + timedelta(days=random.randint(0, 450))

    data_kunjungan.append({
        'id_kunjungan': f'TX-{kunjungan_id:06d}',
        'id_pasien': pasien['id_pasien'],
        'id_dokter': dokter['id_dokter'],
        'kode_prosedur': proc['Kode_Prosedur'],
        'tanggal_kunjungan': tgl_kunjungan.strftime('%Y-%m-%d %H:%M:%S'),
        'tipe_fasilitas': tipe_fasilitas,
        'lama_rawat_hari': lama_rawat,
        'status_keluar': status_keluar,
        'metode_pembayaran': metode_pembayaran,
        'biaya_prosedur': round(proc['biaya_dasar'] + random.uniform(-10, 300), 2),  # Substitusi dari Cost
        'kepatuhan_obat_pdc': pdc_val,  # Substitusi dari pdc
        'bendera_kepatuhan_80': 1 if pdc_val >= 0.8 else 0,  # Substitusi dari pdc_80_flag
        'kategori_pdc': random.choice([0, 1, 2, 3]),  # Substitusi dari pdc_cat
        'kelas_obat': random.choice(kelas_obat_opsi),  # Substitusi dari drug_class
        'kode_tipe_produk': random.choice([1, 2, 3]),  # Substitusi dari idx_prodtypeN
        'kode_tipe_bayar': random.choice([1, 2, 4]),  # Substitusi dari idx_paytypN
        'biaya_bersama_copay': round(nilai_copay, 2),  # Substitusi dari idx_copay
        'log_biaya_bersama_copay': round(np.log(nilai_copay), 4),  # Substitusi dari log_idx_copay
        
        # Metrik Utilitas & Finansial Masa Depan (Post-Period)
        'jumlah_rawat_inap_post': random.randint(0, 5),  # Substitusi dari num_ip_post
        'total_hari_rawat_post': random.randint(0, 14),  # Substitusi dari total_los_post
        'jumlah_rawat_jalan_post': random.randint(0, 25),  # Substitusi dari num_op_post
        'jumlah_igd_post': random.randint(0, 3),  # Substitusi dari num_er_post
        'jumlah_ndc_post': random.randint(0, 40),
        'jumlah_gpi6_post': random.randint(0, 15),
        'penyesuaian_total_30hari_post': round(random.uniform(1.0, 60.0), 4),  # Substitusi dari adjust_total_30d_post
        'tingkat_generik_post': round(random.uniform(0.1, 1.0), 4),  # Substitusi dari generic_rate_post
        'bendera_rawat_inap_post': 1 if biaya_rawat_inap_post > 0 else 0,
        'bendera_igd_post': 1 if biaya_igd_post > 0 else 0,
        'biaya_rawat_inap_post': biaya_rawat_inap_post,
        'biaya_igd_post': biaya_igd_post,
        'biaya_obat_post': biaya_obat_post,
        'biaya_rawat_jalan_post': biaya_bedah_post,
        'biaya_medis_total_post': round(biaya_medis_post, 2),
        'biaya_keseluruhan_post': round(biaya_medis_post + biaya_obat_post, 2),
        
        # Metrik Utilitas & Finansial Masa Lalu (Pre-Period)
        'biaya_rawat_inap_pre': biaya_rawat_inap_pre,
        'biaya_igd_pre': biaya_igd_pre,
        'biaya_obat_pre': biaya_obat_pre,
        'biaya_rawat_jalan_pre': biaya_bedah_pre,
        'biaya_medis_total_pre': round(biaya_medis_pre, 2),
        'biaya_keseluruhan_pre': round(biaya_medis_pre + biaya_obat_pre, 2),
        'jumlah_rawat_inap_pre': random.randint(0, 4),  # Substitusi dari num_ip
        'total_hari_rawat_pre': random.randint(0, 12),  # Substitusi dari total_los
        'jumlah_rawat_jalan_pre': random.randint(0, 20),  # Substitusi dari num_op
        'jumlah_igd_pre': random.randint(0, 2),  # Substitusi dari num_er
        'jumlah_ndc_pre': random.randint(0, 35),
        'jumlah_gpi6_pre': random.randint(0, 12),
        'penyesuaian_total_30hari_pre': round(random.uniform(1.0, 50.0), 4),
        'tingkat_generik_pre': round(random.uniform(0.1, 1.0), 4),
        'bendera_rawat_inap_pre': 1 if biaya_rawat_inap_pre > 0 else 0,
        'bendera_igd_pre': 1 if biaya_igd_pre > 0 else 0,
        'kategori_total_pre': random.randint(1, 8),
        
        # Rincian Obat Generik vs Bermerek (Brand)
        'jumlah_obat_generik_pre': random.randint(0, 20),
        'jumlah_obat_bermerek_pre': random.randint(0, 15),
        'biaya_obat_generik_pre': round(random.uniform(0.0, 3000.0), 2),
        'biaya_obat_bermerek_pre': round(random.uniform(0.0, 4000.0), 2),
        'rasio_biaya_generik_pre': round(random.uniform(0.0, 1.0), 4),
        'jumlah_obat_generik_post': random.randint(0, 25),
        'jumlah_obat_bermerek_post': random.randint(0, 15),
        'biaya_obat_generik_post': round(random.uniform(0.0, 3500.0), 2),
        'biaya_obat_bermerek_post': round(random.uniform(0.0, 4500.0), 2),
        'rasio_biaya_generik_post': round(random.uniform(0.0, 1.0), 4),
        
        # Fitur Nilai Transformasi Logaritma
        'log_biaya_rawat_inap_pre': round(np.log(biaya_rawat_inap_pre + 1), 4),
        'log_biaya_igd_pre': round(np.log(biaya_igd_pre + 1), 4),
        'log_biaya_rawat_jalan_pre': round(np.log(biaya_bedah_pre + 1), 4),
        'log_biaya_obat_pre': round(np.log(biaya_obat_pre + 1), 4)
    })

df_kunjungan = pd.DataFrame(data_kunjungan)


# ==========================================
# 4. MENYIMPAN DATA KE CSV
# ==========================================
OUTPUT_DIR = '/opt/airflow/data_generator/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

df_pasien.to_csv(os.path.join(OUTPUT_DIR, 'source_pasien.csv'), index=False)
df_dokter.to_csv(os.path.join(OUTPUT_DIR, 'source_dokter.csv'), index=False)
df_komorbiditas.to_csv(os.path.join(OUTPUT_DIR, 'source_komorbiditas.csv'), index=False)
df_prosedur.to_csv(os.path.join(OUTPUT_DIR, 'source_prosedur.csv'), index=False)
df_kunjungan.to_csv(os.path.join(OUTPUT_DIR, 'source_kunjungan.csv'), index=False)

print("✅ Pembuatan dataset selesai!")
print(f"   - source_pasien.csv      : {len(df_pasien)} baris")
print(f"   - source_dokter.csv      : {len(df_dokter)} baris")
print(f"   - source_komorbiditas.csv: {len(df_komorbiditas)} baris")
print(f"   - source_prosedur.csv     : {len(df_prosedur)} baris")
print(f"   - source_kunjungan.csv   : {len(df_kunjungan)} baris")