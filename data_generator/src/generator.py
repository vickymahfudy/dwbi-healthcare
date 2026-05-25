import os
import random
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Inisialisasi Faker dengan lokalisasi Indonesia agar nama dan datanya realistis
fake = Faker('id_ID')

# Mengunci seed agar data yang dihasilkan selalu konsisten setiap kali dijalankan
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Konfigurasi Jumlah Data
TOTAL_PASIEN = 2500
TOTAL_DOKTER = 80
TOTAL_TRANSAKSI_KUNJUNGAN = 12000  # Memenuhi syarat minimal 10.000 baris

print("⏳ Memulai pembuatan dataset sintetik rumah sakit pendekatan RELASIONAL...")

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
        'patIndex': 1000 + pasien_id,  # Tetap menyimpan index numerik asli data awal
        'patient_key': random.randint(100000, 999999),
        'nama_pasien': nama,
        'jenis_kelamin': jk,
        'sexN': 1 if jk == 'Laki-laki' else 2,
        'tanggal_lahir': fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
        'age_cat': random.choice([1, 2, 3, 4, 5, 6]),
        'age_grpN': random.choice([1, 2, 3, 4]),
        'regionN': random.choice([1, 2, 3, 4]),
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
list_penyakit = [
    'ALCOHOL_DRUG', 'ASTHMA', 'CARDIAC_ARRYTHMIA', 'CARDIAC_VALVULAR', 'CEREBROVASCULAR',
    'CHRONIC_KIDNEY', 'CHRONIC_PAIN_FIBRO', 'CHF', 'COPD', 'DEMENTIA', 'DEPRESSION',
    'DIABETES', 'DYSLIPIDEMIA', 'EPILEPSY_SEIZURE', 'HEPATITIS', 'HIV_AIDS', 'HYPERTENSION',
    'LIVER_GALLBLADDER_PANCREAS', 'MI_CAD', 'OSTEOARTHRITIS', 'PARALYSIS', 'PEPTIC_ULCER',
    'PERIPHERAL_VASCULAR', 'RENAL_FAILURE', 'RHEUMATOLOGIC', 'SCHIZOPHRENIA', 'SLEEP_DISORDERS',
    'SMOKING', 'THYROID', 'Solid_Tumor', 'Metastatic', 'Leukemia_Lymphoma', 'Other_Cancer', 'Cancer_In_Situ'
]

for pasien in data_pasien:
    comorb_row = {'id_pasien': pasien['id_pasien']}
    for penyakit in list_penyakit:
        comorb_row[penyakit] = random.choices([0, 1], weights=[88, 12])[0]
        
    comorb_row['pre_CCI'] = sum([v for k, v in comorb_row.items() if k != 'id_pasien'])
    data_komorbiditas.append(comorb_row)

df_komorbiditas = pd.DataFrame(data_komorbiditas)


# ==========================================
# 4. GENERATE TABEL SUMBER: MASTER PROSEDUR (SOURCE_PROSEDUR)
# ==========================================
procedure_pool = [
    {"Procedure_Code": "ICD10-0DTJ", "Procedure_Category": "Surgery", "Procedure_Description": "Appendectomy (Open)", "base_cost": 7500.0},
    {"Procedure_Code": "CPT-70450", "Procedure_Category": "Radiology", "Procedure_Description": "CT Scan, Head/Brain", "base_cost": 800.0},
    {"Procedure_Code": "CPT-93000", "Procedure_Category": "Diagnostic", "Procedure_Description": "Electrocardiogram (ECG)", "base_cost": 70.0},
    {"Procedure_Code": "CPT-80053", "Procedure_Category": "Laboratory", "Procedure_Description": "Comprehensive Metabolic Panel", "base_cost": 50.0},
    {"Procedure_Code": "CPT-71045", "Procedure_Category": "Radiology", "Procedure_Description": "Chest X-Ray, single view", "base_cost": 120.0}
]

