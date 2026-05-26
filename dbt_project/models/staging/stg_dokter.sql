select
    id_dokter,
    nama_dokter, -- Langsung panggil nama_dokter tanpa alias 'as'
    spesialisasi,
    nomor_izin_praktek
from {{ source('public', 'src_dokter') }}