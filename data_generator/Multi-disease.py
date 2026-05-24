"""
================================================================
  JOIN + Generate 10.000 Record Healthcare (Multi-Disease Hospital)
  Bebas Dependensi File SQL Luar (Auto-Generate Procedures)
  Sumber:
    - healthcareTest.csv                   (data klinis pasien)
  Output:
    - healthcare_joined_10000.csv
    - healthcare_joined_10000.sql
================================================================
"""

import random
import math
import csv
import numpy as np
import pandas as pd
from pathlib import Path

random.seed(42)
np.random.seed(42)

# ── Path ──────────────────────────────────────────────────────
_dir     = Path(__file__).parent.resolve()
CSV_IN   = _dir / "healthcareTest.csv"
OUT_CSV  = _dir / "healthcare_joined_10000.csv"
OUT_SQL  = _dir / "healthcare_joined_10000.sql"
N_TARGET = 10_000

# Sekarang kita hanya memvalidasi file CSV utama
if not CSV_IN.exists():
    raise FileNotFoundError(f"File tidak ditemukan: {CSV_IN}\nPastikan file 'healthcareTest.csv' ada di folder yang sama dengan skrip ini.")


def sep(title="", w=66):
    if title:
        p = (w - len(title) - 2) // 2
        print(f"\n{'='*p} {title} {'='*(w-p-len(title)-2)}")
    else:
        print("=" * w)


# Master data tindakan medis untuk simulasi pengganti file SQL
PROC_MAP = {
    "CPT-80053":  ("Laboratory",  "Comprehensive Metabolic Panel", 45.01,  54.99),
    "CPT-70450":  ("Radiology",   "CT Scan, Head/Brain",          766.95, 934.31),
    "CPT-71045":  ("Radiology",   "Chest X-Ray, single view",     108.05, 130.50),
    "ICD10-0DTJ": ("Surgery",     "Appendectomy (Open)",         7659.77, 9334.26),
    "CPT-93000":  ("Diagnostic",  "Electrocardiogram (ECG)",       67.59,  82.49),
}


# ── Fungsi Atribusi Multi-Disease & Operasional Rumah Sakit ──
def derive_hospital_features(row):
    """
    Mengonversi flag komorbiditas biner menjadi entitas 
    Diagnosis Utama (ICD-10) dan Kategori Penyakit untuk RS Umum.
    """
    active_diseases = []
    if row.get("DIABETES") == 1:             active_diseases.append(("E11", "Endocrine & Metabolic"))
    if row.get("HYPERTENSION") == 1:         active_diseases.append(("I10", "Cardiovascular"))
    if row.get("ASTHMA") == 1:               active_diseases.append(("J45", "Respiratory"))
    if row.get("CHF") == 1:                  active_diseases.append(("I50", "Cardiovascular"))
    if row.get("COPD") == 1:                 active_diseases.append(("J44", "Respiratory"))
    if row.get("PEPTIC_ULCER") == 1:         active_diseases.append(("K27", "Gastrointestinal"))
    if row.get("Solid_Tumor") == 1:          active_diseases.append(("C80", "Oncology"))
    if row.get("CHRONIC_KIDNEY") == 1:       active_diseases.append(("N18", "Nephrology"))
    if row.get("DEPRESSION") == 1:           active_diseases.append(("F32", "Psychiatry"))
    
    if active_diseases:
        chosen_diag = random.choice(active_diseases)
    else:
        fallbacks = [
            ("A09", "Gastroenteritis (Infectious)"),
            ("M17", "Orthopedics (Osteoarthritis)"),
            ("Z00", "General Medicine Checkup"),
            ("J06", "Acute Upper Respiratory Infection")
        ]
        chosen_diag = random.choice(fallbacks)
        
    admission_type = random.choice(["Emergency", "Elective", "Urgent"])
    return chosen_diag[0], chosen_diag[1], admission_type


# ================================================================
#  1. LOAD DATA ASLI & SIMULASI TINDAKAN MEDIS
# ================================================================
sep("STEP 1 — LOAD DATA ASLI & SINTESIS PROSEDUR")

