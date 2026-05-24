"""
=============================================================
  Skrip Gabung Dataset Healthcare
  - healthcare_dataset.csv      (kunjungan pasien + diagnosis)
  - kaggle_medical_procedures_dummy.sql  (tindakan medis)
=============================================================
"""

import sqlite3
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────
# KONFIGURASI PATH (otomatis deteksi folder skrip)
# ─────────────────────────────────────────────
_dir        = Path(__file__).parent.resolve()
CSV_FILE    = _dir / "healthcare_dataset.csv"
SQL_FILE    = _dir / "kaggle_medical_procedures_dummy.sql"

for f in [CSV_FILE, SQL_FILE]:
    if not f.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {f}")


def sep(title="", w=65):
    if title:
        pad = (w - len(title) - 2) // 2
        print(f"\n{'='*pad} {title} {'='*(w-pad-len(title)-2)}")
    else:
        print("=" * w)


# ─────────────────────────────────────────────
# 1. LOAD CSV
# ─────────────────────────────────────────────
sep("LOAD healthcare_dataset.csv")
df_csv = pd.read_csv(CSV_FILE)
df_csv["patIndex"] = df_csv.index.astype(str)   # row index → kunci relasi
print(f"  Baris   : {len(df_csv):,}")
print(f"  Kolom   : {list(df_csv.columns)}")


# ─────────────────────────────────────────────
# 2. LOAD SQL → SQLite in-memory
# ─────────────────────────────────────────────
sep("LOAD kaggle_medical_procedures_dummy.sql")
with open(SQL_FILE, "r", encoding="utf-8", errors="replace") as f:
    sql_text = f.read().replace("\r\n", "\n").replace("\r", "\n")

conn = sqlite3.connect(":memory:")
ok = err = 0
for stmt in [s.strip() for s in sql_text.split(";") if s.strip()]:
    try:
        conn.execute(stmt); ok += 1
    except:
        err += 1
conn.commit()

df_sql = pd.read_sql_query("SELECT * FROM Medical_Procedures", conn)
print(f"  Baris   : {len(df_sql):,}")
print(f"  Kolom   : {list(df_sql.columns)}")


# ─────────────────────────────────────────────
# 3. JOIN (INNER) pada patIndex
# ─────────────────────────────────────────────
sep("JOIN KEDUA DATASET")
df_merged = pd.merge(df_csv, df_sql, on="patIndex", how="inner")

# Susun ulang kolom berdasarkan 3 poin utama
col_order = [
    # Identitas
    "patIndex", "Name", "Age", "Gender", "Blood Type",
    # ── POINT 1: Kunjungan Pasien ──
    "Date of Admission", "Discharge Date", "Admission Type",
    "Hospital", "Doctor", "Room Number", "Insurance Provider", "Billing Amount",
    # ── POINT 2: Diagnosis ──
    "Medical Condition", "Medication", "Test Results",
    # ── POINT 3: Tindakan Medis ──
    "Procedure_ID", "Procedure_Date", "Procedure_Code",
    "Procedure_Category", "Procedure_Description", "Cost",
]
df_merged = df_merged[col_order]
print(f"  Total baris hasil JOIN : {len(df_merged):,}")
print(f"  Total kolom            : {len(df_merged.columns)}")


# ─────────────────────────────────────────────
# 4. TAMPILKAN STRUKTUR KOLOM
# ─────────────────────────────────────────────
sep("STRUKTUR KOLOM GABUNGAN")
print(f"\n  {'No':<4} {'Nama Kolom':<30} {'Tipe':<15} {'Poin'}")
print(f"  {'-'*4} {'-'*30} {'-'*15} {'-'*25}")

