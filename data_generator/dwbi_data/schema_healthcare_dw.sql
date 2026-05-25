
-- ========================================================
-- DDL SKEMA BINTANG DATA WAREHOUSE HEALTHCARE
-- ========================================================

DROP TABLE IF EXISTS fact_encounter;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_doctor;
DROP TABLE IF EXISTS dim_diagnosis;
DROP TABLE IF EXISTS dim_department;

CREATE TABLE dim_patient (
    patient_id VARCHAR(20) PRIMARY KEY,
    patient_name VARCHAR(100),
    gender VARCHAR(2),
    date_of_birth DATE,
    blood_type VARCHAR(5),
    city VARCHAR(100)
);

CREATE TABLE dim_doctor (
    doctor_id VARCHAR(20) PRIMARY KEY,
    doctor_name VARCHAR(100),
    specialty VARCHAR(100)
);

CREATE TABLE dim_diagnosis (
    icd10_code VARCHAR(10) PRIMARY KEY,
    diagnosis_name VARCHAR(200),
    category VARCHAR(100)
);

CREATE TABLE dim_department (
    dept_id VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100)
);

CREATE TABLE fact_encounter (
    encounter_id VARCHAR(30) PRIMARY KEY,
    patient_id VARCHAR(20) REFERENCES dim_patient(patient_id),
    doctor_id VARCHAR(20) REFERENCES dim_doctor(doctor_id),
    icd10_code VARCHAR(10) REFERENCES dim_diagnosis(icd10_code),
    dept_id VARCHAR(10) REFERENCES dim_department(dept_id),
    encounter_date DATE,
    admission_type VARCHAR(50),
    length_of_stay INTEGER,
    medication_cost NUMERIC(12,2),
    inpatient_cost NUMERIC(12,2),
    total_cost NUMERIC(12,2)
);
