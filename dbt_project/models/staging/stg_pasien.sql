select
    id_pasien,
    nama_pasien, -- Langsung panggil nama_pasien karena dari source-nya sudah bernama ini
    jenis_kelamin,
    cast(tanggal_lahir as date) as tanggal_lahir,
    alamat,
    kota,
    golongan_darah
from {{ source('public', 'src_pasien') }}