df_csv = pd.read_csv(CSV_IN)
df_csv["patIndex"] = df_csv["patIndex"].astype(str)
print(f"  healthcareTest.csv Berhasil Dimuat: {len(df_csv):,} baris")

# Membuat data tindakan medis tiruan langsung di memori untuk menggantikan file SQL
print("  Membuat data tindakan medis secara otomatis pengganti file SQL...")
sql_mock_data = []
proc_codes = list(PROC_MAP.keys())

for idx, pat_idx in enumerate(df_csv["patIndex"]):
    p_code = random.choice(proc_codes)
    p_cat, p_desc, c_min, c_max = PROC_MAP[p_code]
    sql_mock_data.append({
        "patIndex": pat_idx,
        "Procedure_ID": f"TR-{10000 + idx}",
        "Procedure_Date": f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "Procedure_Code": p_code,
        "Procedure_Category": p_cat,
        "Procedure_Description": p_desc,
        "Cost": round(random.uniform(c_min, c_max), 2)
    })

df_sql = pd.DataFrame(sql_mock_data)
print(f"  Data Prosedur (In-Memory) Terbuat: {len(df_sql):,} baris")

# Lakukan JOIN di dalam memori
df_joined = pd.merge(df_csv, df_sql, on="patIndex", how="inner")

print("  Mentransformasikan data ke skenario Rumah Sakit Umum (Multi-Disease)...")
hospital_features = df_joined.apply(lambda r: derive_hospital_features(r), axis=1)
df_joined["Primary_Diagnosis_Code"] = [x[0] for x in hospital_features]
df_joined["Diagnosis_Category"] = [x[1] for x in hospital_features]
df_joined["Admission_Type"] = [x[2] for x in hospital_features]

# Susun struktur susunan kolom final
sql_extra_cols = [c for c in df_sql.columns if c != "patIndex"]
new_hospital_cols = ["Primary_Diagnosis_Code", "Diagnosis_Category", "Admission_Type"]
col_order = list(df_csv.columns) + new_hospital_cols + sql_extra_cols
df_joined = df_joined[col_order]

COLUMNS = list(df_joined.columns)


# ================================================================
#  2. PELAJARI DISTRIBUSI KATEGORIKAL & FLAG
# ================================================================
sep("STEP 2 — ANALISIS DISTRIBUSI DATA")

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


# ================================================================
#  3. FUNGSI GENERATOR DATA DUMMY TAMBAHAN
# ================================================================

