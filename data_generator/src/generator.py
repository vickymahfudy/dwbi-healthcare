import os
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Inisialisasi Faker dengan lokalisasi Indonesia agar nama dan datanya realistis
fake = Faker('id_ID')

# Mengunci seed agar data yang dihasilkan selalu konsisten setiap kali dijalankan (opsional)
Faker.seed(42)
random.seed(42)

# Konfigurasi Jumlah Data
TOTAL_PASIEN = 2500
TOTAL_DOKTER = 80
TOTAL_TRANSAKSI_KUNJUNGAN = 12000  # Memenuhi syarat minimal 10.000 baris

print("⏳ Memulai pembuatan dataset sintetik rumah sakit...")

# ==========================================
# 1. GENERATE TABEL SUMBER: PASIEN (SOURCE_PASIEN)
# ==========================================
data_pasien = []
golongan_darah_opsi = ['A', 'B', 'AB', 'O']
jenis_kelamin_opsi = ['Laki-laki', 'Perempuan']

for pasien_id in range(1, TOTAL_PASIEN + 1):
    jk = random.choice(jenis_kelamin_opsi)
    # Sesuaikan nama berdasarkan jenis kelamin agar realistis
    nama = fake.name_male() if jk == 'Laki-laki' else fake.name_female()
    
    data_pasien.append({
        'id_pasien': f'PSN-{pasien_id:05d}',
        'nama_pasien': nama,
        'jenis_kelamin': jk,
        'tanggal_lahir': fake.date_of_birth(minimum_age=0, maximum_age=85).strftime('%Y-%m-%d'),
        'alamat': fake.street_address(),
        'kota': fake.city(),
        'golongan_darah': random.choice(golongan_darah_opsi)
    })

df_pasien = pd.DataFrame(data_pasien)

# ==========================================
# 2. GENERATE TABEL SUMBER: DOKTER (SOURCE_DOKTER)
# ==========================================
data_dokter = []
spesialisasi_opsi = {
    'Umum': 30, 'Anak': 40, 'Penyakit Dalam': 50, 
    'Bedah': 60, 'Jantung': 80, 'Saraf': 70, 'Mata': 45
}

for dokter_id in range(1, TOTAL_DOKTER + 1):
    spesialisasi = random.choice(list(spesialisasi_opsi.keys()))
    biaya_konsultasi = spesialisasi_opsi[spesialisasi] * 1000  # Misal: Jantung Rp 80.000
    
    data_dokter.append({
        'id_dokter': f'DKT-{dokter_id:03d}',
        'nama_dokter': fake.name(),
        'spesialisasi': spesialisasi,
        'biaya_konsultasi': biaya_konsultasi,
        'nomor_izin_praktek': f'STR-{random.randint(100000, 999999)}'
    })

df_dokter = pd.DataFrame(data_dokter)

# ==========================================
# 3. GENERATE TABEL SUMBER: KUNJUNGAN/TRANSAKSI (SOURCE_KUNJUNGAN)
# ==========================================
data_kunjungan = []
tipe_fasilitas_opsi = ['IGD', 'Rawat Jalan', 'Rawat Inap']
status_keluar_opsi = ['Sembuh', 'Dirujuk', 'Pulang Paksa', 'Meninggal']
metode_pembayaran_opsi = ['BPJS', 'Asuransi Swasta', 'Mandiri']

start_date = datetime(2025, 1, 1)

for kunjungan_id in range(1, TOTAL_TRANSAKSI_KUNJUNGAN + 1):
    # Relasikan acak ke Pasien dan Dokter yang sudah ada
    pasien = random.choice(data_pasien)
    dokter = random.choice(data_dokter)
    
    tipe_fasilitas = random.choice(tipe_fasilitas_opsi)
    metode_pembayaran = random.choice(metode_pembayaran_opsi)
    
    # Logika Lama Rawat Inap (Length of Stay)
    if tipe_fasilitas == 'Rawat Inap':
        lama_rawat = random.randint(1, 14)  # 1 sampai 14 hari
        status_keluar = random.choices(status_keluar_opsi, weights=[80, 12, 6, 2])[0]
        biaya_kamar = lama_rawat * random.choice([250000, 500000, 1200000]) # Kelas 3, 2, VIP
    else:
        lama_rawat = 0  # IGD atau Rawat Jalan langsung pulang hari itu juga
        status_keluar = 'Sembuh'
        biaya_kamar = 0

    # Simulasi Komponen Biaya Medis
    biaya_konsul = dokter['biaya_konsultasi']
    biaya_obat = random.randint(50000, 750000) if tipe_fasilitas != 'IGD' else random.randint(30000, 200000)
    biaya_tindakan = random.choice([0, 150000, 300000, 1500000]) if tipe_fasilitas in ['IGD', 'Rawat Inap'] else 0
    
    total_biaya = biaya_konsul + biaya_obat + biaya_tindakan + biaya_kamar
    
    # Tanggal Kunjungan acak sepanjang tahun 2025 s.d awal 2026
    tgl_kunjungan = start_date + timedelta(days=random.randint(0, 450))
    
    data_kunjungan.append({
        'id_kunjungan': f'TX-{kunjungan_id:06d}',
        'id_pasien': pasien['id_pasien'],
        'id_dokter': dokter['id_dokter'],
        'tanggal_kunjungan': tgl_kunjungan.strftime('%Y-%m-%d %H:%M:%S'),
        'tipe_fasilitas': tipe_fasilitas,
        'lama_rawat_hari': lama_rawat,
        'status_keluar': status_keluar,
        'metode_pembayaran': metode_pembayaran,
        'biaya_konsultasi': biaya_konsul,
        'biaya_obat': biaya_obat,
        'biaya_tindakan': biaya_tindakan,
        'biaya_kamar': biaya_kamar,
        'total_biaya': total_biaya
    })

df_kunjungan = pd.DataFrame(data_kunjungan)

# ==========================================
# 4. MENYIMPAN DATA KE CSV (Bisa diubah ke SQL Insert)
# ==========================================
# Pastikan folder output ada
os.makedirs('data_generator/output', exist_ok=True)

df_pasien.to_csv('data_generator/output/source_pasien.csv', index=False)
df_dokter.to_csv('data_generator/output/source_dokter.csv', index=False)
df_kunjungan.to_csv('data_generator/output/source_kunjungan.csv', index=False)

print("✅ Pembuatan dataset selesai!")
print(f"   - Total Pasien   : {len(df_pasien)} baris")
print(f"   - Total Dokter   : {len(df_dokter)} baris")
print(f"   - Total Kunjungan: {len(df_kunjungan)} baris (Memenuhi syarat tugas!)")