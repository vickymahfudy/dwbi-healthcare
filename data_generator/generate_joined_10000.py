"""
================================================================
  JOIN + Generate 10.000 Record Healthcare
  Sumber:
    - kaggle_medical_procedures_dummy.sql  (tindakan medis)
    - healthcareTest.csv                   (data klinis pasien)
  Output:
    - healthcare_joined_10000.csv
    - healthcare_joined_10000.sql
================================================================
"""

import random
import math
import sqlite3
import csv
import numpy as np
import pandas as pd
from pathlib import Path

random.seed(42)
np.random.seed(42)

# ── Path ──────────────────────────────────────────────────────
_dir     = Path(__file__).parent.resolve()
CSV_IN   = _dir / "healthcareTest.csv"
SQL_IN   = _dir / "kaggle_medical_procedures_dummy.sql"
OUT_CSV  = _dir / "healthcare_joined_10000.csv"
OUT_SQL  = _dir / "healthcare_joined_10000.sql"
N_TARGET = 10_000

for f in [CSV_IN, SQL_IN]:
    if not f.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {f}\nPastikan ada di folder yang sama dengan skrip ini.")


def sep(title="", w=66):
    if title:
        p = (w - len(title) - 2) // 2
        print(f"\n{'='*p} {title} {'='*(w-p-len(title)-2)}")
    else:
        print("=" * w)


# ================================================================
#  1. LOAD & JOIN DATA ASLI
# ================================================================
sep("STEP 1 — LOAD & JOIN DATA ASLI")

df_csv = pd.read_csv(CSV_IN)
df_csv["patIndex"] = df_csv["patIndex"].astype(str)
print(f"  healthcareTest.csv  : {len(df_csv):,} baris, {len(df_csv.columns)} kolom")

with open(SQL_IN, "r", encoding="utf-8", errors="replace") as f:
    sql_text = f.read().replace("\r\n", "\n").replace("\r", "\n")

conn = sqlite3.connect(":memory:")
for stmt in [s.strip() for s in sql_text.split(";") if s.strip()]:
    try: conn.execute(stmt)
    except: pass
conn.commit()
df_sql = pd.read_sql_query("SELECT * FROM Medical_Procedures", conn)
df_sql["patIndex"] = df_sql["patIndex"].astype(str)
print(f"  Medical_Procedures  : {len(df_sql):,} baris, {len(df_sql.columns)} kolom")

df_joined = pd.merge(df_csv, df_sql, on="patIndex", how="inner")
print(f"  Hasil JOIN          : {len(df_joined):,} baris, {len(df_joined.columns)} kolom")

# ── Susun ulang kolom: CSV dulu, lalu kolom SQL (tanpa duplikat) ──
sql_extra_cols = [c for c in df_sql.columns if c != "patIndex"]
col_order = list(df_csv.columns) + sql_extra_cols
df_joined = df_joined[col_order]

COLUMNS = list(df_joined.columns)
print(f"  Total kolom final   : {len(COLUMNS)}")


# ================================================================
#  2. PELAJARI DISTRIBUSI DARI DATA ASLI
# ================================================================
sep("STEP 2 — ANALISIS DISTRIBUSI")

# ── Kolom kategorikal (distribusi proporsional) ──
CAT_COLS = {
    "pdc_cat":       df_joined["pdc_cat"].value_counts(normalize=True).to_dict(),
    "age_grpN":      df_joined["age_grpN"].value_counts(normalize=True).to_dict(),
    "sexN":          df_joined["sexN"].value_counts(normalize=True).to_dict(),
    "regionN":       df_joined["regionN"].value_counts(normalize=True).to_dict(),
    "idx_prodtypeN": df_joined["idx_prodtypeN"].value_counts(normalize=True).to_dict(),
    "idx_paytypN":   df_joined["idx_paytypN"].value_counts(normalize=True).to_dict(),
    "age_cat":       df_joined["age_cat"].value_counts(normalize=True).to_dict(),
    "pre_total_cat": df_joined["pre_total_cat"].value_counts(normalize=True).to_dict(),
    "drug_class":    df_joined["drug_class"].value_counts(normalize=True).to_dict(),
    "Procedure_Code":    df_joined["Procedure_Code"].value_counts(normalize=True).to_dict(),
    "Procedure_Category":df_joined["Procedure_Category"].value_counts(normalize=True).to_dict(),
}

