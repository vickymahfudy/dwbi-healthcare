-- ============================================
-- Business Question 4: Analisis Length of Stay (LOS)
-- ============================================
-- Kategori: Efisiensi Klinis
-- KPI: Rata-rata lama_rawat_hari, biaya_kamar, total_biaya
-- Deskripsi: Berapa rata-rata lama rawat inap (Length of Stay) pasien 
--            dan bagaimana pengaruhnya terhadap biaya kamar serta total biaya transaksi?
-- ============================================

SELECT 
    CASE 
        WHEN fk.lama_rawat_hari = 0 THEN '0 hari (Rawat Jalan/IGD)'
        WHEN fk.lama_rawat_hari BETWEEN 1 AND 3 THEN '1-3 hari'
        WHEN fk.lama_rawat_hari BETWEEN 4 AND 7 THEN '4-7 hari'
        WHEN fk.lama_rawat_hari BETWEEN 8 AND 14 THEN '8-14 hari'
        ELSE '> 14 hari'
    END AS kategori_los,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    ROUND(AVG(fk.lama_rawat_hari), 2) AS rata_rata_lama_rawat,
    ROUND(AVG(fk.biaya_kamar), 2) AS rata_rata_biaya_kamar,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_total_biaya,
    SUM(fk.total_biaya) AS total_pendapatan,
    ROUND(
        AVG(fk.biaya_kamar) * 100.0 / NULLIF(AVG(fk.total_biaya), 0), 
        2
    ) AS persentase_biaya_kamar_terhadap_total
FROM fact_kunjungan fk
GROUP BY 
    CASE 
        WHEN fk.lama_rawat_hari = 0 THEN '0 hari (Rawat Jalan/IGD)'
        WHEN fk.lama_rawat_hari BETWEEN 1 AND 3 THEN '1-3 hari'
        WHEN fk.lama_rawat_hari BETWEEN 4 AND 7 THEN '4-7 hari'
        WHEN fk.lama_rawat_hari BETWEEN 8 AND 14 THEN '8-14 hari'
        ELSE '> 14 hari'
    END
ORDER BY 
    MIN(fk.lama_rawat_hari);
