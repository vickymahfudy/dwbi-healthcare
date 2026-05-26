-- Jantung Arsitektur: Transaction Fact Table (5 FK + 6 Measures)
with kunjungan as (
    select * from {{ ref('stg_kunjungan') }}
),
pasien as (
    select * from {{ ref('dim_pasien') }}
),
dokter as (
    select * from {{ ref('dim_dokter') }}
),
waktu as (
    select * from {{ ref('dim_waktu') }}
),
fasilitas as (
    select * from {{ ref('dim_fasilitas') }}
),
pembayaran as (
    select * from {{ ref('dim_pembayaran') }}
)

select
    p.pasien_key,
    d.dokter_key,
    w.date_key,
    f.fasilitas_key,
    pay.bayar_key,
    k.lama_rawat_hari,
    k.biaya_konsultasi,
    k.biaya_obat,
    k.biaya_tindakan,
    k.biaya_kamar,
    k.total_biaya
from kunjungan k
left join pasien p on k.id_pasien = p.id_pasien
left join dokter d on k.id_dokter = d.id_dokter
left join waktu w on k.tanggal_kunjungan = w.tanggal
left join fasilitas f on k.tipe_fasilitas = f.tipe_fasilitas and k.status_keluar = f.status_keluar
left join pembayaran pay on k.metode_pembayaran = pay.metode_pembayaran