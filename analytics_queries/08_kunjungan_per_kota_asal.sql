-- ============================================
-- Business Question 8: Kunjungan per Kota Asal Pasien
-- ============================================
-- Kategori: Geografi
-- KPI: Count(id_kunjungan), Sum(total_biaya) per kota
-- Deskripsi: Kota asal pasien manakah yang memiliki beban pemanfaatan layanan 
--            dan frekuensi kunjungan tertinggi di rumah sakit?
-- ============================================

SELECT 
    p.kota,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    COUNT(DISTINCT p.pasien_key) AS jumlah_pasien_unik,
    SUM(fk.total_biaya) AS total_biaya_pelayanan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_kunjungan,
    ROUND(
        COUNT(fk.pasien_key) * 1.0 / COUNT(DISTINCT p.pasien_key), 
        2
    ) AS rata_rata_kunjungan_per_pasien,
    ROUND(
        COUNT(fk.pasien_key) * 100.0 / SUM(COUNT(fk.pasien_key)) OVER (), 
        2
    ) AS persentase_kunjungan,
    ROUND(
        SUM(fk.total_biaya) * 100.0 / SUM(SUM(fk.total_biaya)) OVER (), 
        2
    ) AS persentase_pendapatan
FROM fact_kunjungan fk
JOIN dim_pasien p ON fk.pasien_key = p.pasien_key
GROUP BY p.kota
ORDER BY jumlah_kunjungan DESC, total_biaya_pelayanan DESC
LIMIT 20;
