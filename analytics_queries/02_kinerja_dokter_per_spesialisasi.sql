-- ============================================
-- Business Question 2: Kinerja Dokter per Spesialisasi
-- ============================================
-- Kategori: Kinerja Dokter
-- KPI: Count(id_kunjungan), Sum(total_biaya) per spesialisasi
-- Deskripsi: Spesialisasi dokter manakah yang menghasilkan volume transaksi 
--            kunjungan tertinggi dan total biaya penagihan terbesar?
-- ============================================

SELECT 
    d.spesialisasi,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    SUM(fk.total_biaya) AS total_biaya_penagihan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_kunjungan,
    COUNT(DISTINCT d.dokter_key) AS jumlah_dokter,
    ROUND(
        COUNT(fk.pasien_key) * 1.0 / COUNT(DISTINCT d.dokter_key), 
        2
    ) AS rata_rata_kunjungan_per_dokter
FROM fact_kunjungan fk
JOIN dim_dokter d ON fk.dokter_key = d.dokter_key
GROUP BY d.spesialisasi
ORDER BY jumlah_kunjungan DESC, total_biaya_penagihan DESC;
