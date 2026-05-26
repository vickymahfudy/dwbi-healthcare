-- ============================================
-- Business Question 10: Biaya Obat IGD vs Rawat Jalan
-- ============================================
-- Kategori: Farmasi & Biaya
-- KPI: Rata-rata biaya_obat per tipe_fasilitas (IGD vs Rawat Jalan)
-- Deskripsi: Berapa rata-rata biaya obat yang dikeluarkan oleh pasien 
--            pada fasilitas IGD dibandingkan dengan fasilitas Rawat Jalan?
-- ============================================

SELECT 
    f.tipe_fasilitas,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    ROUND(AVG(fk.biaya_obat), 2) AS rata_rata_biaya_obat,
    ROUND(MIN(fk.biaya_obat), 2) AS biaya_obat_minimum,
    ROUND(MAX(fk.biaya_obat), 2) AS biaya_obat_maksimum,
    ROUND(STDDEV(fk.biaya_obat), 2) AS standar_deviasi,
    SUM(fk.biaya_obat) AS total_biaya_obat,
    ROUND(
        AVG(fk.biaya_obat) * 100.0 / NULLIF(AVG(fk.total_biaya), 0), 
        2
    ) AS persentase_biaya_obat_terhadap_total
FROM fact_kunjungan fk
JOIN dim_fasilitas f ON fk.fasilitas_key = f.fasilitas_key
WHERE f.tipe_fasilitas IN ('IGD', 'Rawat Jalan')
GROUP BY f.tipe_fasilitas
ORDER BY rata_rata_biaya_obat DESC;
