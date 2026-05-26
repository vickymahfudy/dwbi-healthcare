-- ============================================
-- Business Question 12: Average Ticket Size
-- ============================================
-- Kategori: Finansial
-- KPI: Rata-rata total_biaya dari seluruh total baris transaksi
-- Deskripsi: Berapa rata-rata pengeluaran total biaya per satu kali transaksi 
--            kunjungan pasien (average ticket size) di rumah sakit?
-- ============================================

SELECT 
    COUNT(*) AS total_transaksi,
    ROUND(AVG(total_biaya), 2) AS average_ticket_size,
    ROUND(MIN(total_biaya), 2) AS biaya_minimum,
    ROUND(MAX(total_biaya), 2) AS biaya_maksimum,
    ROUND(STDDEV(total_biaya), 2) AS standar_deviasi,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_biaya), 2) AS kuartil_1,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_biaya), 2) AS median,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_biaya), 2) AS kuartil_3,
    SUM(total_biaya) AS total_pendapatan_keseluruhan
FROM fact_kunjungan;

-- ============================================
-- Breakdown Average Ticket Size per Dimensi
-- ============================================

-- Per Tipe Fasilitas
SELECT 
    'Per Tipe Fasilitas' AS kategori,
    f.tipe_fasilitas AS sub_kategori,
    COUNT(*) AS jumlah_transaksi,
    ROUND(AVG(fk.total_biaya), 2) AS average_ticket_size
FROM fact_kunjungan fk
JOIN dim_fasilitas f ON fk.fasilitas_key = f.fasilitas_key
GROUP BY f.tipe_fasilitas

UNION ALL

-- Per Metode Pembayaran
SELECT 
    'Per Metode Pembayaran' AS kategori,
    pb.metode_pembayaran AS sub_kategori,
    COUNT(*) AS jumlah_transaksi,
    ROUND(AVG(fk.total_biaya), 2) AS average_ticket_size
FROM fact_kunjungan fk
JOIN dim_pembayaran pb ON fk.bayar_key = pb.bayar_key
GROUP BY pb.metode_pembayaran

UNION ALL

-- Per Spesialisasi Dokter
SELECT 
    'Per Spesialisasi' AS kategori,
    d.spesialisasi AS sub_kategori,
    COUNT(*) AS jumlah_transaksi,
    ROUND(AVG(fk.total_biaya), 2) AS average_ticket_size
FROM fact_kunjungan fk
JOIN dim_dokter d ON fk.dokter_key = d.dokter_key
GROUP BY d.spesialisasi

ORDER BY kategori, average_ticket_size DESC;