def wrand(d: dict):
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
    row["patIndex"] = str(pat_index)

    row["pdc_cat"]       = wrand(CAT_COLS["pdc_cat"])
    row["age_grpN"]      = wrand(CAT_COLS["age_grpN"])
    row["sexN"]          = wrand(CAT_COLS["sexN"])
    row["regionN"]       = wrand(CAT_COLS["regionN"])
    row["idx_prodtypeN"] = wrand(CAT_COLS["idx_prodtypeN"])
    row["idx_paytypN"]   = wrand(CAT_COLS["idx_paytypN"])
    row["age_cat"]       = wrand(CAT_COLS["age_cat"])
    row["pre_total_cat"] = wrand(CAT_COLS["pre_total_cat"])
    row["drug_class"]    = wrand(CAT_COLS["drug_class"])

    pdc_cat = row["pdc_cat"]
    if   pdc_cat == 1: pdc = rand_norm(0.85, 0.12, 0.8, 1.0)
    elif pdc_cat == 2: pdc = rand_norm(0.55, 0.13, 0.4, 0.79)
    elif pdc_cat == 3: pdc = rand_norm(0.28, 0.12, 0.1, 0.39)
    else:              pdc = rand_norm(0.15, 0.07, 0.07, 0.24)
    row["pdc"]           = round(pdc, 9)
    row["pdc_80_flag"]   = 1 if pdc >= 0.8 else 0

    for col in FLAG_COLS:
        if col not in ("pdc_80_flag",):
            row[col] = int(random.random() < FLAG_PROB[col])

    # Menyisipkan info penyakit & operasional RS ke data baru
    diag_code, diag_cat, adm_type = derive_hospital_features(row)
    row["Primary_Diagnosis_Code"] = diag_code
    row["Diagnosis_Category"] = diag_cat
    row["Admission_Type"] = adm_type

    # Simulasi Biaya & Utilisasi Rumah Sakit
    pre_ip_flag = row["pre_ip_flag"]
    pre_er_flag = row["pre_er_flag"]
    row["pre_ip_cost"]  = round(rand_pos_norm(1531.38, 7363.84) if pre_ip_flag else 0.0, 6)
    row["pre_er_cost"]  = round(rand_pos_norm(185.33,   678.32) if pre_er_flag else 0.0, 6)
    row["pre_rx_cost"]  = round(rand_pos_norm(1056.71, 1761.11, lo=0.0), 6)
    row["pre_op_cost"]  = round(rand_pos_norm(2267.05, 4550.48, lo=0.0), 6)
    row["pre_medical_cost"] = round(row["pre_ip_cost"] + row["pre_er_cost"] + row["pre_op_cost"], 6)
    row["pre_total_cost"]   = round(row["pre_medical_cost"] + row["pre_rx_cost"], 6)

    post_ip_flag = row["post_ip_flag"]
    post_er_flag = row["post_er_flag"]
    row["post_ip_cost"] = round(rand_pos_norm(1084.03, 4195.50) if post_ip_flag else 0.0, 6)
    row["post_er_cost"] = round(rand_pos_norm(159.62,   561.75) if post_er_flag else 0.0, 6)
    row["post_rx_cost"] = round(rand_pos_norm(1597.37, 2261.36, lo=3.38), 6)
    row["post_op_cost"] = round(rand_pos_norm(2596.58, 5276.33, lo=0.0), 6)
    row["post_medical_cost"] = round(row["post_ip_cost"] + row["post_er_cost"] + row["post_op_cost"], 6)
    row["post_total_cost"]   = round(row["post_medical_cost"] + row["post_rx_cost"], 6)

    idx_copay = rand_pos_norm(15.95, 22.85, lo=0.01, hi=141.10)
    row["idx_copay"]     = round(idx_copay, 6)
    row["log_idx_copay"] = round(math.log(idx_copay) if idx_copay > 0 else -4.60517, 9)

    row["num_ip"]      = rand_int_norm(0.10, 0.38, 0, 3)
    row["total_los"]   = rand_int_norm(0.49, 2.79, 0, 34)
    row["num_op"]      = rand_int_norm(6.46, 7.36, 0, 55)
    row["num_er"]      = rand_int_norm(0.30, 0.84, 0, 7)
    row["num_ndc"]     = rand_int_norm(10.80, 10.73, 0, 67)
    row["num_gpi6"]    = rand_int_norm(5.19, 3.66, 0, 20)

    row["num_ip_post"]      = rand_int_norm(0.11, 0.37, 0, 2)
    row["total_los_post"]   = rand_int_norm(0.62, 2.43, 0, 30)
    row["num_op_post"]      = rand_int_norm(7.35, 8.28, 0, 56)
    row["num_er_post"]      = rand_int_norm(0.24, 0.63, 0, 4)
    row["num_ndc_post"]     = rand_int_norm(16.82, 12.46, 1, 88)
    row["num_gpi6_post"]    = rand_int_norm(6.89, 4.11, 1, 24)

    row["numofgen"]     = rand_int_norm(7.90, 8.24, 0, 52)
    row["numofbrand"]   = rand_int_norm(2.94, 4.38, 0, 27)
    row["generic_cost"] = round(rand_pos_norm(224.63, 370.68, lo=0.0), 6)
    row["brand_cost"]   = round(rand_pos_norm(793.87, 1579.95, lo=0.0), 6)
    total_drug_pre = row["generic_cost"] + row["brand_cost"]
    row["ratio_G_total_cost"] = round(row["generic_cost"] / total_drug_pre if total_drug_pre > 0 else None, 6) if total_drug_pre > 0 else None

    row["numofgen_post"]     = rand_int_norm(12.20, 9.51, 0, 64)
    row["numofbrand_post"]   = rand_int_norm(4.66, 5.53, 0, 41)
    row["generic_cost_post"] = round(rand_pos_norm(300.0, 450.0, lo=0.0), 6)
    row["brand_cost_post"]   = round(rand_pos_norm(900.0, 1700.0, lo=0.0), 6)
    total_drug_post = row["generic_cost_post"] + row["brand_cost_post"]
    row["ratio_G_total_cost_post"] = round(row["generic_cost_post"] / total_drug_post if total_drug_post > 0 else None, 6) if total_drug_post > 0 else None

    row["generic_rate"]      = round(clamp(rand_norm(0.746, 0.307, 0.0, 1.0), 0, 1), 9)
    row["generic_rate_post"] = round(clamp(rand_norm(0.732, 0.269, 0.0, 1.0), 0, 1), 9)

    row["adjust_total_30d"]      = round(rand_pos_norm(20.53, 15.98, lo=1.0), 8)
    row["adjust_total_30d_post"] = round(rand_pos_norm(21.51, 16.78, lo=1.0), 8)

    def safe_log(v): return round(math.log(v) if v and v > 0 else -4.60517, 9)
    row["log_pre_ip_cost"] = safe_log(row["pre_ip_cost"])
    row["log_pre_er_cost"] = safe_log(row["pre_er_cost"])
    row["log_pre_op_cost"] = safe_log(row["pre_op_cost"])
    row["log_pre_rx_cost"] = safe_log(row["pre_rx_cost"])

    row["pre_CCI"] = rand_int_norm(1.03, 1.19, 0, 8)
    row["patient_key"] = random.randint(100, 600000)

    # Prosedur Tindakan Medis Dummy
    proc_code = wrand(CAT_COLS["Procedure_Code"])
    proc_cat, proc_desc, cost_min, cost_max = PROC_MAP[proc_code]
    row["Procedure_ID"]          = f"TR-{20000 + pat_index}"
    row["Procedure_Date"]        = f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    row["Procedure_Code"]        = proc_code
    row["Procedure_Category"]    = proc_cat
    row["Procedure_Description"] = proc_desc
    row["Cost"]                  = round(random.uniform(cost_min, cost_max), 2)

    return row


