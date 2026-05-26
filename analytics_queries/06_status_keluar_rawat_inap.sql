-- ============================================
-- Business Question 6: Status Keluar Pasien Rawat Inap
-- ============================================
-- Kategori: Mutu Pelayanan
-- KPI: Rasio dan jumlah status_keluar where tipe_fasilitas = 'Rawat Inap'
-- Deskripsi: Bagaimana proporsi status keluar pasien (Sembuh, Dirujuk, Pulang Paksa, Meninggal) 
--            khusus pada tipe fasilitas Rawat Inap?
-- ============================================

SELECT 
    f.status_keluar,
    COUNT(fk.pasien_key) AS jumlah_pasien,
    ROUND(AVG(fk.lama_rawat_hari), 2) AS rata_rata_lama_rawat,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_total_biaya,
    ROUND(
        COUNT(fk.pasien_key) * 100.0 / SUM(COUNT(fk.pasien_key)) OVER (), 
        2
    ) AS persentase_proporsi
FROM fact_kunjungan fk
JOIN dim_fasilitas f ON fk.fasilitas_key = f.fasilitas_key
WHERE f.tipe_fasilitas = 'Rawat Inap'
GROUP BY f.status_keluar
ORDER BY jumlah_pasien DESC;
