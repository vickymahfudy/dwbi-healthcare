select
    id_kunjungan,
    id_pasien,
    id_dokter,
    cast(tanggal_kunjungan as date) as tanggal_kunjungan,
    tipe_fasilitas,
    status_keluar,
    metode_pembayaran,
    coalesce(cast(lama_rawat_hari as integer), 0) as lama_rawat_hari,
    coalesce(cast(biaya_konsultasi as decimal(12,2)), 0) as biaya_konsultasi,
    coalesce(cast(biaya_obat as decimal(12,2)), 0) as biaya_obat,
    coalesce(cast(biaya_tindakan as decimal(12,2)), 0) as biaya_tindakan,
    coalesce(cast(biaya_kamar as decimal(12,2)), 0) as biaya_kamar,
    coalesce(cast(total_biaya as decimal(12,2)), 0) as total_biaya
from {{ source('public', 'src_kunjungan') }}