-- ============================================
-- Business Question 9: Profil Demografi Pasien
-- ============================================
-- Kategori: Demografi
-- KPI: Analisis cross-tabulation Count(id_kunjungan) per jenis_kelamin dan golongan_darah
-- Deskripsi: Bagaimana profil distribusi kunjungan pasien jika dikelompokkan 
--            berdasarkan variabel jenis kelamin dan golongan darah?
-- ============================================

SELECT 
    p.jenis_kelamin,
    p.golongan_darah,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    COUNT(DISTINCT p.pasien_key) AS jumlah_pasien_unik,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya,
    ROUND(AVG(fk.lama_rawat_hari), 2) AS rata_rata_lama_rawat,
    ROUND(
        COUNT(fk.pasien_key) * 100.0 / SUM(COUNT(fk.pasien_key)) OVER (), 
        2
    ) AS persentase_total_kunjungan,
    ROUND(
        COUNT(fk.pasien_key) * 100.0 / SUM(COUNT(fk.pasien_key)) OVER (PARTITION BY p.jenis_kelamin), 
        2
    ) AS persentase_dalam_jenis_kelamin
FROM fact_kunjungan fk
JOIN dim_pasien p ON fk.pasien_key = p.pasien_key
GROUP BY p.jenis_kelamin, p.golongan_darah
ORDER BY p.jenis_kelamin, jumlah_kunjungan DESC;
