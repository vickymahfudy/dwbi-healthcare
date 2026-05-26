-- ============================================
-- Business Question 3: Distribusi Metode Pembayaran
-- ============================================
-- Kategori: Finansial & Payer
-- KPI: Persentase akumulasi total_biaya per metode_pembayaran
-- Deskripsi: Bagaimana distribusi penggunaan metode pembayaran 
--            (BPJS, Asuransi Swasta, Mandiri) terhadap total biaya pelayanan?
-- ============================================

SELECT 
    pb.metode_pembayaran,
    COUNT(fk.pasien_key) AS jumlah_transaksi,
    SUM(fk.total_biaya) AS total_biaya_pelayanan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_transaksi,
    ROUND(
        COUNT(fk.pasien_key) * 100.0 / SUM(COUNT(fk.pasien_key)) OVER (), 
        2
    ) AS persentase_transaksi,
    ROUND(
        SUM(fk.total_biaya) * 100.0 / SUM(SUM(fk.total_biaya)) OVER (), 
        2
    ) AS persentase_total_biaya
FROM fact_kunjungan fk
JOIN dim_pembayaran pb ON fk.bayar_key = pb.bayar_key
GROUP BY pb.metode_pembayaran
ORDER BY total_biaya_pelayanan DESC;
