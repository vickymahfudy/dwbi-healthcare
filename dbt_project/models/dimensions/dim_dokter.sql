-- SCD Tipe 1 Overwrite (Surrogate Key berbasis MD5 Hash dari ID Alami)
select
    md5(cast(id_dokter as varchar)) as dokter_key,
    id_dokter,
    nama_dokter,
    spesialisasi,
    nomor_izin_praktek
from {{ ref('stg_dokter') }}