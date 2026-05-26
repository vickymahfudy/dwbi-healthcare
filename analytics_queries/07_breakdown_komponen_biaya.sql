-- ============================================
-- Business Question 7: Breakdown Komponen Biaya
-- ============================================
-- Kategori: Analisis Biaya
-- KPI: Breakdown rata-rata dan total biaya_konsultasi, biaya_obat, biaya_tindakan, biaya_kamar
-- Deskripsi: Bagaimana rincian kontribusi masing-masing komponen biaya 
--            (konsultasi, obat, tindakan, kamar) terhadap struktur total penagihan?
-- ============================================

WITH komponen_biaya AS (
    SELECT 
        'Biaya Konsultasi' AS komponen,
        SUM(biaya_konsultasi) AS total_biaya,
        ROUND(AVG(biaya_konsultasi), 2) AS rata_rata_biaya
    FROM fact_kunjungan
    
    UNION ALL
    
    SELECT 
        'Biaya Obat' AS komponen,
        SUM(biaya_obat) AS total_biaya,
        ROUND(AVG(biaya_obat), 2) AS rata_rata_biaya
    FROM fact_kunjungan
    
    UNION ALL
    
    SELECT 
        'Biaya Tindakan' AS komponen,
        SUM(biaya_tindakan) AS total_biaya,
        ROUND(AVG(biaya_tindakan), 2) AS rata_rata_biaya
    FROM fact_kunjungan
    
    UNION ALL
    
    SELECT 
        'Biaya Kamar' AS komponen,
        SUM(biaya_kamar) AS total_biaya,
        ROUND(AVG(biaya_kamar), 2) AS rata_rata_biaya
    FROM fact_kunjungan
)
SELECT 
    komponen,
    total_biaya,
    rata_rata_biaya,
    ROUND(
        total_biaya * 100.0 / SUM(total_biaya) OVER (), 
        2
    ) AS persentase_kontribusi,
    ROUND(
        total_biaya * 1.0 / (SELECT COUNT(*) FROM fact_kunjungan), 
        2
    ) AS biaya_per_transaksi
FROM komponen_biaya
ORDER BY total_biaya DESC;