# ================================================================
#  4. PROSES PENGGABUNGAN DATA
# ================================================================
sep("STEP 3 — GABUNGKAN DATA ASLI + DATA GENERATE")

original_records = df_joined.to_dict(orient="records")
n_original = len(original_records)
n_dummy    = N_TARGET - n_original
print(f"  Data asal dari CSV     : {n_original:,} baris")
print(f"  Data dummy tambahan    : {n_dummy:,} baris")

print(f"  Sedang memproses {n_dummy:,} data dummy...", end=" ", flush=True)
dummy_records = [generate_row(n_original + i + 1) for i in range(n_dummy)]
print("Selesai!")

for r in dummy_records:
    for col in COLUMNS:
        if col not in r:
            r[col] = None

all_records = original_records + dummy_records
random.shuffle(all_records)


# ================================================================
#  5. EKSPOR DATA KE FILE (CSV & SQL)
# ================================================================
sep("STEP 4 — PENYIMPANAN OUTPUT")

print(f"  Menulis file {OUT_CSV.name}...", end=" ", flush=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_records)
print("Selesai!")

print(f"  Menulis file {OUT_SQL.name}...", end=" ", flush=True)
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
--  Dataset DWBI Satu Rumah Sakit Lintas Penyakit (10.000 Baris)
-- ================================================================

DROP TABLE IF EXISTS hospital_encounters;

CREATE TABLE hospital_encounters (
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
        f.write(f"INSERT INTO hospital_encounters VALUES ({', '.join(vals)});\n")
print("Selesai!")


# ================================================================
#  6. ANALISIS AKHIR OPERASIONAL RS
# ================================================================
sep("STEP 5 — ANALISIS RINGKASAN DATA RUMAH SAKIT")

df_out = pd.read_csv(OUT_CSV)
print(f"\n  Total Baris Berhasil Terbuat : {len(df_out):,}")

for col in ["Diagnosis_Category", "Admission_Type", "Procedure_Category"]:
    print(f"\n  [Distribusi Atribut: {col}]")
    for v, c in df_out[col].value_counts().items():
        bar = "█" * int(c / len(df_out) * 35)
        print(f"    {str(v):<32} {c:>6,} ({c/len(df_out)*100:5.1f}%)  {bar}")

sep()