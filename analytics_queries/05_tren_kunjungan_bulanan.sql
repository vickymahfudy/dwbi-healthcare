-- ============================================
-- Business Question 5: Tren Kunjungan Bulanan
-- ============================================
-- Kategori: Tren Kunjungan
-- KPI: Volume Count(id_kunjungan) berdasarkan ekstrak tren tanggal_kunjungan
-- Deskripsi: Bagaimana tren bulanan jumlah kunjungan pasien di rumah sakit 
--            sepanjang periode tahun 2025 hingga awal 2026?
-- ============================================

SELECT 
    w.tahun,
    w.bulan,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    SUM(fk.total_biaya) AS total_pendapatan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_kunjungan,
    LAG(COUNT(fk.pasien_key)) OVER (ORDER BY w.tahun, w.bulan) AS kunjungan_bulan_sebelumnya,
    ROUND(
        (COUNT(fk.pasien_key) - LAG(COUNT(fk.pasien_key)) OVER (ORDER BY w.tahun, w.bulan)) * 100.0 
        / NULLIF(LAG(COUNT(fk.pasien_key)) OVER (ORDER BY w.tahun, w.bulan), 0),
        2
    ) AS persentase_pertumbuhan
FROM fact_kunjungan fk
JOIN dim_waktu w ON fk.date_key = w.date_key
WHERE w.tahun IN (2025, 2026)
GROUP BY w.tahun, w.bulan
ORDER BY w.tahun, w.bulan;
