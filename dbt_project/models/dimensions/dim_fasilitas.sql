-- SCD Tipe 1 (Diturunkan dari kombinasi unik di tabel transaksi)
with distinct_facilities as (
    select distinct tipe_fasilitas, status_keluar
    from {{ ref('stg_kunjungan') }}
    where tipe_fasilitas is not null
)
select
    row_number() over (order by tipe_fasilitas, status_keluar) as fasilitas_key,
    tipe_fasilitas,
    status_keluar
from distinct_facilities