# ── Flag columns (Bernoulli probability) ──
FLAG_COLS = [
    "post_ip_flag","post_er_flag","pre_ip_flag","pre_er_flag","pdc_80_flag",
    "ALCOHOL_DRUG","ASTHMA","CARDIAC_ARRYTHMIA","CARDIAC_VALVULAR","CEREBROVASCULAR",
    "CHRONIC_KIDNEY","CHRONIC_PAIN_FIBRO","CHF","COPD","DEMENTIA","DEPRESSION",
    "DIABETES","DYSLIPIDEMIA","EPILEPSY_SEIZURE","HEPATITIS","HIV_AIDS","HYPERTENSION",
    "LIVER_GALLBLADDER_PANCREAS","MI_CAD","OSTEOARTHRITIS","PARALYSIS","PEPTIC_ULCER",
    "PERIPHERAL_VASCULAR","RENAL_FAILURE","RHEUMATOLOGIC","SCHIZOPHRENIA","SLEEP_DISORDERS",
    "SMOKING","THYROID","Solid_Tumor","Metastatic","Leukemia_Lymphoma","Other_Cancer","Cancer_In_Situ",
]
FLAG_PROB = {c: float(df_joined[c].mean()) for c in FLAG_COLS}

# ── Statistik numerik (mean & std untuk normal/lognormal sampling) ──
def col_stats(col):
    s = df_joined[col].dropna()
    return float(s.mean()), float(s.std()), float(s.min()), float(s.max())

PROC_MAP = {
    "CPT-80053":  ("Laboratory",  "Comprehensive Metabolic Panel", 45.01,  54.99),
    "CPT-70450":  ("Radiology",   "CT Scan, Head/Brain",          766.95, 934.31),
    "CPT-71045":  ("Radiology",   "Chest X-Ray, single view",     108.05, 130.50),
    "ICD10-0DTJ": ("Surgery",     "Appendectomy (Open)",         7659.77, 9334.26),
    "CPT-93000":  ("Diagnostic",  "Electrocardiogram (ECG)",       67.59,  82.49),
}

print(f"  Kolom kategorikal   : {len(CAT_COLS)}")
print(f"  Kolom flag binary   : {len(FLAG_COLS)}")
print(f"  Total kolom dataset : {len(COLUMNS)}")


# ================================================================
#  3. FUNGSI GENERATOR SATU BARIS
# ================================================================

def wrand(d: dict):
    """Weighted random dari dict {value: prob}."""
    keys = list(d.keys())
    probs = list(d.values())
    return random.choices(keys, weights=probs, k=1)[0]

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def rand_norm(mean, std, lo, hi):
    return clamp(float(np.random.normal(mean, std)), lo, hi)

def rand_pos_norm(mean, std, lo=0.0, hi=None):
    v = max(lo, float(np.random.normal(mean, std)))
    return v if hi is None else min(v, hi)

def rand_int_norm(mean, std, lo=0, hi=None):
    v = max(lo, int(round(np.random.normal(mean, std))))
    return v if hi is None else min(v, hi)

