-- ============================================
-- Business Question 1: Total Pendapatan per Tipe Fasilitas
-- ============================================
-- Kategori: Finansial
-- KPI: total_biaya, tipe_fasilitas
-- Deskripsi: Berapa total pendapatan rumah sakit dan bagaimana distribusinya 
--            berdasarkan tipe fasilitas (IGD, Rawat Jalan, Rawat Inap)?
-- ============================================

SELECT 
    f.tipe_fasilitas,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    SUM(fk.total_biaya) AS total_pendapatan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_kunjungan,
    ROUND(
        SUM(fk.total_biaya) * 100.0 / SUM(SUM(fk.total_biaya)) OVER (), 
        2
    ) AS persentase_kontribusi
FROM fact_kunjungan fk
JOIN dim_fasilitas f ON fk.fasilitas_key = f.fasilitas_key
GROUP BY f.tipe_fasilitas
ORDER BY total_pendapatan DESC;