data_prosedur = []
for proc in procedure_pool:
    data_prosedur.append({
        'Procedure_Code': proc['Procedure_Code'],
        'Procedure_Category': proc['Procedure_Category'],
        'Procedure_Description': proc['Procedure_Description']
    })

df_prosedur = pd.DataFrame(data_prosedur)


# ==========================================
# 5. GENERATE TABEL TRANSAKSI: KUNJUNGAN (SOURCE_KUNJUNGAN)
# ==========================================
data_kunjungan = []
drug_classes_opsi = ['*ANTIDIABETICS*', '*ANTIHYPERTENSIVES*', '*STATINS*', '*ANALGESICS*']
tipe_fasilitas_opsi = ['IGD', 'Rawat Jalan', 'Rawat Inap']
status_keluar_opsi = ['Sembuh', 'Dirujuk', 'Pulang Paksa', 'Meninggal']
metode_pembayaran_opsi = ['BPJS', 'Asuransi Swasta', 'Mandiri']

start_date = datetime(2025, 1, 1)

for kunjungan_id in range(1, TOTAL_TRANSAKSI_KUNJUNGAN + 1):
    pasien = random.choice(data_pasien)
    dokter = random.choice(data_dokter)
    proc = random.choice(procedure_pool)
    
    tipe_fasilitas = random.choice(tipe_fasilitas_opsi)
    metode_pembayaran = random.choice(metode_pembayaran_opsi)
    pdc = round(random.uniform(0.05, 1.0), 4)
    
    # Logika Lama Rawat Inap (Length of Stay)
    if tipe_fasilitas == 'Rawat Inap':
        lama_rawat = random.randint(1, 14)
        status_keluar = random.choices(status_keluar_opsi, weights=[80, 12, 6, 2])[0]
    else:
        lama_rawat = 0
        status_keluar = 'Sembuh'

    # Finansial Medis Masa Lalu & Masa Depan
    post_rx_cost = round(random.uniform(10.0, 6000.0), 2)
    post_op_cost = round(random.uniform(0.0, 15000.0), 2)
    post_ip_cost = round(random.choice([0.0, 0.0, random.uniform(1000.0, 8000.0)]), 2)
    post_er_cost = round(random.choice([0.0, random.uniform(200.0, 1500.0)]), 2)
    post_medical_cost = post_op_cost + post_ip_cost + post_er_cost
    
    pre_rx_cost = round(random.uniform(10.0, 5000.0), 2)
    pre_op_cost = round(random.uniform(0.0, 12000.0), 2)
    pre_ip_cost = round(random.choice([0.0, 0.0, random.uniform(1000.0, 7000.0)]), 2)
    pre_er_cost = round(random.choice([0.0, random.uniform(200.0, 1200.0)]), 2)
    pre_medical_cost = pre_op_cost + pre_ip_cost + pre_er_cost

    copay_val = random.uniform(0.01, 100.0)
    tgl_kunjungan = start_date + timedelta(days=random.randint(0, 450))

    data_kunjungan.append({
        'id_kunjungan': f'TX-{kunjungan_id:06d}',
        'id_pasien': pasien['id_pasien'],
        'id_dokter': dokter['id_dokter'],
        'Procedure_Code': proc['Procedure_Code'],
        'tanggal_kunjungan': tgl_kunjungan.strftime('%Y-%m-%d %H:%M:%S'),
        'tipe_fasilitas': tipe_fasilitas,
        'lama_rawat_hari': lama_rawat,
        'status_keluar': status_keluar,
        'metode_pembayaran': metode_pembayaran,
        'Cost': round(proc['base_cost'] + random.uniform(-10, 300), 2),
        'pdc': pdc,
        'pdc_80_flag': 1 if pdc >= 0.8 else 0,
        'pdc_cat': random.choice([0, 1, 2, 3]),
        'drug_class': random.choice(drug_classes_opsi),
        'idx_prodtypeN': random.choice([1, 2, 3]),
        'idx_paytypN': random.choice([1, 2, 4]),
        'idx_copay': round(copay_val, 2),
        'log_idx_copay': round(np.log(copay_val), 4),
        
        # Metrik Post-Period (Masa Depan)
        'num_ip_post': random.randint(0, 5),
        'total_los_post': random.randint(0, 14),
        'num_op_post': random.randint(0, 25),
        'num_er_post': random.randint(0, 3),
        'num_ndc_post': random.randint(0, 40),
        'num_gpi6_post': random.randint(0, 15),
        'adjust_total_30d_post': round(random.uniform(1.0, 60.0), 4),
        'generic_rate_post': round(random.uniform(0.1, 1.0), 4),
        'post_ip_flag': 1 if post_ip_cost > 0 else 0,
        'post_er_flag': 1 if post_er_cost > 0 else 0,
        'post_ip_cost': post_ip_cost,
        'post_er_cost': post_er_cost,
        'post_rx_cost': post_rx_cost,
        'post_op_cost': post_op_cost,
        'post_medical_cost': round(post_medical_cost, 2),
        'post_total_cost': round(post_medical_cost + post_rx_cost, 2),
        
        # Metrik Pre-Period (Masa Lalu)
        'pre_ip_cost': pre_ip_cost,
        'pre_er_cost': pre_er_cost,
        'pre_rx_cost': pre_rx_cost,
        'pre_op_cost': pre_op_cost,
        'pre_medical_cost': round(pre_medical_cost, 2),
        'pre_total_cost': round(pre_medical_cost + pre_rx_cost, 2),
        'num_ip': random.randint(0, 4),
        'total_los': random.randint(0, 12),
        'num_op': random.randint(0, 20),
        'num_er': random.randint(0, 2),
        'num_ndc': random.randint(0, 35),
        'num_gpi6': random.randint(0, 12),
        'adjust_total_30d': round(random.uniform(1.0, 50.0), 4),
        'generic_rate': round(random.uniform(0.1, 1.0), 4),
        'pre_ip_flag': 1 if pre_ip_cost > 0 else 0,
        'pre_er_flag': 1 if pre_er_cost > 0 else 0,
        'pre_total_cat': random.randint(1, 8),
        
        # Breakdown Obat & Log Transaksi
        'numofgen': random.randint(0, 20),
        'numofbrand': random.randint(0, 15),
        'generic_cost': round(random.uniform(0.0, 3000.0), 2),
        'brand_cost': round(random.uniform(0.0, 4000.0), 2),
        'ratio_G_total_cost': round(random.uniform(0.0, 1.0), 4),
        'numofgen_post': random.randint(0, 25),
        'numofbrand_post': random.randint(0, 15),
        'generic_cost_post': round(random.uniform(0.0, 3500.0), 2),
        'brand_cost_post': round(random.uniform(0.0, 4500.0), 2),
        'ratio_G_total_cost_post': round(random.uniform(0.0, 1.0), 4),
        'log_pre_ip_cost': round(np.log(pre_ip_cost + 1), 4),
        'log_pre_er_cost': round(np.log(pre_er_cost + 1), 4),
        'log_pre_op_cost': round(np.log(pre_op_cost + 1), 4),
        'log_pre_rx_cost': round(np.log(pre_rx_cost + 1), 4)
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

print("✅ Pembuatan dataset relasional dengan format SOURCE selesai!")
print(f"   - source_pasien.csv      : {len(df_pasien)} baris")
print(f"   - source_dokter.csv      : {len(df_dokter)} baris")
print(f"   - source_komorbiditas.csv: {len(df_komorbiditas)} baris")
print(f"   - source_prosedur.csv     : {len(df_prosedur)} baris")
print(f"   - source_kunjungan.csv   : {len(df_kunjungan)} baris")