def generate_row(pat_index: int) -> dict:
    row = {}

    # ── Identitas / kunci ──────────────────────────────────────
    row["patIndex"]      = str(pat_index)

    # ── Kategorikal ───────────────────────────────────────────
    row["pdc_cat"]       = wrand(CAT_COLS["pdc_cat"])
    row["age_grpN"]      = wrand(CAT_COLS["age_grpN"])
    row["sexN"]          = wrand(CAT_COLS["sexN"])
    row["regionN"]       = wrand(CAT_COLS["regionN"])
    row["idx_prodtypeN"] = wrand(CAT_COLS["idx_prodtypeN"])
    row["idx_paytypN"]   = wrand(CAT_COLS["idx_paytypN"])
    row["age_cat"]       = wrand(CAT_COLS["age_cat"])
    row["pre_total_cat"] = wrand(CAT_COLS["pre_total_cat"])
    row["drug_class"]    = wrand(CAT_COLS["drug_class"])

    # ── pdc (Proportion of Days Covered) ─────────────────────
    pdc_cat = row["pdc_cat"]
    if   pdc_cat == 1: pdc = rand_norm(0.85, 0.12, 0.8, 1.0)
    elif pdc_cat == 2: pdc = rand_norm(0.55, 0.13, 0.4, 0.79)
    elif pdc_cat == 3: pdc = rand_norm(0.28, 0.12, 0.1, 0.39)
    else:              pdc = rand_norm(0.15, 0.07, 0.07, 0.24)
    row["pdc"]           = round(pdc, 9)
    row["pdc_80_flag"]   = 1 if pdc >= 0.8 else 0

    # ── Flag binary (penyakit komorbid) ──────────────────────
    for col in FLAG_COLS:
        if col not in ("pdc_80_flag",):
            row[col] = int(random.random() < FLAG_PROB[col])

    # ── Biaya PRE-index ───────────────────────────────────────
    pre_ip_flag = row["pre_ip_flag"]
    pre_er_flag = row["pre_er_flag"]
    row["pre_ip_cost"]  = round(rand_pos_norm(1531.38, 7363.84) if pre_ip_flag else 0.0, 6)
    row["pre_er_cost"]  = round(rand_pos_norm(185.33,   678.32) if pre_er_flag else 0.0, 6)
    row["pre_rx_cost"]  = round(rand_pos_norm(1056.71, 1761.11, lo=0.0), 6)
    row["pre_op_cost"]  = round(rand_pos_norm(2267.05, 4550.48, lo=0.0), 6)
    row["pre_medical_cost"] = round(row["pre_ip_cost"] + row["pre_er_cost"] + row["pre_op_cost"], 6)
    row["pre_total_cost"]   = round(row["pre_medical_cost"] + row["pre_rx_cost"], 6)

    # ── Biaya POST-index ──────────────────────────────────────
    post_ip_flag = row["post_ip_flag"]
    post_er_flag = row["post_er_flag"]
    row["post_ip_cost"] = round(rand_pos_norm(1084.03, 4195.50) if post_ip_flag else 0.0, 6)
    row["post_er_cost"] = round(rand_pos_norm(159.62,   561.75) if post_er_flag else 0.0, 6)
    row["post_rx_cost"] = round(rand_pos_norm(1597.37, 2261.36, lo=3.38), 6)
    row["post_op_cost"] = round(rand_pos_norm(2596.58, 5276.33, lo=0.0), 6)
    row["post_medical_cost"] = round(row["post_ip_cost"] + row["post_er_cost"] + row["post_op_cost"], 6)
    row["post_total_cost"]   = round(row["post_medical_cost"] + row["post_rx_cost"], 6)

    # ── Copay & log ───────────────────────────────────────────
    idx_copay = rand_pos_norm(15.95, 22.85, lo=0.01, hi=141.10)
    row["idx_copay"]     = round(idx_copay, 6)
    row["log_idx_copay"] = round(math.log(idx_copay) if idx_copay > 0 else -4.60517, 9)

    # ── Utilisasi PRE ─────────────────────────────────────────
    row["num_ip"]      = rand_int_norm(0.10, 0.38, 0, 3)
    row["total_los"]   = rand_int_norm(0.49, 2.79, 0, 34)
    row["num_op"]      = rand_int_norm(6.46, 7.36, 0, 55)
    row["num_er"]      = rand_int_norm(0.30, 0.84, 0, 7)
    row["num_ndc"]     = rand_int_norm(10.80, 10.73, 0, 67)
    row["num_gpi6"]    = rand_int_norm(5.19, 3.66, 0, 20)

    # ── Utilisasi POST ────────────────────────────────────────
    row["num_ip_post"]      = rand_int_norm(0.11, 0.37, 0, 2)
    row["total_los_post"]   = rand_int_norm(0.62, 2.43, 0, 30)
    row["num_op_post"]      = rand_int_norm(7.35, 8.28, 0, 56)
    row["num_er_post"]      = rand_int_norm(0.24, 0.63, 0, 4)
    row["num_ndc_post"]     = rand_int_norm(16.82, 12.46, 1, 88)
    row["num_gpi6_post"]    = rand_int_norm(6.89, 4.11, 1, 24)

    # ── Generic/Brand obat PRE ────────────────────────────────
    row["numofgen"]     = rand_int_norm(7.90, 8.24, 0, 52)
    row["numofbrand"]   = rand_int_norm(2.94, 4.38, 0, 27)
    row["generic_cost"] = round(rand_pos_norm(224.63, 370.68, lo=0.0), 6)
    row["brand_cost"]   = round(rand_pos_norm(793.87, 1579.95, lo=0.0), 6)
    total_drug_pre = row["generic_cost"] + row["brand_cost"]
    row["ratio_G_total_cost"] = round(
        row["generic_cost"] / total_drug_pre if total_drug_pre > 0 else None, 6
    ) if total_drug_pre > 0 else None

    # ── Generic/Brand obat POST ───────────────────────────────
    row["numofgen_post"]     = rand_int_norm(12.20, 9.51, 0, 64)
    row["numofbrand_post"]   = rand_int_norm(4.66, 5.53, 0, 41)
    row["generic_cost_post"] = round(rand_pos_norm(300.0, 450.0, lo=0.0), 6)
    row["brand_cost_post"]   = round(rand_pos_norm(900.0, 1700.0, lo=0.0), 6)
    total_drug_post = row["generic_cost_post"] + row["brand_cost_post"]
    row["ratio_G_total_cost_post"] = round(
        row["generic_cost_post"] / total_drug_post if total_drug_post > 0 else None, 6
    ) if total_drug_post > 0 else None

    # ── Generic rate ──────────────────────────────────────────
    row["generic_rate"]      = round(clamp(rand_norm(0.746, 0.307, 0.0, 1.0), 0, 1), 9)
    row["generic_rate_post"] = round(clamp(rand_norm(0.732, 0.269, 0.0, 1.0), 0, 1), 9)

    # ── Adjust total (utilisasi terbobot) ─────────────────────
    row["adjust_total_30d"]      = round(rand_pos_norm(20.53, 15.98, lo=1.0), 8)
    row["adjust_total_30d_post"] = round(rand_pos_norm(21.51, 16.78, lo=1.0), 8)

    # ── Log biaya ─────────────────────────────────────────────
    def safe_log(v): return round(math.log(v) if v and v > 0 else -4.60517, 9)
    row["log_pre_ip_cost"] = safe_log(row["pre_ip_cost"])
    row["log_pre_er_cost"] = safe_log(row["pre_er_cost"])
    row["log_pre_op_cost"] = safe_log(row["pre_op_cost"])
    row["log_pre_rx_cost"] = safe_log(row["pre_rx_cost"])

    # ── CCI (Charlson Comorbidity Index) ──────────────────────
    row["pre_CCI"] = rand_int_norm(1.03, 1.19, 0, 8)

    # ── patient_key ───────────────────────────────────────────
    row["patient_key"] = random.randint(100, 600000)

    # ── Prosedur medis (dari SQL) ──────────────────────────────
    proc_code = wrand(CAT_COLS["Procedure_Code"])
    proc_cat, proc_desc, cost_min, cost_max = PROC_MAP[proc_code]
    row["Procedure_ID"]          = f"TR-{20000 + pat_index}"
    row["Procedure_Date"]        = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    row["Procedure_Code"]        = proc_code
    row["Procedure_Category"]    = proc_cat
    row["Procedure_Description"] = proc_desc
    row["Cost"]                  = round(random.uniform(cost_min, cost_max), 2)

    return row


