-- SCD Tipe 2 Pemetaan Kunci Historis (Menggunakan MD5 Hash sebagai Surrogate Key)
select
    md5(cast(id_pasien as varchar) || '-' || cast(tanggal_lahir as varchar)) as pasien_key,
    id_pasien,
    nama_pasien,
    jenis_kelamin,
    tanggal_lahir,
    alamat,
    kota,
    golongan_darah
from {{ ref('stg_pasien') }}