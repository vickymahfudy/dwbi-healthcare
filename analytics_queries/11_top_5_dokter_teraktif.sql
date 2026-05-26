-- ============================================
-- Business Question 11: Top 5 Dokter Teraktif
-- ============================================
-- Kategori: Kinerja Dokter
-- KPI: Ranking 5 Teratas nama_dokter berdasarkan Count(id_kunjungan)
-- Deskripsi: Siapakah 5 dokter teratas (Top 5 Doctors) yang memiliki 
--            kontribusi pelayanan transaksi kunjungan paling aktif di rumah sakit?
-- ============================================

SELECT 
    d.nama_dokter,
    d.spesialisasi,
    d.nomor_izin_praktek,
    COUNT(fk.pasien_key) AS jumlah_kunjungan,
    SUM(fk.total_biaya) AS total_pendapatan,
    ROUND(AVG(fk.total_biaya), 2) AS rata_rata_biaya_per_kunjungan,
    ROUND(AVG(fk.lama_rawat_hari), 2) AS rata_rata_lama_rawat,
    RANK() OVER (ORDER BY COUNT(fk.pasien_key) DESC) AS ranking_kunjungan
FROM fact_kunjungan fk
JOIN dim_dokter d ON fk.dokter_key = d.dokter_key
GROUP BY d.nama_dokter, d.spesialisasi, d.nomor_izin_praktek
ORDER BY jumlah_kunjungan DESC
LIMIT 5;