# ================================================================
#  4. GABUNG DATA ASLI + GENERATE DUMMY
# ================================================================
sep("STEP 3 — GABUNGKAN DATA ASLI + GENERATE DUMMY")

# Data asli (hasil JOIN)
original_records = df_joined.to_dict(orient="records")
n_original = len(original_records)
n_dummy    = N_TARGET - n_original
print(f"  Data asli (JOIN)    : {n_original:,} baris")
print(f"  Data dummy generate : {n_dummy:,} baris")
print(f"  Total target        : {N_TARGET:,} baris")

# Generate dummy
print(f"  Generating {n_dummy:,} dummy records...", end=" ", flush=True)
dummy_records = [generate_row(n_original + i + 1) for i in range(n_dummy)]
print("Done!")

# Pastikan kolom dummy sama persis dengan kolom joined
for r in dummy_records:
    for col in COLUMNS:
        if col not in r:
            r[col] = None

all_records = original_records + dummy_records
random.shuffle(all_records)   # acak urutan agar tidak terblok


# ================================================================
#  5. SIMPAN KE CSV
# ================================================================
sep("STEP 4 — SIMPAN OUTPUT")

print(f"  Menulis {OUT_CSV.name}...", end=" ", flush=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_records)
print("Done!")


# ================================================================
#  6. SIMPAN KE SQL
# ================================================================
print(f"  Menulis {OUT_SQL.name}...", end=" ", flush=True)

