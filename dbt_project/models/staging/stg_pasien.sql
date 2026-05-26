select
    id_pasien,
    nama as nama_pasien,
    jenis_kelamin,
    cast(tanggal_lahir as date) as tanggal_lahir,
    alamat,
    kota,
    golongan_darah
from {{ source('public', 'src_pasien') }}