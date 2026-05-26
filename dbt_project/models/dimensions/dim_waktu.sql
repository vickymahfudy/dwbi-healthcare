-- SCD Tipe 0 Retain (Diturunkan dari nilai distinct tanggal_kunjungan)
with distinct_dates as (
    select distinct tanggal_kunjungan as tanggal
    from {{ ref('stg_kunjungan') }}
)
select
    cast(to_char(tanggal, 'YYYYMMDD') as integer) as date_key,
    tanggal,
    to_char(tanggal, 'Day') as nama_hari,
    to_char(tanggal, 'Month') as bulan,
    extract(quarter from tanggal) as kuartal,
    extract(year from tanggal) as tahun,
    case when extract(isodow from tanggal) in (6, 7) then 1 else 0 end as is_weekend_flag
from distinct_dates