poin_map = {
    "patIndex"           : "🔑 Kunci Relasi",
    "Name"               : "👤 Identitas Pasien",
    "Age"                : "👤 Identitas Pasien",
    "Gender"             : "👤 Identitas Pasien",
    "Blood Type"         : "👤 Identitas Pasien",
    "Date of Admission"  : "✅ Kunjungan Pasien",
    "Discharge Date"     : "✅ Kunjungan Pasien",
    "Admission Type"     : "✅ Kunjungan Pasien",
    "Hospital"           : "✅ Kunjungan Pasien",
    "Doctor"             : "✅ Kunjungan Pasien",
    "Room Number"        : "✅ Kunjungan Pasien",
    "Insurance Provider" : "✅ Kunjungan Pasien",
    "Billing Amount"     : "✅ Kunjungan Pasien",
    "Medical Condition"  : "✅ Diagnosis",
    "Medication"         : "✅ Diagnosis",
    "Test Results"       : "✅ Diagnosis",
    "Procedure_ID"       : "✅ Tindakan Medis",
    "Procedure_Date"     : "✅ Tindakan Medis",
    "Procedure_Code"     : "✅ Tindakan Medis",
    "Procedure_Category" : "✅ Tindakan Medis",
    "Procedure_Description": "✅ Tindakan Medis",
    "Cost"               : "✅ Tindakan Medis",
}

for i, col in enumerate(df_merged.columns, 1):
    dtype = str(df_merged[col].dtype)
    poin  = poin_map.get(col, "")
    print(f"  {i:<4} {col:<30} {dtype:<15} {poin}")


# ─────────────────────────────────────────────
# 5. TAMPILKAN SAMPLE DATA PER POIN
# ─────────────────────────────────────────────
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 130)
pd.set_option("display.max_colwidth", 28)

sep("SAMPLE DATA — KUNJUNGAN PASIEN (5 baris)")
kunjungan_cols = ["patIndex","Name","Date of Admission","Discharge Date",
                  "Admission Type","Hospital","Doctor","Room Number"]
print(df_merged[kunjungan_cols].head(5).to_string(index=False))

sep("SAMPLE DATA — DIAGNOSIS (5 baris)")
diagnosis_cols = ["patIndex","Name","Medical Condition","Medication","Test Results"]
print(df_merged[diagnosis_cols].head(5).to_string(index=False))

sep("SAMPLE DATA — TINDAKAN MEDIS (5 baris)")
tindakan_cols = ["patIndex","Procedure_ID","Procedure_Date",
                 "Procedure_Code","Procedure_Category","Procedure_Description","Cost"]
print(df_merged[tindakan_cols].head(5).to_string(index=False))

sep("SAMPLE DATA — GABUNGAN LENGKAP (5 baris)")
print(df_merged.head(5).to_string(index=False))


# ─────────────────────────────────────────────
# 6. RINGKASAN STATISTIK
# ─────────────────────────────────────────────
sep("RINGKASAN STATISTIK")
print(f"\n  Total record gabungan    : {len(df_merged):,}")
print(f"  Pasien unik (patIndex)   : {df_merged['patIndex'].nunique():,}")
print(f"  Kondisi medis unik       : {df_merged['Medical Condition'].nunique()}")
print(f"  Jenis tindakan unik      : {df_merged['Procedure_Description'].nunique()}")
print(f"  Rentang kunjungan        : {df_merged['Date of Admission'].min()} s/d {df_merged['Date of Admission'].max()}")
print(f"  Rentang tindakan         : {df_merged['Procedure_Date'].min()} s/d {df_merged['Procedure_Date'].max()}")
print(f"\n  Distribusi Admission Type:")
for v, c in df_merged["Admission Type"].value_counts().items():
    pct = c/len(df_merged)*100
    print(f"    {v:<12}: {c:>5,}  ({pct:.1f}%)")
print(f"\n  Distribusi Procedure_Category:")
for v, c in df_merged["Procedure_Category"].value_counts().items():
    pct = c/len(df_merged)*100
    print(f"    {v:<14}: {c:>5,}  ({pct:.1f}%)")
print(f"\n  Distribusi Medical Condition:")
for v, c in df_merged["Medical Condition"].value_counts().items():
    pct = c/len(df_merged)*100
    print(f"    {v:<20}: {c:>5,}  ({pct:.1f}%)")

sep("CHECKLIST 3 POIN UTAMA")
print("  ✅  Kunjungan Pasien  → Date of Admission, Discharge Date, Admission Type, Hospital, Doctor")
print("  ✅  Diagnosis         → Medical Condition, Medication, Test Results")
print("  ✅  Tindakan Medis    → Procedure_Code, Procedure_Category, Procedure_Description, Cost")
sep()

conn.close()