# Buat kolom DDL otomatis dari tipe pandas
df_final = pd.read_csv(OUT_CSV, nrows=5)
def pandas_to_sql_type(dtype):
    if "int" in str(dtype):   return "INTEGER"
    if "float" in str(dtype): return "REAL"
    return "TEXT"

col_defs = ",\n    ".join(
    f"{col}  {pandas_to_sql_type(df_final[col].dtype)}"
    for col in COLUMNS
)
ddl = f"""-- ================================================================
--  healthcare_joined_10000  ({N_TARGET:,} records)
--  Gabungan: healthcareTest.csv + kaggle_medical_procedures_dummy.sql
--  + {n_dummy:,} data dummy tambahan
-- ================================================================

DROP TABLE IF EXISTS healthcare_joined;

CREATE TABLE healthcare_joined (
    {col_defs}
);

"""

with open(OUT_SQL, "w", encoding="utf-8") as f:
    f.write(ddl)
    for row in all_records:
        vals = []
        for col in COLUMNS:
            v = row.get(col)
            if v is None:
                vals.append("NULL")
            elif isinstance(v, str):
                vals.append(f"'{v.replace(chr(39), chr(39)*2)}'")
            elif isinstance(v, float) and math.isnan(v):
                vals.append("NULL")
            else:
                vals.append(str(v))
        f.write(f"INSERT INTO healthcare_joined VALUES ({', '.join(vals)});\n")
print("Done!")


# ================================================================
#  7. VALIDASI & TAMPILKAN RINGKASAN
# ================================================================
sep("STEP 5 — VALIDASI")

df_out = pd.read_csv(OUT_CSV)
print(f"\n  Total baris         : {len(df_out):,}")
print(f"  Total kolom         : {len(df_out.columns)}")
print(f"  Nilai null          : {df_out.isnull().sum().sum():,}")

