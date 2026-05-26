select
    id_dokter,
    nama as nama_dokter,
    spesialisasi,
    nomor_izin_praktek
from {{ source('public', 'src_dokter') }}