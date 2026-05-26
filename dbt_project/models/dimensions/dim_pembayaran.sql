-- SCD Tipe 1 (Diturunkan dari metode pembayaran unik di tabel transaksi)
with distinct_payments as (
    select distinct metode_pembayaran
    from {{ ref('stg_kunjungan') }}
    where metode_pembayaran is not null
)
select
    row_number() over (order by metode_pembayaran) as bayar_key,
    metode_pembayaran
from distinct_payments