sep("STRUKTUR KOLOM")
# Kelompokkan kolom berdasarkan kategori
groups = {
    "🔑 Identitas / Kunci"   : ["patIndex","patient_key","drug_class"],
    "📋 PDC & Flag Kualitas" : ["pdc","pdc_cat","pdc_80_flag","age_grpN","sexN","regionN",
                                 "idx_prodtypeN","idx_paytypN","age_cat"],
    "🏥 Komorbiditas (Flag)" : [c for c in FLAG_COLS if c not in ("post_ip_flag","post_er_flag","pre_ip_flag","pre_er_flag","pdc_80_flag")],
    "💊 Utilisasi PRE"       : ["num_ip","total_los","num_op","num_er","num_ndc","num_gpi6",
                                 "pre_ip_flag","pre_er_flag"],
    "💰 Biaya PRE"           : ["pre_ip_cost","pre_er_cost","pre_rx_cost","pre_op_cost",
                                 "pre_medical_cost","pre_total_cost","pre_CCI","pre_total_cat",
                                 "log_pre_ip_cost","log_pre_er_cost","log_pre_op_cost","log_pre_rx_cost"],
    "💊 Utilisasi POST"      : ["num_ip_post","total_los_post","num_op_post","num_er_post",
                                 "num_ndc_post","num_gpi6_post","post_ip_flag","post_er_flag"],
    "💰 Biaya POST"          : ["post_ip_cost","post_er_cost","post_rx_cost","post_op_cost",
                                 "post_medical_cost","post_total_cost","adjust_total_30d_post"],
    "💊 Obat Generik/Brand"  : ["numofgen","numofbrand","generic_cost","brand_cost",
                                 "ratio_G_total_cost","generic_rate","numofgen_post",
                                 "numofbrand_post","generic_cost_post","brand_cost_post",
                                 "ratio_G_total_cost_post","generic_rate_post"],
    "🔧 Lainnya"             : ["idx_copay","log_idx_copay","adjust_total_30d"],
    "✅ Tindakan Medis (SQL)" : ["Procedure_ID","Procedure_Date","Procedure_Code",
                                  "Procedure_Category","Procedure_Description","Cost"],
}

no = 1
for grp, cols in groups.items():
    print(f"\n  {grp}")
    for col in cols:
        if col in df_out.columns:
            print(f"    {no:<4} {col:<35} {str(df_out[col].dtype)}")
            no += 1

sep("DISTRIBUSI KOLOM KUNCI")
for col in ["pdc_cat","sexN","age_grpN","regionN","Procedure_Category","pdc_80_flag"]:
    print(f"\n  [{col}]")
    for v, c in df_out[col].value_counts().items():
        bar = "█" * int(c / len(df_out) * 35)
        print(f"    {str(v):<20} {c:>6,} ({c/len(df_out)*100:5.1f}%)  {bar}")

sep("STATISTIK NUMERIK KUNCI")
key_num = ["pdc","pre_total_cost","post_total_cost","idx_copay","Cost"]
for col in key_num:
    s = df_out[col].dropna()
    print(f"\n  {col}")
    print(f"    Min: {s.min():>14,.4f}   Max: {s.max():>14,.4f}")
    print(f"    Avg: {s.mean():>14,.4f}   Std: {s.std():>14,.4f}")

sep("SAMPLE DATA (3 baris)")
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 130)
pd.set_option("display.max_colwidth", 22)
show_cols = ["patIndex","pdc","pdc_cat","sexN","age_cat","DIABETES","HYPERTENSION",
             "pre_total_cost","post_total_cost","Procedure_Category","Procedure_Description","Cost"]
print(df_out[show_cols].head(3).to_string(index=False))

sep("OUTPUT FILE")
print(f"  📄 CSV : {OUT_CSV}  ({OUT_CSV.stat().st_size/1024:,.1f} KB)")
print(f"  📄 SQL : {OUT_SQL}  ({OUT_SQL.stat().st_size/1024:,.1f} KB)")
sep()
