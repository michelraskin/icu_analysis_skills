# ACCM PMAP Data Catalog (authoritative reference)

> Source: `ACCM-PMAP-Data-Catalog1.docx` (JIRA PS-68, "Anesthesiology and Critical
> Care Medicine Research Resource", IRB00227042; PI Adam Sapirstein). Converted to
> markdown for use as a `pmap-dataset` skill reference. This is the **canonical
> column-level dictionary** for the `accm_projection` database that the PMAP export
> is built from — use it to confirm exact table/column names, coded `_c` value
> meanings, code-system reference tables, and update cadence before trusting an
> assumption. Tables here are derived from upstream PMAP and live in the
> `accm_projection` DB; the on-disk CSVs in the lab export are named
> `dbo.accm_<table>.csv` (see the lcicm-cluster skill for paths).

## Data Projection Background and Status

JIRA:
PS-68
Study PI:
Adam Sapirstein
Study Title:
Anesthesiology and Critical Care Medicine Research Resource
Contact:
Adam Sapirstein, Jim Fackler, Jules Bergmann, Heather Zellner
Date:
12/11/2019
Extract purpose:
To create an expanded data resource to cover all patients cared for by the entire ACCM Department, in support of quality improvement, research, and grants.
Current IRB status:
IRB00227042, Approved
Funding available:
TBD
Extract frequency:
TBD
Data Types:
Relational, Imaging, Physiological Monitoring, Notes metadata, Genomic metadata and VCF files
Data Sources:
Epic Clarity, DICOM, PhysioCloud, <genomics sources TBD>
(all via PMAP)
Data Projection Name:
ACCM_PMAP_Projection
List of Users:
No users specified by name in IRB
Heather Zellner, as ACCM’s CCDA Adjunct
Heather to be able to deliver sub-projections to ACCM researchers:
(Maybe deliver as different schemas in the same projection DB)
Limited Data set:
No
Data Shared with external entity?
No

## Inclusion criteria

Only patients with the following criteria will be included in the extract results:
Patients seen at any JHMI facility having the following characteristics:
An anesthesia data record (equivalent to an entry in Clarity F_AN_RECORD_SUMMARY)
Having an ADT record with a location of an ACCM ICU (location defined by study team)
Having an encounter with the chronic pain clinic
Having a pain service consult (adult or pediatric)
Having an evaluation in the pre-op clinic
Having a difficult airway

## Exclusion criteria

Patients with the following criteria will be excluded from the extract results:
N/A

## Primary Data Tables

The following tables are generated from upstream PMAP and populated in the `accm_projection` database.
Update schedule: The full accm_flowsheet and accm_labs tables are updated weekly (Monday morning).  The 90-days of most recent history (accm_flowsheet_increment and accm_labs_increment) are updated on remaining days (except Sunday morning).  All other tables are update daily, except on Sunday mornings.
At time of update, data is ~24 hours old (eg the Monday projections contain data up to Saturday midnight).

### Patient Demographics (accm_patient)

Contains one row for each patient in the ACCM cohort.  Osler_id uniquely indexes patients.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient unique identifier |
| emrn | Enterprise MRN |
| jhhmrn | JHH MRN |
| bmcmrn | Bayview MRN |
| hcgmrn | HCGH MRN |
| smhmrn | Suburban MRN |
| shmrn | Sibley MRN |
| lastname | Patient last name |
| firstname | Patient first name |
| middlename | Patient middle name |
| namesuffix |  |
| birth_date | Date of birth |
| pat_status | Alive, or Deceased |
| death_date | Date of Death |
| gender | Patient gender.  One of: - Female, Male, Nonbinary, Other, Unknown |
| genderabbr | F, M, BN, O, U |
| ethnic_group | Patient ethnic group.  One of: - Hispanic, Not Hispanic, Pt Refused, Unknown |
| first_race | First documented patient race.  One of: - Am Indian, Asian, Black, Declined, Hispanic, Native Hawai, Other, Other Pacifi, Pac Islander, Two or More, Unknown, White |
| racew | White race - Y or Null |
| raceb | Black race – ‘Y’ or Null |
| racei | American Indian race – ‘Y’ or Null |
| racea | Asian race – ‘Y’ or Null |
| racep | Pacific Islander race – ‘Y’ or Null |
| raceo | Other race – ‘Y’ or Null |
| racerf | ?? Always Null |
| raceu | Unknown race – ‘Y’ or Null |
| racetwo | Two or more races – ‘Y’- or Null |
| racedec | Declined race – ‘Y’ or Null |
| raceh | ?Hispanic |
| address1 | Street address |
| address2 | Apartment or mailing code |
| city | City |
| stateabbr | State |
| county |  |
| country |  |
| zipcode |  |
| marital_status | One of: Declined to Answer, Divorced, Legally Separated, Married, Other, Significant Other, Single, Unknown, Widowed. |
| language |  |
| restricted_yn |  |
| first_contact |  |
| last_contact |  |
| next_contact |  |
| employment_status | One of: Disabled, Full Time, Never Worked, Not Employed, On Active Military Duty, Part Time, Retired, Self Employed, Student – Full Time, Student – Part Time, Unknown. |

### Inpatient Encounters (accm_inpatient)

One row for each inpatient encounter (admission, certain types of out-patient encounters).
From PMAP data catalog entry for epic (derived) / inpatient_encounters: “Hospital encounters created through an Admission/Discharge/Transfer (ADT) workflow, such as preadmission, admission, ED arrival, and Hospital Outpatient Visit (HOV).”

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_date_real |  |
| pat_enc_csn_id | Encounter identifier (each row in this table has unique value) |
| adt_pat_class_c | Patient class code (‘ZC_PAT_CLASS’) - 101 = ‘Inpatient’ - 102 = ‘Outpatient’ - 103 = ‘Emergency’ - 104 = ‘Observation’ - 106 = ‘Hospital Outpatient Surgery’ - 107 = ‘Newborn’ - 108 = ‘Surgery Admit’ - 109 = ‘Specimen’ - 124 = ‘Psychiatric’ - 126 = ‘Extended Surgical Recovery’ … others |
| adt_patient_stat_c | Patient status code (‘ZC_PAT_STATUS’) - ‘1’ = ‘Preadmission’ - ‘2’ = ‘Admission’ - ‘3’ = ‘Discharged’ - ‘5’ = ‘Leave of Absence’ - ‘6’ = ‘Hospital Outpatient Visit’ (Not ‘ZC_PATIENT_STATUS’): |
| pending_disch_time |  |
| exp_admission_time |  |
| exp_len_of_stay |  |
| admit_source_c | Admit source (OR ‘ZC_ADM_SOURCE’) - 1 = ‘Home, workplace, or non-healthcare facility’ - 34 = ‘From another health care facility’ - 45 = ‘From another acute care hospital or ED’ (Not ‘ZC_ADMIT_SOURCE’) |
| delivery_type_c | Delivery type (‘ZC_DELIVERY_TYPE’) - 250 = ‘Vaginal, Spontaneous’ - … |
| labor_status_c | Labor status (‘ZC_LABOR_STATUS’) - 5 = ‘Newborn’ (usually assigned to child) - 10 = ‘Discharged’ (usually assigned to mother |
| adt_arrival_time |  |
| hosp_admsn_time |  |
| hosp_disch_time |  |
| discharge_prov |  |
| admission_prov |  |
| hosp_admsn_type_c | Admission type (‘ZC_HOSP_ADMSN_TYPE’) - 1 = ‘Emergency’ - 2 = ‘Urgent’ - 3 = ‘Elective’ - 4 = ‘Newborn’ - 5 = ‘Trauma’ - 22 = ‘Other’ (20 total categories) |
| department_id |  |
| dep_speciality |  |
| dep_rpt_grp_ten |  |
| ZC_DEP_RPT_GRP_10 | - 1 = ‘JHCP’ - 2 = ‘SOM’ - 3 = ‘JHH’ - 4 = ‘Bayview Medical Center’ - 5 = ‘HCGH’ - 6 = ‘Sibley Memorial Hospital’ - 7 = ‘Suburban Hospital’ - 8 = ‘JHHC’ - 10 = ‘KKI’ - 11 = ‘Sibley Medical Group’ - 16 = ‘ACH’ (not in emr_dictionary) (14 total categories) |
| disch_disp_c | Discharge disposition (ZC_DISCH_DISP) - 1 = ‘Home or Self Care’ - 2 = ‘Acute care hospital’ - 3 = ‘Skilled nursing facility’ - 4 = ‘Custodial care facility’ - 5 = ‘Designated Cancer Center or Children’s Hospital’ - 6 = ‘Home-Health Care Services’ - 7 = ‘Left AMA’ - 9 = ‘Admitted as inpatient’ - 20 = ‘Expired’ - 206 = ‘Left Without Being Seen’ - 252 = ‘Other Health Care Facility’ - 261 = ‘AWOL’ - 276 = ‘IP Rehabilitation Facility …’ - 30 = ‘Still Patient (Leave of absence or interim bills) - 50 = ‘Hospice Home’ - 51 = ‘Hospice Facility’ - 62 = ‘Rehab’ - 63 = ‘Chronic Hospital …’ - 100 = ‘ED Dismiss – Never arrived’ (111 total categories) |
| hsp_account_id |  |
| inpatient_data_id |  |
| ip_episode_id |  |
| contact_date |  |
| ed_episode_id |  |
| inp_adm_date | Date-time of the inpatient admission – “date/time during the hospital encounter when the patient first received a base patient class of inpatient. This can be different than the value for the hospital admission date/time if the patient as assigned an emergency or outpatient base patient class” |
| ed_departure_date |  |
| op_adm_date | Date/time during the hospital encounter when the patient first received a base patient class of outpatient. |
| emer_adm_date |  |
| hospital_service |  |
| serv_area_name | One of: JHI BILLING, JHM CLINICAL, or ‘*Service area not specified’ |
| ed_visit_yn | ED Visit Y/N |

### ADT Events (accm_adt)

Unit, Service, and Events for inpatient encounters
Data Field
Notes
osler_id
event_id
event_type_c
One of (ZC_EVENT_TYPE):
- 1 Admission
- 2: Discharge
- 3: Transfer In
- 4: Transfer Out
- 5: Patient Update
- 6: Census
- 7: Hospital Outpatient
- 8: Leave of Absence Out
- 9: Leave of Absence Return
- 10: Leave of Absence Census
(Cannot be NULL)
event_subtype_c
department_id
room_id
room_csn_id
bed_id
room_csn_id
bed_status_c
effective_time
pat_enc_date_real
pat_enc_csn_id
event_type
pat_class_c
pat_service_c
pat_lvl_of_care_c
delete_time
canc_event_id
xfer_event_id
swap_event_id
comments
reason_c
accommodation_c
accom_reason_c
alt_event_type_c
orig_event_time
prev_upd_evnt_time
orig_eff_time
prev_upd_eff_time
xfer_in_event_id
next_out_event_id
last_in_event_id
base_pat_class_c
seq_num_in_enc
seq_num_in_bed_min
cancel_reason_c
out_event_type_c
in_event_type_c
from_base_class_c
to_base_class_c
labor_status_c
first_ip_in_ip_yn
order_id
source_loc_evnt_id
original_event_id
loa_reason_c
action_source_c
Related concepts:
Base.adt

### Anesthesia Episode (accm_an_record_summary)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
an_episode_id
Link to data not in projection
update_date
an_53_enc_csn_id
“AN_53” CSN (unrelated to admission or surgery)
an_52_enc_csn_id
“AN_52” CSN (unrelated to admission or surgery)
- associated with flowsheet and MAR entries
- will sometimes have profee procedures associated
an_inpatient_data_id
an_log_id
Note: Prefer an_log_id over case_id/log_id.  An_log_id is always defined if either case_id or log_id is defined.
an_resp_prov_id
an_date
Date of anesthesia encounter
an_time
an_start_datetime
Datetime of anesthesia start (None if canceled)
an_stop_datetime
Datetime of anesthesia stop (None if canceled)
an_proc_name
case_id
log_id
an_primary_note_id
has_perfusion_yn
rpt_status_c
This flag on the anesthesia record indicates the given record is inactive for analytical reporting downstream. A record might be flagged as inactive if it is linked to a canceled or voided case or procedure, was unlinked from a canceled or voided case or procedure, administrative documentation was made against the record indicating it was incomplete, or if there was no intraprocedure documentation.
- 1 = Active
- 2 = Inactive
an_billing_csn_id (new)
Typically the PAT_ENC_CSN_ID for the encounter
anes_ept_csn_link (new)
primary_log_enc_csn (new)
primary_prc_enc_csn (new)

### Anesthesia Datamart (accm_dm_anesthesia)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
record_id
dm_date
registry_status_c
pat_enc_csn_id
“AN_52” CSN (unrelated to admission or surgery)
- links to accm_an_record_summary.an_52_enc_csn_id
an_episode_id
record_date
…
X
extubation_dttm
Instant patient was extubated, or null if extubation event was not filed or airway LDA not documented as removed after procedure completion.

### Anesthesia Events (accm_ed_iev_events)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
pat_enc_csn_id
“AN_52” CSN (unrelated to admission or surgery)
- links to accm_an_record_summary.an_52_enc_csn_id
an_episode_id
an_53_enc_csn_id
event_id
event_line
ptmpl_record_type
DO NOT USE.
Event type (same code system as etmpl_record_type, but appears to be delayed?)
etmpl_record_type
Event type (appears to be from ED_IEV_EVENT_INFO).
- Numeric
ptmpl_event_name
DO NOT USE.
etmpl_event_name
1:1 name with etmpl_record_type
etmpl_display_name
RECOMMEND USING etmp_event_name instead.
Display name
- 1:1 with etmpl_record_type, when non-null
- sometimes null, even though event_name and record_name are non-null.
etmpl_record_name
Record name.  Has all caps meas_id flavor.
- 1:1 with etmpl_record_type
patevent_date
event_time
event_record_time
create_dttm
update_date
enc_contact_date
event_cmt
event_user_id
create_user_id
event_dept_id
event_note_id
event_prov_id
event_status_c
One of (from ED_IEV_EVENT_INFO Clarity documentation):
- 0 = Active
- 1 = Inactive
- 2 = Deleted
- 3 = Inactive and Deleted
- 4 = Hidden
- 5 = Inactive and Hidden
- 6 = Deleted and Hidden
- 7 = Inactive, Deleted, and Hidden

### Surgeries (accm_surgeries)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
proc_name
Procedure name
or_proc_id
Procedure ID (1:1 with proc_name)
** note – these do not index into CLARITY_EAP **
or_proc_line
Index of surgery for case_id/log_id
(Note: almost unique per case_id/log_id – some case_ids have duplicate rows differing only in csn_dtreal)
pat_enc_csn_id
CSN for group of surgeries (shared with other surgeries that have same case/log_id)
or_link_csn
CSN of Encounter
csn_dtreal
log_id
log_id and case_id always have same value, or are both null.
case_id
“ “
surgery_date
Date of surgery.
service_c
(ZC_OR_SERVICE)
- ‘190’ = Neurosurgery
case_class_c
One of (ZC_OR_CASE_CLASS)
- ’10’ = Elective  (47%)
- ‘50’ = Add on (4.6%)
- ‘55’ = Standby (3.8%)
- ‘60’ = ‘Level I’ (0.8%)
- ‘70’ = ‘Level II’  (1.5%)
- ‘80’ = ‘Level III’ (1.2%)
- ‘90’ = ‘Level IV’ (0.7%)
- ‘100’ = ‘Level V’ (0.3%)
- NULL   (39%)
pat_type_c
(ZC_PAT_CLASS)
or_status_c
One of (ZC_OR_STATUS)
- ‘1’ = ‘Missing Information’ (never occurs in ACCM PMAP)
- ‘2’ = ‘Posted’ (97.8%)
- ‘3’ = ‘Unposted’(  0.7%)
- ‘4’ = ‘Voided’(
- ‘5’ = ‘Completed’(
- ‘6’ = ‘Canceled’(
inpatient_data_id
is_clinical_trial
loc_id
Foreign key CLARITY_LOC.
- 110124 = ‘JHH ZBOR 5’
- 110128 = ‘JHH ENDOSCOPY’
- 110208 = ‘BMC CVIL’
- 110304 = ‘HCGH IRCV LAB’
room_id
sched_start_time
srgenc_contact_date
srgenc_type_c
Always ‘51’.
(Possibly ZC_DISP_ENC_TYPE, or ZC_EVENT_CE_ENC_TYPE_CMP )
srgenc_dept_id
Department where surgery was performed.
- Foreign key `department_id` in CLARIDY_DEP
srgenc_effective_dt
adtenc_contact_date
adtenc_type_c
adtenc_admit_time
adtenc_discharge_time
hsp_account_id
adt_dept_id
num_of_panels
Number of panels
panel_id
Panel ID.
Note: for a single log_id/case_id, multiple “surgeries” can have same panel_id.
primary_surgeon_id
Primary surgeon.
- Foreign key ‘prov_id’ in CLARITY_SER
asa_rating_c
ASA Rating.  One of
- 1 – Healthy (I)
- 2 – Mild systemic disease (II)
- 3 – Severe systemic disease (III)
- 4 – Incapacitating disease (IV)
- 5 – Moribund (V)
- 6 – Brain dead (VI)
May be null.
(ZC_OR_ASA_RATING)
anes_type_c
(ZC_OR_ANESTH_TYPE)
laterality_c
body_region_c
(ZC_OR_OP_REGION)
wound_class_c
loc_name (*)
proc_not_perf_c
Procedure not performed reason:
- 101 = “Canceled in Pre-op”
- 104 = “Aborted in OR”
(3 total values, including null)
proc_not_perf_reason
cancel_reason_c
Case cancellation reason:
- 2340 = “OTH-Other”
- 2650 = “SUR-Rescheduled by surgeon/schedule issue”
- 2520 = “PT-Patient/guardian requested reschedule”
- 2260 = “OR-Rescheduled by or/schedule issue”
- 2240 = “OR-Incorrect posting”
(82 total values, including null)
case_cancel_reason
cancel_date
log_type_c
adt_facility
sensitive_yn
srgenc_facility
Note:
- fields starting with ‘loc_name’ were added in Mar 2022.

### Encounter Diagnoses (accm_encounter_dx)

All diagnoses associated with an inpatient encounter
Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
pat_enc_csn_id
Encounter CSN
line
Ordering of diagnoses with admissions
dx_id
Unique internal (EPIC) identifier for the diagnosis
dx_name
Diagnosis name, (associated with dx_id). Note: the EMR allows different related diagnoses names to be associated with the same ICD-10 code.
dx_group
parent_dx_id
parnt_dx_name
icd10_code
icd9_code
enc_contact_date
annotation
dx_qualifer
primary_dx_yn
‘Y’ if diagnosis is a primary diagnosis for this encounter
dx_chronic_yn
‘Y’ if diagnosis is chronic
dx_unique
dx_ed_yn
dx_link_prob_id

### Clinic and other Outpatient Encounters (accm_outpatient)

In-person encounters with clinics specified by the study team
Data Field
Notes
osler_id
Patient identifier, links to ‘accm_patient’ table
pat_enc_date_real
pat_enc_csn_id
Patient encounter CSN (should be UNIQUE)
contact_date
enc_type_c
FIND ZTABLE
enc_type
Type of encounter:
- ‘Office Visit’
- ‘Appointment’
- ‘Historical Encounter’
- ‘Visit Encounter’
- ‘Home Care Visit’
- ‘Procedure visit’
… (28 total values)
visit_prov_id
visit_provider
department_id
department_name
Encounter department name
dep_specialty
dept_rpt_grp_ten
Facility of encounter (ZC_DEP_RPT_GRP_10)
- 1 = ‘JHCP’
- 2 = ‘SOM’
- 3 = ‘JHH’
- 4 = ‘Bayview Medical Center’
- 5 = ‘HCGH’
- 6 = ‘Sibley Memorial Hospital’
- 7 = ‘Suburban Hospital’
- 8 = ‘JHHC’
- 10 = ‘KKI’
- 11 = ‘Sibley Medical Group’
- 16 = ‘ACH’ (not in emr_dictionary)
dept_rev_loc_id
eff_dept_id
eff_dept_name
eff_dept_specialty
eff_dept_rpt_grp_ten
eff_dept_rev_loc_id
appt_time
appt_status_c
Appointment Status
One of:
- 1 / Scheduled (0.7%)
- 2 / Completed (42.5%)
- 3 / Canceled (19.0%)
- 4 / No Show (4.0%)
- 5 / Left without seen (0.06%)
- 6 / Arrived (0.04%)
- 7 / Present (0.0001%)
- 101 / Home Health Visit Incomplete (0.00003%)
- Null / Null (33.8%)
(May be NULL)
appt_prc_id
appt_visit_type
One of
appt_visit_abbr
appt_cancel_date
los_proc_code
los_proc_name
Imp_date
Imp_other
hsp_account_id
referral_id
referral_source_id
bp_systolic
Patient SBP
bp_diastolic
Patient DBP
temperature
Patient temperature (degrees F)
pulse
Patient HR
weight
Patient weight (ounces)
height
Patient height (unit?)
respirations
Patient respiratory rate
bmi
Computed BMI
bsa
Compuated body surface area (m^2)
inpatient_data_id
update_date
sensitive_yn
facilicity
is_historical
has_vitals

### EKG Results (accm_ecg_results)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
order_proc_id
performed_date
Date/time EKG performed
accession_number
accession_domain
resulting_time
resulting_lab
p_duration
pr_interval
qrs_duration
qt_interval
qtc_interval
p_axis
qrs_axis
t_axis
ventricular_rate
atrial_rate
interpretation
lab_status_c
result_lab_c

### Problem List (accm_problem_list)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
problem_list_id
Encounter CSN
dx_id
Unique internal (EPIC) identifier for the diagnosis
dx_name
Diagnosis name, (associated with dx_id). Note: the EMR allows different related diagnoses names to be associated with the same ICD-10 code.
dx_group
parent_dx_id
parnt_dx_name
icd10_code
icd9_code
problem_status
One of:
- ‘Active’ – problem is active
- ‘Resolved’ – problem has been resolved
- ‘Deleted’ – problem has been deleted (perhaps it was entered in error, was a duplicated, or has morphed into another problem)
noted_date
noted_end_date
resolved_date
date_of_entry
chronic_yn
‘Y’ if diagnosis is chronic
(Note: spelled ‘chronic_yn’, vs ‘dx_chronic_yn’ in enc_dx)
principal_pl_yn
‘Y’ if problem is a principal problem for patient.
overview_note_id
creating_order_id
problem_status_c
ZC_PROBLEM_STATUS
(Currently redundant with ‘problem_status’ field)
class_of_problem_c
One of (ZC_CLASS_OF_PROBLE):
- 1 = ‘Acute’
- 2 = ‘Chronic’
- 3 = ‘Minor’
- 4 = ‘Temporary’
- 5 = ‘Stage 1’
- 6 = ‘Stage 2’
- 7 = ‘Stage 3’
- 8 = ‘End Stage’
- NULL (most common … 99.47%)
priority_c
One of (ZC_PRIORITY_3):
- 1 = ‘High’
- 2 = ‘Medium’
- 3 = ‘Low’
- NULL (most common … 98.29%)
treat_summ_status_c
One of (ZC_TREAT_SUMM_STATUS):
- 1 = ‘Has Treatment Summary’
- 2 = ‘Treatment Summary Not Needed’
- NULL (Most common … 99.98%)

### Flowsheets (accm_flowsheet, accm_flowsheet_increment)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| inpatient_data_id | ??? |
| recorded_time | Time observation was made. (Note: actual observation may have been entered into EMR at a later time.  Entry time is available in EPIC but not projected.) |
| meas_value | Value of observation for concept type defined by the meas_id. |
| meas_comment | Comments associated with observation. |
| meas_id | Identifier for measurement type, links to the d_flowsheet table. |
| meas_row_type_c |  |
| ZC_ROW_TYP |  |
| meas_val_type_c |  |
| ZC_VAL_TYPE |  |
| meas_template_id | Template that meas_id was instantiated as part of, if any. |
| meas_fs_id | ??? |
| meas_line |  |
| meas_occurance |  |
| rw_meas_id |  |
| ip_lda_id |  |
| ro_row_type_c |  |
| rw_val_type_c | ` |
| meas_taken_user_id | User making observation. |

### Flowsheet Occurance [sic] Names (flowsheet_rows_name)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| inpatient_data_id |  |
| rw_row_name | Occurance row name |
| meas_occurance | Occurance number (unique to `pat_enc_csn_id`) |
| rw_meas_id | ? |
| ip_lda_id | LDA ID associated with occurance.  May be NULL |
| ipds_template_id | ? |
| DRC | pat_enc_csn_id, meas_occurance are UNIQUE meas_occurance cannot be NULL. |

### Geocode Info, Patient (accm_geocode_patient)

| Data Element | Notes |
| --- | --- |
| osler_id |  |
| postal_code | USPS Zip Code (5 digits) |
| latitude_char |  |
| longitude_char |  |
| zip_plus4_x | Last 4 digits of Zip+4 |
| census_tract_x | FIPS representation of census geographic region.  Depending on ??? may be either 5,  12, or 15 characters. |
| Formats | - 5 digits = state + county (either 00000 or 25000) - 12 digits = ??? - 15 digits = State+County+Tract+Block (May also be ‘*Unknown’) |
| Encoding |  |

| Digits | Meaning |
| --- | --- |
| 1-2 | State code (eg MD = 24) |
| 3-5 | County code (eg Baltimore City = 510) |
| 6-11 | Tract code (zero padded on left/right, decimal point dropped – eg tract 11.2 encoded as 001120) |
| 12-15 | Block code |

Notes:
- Unclear why some missing/incomplete addresses are mapped to ‘00000’ vs ‘*Unknown’
- Patient with postal_code ‘MA 05’ mapped to ‘25000’.  Is this a UK postal code?
Per Rob Oberteuffer (email 10/20/2021):
“The EDW AddressDim table is updated on a bi-weekly basis using Alteryx which incorporates both a TomTom GIS database and a USPS Coding Accuracy Support System (CASS) database for address validation and correction”
References
State codes: www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696
County codes: www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013697
https://www.nass.usda.gov/Data_and_Statistics/County_Data_Files/Frequently_Asked_Questions/county_list.txt

### Geocode Info, Encounter (accm_geocode_visit)

| Data Element | Notes |
| --- | --- |
| osler_id |  |
| encounter_date |  |
| pat_enc_csn_id |  |
| postal_code |  |
| latitude_char |  |
| longitude_char |  |
| zip_plus4_x |  |
| census_tract_x |  |

### Labor and Delivery  (Not projected yet)

Retain linkage from baby to mother – based on V_OB_DEL_RECORDS

| Data Element | Notes |
| --- | --- |
|  | Cohort ID Baby ID Baby CSN Birth encounter link Mom ID Mom CSN Birth encounter link |
| GA | Gestational Age, birth in weeks and days. Ex. '39w 3d'. Delivery date/time |

### Provider (Needs to be updated)

Data Field
Notes
Provider ID
Provider First Name
Provider Last Name
NPI
Specialty

### Lab Results (accm_labs)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| order_proc_id | Order procedure ID (unique to group of labs, links together multiple rows in this table generated from same order). |
| pat_enc_csn_id | Encounter identifier, links to ‘accm_inpatient’ table |
| proc_id | Unique ID of the procedure.  Links to description in ‘PMAP_COMMONS.DBO.CLARITY_EAP’. For reference, some common lab proc_ids include: - 678 = ‘BASIC METABOLIC PANEL’ - 682 = ‘COMPREHENSIVE METABOLIC PANEL’ - 800 = ‘BLOOD GASES, ARTERIAL’ - 7564 = ‘BACTERIAL/YEAST CULTURE, BLOOD’ - 90001 = ‘CBC + AUTO DIFF’ Note that add-ons have their own proc_id (105477). |
| proc_cat_id | Unique ID for procedure category |
| sensitive_yn | ‘Y’ if laboratory test considered sensitive. |
| order_type | One of ‘Lab’, ‘Blood Blank Products’, ‘Microbiology’, ‘Pathology and Cytology’, or ‘Point of Care Testing’ |
| lab_group | On of ‘lab’, ‘microbiology’, ‘pathology’, ‘point of care’ |
| resulting_lab | Lab producing result |
| order_time | Date/time order placed |
| result_time | Date/time result available in EMR |
| authorizing_prov_id |  |
| referring_prov_id |  |
| specimen_taken_time | Date/time specimen taken from patient |
| specimen_recv_time | Date/time specimen received in lab (?) |
| specimen_type | One of ‘Blood’, ‘Urine’, ‘Other’, ‘CSF’, …  May be NULL |
| specimen_source | One of ‘Blood’, ‘Urine’, ‘Other’, ‘CSF’, …  May be NULL |
| order_results_line | Line number of result component within each ordered procedure (order_proc_id) |
| component_id | Identifies laboratory type test/culture.  Links to PMAP_Commons ‘d_component’ table. |
| result_flag | One of ‘High’, ‘Low’, ‘Low Panic’, ‘High Panic’, ‘Abnormal’, ‘Low Off-Scale’, ‘Sig Change Down’, ‘High Off-Scale’, or ‘(NONE)’.  May be NULL. |
| order_status | One of ‘Completed’ or ‘Sent’.  May be NULL. |
| result_status | One of - ‘Preliminary’ - ‘Final’ - ‘Corrected’ - ‘Incomplete’ May be NULL. |
| lab_status | One of: - ‘In process’ - ‘Preliminary Result’ - ‘Final Result’ - ‘Edited’ - ‘Edited Result – FINAL’ Note: the meaning of labs with lab_status ‘Preliminary result’ is unclear, since all extracted labs have result_status  ‘Final’ or ‘Corrected’. Use with caution. |
| ord_value | Value of lab result. |
| ord_num_value | Numeric value of lab result, if applicable |
| reference_low | Low end of normal range |
| reference_high | High end of normal range |
| reference_unit | Units of ‘reference_low’ and ‘reference_high’ |
| result_sub_idn |  |
| res_comp_singleline | Single-line result value |
| res_comp_multiline | Multi-line result value (for cultures) |
| result_in_range_yn |  |
| lrr_based_organ_id |  |
| data_type |  |
| loinc_code |  |

### LDA (accm_lda_data)

Data Field
Notes
osler_id
Patient identifier, links to ‘accm_patient’ table
ip_lda_id
pat_enc_csn_id
removal_instant
placement_instant
description
properties_display
site
lda_group_meas_id
lda_group_version
fsd_id
enc_contact_date
enc_type_c

### Microbiology

Microbiology (cultures, etc) results are contained within the accm_labs table.

### MIC Values (accm_micro_sensitivities)

Data Field
Notes
osler_id
Patient identifier, links to ‘accm_patient’ table
order_proc_id
Order ID (links to culture order in accm_labs).
line
specimen_taken_time
specimen_recv_time
organism_name
antibiotic
susceptibility
One of:
- Susceptible
- Resistant
- Epidemiological cutoff value Non-Wild Type63
- Epidemiological cutoff value Wild Type876
- Extended Spectrum Beta-Lactamase95
- Inducible Beta-lactamase1482
- Intermediate98455
- No CLSI Interpretation3127
- No Interpretation204
- Non Susceptible13
- Not Defined18
- Resistant in vivo10320
- Susceptible Dose Dependent1889
- Very Susceptible
(May be NULL)
sensitivity_value
sensitivity_units
sens_organism_isd
sens_obs_inst_tm
timestamp
sens_obs_anl_tm
timestamp
result_detail
ordered_lab
component_name
specimen_source
specimen_type
order_type
result_status
result_flag
lab_status
antibiotic_loinc_code
method_loinc_code
sens_method_name
proc_id
pat_enc_csn_id
order_type_c
specimen_source_c
specimen_type_c
organism_id
antibiotic_c
suscept_c
lab_status_c
sens_status_c
sens_method_id
antibio_lnc_id
method_lnc_id
component_id
result_flag_c

### Medical History (medical_hx_summary)

Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
medical_hx_date
med_hx_start_dt
med_hx_end_dt
dx_id
dx_name
dx_group
parent_dx_name
icd10_code
icd9_code
annotation

### Medication Orders (accm_med_orders)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| start_date | Order start date |
| end_date | Order end_date |
| med_display_name | Medication name.  Related to, but rarely identical to, the medication_name and generic_name fields from the MAR entries with a matching order_med_id. |
| order_mode | One of: - ‘Inpatient’ – inpatient medication order - ‘Outpatient’ – outpatient prescription |
| dose | Numeric value of dose |
| unit | Units of ‘dose’ |
| sig | Free text sig for prescription (eg “Take thrice per fortnight as directed”).  Only used when ‘order_mode’ = ‘Outpatient’.  May be NULL. |
| frequency | Frequency +/- PRN.  For example: - ‘4 times daily’ - ‘4 times daily after meals and nightly’ - ‘4 times daily after meals and nightly PRN - et cetera May be NULL. |
| therapeutic_class |  |
| pharmaceutical_class |  |
| pharmaceutical_subclass |  |
| ordering_dttm | Date/time order placed. |
| discon_time | Date/time order discontinued |
| current_med_yn | ‘Y’ if medication current, ‘N’ otherwise. |
| discont_med_yn | ‘Y’ if medication discontinued, ‘N’ otherwise. |
| order_med_id | Medication order identifier, links from MAR table.  UNIQUE. |
| ord_status | One of: - ‘Completed’ (Inpatient only) - ‘Discontinued’ (Inpatient only) - ‘Dispensed’ (Inpatient only) - ‘Verified’ (primarily Inpatient) - ‘Suspend’ (Outpatient only) - ‘Sent’ (primarily Outpatient) - NULL |
| rxnorm_codes |  |
| NFC |  |

### Medication Administration (accm_med_admin)

Medications administered during the admission
Data Field
Notes
osler_id
Patient identifier, links to accm_patient table
pat_enc_csn_id
Encounter identifier
order_med_id
Medication order identifier, links to ‘med_orders’
line
Sequence of administration within ‘order_med_id’
hosp_admsn_time
NFCWTIH
hosp_disch_time
NFCWTIH
medication_name
Detailed medication name
generic_name
Generic medication name
medication_id
Medication ID
thera_classname
Therapeutic classname
pharm_classname
Pharmacologic classname
pharm_subclassname
Pharmacologic subclassname
taken_time
Time action taken
ordering_date
Date (not time) medication ordered
order_end_time
scheduled_time
Scheduled time on MAR
saved_time
?
mar_time_source
mar_action / mar_action_c
Action taken, includes:
- ‘Given (1)’: medication given
- ‘Rate Verify’ (14): rate of continuous med verified, no change
- ‘New Bag’ (6): new medication bag ??? admin
- ‘Handoff’ (111): rate verified during RN handoff, no change
- ‘Missed’ (2): admin due, but not given.  See ‘reason’.
- ‘Rate/Dose Verify’ (121)
- ‘Rate Change’ (9)
- ‘Stopped’ (
- ‘Due’: medication due, but not yet given.  Typically in future.
- ‘MAR Hold’/’MAR Unhold’: meds held/unheld around OR.
- ‘Refused’: admin refused.  See ‘reason’
Note be NULL.  Total of 37 distinct values
user_nm
User name.
- Maps to dbo_commons.dbo.clarity_ser prov_name
mar_doc_user_nm
Doc user name
- maps to dbo_commons.dbo.clarity_ser prov_name
route
Route of medication administration.  Includes:
- ‘Intravenous’
- ‘Oral’, ‘G-Tube’, ..
- ‘Inhalation’, ‘Nebulization’, …
- etc
Total of 125 values.
sig
Numeric dose value of the medication administration (units in ‘dose_unit’).  For example, a 500 ml bolus would have a ‘sig’ of ‘500’ and a ‘dose_unit’ of ‘ml’.
site
Site of medication administration.  Most commonly ‘NONE’.
dose_unit
Unit of measurement for ‘sig’.  Includes:
- ‘mcg’, ‘mg’, ‘mL’, ‘Units’, …
- ‘mcg/hr’, ‘mg’/hr’, ‘mL/hr’, ‘Units/hr’, …
- ‘mcg/kg/hr’, ‘mg/kg/hr’, …
Total of 129 values.
infustion_rate
Numeric rate value for infusions (units in ‘mar_inf_rate_unit’).
mar_inf_rate_unit
Unit of measurement for ‘infusion_rate’.  One of:
- ‘mL/hr’
- NULL
mar_duration
Numeric value of duration of medication administration (units in ‘duration_unit’)
duration_unit
Unit of measurement for ‘mar_duration’.  One of:
- ‘Minutes’
- ‘Hours’
- ‘Days’
Only NULL if ‘mar_duration’ is also NULL
frequency
Frequency of medication administration.  Includes:
- ‘Continuous’
- ‘Daily’, ‘BID’, ‘TID’, ‘QID’, …
- ‘Q24H’, ‘Q12H’, ‘Q8H’, ‘Q6H’, …
- ‘Daily PRN’, ‘Q6H PRN’, …
Total of 152 values.
freq_period
NFC
number_of_times
NFC
time_unit
NFC
now_yn
‘Y’ if frequency of medication order this administration is part of included ‘now’ as a scheduled time.
reason
Reason category associated with ‘mar_action’.  Includes:
- ‘Unreviewed transfer orders’
- ‘Other’
- ‘Order parameters not met’,
- ‘Contraindicated’
- ‘Medication order discontinued’
- ‘Patient NPO’
- ‘Medication not available’
- etc
Total of 13 values.  May be NULL.
mar_imm_link_id
Unique ID of immunization associated w/administration
mar_admin_dep
Department where medication administered
mar_ord_dat
EPIC numeric date thing.
mar_billing_prov
Billing provider
pat_supplied_yn
‘Y’ if medication supplied by patient, ‘N’ otherwise.
May be NULL.
sensitive_yn
‘Y’ if medication considered sensitive, ‘N’ otherwise.
Associated with opioid agonists/antagonists (naloxone and buprenorphine).
mar_action_c
MAR action code for this administration (ZC_EDIT_MAR_RSLT).  One-to-one equivalent with ‘mar_action’.

### Social History (dbo.accm_social_hx_changes)

### Blood Administration (dbo.accm_blood_admin)

Data Field
Notes
osler_id
pat_enc_csn_id
CSN
instance_order_id
proc_id
proc_code
proc_name
blood_unit_num
blood_product_code
lab_issue_time
(dt)
blood_start_instant
blood_end_instant
result_time
lab_blood_status
lab_blood_type
Blood ABO/Rh type, one of:
- ‘O Pos’ / ‘OP’
- ‘A Pos’ / ‘AP’
- ‘B Pos’ / ‘BP
- ‘O Neg’ / ‘ON’
- ‘A Neg’ / ‘AN’
- ‘B Neg’ / ‘BN’
- ‘AB Pos’ / ‘ABP’
- ‘AB Neg’ / ‘ABN’
- ‘A’ / ‘O’ / ‘B’ – WTF
- ‘PENDING’
May be NULL
lab_product_type
Blood product type, one of:
- ‘Red Blood Cells’
- ‘FFP’
- ‘Platelet’
- ‘Cryoprecipitate’
.. (73 possible values)
May be NULL
result_sub_idn
quantity
authorizing_prov_id
order_status
One of:
- ‘Completed’
- ‘Canceled’
- ‘Discontinued’
- ‘Sent’
May be NULL
row_type
One of:
- ‘LAB’
- ‘TRANSFUSE’
enc_type
One of:
- ‘Hospital Encounter’
- ‘Provider Procedure’
- Office Visit’
- ‘Visit Encounter’
- ‘Procedure visit’
- ‘Infusion’
… (29 possible values)
May not be NULL
enc_department_id
primary_loc_id

### Allergy (Not projected yet)

Data Field
Notes
Enterprise ID
Allergy Name
Reaction
Date Noted
Not a date/time field – free text
Severity
Status
Active, Inactive
Certainty
Source

### Patient MRNs (dbo.accm_patient_mrn)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| mrndomain | One of: / - ‘EMRN’ / - ‘JHHMRN’ / - ‘BMCMRN’ / - ‘SHMRN’ / - ‘SMHMRN’ |
| mrn | Medical record number, in given domain |
| mrnstatus | One of: / - ‘Primary’ / - ‘Alias’ – MRN used in past that has been merged with current primary ‘MRN’. |

### Imaging Procedures (dbo.accm_radiology)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| order_proc_id | Order identifier. UNIQUE |
| proc_code | Imaging code |
| proc_name | Imaging description (1:1 with proc_code) |
| proc_category | Imaging category. One of: - IMG DIAGNOSTIC IMAGING ORDERABLES (38.4%) - IMG CT ORDERABLES188944922.701846 - IMG MRI ORDERABLES7843349.423821 - IMG US ORDERABLES6732258.088840 - IMG MAMMOGRAPHY ORDERABLES5404566.493612 - NURSING ACTIVITY ORDERABLES - ONCE OR AT INTER... (3.7%) - IMG IR ORDERABLES2413272.899559 - IMG FLUOROSCOPY ORDERABLES2130532.559845 - IMG NM ORDERABLES1261261.515412 - IMG EXTERNAL IMAGES1138771.368239 - IMG DXA ORDERABLES766340.920762 - IMG PET ORDERABLES632580.760049 - OB GYNE ORDERABLES613310.736896 - HEALTH MAINTENANCE186780.224417 - IMG ENTERPRISE IMAGING56130.067441 - IMG PROTOCOL ORDERABLES34930.041969 - IMG MSK ORDERABLES410.000493 |
| order_status | One of - ‘Completed’ - ‘Canceled’ - ‘Sent’ - Null |
| pat_enc_csn_id | Encounter identifier |
| resulting_lab | Service completing image - ‘JHH RADIOLOGY’ (57.7%) - ‘BMC RADIOLOGY’ (11.7%) - ‘SMH RADIOLOGY’ - Null … |
| order_time | Never NULL. |
| result_time | Rarely NULL (0.0012%) |
| review_time |  |
| result_status | One of: - ‘Final result’ - ‘Edited Result – FINAL’ |
| accession |  |
| authrzing_prov_id |  |
| authorizing_provider |  |
| specimen_taken_date | May be NULL |
| study_instance | Long sequence of numbers, must be link into PACS or something. |
| images_avail_yn | ‘Y’, ‘N’, Null |
| image_avail_dttm |  |
| image_location | Once of: - JHHVITAL279062033.529471 1138919516.691264 2JHHMRN Imaging VNA129805315.596187 3EMRN Imaging VNA101843412.236547 4HCGHDRWEBPACS3705124.451725 5BMCMRN Imaging VNA3049953.664534 6SHMRN Imaging VNA2427762.916969 7SMHGEWEBPACS2425262.913965 8BMCVITAL1993982.395779 9Suburban Hospital GE PACS1732722.081874 10SMHMRN Imaging VNA1652681.985705 11Carestream VueMotion Image Link999741.201194 |
| department_name |  |
| specimen_type | Anatomic location in image (rarely used) - ‘None’ (99.996%) - ‘Pelvic’, ‘Breast’, ‘Bone’, … |
| specimen_src | Always ‘None’ |

### Other Ordered Procedures (Not Projected Yet)

| Data Element | Notes |
| --- | --- |
|  | Enterprise ID Encounter ID Procedure Name ECHO, Diet orders, etc. The PMAP team will provide a distinct list of procedures for the study team to validate for inclusion. Procedure date/time Order date/time |

### Hospital Billing Diagnoses (accm_hosp_billing_dx)

Note: Multiple hsp_account_ids may map to same pat_enc_csn_id.  Hence, joining by ‘pat_enc_csn_id’ may result in multiple (possibly different) diagnoses having the same ‘line’.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| hsp_acount_id |  |
| line | Approximate order of diagnoses in importance during encounter.  Primary diagnoses has line = 1. |
| pat_enc_csn_id | Encounter |
| adm_date_time |  |
| dx_id | EPIC Diagnoses ID, links to ‘CLARITY_EDG’ table |
| icd10_code |  |
| icd9_code |  |
| current_icd10_list | List of ICD-10 codes. - Always non-null if ‘icd10_code’ is non-null. - If ‘icd9_code’ is null, list only contains ‘icd10_code’ - if ‘icd9_code’ is non-null, list starts with ‘icd10_code’, may contain additional codes. |
| current_icd9_list |  |
| dx_affects_drg_yn | Flag indicating if diagnosis affects DRG calculation - ‘Y’ 1.2% - ‘N’ 10.4% - Null 88.3% |
| final_dx_soi_c | Category value for final diagnosis severity of illness (SOI) (ZC_SOI_ROM) - Null 75% |
| final_dx_rom_c | Category value for final diagnosis risk of mortality (ROM) (ZC_SOI_ROM) - Null 75% |
| final_dx_excld_yn | Final diagnosis excluded from clinical reporting. - ‘Y’ 0.8% - ‘N’ 0.00005% - Null 99.1% |
| fnl_dx_afct_soi_yn | Flag indicating if diagnosis affects SOI - ‘Y’ 5.2% - ‘N’ 19.1% - Null 75.6% |
| fnl_dx_afct_rom_yn | Flag indicating if diagnosis affects ROM - ‘Y’ 4.9% - ‘N’ 19.3% - Null 75.8% |
| final_dx_poa_c | Diagnoses present on admission. (ZC_DX_POA) - ‘1’ = Y/Yes (16.7%) - ‘2’ = N/No (2.1%) - ‘3’ = U/Unknown (0.0014%) - ‘4’ = W/Clinically undetermined (0.0085%) - ‘5’ = E/Exempt from POA reporting (6.5%) - Null (74.7%) |
| dx_comorbidity_c | Flag indicating if diagnosis represents a comorbidity - ‘Y’ (2.2%) - ‘N’ (9.5%) - Null (88.3%) |
| dx_hac_yn | Flag if diagnosis contributed to a hospital acquired condition. - ‘Y’ (0.003%) - ‘N’ (0.00003%) - Null (99.996%) |
| dx_type_c | “Type of diagnosis: action or secondary” - Always NULL |
| dx_start_dt | Start date of a diagnosis - Always NULL |
| dx_end_dt | End date of a diagnosis - Always NULL |
| dx_problem_id | Per [1] “Specifies networked problem ID for the related diagnosis” - Always NULL |
| dx_chronic_flag_yn | Flag if diagnosis represents a chronic condition Always NULL |
| dx_supp_atc_code_c | Per [1] “ATC code for diagnosis (See Wikipedia ATC_code_V04)” - Always NULL |
| dx_hsp_prob_flag_yn | Flag if diagnosis is a hospital problem diagnosis. - Always NULL |
| dx_overridden_dx_id | Per [1] “this item stores the diagnosis that was on the problem list at the time that it was associated. This overridden diagnosis is only populated if the diagnosis is overwridden” - Always NULL |
| dx_disproven_yn | Flag if diagnosis has been clinically disproven. - Always NULL |
| dk_cancer_status_c | () - Always NULL |
| dx_documenting_user_id | User ID who documented diagnosis. - Always NULL |
| fnl_dx_qualifer_c | Per [1] “Diagnosis qualifier for UK ECDS code”. Always NULL |
| term_dx_id | Per [1] “Diagnosis term record that the billing diagnosis is mapped from. May be null for old hospital accounts” - Always NULL Percentages computed 5/26/2022. |
| References | [1] JH-Crown derived_hosp_billing_dx documentation (accessed 5/26/2022) |

### Hospital Billing Procedures (accm_hosp_billing_px)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| pat_enc_csn_id |  |
| hsp_account_id |  |
| proc_name |  |
| code_set_c | Takes values Null (17970k), 1 (235k), or 2 (872k) - Null => codes like ‘99211’ (~8500 distinct codes) - 1 => codes like ’54.59’ (~2150 distinct codes) - 2 => codes like 0H9HXZZ’ (~16870 distinct codes) |
| ZC_HCD_CODE_SET | - 1 = ‘ICD-9-CM’ - 2 = ‘ICD-10-PCS’ - 3 = ‘OPCS-4’ - 4 = ‘A&E Inv/Tre’ |
| code |  |
| proc_date |  |
| proc_perf_prov_id |  |
| px_cpt_modifiers |  |
| px_cpt_quantity |  |
| icd_px_id |  |
| source_key |  |
| line |  |
| coding_info_cpt_line |  |
| exclude_yn |  |
| affects_soi_yn |  |
| affects_rom_yn |  |
| event_number |  |

### Provider Procedures (accm_profee_billing_px)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| pat_enc_csn_id |  |
| account_id |  |
| proc_name |  |
| code_set_c | Always null |
| code | 8471 distinct codes |
| proc_date |  |
| proc_peerf_prov_id |  |
| px_cpt_modifiers |  |
| px_cpt_quantity |  |
| proc_id |  |
| tx_id |  |
| serevice_area_id |  |
| loc_id |  |
| pos_id |  |
| department_id |  |
| void_date |  |
| panel_id |  |
| enc_type_c |  |
| appt_status_c |  |

### (accm_ip_io_daily_totals)

### Encounter Coverage (accm_encounter_coverage)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| pat_enc_csn_id |  |
| Contact_date |  |
| Payor | AETNA, etc |
| Fin_class | Aetna, etc |
| Guarantor_pat_rel | Parent, etc |
| Guarantor_zip |  |
| Account_id |  |
| Account_active_yn |  |
| Acct_adr_lnk_yn |  |
| Coverage_id |  |
| Effective_dept_id |  |
| Guarantor_state_c |  |
| Guarantor_country_c |  |
| Guarantor_county_c |  |

### Cohort Pivot (accm_cohort_pivot)

For each patient in ACCM PMAP cohort, label inclusion criteria.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| pat_id |  |
| anestrecord |  |
| icu |  |
| painclinic |  |
| painservice |  |
| preop |  |
| dart |  |

## Subprojections Primary Data Tables

For ACCM PMAP subprojections, attempts are made to preserve table schemas.
Limited-data sets (LDS) and fully de-identified data sets require modifications.
Optimizations

### Subcohort Flowsheets (flowsheet)

All flowsheet rows where ‘rw_meas_id’ is NULL (see ‘flowsheet_rw’ for rows where ‘rw_meas_id’ is non-NULL)

| Data Element | Notes |
| --- | --- |
| study_id | Patient identifier, links to ‘patient’ table |
| enc_id | Encounter identifier |
| recorded_time | Time observation was made. (Note: actual observation may have been entered into EMR at a later time.  Entry time is available in EPIC but not projected.) |
| meas_value | Value of observation for concept type defined by the meas_id. |
| meas_comment | Comments associated with observation. |
| meas_id | Identifier for measurement type, links to the ‘d_flo_measures’ table. |
| meas_template_id | Template that meas_id was instantiated as part of, if any.  Links to the ‘d_flo_measures’ table. |
| meas_taken_user_id | User making observation. |

### Flowsheets with rw_meas_id (raw.flowsheet_rw)

All flowsheet rows where ‘rw_meas_id’ is not NULL.

| Data Element | Notes |
| --- | --- |
| study_id | Patient identifier, links to ‘patient’ table |
| enc_id | Encounter identifier |
| recorded_time | Time observation was made. (Note: actual observation may have been entered into EMR at a later time.  Entry time is available in EPIC but not projected.) |
| meas_value | Value of observation for concept type defined by the meas_id. |
| meas_comment | Comments associated with observation. |
| meas_id | Identifier for measurement type, links to the ‘d_flo_measures’ table. |
| meas_template_id | Template that meas_id was instantiated as part of, if any.  Links to the ‘d_flo_measures’ table. |
| meas_occurance | Occurance [sic] identifier to link related rows together |
| rw_meas_id | Identifier for row measure type, links to the ‘d_flo_measures’ table.  Will not be NULL in this table, by definition. |
| ip_lda_id | LDA identifier.  Links related rows together.  May be NULL. |
| meas_taken_user_id | User making observation. |

## Physiologic Time Series Data (PTSD) Metadata

### PTSD Devices/Signals

ACCM PMAP physiologic time series data (or PTSD) represent signals (eg heart rate, end-tidal CO2) measured by different medical devices (eg GE physiologic monitor, Drager ventilator) and sampled/recorded by an archival system (eg SickBay or physiocloud).  Sampling can either be of numeric values (eg the heart rate is 96), or of waveforms (eg the EKG signal voltages).  A single physiologic signal, such as an EKG lead, can generate multiple numeric values, such heart rate and ST segment elevation, but usually only a single waveform.
ACCM PMAP encodes the medical device and archival system in the ‘device’ column.  All signals captured by physiocloud have device ‘TSDB’.  Signals captured by SickBay have separate devices according to the actual medical device and resolution:
- GEVITAL: numeric signals from the GE physiologic monitor, recorded at 2 sec intervals
- MEDIBUSVITAL: numeric signals from the Drager ventilator, recorded at 2 second intervals.
- INVOSVITAL: numeric signals from the NIRS monitor.
- GEWAVE: waveform signals from the GE physiologic monitor.
For transparency, ACCM PMAP uses the signal names provided by archival systems.
Device/Signals of interest

| Device | Signal | Description |
| --- | --- | --- |
| TSDB | SpO2_7874 | Blood oxygen saturation, as measured by pulse oximeter |
|  | HR_SpO2_7876 | Heart rate, as measured by pulse oximeter. |
|  | HR | Heart rate, as measured by EKG chest lead |
|  | RR_2344 | Respiratory rate, as measured by impedance chest lead |
|  | NIBP_X | Non-invasive blood pressure (where X = ‘S’ystolic/’D’iastolic/’M’ean) |
|  | ECG_X_ST | ST segment difference (where X = ‘I’, ‘II’, ‘III’, ‘V1’, …) |
|  | ABP_S_2320 | Systolic blood pressure, as measured by arterial catheter |
|  | ABP_D_2319 | Systolic blood pressure, as measured by arterial catheter |
|  | ABP_M_2318 | Systolic blood pressure, as measured by arterial catheter |
|  | HR_Art_2930 | Heart rate, as measured by arterial catheter |
|  | EtCO2_2905 | End-tidal CO2 |
|  | asRR_3495 | Respiratory rate, as measured by end-tidal CO2 waveform. |
|  | Temp | Patient temperature (probe 1 – typically core temp) |
|  | Temp2 | Patient temperature (probe 2 – typically peripheral, eg toe) |

### PTSD Directory structure/file naming convention for extracts

PTSD files for extracts are typically organized as follows:
Within the root PTSD directory there will be a subdirectory for each major class of PTSD devices:
‘vitals-tsdb’ for all TSDB files,
‘vitals-sb’ for all Sickbay files.
Within the vitals-tsdb/vitals-sb  directories, files will be organized into subdirectories by the last three digits of the pat_enc_csn_id/pat_enc_csn_sid.
File base name is the `filename` field in the `ptsd_record` table.
File suffix depends on the `fmt` field in the `ptsd_record` table.

### PTSD Encounter (core.ptsd_encounter)

Row indicates availability of device data for an encounter.  If row exists, presence of data indicated by `has_data`.  If row does not exist, data availability has not been ascertained.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| emrn | Enterprise MRN used matching PMAP patient to device patient. Used for Sickbay devices. |
| pat_enc_csn_id | Encounter identifier |
| device | Device/archival system (see Devices/Signals above) |
| dev_pid | Recording device specific patient identifier. NULL for TSDB. |
| dev_status |  |
| cur_end_time |  |
| data_avail | ‘1’ if data for patient encounter is available on device |
| data_local | ‘1’ if data for patient encounter has been downloaded locally |
| data_stats |  |
| dt | (Administrative time that entry/file were initially sampled from capturing device) |

### PTSD File record (ptsd_record)

Contains one row per PTSD file.

| Data Element | Notes |
| --- | --- |
| record_id | Record ID, unique to this row.  Links to entries in `ptsd_signal`. UNIQUE. |
| emrn | Enterprise MRN used matching PMAP patient to device patient. Used for Sickbay devices. |
| pat_enc_csn_id | Encounter identifier |
| device | Device/archival system (see Devices/Signals above) |
| dev_pid | Recording device specific patient identifier. - Sickbay patient ID for sickbay. - NULL for TSDB. |
| record_date | Date of recording (current implementation stores data in chunks that do not cross midnight boundary) |
| filename | Base name of file. - suffix depends on file format |
| fmt | File format. - ‘feather’ = Apache Feather format (suffix ‘.feather’) - ‘zarr’ – Zarr file format (suffix ‘.zip’) |
| start_time | Time of first data sample included in file |
| end_time | Time of last data sample included in file |
| n_sample | Number of samples in this file |
| n_signal | Number of signals in this file. |
| rate | Sample rate (Hz) - 0.016 for TSDB - 0.5 for Sickbay numerics - 60-240 for Sickbay waveforms |
| dt | (Administrative time that entry/file were initially sampled from capturing device) |

### PTSD Processed record (ptsd_processed_record)

One row for each file of processed PTSD data.

| Data Element | Notes |
| --- | --- |
| prec_id | Processed record ID, unique to this row.  UNIQUE. |
| pat_enc_csn_id | Encounter identifier |
| device | Device/archival system (see Devices/Signals above) pre-processed PTS data sourced from. |
| algorithm | Algorithm name |
| record_date | Date of recording (current implementation stores data in chunks that do not cross midnight boundary) |
| seq | File sequence number (within date/rate) |
| filename | Base name of file.  Null if error during processing. - suffix depends on file format |
| fmt | File format. - ‘feather’ = Apache Feather format (suffix ‘.feather’) - ‘zarr’ – Zarr file format (suffix ‘.zip’) |
| struct | TBD |
| start_time | Time of first data sample in pre-processed PTS data. |
| end_time | Time of last data sample pre-processed PTS data. |
| n_sample | Number of samples in this file |
| n_signal | Number of signals in this file. |
| rate | Sample rate (Hz) of pre-processed PTS data. |
| status | Status of processing - ‘ok’ if processing successful - ‘except’ if exception occurred during processing |
| dt | (Administrative time that entry/file were initially sampled from capturing device) Notes: Filename follows format: CSN-YEAR-MO-DAY-RATE-SEQ-alg-ALGNAME where ALGNAME is ‘algorithm’ column Some fields describe characteristics of the pre-processed data (device, start_time, end_time, rate). If processing unsuccessful (status = ‘except’) then filename will be null. |

### PTSD Signal (ptsd_signal)

| Data Element | Notes |
| --- | --- |
| record_id | Record ID of file.  Links to `ptsd_record` table. |
| emrn | Enterprise MRN used matching PMAP patient to device patient. Used for Sickbay devices. |
| pat_enc_csn_id | Encounter identifier |
| device | Device/archival system (see Devices/Signals above) |
| dev_pid | Recording device specific patient identifier. / NULL for TSDB. |
| signal | Signal name |
| record_date | Date of recording (current implementation stores data in chunks that do not cross midnight boundary) |
| start_time | Time of first data sample included in file |
| end_time | Time of last data sample included in file |
| n_sample | Number of samples in this file |
| rate | Sample rate (Hz) |
| dt | (Administrative time that entry/file were initially sampled from capturing device) |

### PTSD Signal summary (ptsd_sum)

| Data Element | Notes |
| --- | --- |
| pat_enc_csn_id | Encounter identifier |
| device | Device/archival system (see Devices/Signals above) |
| signal | Signal name (see Devices/Signals above). |
| start_time | Time of first data sample included in interval |
| end_time | Time of last data sample included in interval |
| n_sample | Number of samples in this interval |
| mean_val | Mean signal value during interval |
| std_var | Standard deviation of signal value during interval |
| skewness | Skewness of signal value during interval |
| kurtosis | Kurtosis of signal value during interval |
| slope | Slope of linear regression during interval |
| min_val | Minimum signal value during interval |
| max_val | Maximum signal value during interval |
| p03 | 3rd centile signal value during interval |
| p10 | 10th centile signal value during interval |
| p25 | 25th centile signal value during interval |
| p50 | 50th centile signal value during interval |
| p75 | 75th centile signal value during interval |
| p90 | 90th centile signal value during interval |
| p97 | 97th centile signal value during interval |
| dt | (Administrative time that statistics were computed from capturing device) |

## PMAP Commons Dictionaries

### AVOID - Clarity Departments (dbo.CLARITY_DEP)

AVOID using this table: department_id/department_name rows can be repeated.
Prefer `core.d_department_id` instead, which fixes this issue

| Data Element | Notes |
| --- | --- |
| department_id | Department ID |
| department_name | Department name |
| dept_abbreviation | Abbreviated dept name |
| specialty | ? |
| rev_loc_id | ? |
| dep_group | ? |
| gl_prefix | ? |
| rpt_grp_one |  |
| rpt_grp_two |  |
| rpt_grp_three |  |
| rpt_grp_four |  |
| rpt_group_five |  |
| rpt_group_siz |  |
| rpt_group_seven |  |
| rpt_group_eight |  |
| rpt_group_nine |  |
| rpt_group_ten | Location … |
| adt_parent_id |  |
| serv_area_id |  |
| speciality_dep_c |  |
| licensed_beds |  |
| master_pool_id |  |
| master_pool_name |  |
| covering_pool_id |  |
| covering_pool_name | … |

### Clarity Locations (pmap_commons.dbo.CLARITY_LOC)

| Data Element | Notes |
| --- | --- |
| loc_id | Location ID (UNIQUE?) |
| loc_name | Location name |
| location_group |  |
| default_dept_id | ? null, at least for OR loc_ids … |
| hosp_parent_loc_id | Parent loc_id … |

### Clarity Procedures (pmap_commons.dbo.CLARITY_EAP)

| Data Element | Notes |
| --- | --- |
| proc_id | Procedure ID (UNIQUE?) |
| proc_name | Procedure name |
| proc_code | Procedure Code - LABNNN - … |
| short_name |  |
| order_display_name | … |
| RPT_GRP_TWO | Dollar amounts – is this the cost? … |
| RPT_GRP_ELEVEN_C | Orderable as STAT (‘ZC_EAP_RPT_GRP_11’) - ‘1’ = orderable as STAT Null otherwise … |
| DFLT_SPEC_TYPE_C | Default specimen type (‘ZC_DFLT_SPEC_TYPE’) - 1004 = Blood |

### Clairty Providers (pmap.commons.dbo.CLARITY_SER)

| Data Element | Notes |
| --- | --- |
| prov_id | Provider ID |
| prov_name | Provider name (last name, first name) |
| prov_type | Provider ?speciality? type |
| … |  |
| is_resident |  |
| user_id |  |
| epic_prov_id | Same as provider ID (todo: confirm) |
| … |  |
| clinician_tile | E.g. MD (todo: list) |
| active_status |  |
| … |  |
| dea_number |  |
| sex | todo: list |

### Clarity Diagnoses (pmap_commons.dbo.CLARITY_EDG)

| Data Element | Notes |
| --- | --- |
| dx_id | Diagnoses ID |
| dx_name | Diagnoses name |
| dx_status | Always NULL |
| dx_group |  |
| ICD9_CODE | Always NULL |
| … |  |
| CURRENT_ICD9_LIST |  |
| CURRENT_ICD10_LIST |  |

### Flowsheet Measure IDs (pmap_commons.dbo.d_flo_measures)

Prefer this over core.d_flowsheet

| Data Element | Notes |
| --- | --- |
| flo_meas_id | Flowsheet measure ID (UNIQUE) |
| flo_meas_name | All CAPS version of the name |
| site_row_id | ??? |
| record_state_c | ??? |
| allow_comp_yn | ??? |
| disp_name | Friendly version of the name |
| abbr_p |  |
| row_typ_c |  |
| ZC_ROW_TYP |  |
| chg_trg_type_c |  |
| val_type_c |  |
| ZC_VAL_TYPE | - 8 = Custom List) 43% - 2 = String Type) 19% - None 16.6% - 1 = Numeric Type (16%) - 3 = Category Type (1%) - 9 = Date (1%) - 10 = Time (0.6%) … - 4 = Blood Pressure (0.3%) … … |

### Laboratory Component ID Dictionary (pmap_commons. dbo.d_component)

| Data Element | Notes |
| --- | --- |
| component_id | Unique ID for laboratory component |
| component_name | Name of laboratory component |
| component_abbr | Abbreviated name |
| component_external_name | External version of name |
| component_base_name | Base version of name … |
| component_common_name | Common version of name … |
| dflt_units | Default units |

### ZC Tables (pmap_commons.dbo.emr_dictionary)

| Data Element | Notes |
| --- | --- |
| table_name | ‘ZC***’ |
| id |  |
| name |  |
| title |  |
| abbr |  |
| internal_id |  |
| load_dttm |  |

## Dictionaries

### Culture Component ID Dictionary (core.d_culture_cid)

Subset of pmap_commons.dbo.d_component’s with either ‘culture’, ‘nat’, or ‘covid’ in the component_name, transitively extended by base_name (if since base_name and component_name are not 1:1, if any component_name associated with base_name qualifies, than all component_id’s associated with base_name are included regardless of whether their component_name qualifies).

| Data Element | Notes |
| --- | --- |
| component_id | Unique ID for laboratory component |
| component_name | Name of laboratory component |
| component_abbr | Abbreviated name |
| component_external_name | External version of name |
| component_base_name | Base version of name … |
| component_common_name | Common version of name … |

### Department Types (core.d_dept_type)

| Data Element | Notes |
| --- | --- |
| department_id | Department ID (links to d_department_id.department_id) |
| is_icu | ‘1’ if department is an ICU (‘0’ otherwise) |
| is_or | ‘1’ if department is an OR (‘0’ otherwise) |
| loc | Abbreviated department name.  Either ICU name (‘picu’, ‘bmc_sicu’, etc), ‘ed’, ‘floor’, ‘or’, ‘rads’, or ‘clinic’ |

### Department Names (core.d_department_id)

Note: prefer this table over ‘pmap_commons.dbo.clarity_dep’ which contains duplicate rows.

| Data Element | Notes |
| --- | --- |
| department_id | Department ID (UNIQUE) |
| department_name | Department name. |
| Speciality | Department specialty (may be NULL). |

### DEPRECATED - Diagnoses Dictionary (core.d_diagnoses)

Deprecated.  Prefer `pmap_commons.dbo.clarity_edg` instead, which should be more complete.

| Data Element | Notes |
| --- | --- |
| dx_id | EPIC Diagnoses ID |
| dx_name | Diagnoses name |
| dx_group |  |
| parent_dx_id |  |
| parent_dx_name |  |
| icd9_code |  |
| icd10_code | ICD-10 code that dx_id is part of (multiple dx_id codes may map to the same ICD-10 code) |

### DEPRECATED - Flowsheet Dictionary (core.d_flowsheet)

Deprecated.  Prefer `pmap_commons.dbo.d_flo_meas` instead, which should be more complete.

### Medication Dictionary (core.d_med)

| Data Element | Notes |
| --- | --- |
| medication_id | Medication ID (UNIQUE) |
| medication_name | Medication name (not always a commercial name). |
| generic_name | Generic name of medication.  May be NULL. |
| thera_classname | Therapeutic class of medication. |
| pharm_classname | Pharmacologic class of medication. |
| pharm_subclassname | Pharmacologic sub-class of medication. |

## Base Tables

ACCM PMAP Base Tables

### Flowsheets with meas_occurance [sic] (base.fs_rw)

Index on osler_id

## Concepts for Cohorts and Diagnoses Codes

### ICU Cohort (base.icu_cohort)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| jhh_picu | ‘1’ if patient has ADT entry for JHH PICU bed, ‘0’ otherwise. (Equivalent to having at least one PICU icustay) |
| jhh_nccu |  |
| jhh_cvsicu |  |
| jhh_sicu |  |
| bmc_burn_icu |  |
| bmc_nccu_ |  |
| bmc_sizue |  |
| hoco_icu |  |
| smh_icu |  |
| sh_icu | (Definition: base/adt/icu-cohort.sql) |

### Ventilated Cohort (core.vent_cohort)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| num_dur | Number of mechanical ventilation durations |
| tot_dur_hr | Total duration of mechanical ventilation |
| inp |  |
| anes |  |
| other_loc |  |

(Definition: core/vent_dur/vent-cohort.sql)

## Concepts for Diagnoses Codes

### Elixhauser Comorbidities (core.elixhauser_aqi_pivot)

AQI-Style Elixhauser comorbidities, computed from admission billing codes.  One row for each encounter.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient ID. Uniquely identifies patient. Study specific. |
| pat_enc_csn_id | Encounter ID. Uniquely identifies hospital admission/encounter. |
| CHF | ‘1’ if patient has comorbidity of congestive heart failure, ‘0’ otherwise |
| VALVE | … Valvular disease |
| PULMCIRC | … Pulmonary circulation disease |
| PERIVASC | … Peripheral vascular disease |
| HTN | … Hypertension, uncomplicated |
| HTNCX | … Hypertension, complicated |
| PARA | … Paralysis |
| NEURO | … Other neurologic disorders |
| CHRNLUNG | … Chronic pulmonary disease |
| DM | … Diabetes without chronic complications |
| DMCX | … Diabetes with chronic complications |
| HYPOTHY | … Hypothyroidism |
| RENLFAIL | … Renal failure |
| LIVER | … Liver disease |
| ULCER | … Peptic ulcer disease x bleeding |
| AIDS | … Acquired immune deficiency syndrome |
| LYMPH | … Lymphoma |
| METS | … Metastatic cancer |
| TUMOR | … Solid tumor w/o metastasis |
| ARTH | … Rheumatoid arthritis/collagen vas |
| COAG | … Coagulopathy |
| OBESE | … Obesity |
| WGHTLOSS | … Weight loss |
| LYTES | … Fluid and electrolyte disorders |
| BLDLOSS | … Chronic blood loss anemia |
| ANEMDEF | … Deficiency anemias |
| ALCOHOL | … Alcohol abuse |
| DRUG | … Drug abuse |
| PSYCH | … Psychoses |
| DEPRESS | … Depression |

### Hypertension ICD-10 Diagnoses Codes (core.d_htn_dx)

Derived from AAFP toolbox for HTN coding (www.aafp.org/fpm/2014/0300/fpm20140300p5-rt1.pdf)

| Data Element | Notes |
| --- | --- |
| dx_id | EPIC diagnosis ID (links to pmap_commons.dbo.clairty_edg) |
| dx_name | EPIC diagnoses name |
| current_icd10_list | ICD-10 codes associated with dx_id |
| cat | Hypertension category: - ‘primary’ for primary (aka essential) hypertension diagnoses - ‘secondary’ for secondary hypertension diagnoses (Definition: concepts/htn_cohort/d-htn-dx.sql) |

## Concepts for ADT

### Bed durations (base.adt)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| department_id | Department. Lookup in d_department_id or d_dept_type. (avoid pmap_commons.dbo.d_department due to duplicates) |
| room_id |  |
| Room (lookup in pmap_commons.dbo.d_room) |  |
| bed_id |  |
| Bed (lookup in pmap_commons.dbo.d_bed) |  |
| seq_stay | Sequence of this bed duration with encounter |
| first_event_type_c |  |
| num_in_etc |  |
| num_out_etc |  |
| in_event_type_c |  |
| out_event_type_c |  |
| in_time | Start time at this location |
| out_time | End time at this location |
| num_error |  |
| QC |  |

## Concepts for Encounters/Admissions

### Core.encounters

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| inp | ‘1’ if in-patient encounter (from ‘accm_inpatient’) |
| outp | ‘1’ if out-patient encounter (from ‘accm_outpatient’) |
| an52 | ‘1’ if anesthesia “52” encounter (from ‘accm_an_record_summary.an_52_enc_csn_id’) |
| an53 | ‘1’ if anesthesia “53” encounter (from ‘accm_an_record_summary.an_53_enc_csn_id’) |
| surg | ‘1’ if surgery encounter (from ‘accm_surgeries.pat_enc_csn_id’) |

### Core.adt_adm

All CSNs with ADT entries.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| in_time | Start of admission |
| out_time | End of admission (discharge) |
| adm_dt |  |
| hop_dt |  |
| mm_dt |  |
| dc_dt |  |
| status |  |
| any_floor |  |
| any_or |  |
| any_ed |  |
| any_clinic |  |
| any_rads |  |
| num_real_op |  |
| num_real_ip |  |
| adt_pat_class_c |  |
| hosp_admsn_type_c |  |
| admit_source_c |  |
| adt_patient_stat_c |  |
| disch_disp_c |  |
| dep_rpt_grp_ten |  |
| department_id | Department ID for encounter from accm_inpatient table. |
| dep_speciality |  |
| hosp_admsn_time |  |
| hosp_disch_time |  |
| contact_date |  |
| inp_adm_date |  |
| op_adm_date |  |
| emer_adm_date |  |
| hospital_service |  |
| in_icu_cohort |  |
| in_picu_cohort |  |
| num_concur_adm |  |
| group_in_time |  |
| group_out_time |  |
| adm_group |  |
| group_pri |  |
| adm_group_seq | (source: core/adt/adt-adm.sql) |

### Core.adm_info

Join of core.adt_adm (all admissions) with
- use of ventilation (max level during admission)
- use of ECMO (yes/no during admission)

### Core.icu_adm

Inpatient admissions for patients in ICU cohort (includes admissions with/without  an associated ICU stay).

### Admission mortality (core.info_adm_death)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| disch_disp_c |  |
| hosp_disch_time |  |
| death_date |  |
| pat_status |  |
| adm_death | ‘1’ if patient died during admission, defined at least one of: - death time within 24 hours of hospital discharge time - death date same as hospital discharge date - discharge disposition one of: - 20 = Expired - 40 = Expired at Home - 41 = Expired medical facility, hospital, SNF, ICF, … - 42 = Expired place unknown - 229 = Organ death |
| adm_30_day_death | ‘1’ if died within 30 days of discharge, defined as: - patient died during admission (above), or - death date is within 30 days of hospital discharge time. |

### Admission Length of Stay - VIEW (core.view_info_adm_los)

One row for each admission in the ‘core.adt_adm’ table.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Admission CSN |
| adm_los | Length of stay (days) for hospital admission |
| icu_los | Length of stay (days), for all ICU stays within admission (source concepts/info/view-info-adm-los.sql) |

## Concepts for ICU stays

### ICU Stays (icustay)

Table of ICU stays

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | ICU stay sequence within encounter, independent of ICU type. |
| icu | ICU type: / One of (ACCM): / - ‘picu’, ‘sicu’, ‘nccu’, ‘wicu’, ‘cvsicu’ / - ‘bmc_sicu’, ‘bmc_nccu’, ‘bmc_burn_icu’ / - ‘smh_icu’, ‘hoco_icu’, ‘sh_icu’, / Or (non-ACCM): / - ‘micu’, ‘onc_micu’, ‘ccu’, ‘bmc_micu’, ‘bmc_cicu’, / - ‘nicu’, ‘bmc_nicu’, ‘hoco_nicu’, ‘shm_nicu’ |
| accm | Is an ACCM ICU / - ‘1’ = ACCM ICU / - ‘0’ = Non-ACCM ICU |
| in_time | ICU admission time |
| out_time | ICU discharge time |
| origin | Location prior to ICU / - ‘ed’ / - ‘floor’ / - ‘or’ |
| Inc_or | - ‘1’ if ICU stay includes an OR location (ignoring those that proceed or follow the ICU stay) / - ‘0’ otherwise |

### ICU Stay – Mechanical Ventilation (core.info_stay_mv)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | ICU sequence (the pat_enc_csn_id, seq pair is UNIQUE) |
| icu | ICU type (see core.icustay) |
| origin | Origin (duplicate of core.icustay) |
| mv_total_hr | Total hours of mechanical ventilation during ICUstay (includes ventilation during embedded anesthesia encounters). |
| mv_adr_hr | Hours of mechanical ventilation during anesthesia encounters embedded in ICUstay. |
| mv_handoff_hr | Hours of mechanical ventilation that occurred in the ICU during the first hour after an embedded anesthesia encounter. |
| mv_icu_hr | Hours of mechanical ventilation that occurred in the ICU, excluding those in an embedded anesthesia encounter (equal to mv_total_hr – mv_adr_hr) |

### ICU Stay w/information (core.icustay_info)

Join of ICU stays (core.icustay) with
- use mechanical ventilation (hours during ICU stay)
- use of ECMO (yes/no)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | ICU sequence (the pat_enc_csn_id, seq pair is UNIQUE) |
| icu | ICU |
| in_time | ICU admission time |
| out_time | ICU discharge time |
| max_level | max ventilation level used during ICU stay |

## Concepts for Laboratory Results

### Respiratory Viral Panel PIVOT (core.resp_viral_panel)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| order_proc_id | Order identifier, shared by all component IDs in panel. |
| proc_id | Panel procedure identifier |
| specimen_taken_time | Date/time specimen taken |
| influ_a | Results of influenza A testing.  One of: - ‘RNA Detected’ - ‘No RNA Detected’ - ‘Indeterminate’ - ‘error-no-result’ - NULL – test not performed with panel |
| influ_b | Results of influenza B testing. |
| rsv | Results of RSV testing. |
| corona | Results of coronavirus testing (this is not specific to SARS-CoV-2, the virus that causes COVID-19). |
| para_flu_1 | Results of parainfluenza virus 1 testing. |
| para_flu_2 | Results of parainfluenza virus 2 testing. |
| para_flu_3 | Results of parainfluenza virus 3 testing. |
| para_flu_4 | Results of parainfluenza virus 4 testing. |
| rhino | Results of rhinovirus testing. |
| hmpv | Results of human metapneumovirus testing. |
| adeno | Result of adenovirus testing.  One of - ‘DNA Detected’ - ‘Low Level DNA Detected’ - ‘No DNA Detected’ - ‘Indeterminate’ - ‘error-no-results’ – collection of various errors - NULL if test not performed w/panel (Note: RNA results reported for some tests) |
| chlamydia | Result of chlamydia pneumonia testing.  One of - ‘No DNA Detected’ - ‘No RNA Detected’ - ‘error-no-results’ – collection of various errors - NULL if test not performed w/panel Note: no positive results found in ACCM PMAP. |
| mycoplasma | Result of mycoplasma pneumonia testing.  One of - ‘DNA Detected’ - ‘No DNA Detected’ - ‘No RNA Detected’ - ‘error-no-result’ - NULL – test not performed w/panel |
| num_pos | Number of organisms testing positive in panel. |
| num_err_ind | Number of organisms with errors or indeterminate results in panel. |
| num_final | Number of panel tests marked as final (lab.result_status = ‘Final’ |
| num_abnormal | Number of tests in pnale marked as abnormal (lab.result_flag = ‘Abnormal’ or ‘High’).  In general this should equal ‘num_pos’. |
| num_components | Total number of tests in panel. |
| organism | One of: - ‘Multiple’ if multiple organisms test positive - ‘E/I’ if any error or indeterminate results - Name of organism if single test positive. - NULL if not test positive |

## Concepts for LDAs

### LDA Table (core.lda)

This table is derived from data in the accm_flowsheet table (the base.fs_rw subset).  An alternate table provided from EPIC is `dbo.accm_lda_data`.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| ip_lda_id | LDA identifier (UNIQUE) |
| fs_rw_meas_id |  |
| rw_meas_id |  |
| detail |  |
| subdetail |  |
| type |  |
| n_place |  |
| n_remove |  |
| n_csn |  |
| poa |  |
| poa_count |  |
| place_dt |  |
| remove_dt |  |

## Concepts for Medications

### Antibiotic Durations (core.abx_dur)

Note: Computed for PICU cohort only.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| pat_enc_csn_id | Encounter identifier |
| name | Antibiotic name |
| route | Medication administration route |
| seq |  |
| order_time | Order time (earliest order time of doses given during duration). |
| start_time | Start time of antibiotic duration |
| stop_time | Stop time of antibiotic duration |
| num_doses | Number of doses given during duration |
| dur_hr | Duration of duration (in hours) |

### Anesthetic (Induction, NMBs, IV agents) Durations (core.anes_dur)

Bolus and infusions of the following medications
- rocuronium, vecuronium, cisatricurium
- ketamine, propofol, etomidate
- fentanyl, morphine, hydromorphone
- midazolam

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to ‘accm_patient’ table |
| name | Medication name |
| route | Medication administration route |
| seq |  |
| start_time | Start time of antibiotic duration |
| stop_time | Stop time of antibiotic duration |
| min_dose |  |
| max_dose |  |
| num_entries | Number of doses given during duration |
| gap_hr |  |
| dur_hr | Duration of duration (in hours) Note: pat_enc_csn_id is not included.  Search instead by patient (osler_id) and time frame of interest. This insures that anesthetics documented in an embedded CSN (such as the OR) are included. |

### Anesthetic MAR (core.anes_mar)

Details of anesthetic infusions and boluses.
TBD

## Concepts for Resource Utilization

### Lab Utilization (core.lab_util)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| proc_id | Laboratory ‘proc_id’ |
| lab_cat | Lab category |
| lab_name | Lab name or lab group name (‘proc_name’ from CLARITY_EAP) |
| cnt | Number of occurrences for lab (by patient-encounter) |
| first_dt | Date/time of first occurrence |
| last_dt | Date/time of last occurrence |
| cost | Cost ($) (from CLARITY_EAP) |

### Radiology Utilization (core.rad_util)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| proc_code | Radiology study “code” |
| name | Radiology study name (eg “XR CHEST AP ONLY”) |
| cnt | Number of occurrences (by patient-encounter) |
| first_dt | Date/time of first occurrence |
| last_dt | Date/time of last occurrence |

### Transfusion Utlization (core.blood_util)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| product_type | Blood product type.  One of: - ‘prbc’, ‘prbc-leukoreduced-hats’, ‘prbc-ecmo’, ‘prbc-unmatched’, - ‘platelets’, ‘platelets-ecmo’, - ‘plasma’, ‘plasma-hats’, - ‘cryo’, ‘cyro-pooled’, - ‘whole-blood’, - ‘rhogam’, - ‘hemopure’, - ‘init-mtp’, - ‘ecmo-pump-change’ |
| cnt | Number of product occurrences given (by patient-encounter) |
| first_dt | Date/time of first occurrence |
| last_dt | Date/time of last occurrence |

## Concepts for Scores

### PRISM-III (core.prism3)

Each row corresponds to the PRISM-3 score computed on the first day a PICU admission

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | ICUstay ‘seq’uence number (from icustay table) |

### PSOFA / PELOD (core.psofa_q1)

Each row corresponds to the PSOFA / PELOD score evaluated using data from the previous 24 hour. Rows are spaced along 1 hour intervals starting 24 hours before PICU admission and ending with PICU discharge.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | ICUStay ‘seq’uence number (from icustay table) |
| age_m | Patient age (months) at ‘start_time’ |
| start_time | Row interval start time |
| end_time | Row interval end time |
| s_psofa_pf | PSOFA score calculated over previous 24 hours data using P/F ratio |
| s_psofa_sf | PSOFA S/F score for this interval.  Used to calculate s_psofa_pf_24. |
| s_psofa_plt | PSOFA PLT score for this interval |
| s_psofa_bili | PSOFA bilirubin score for this interval |
| s_psofa_map | PSOFA MAP (mean arterial pressure) score for this interval |
| s_psofa_gcs | PSOFA GCS (glascow coma score) for this interval |
| s_psofa_cr | PSOFA creatinine score for this interval |
| s_psofa_pf_24 | Total PSOFA score calculated over previous 24 hours data using P/F ratio |
| s_psofa_sf_24 | Total PSOFA score calculated over previous 24 hours data using S/F ratio |
| s_gcs | PELOD GCS sub-score for this interval |
| s_pupils |  |
| s_lac |  |
| s_map |  |
| s_cr |  |
| s_pf |  |
| s_paco2 |  |
| s_vent |  |
| s_wbc |  |
| s_plt |  |
| s_neuro_24 |  |
| s_cv_24 |  |
| s_renal_24 |  |
| s_resp_24 |  |
| s_heme_24 |  |
| s_pelod_24 | Total PELOD score calculated over with previous 24 hours data. |

### Vasoactive-Introtropic Score (core.vis)

Vasoactive-inotropic score (VIS) as defined by Gaies et al (PCCM 2010).

| VIS = | 1 x | Dopamine dose (mcg/kg/min) + |
| --- | --- | --- |
|  | 1 x | Dobutamine dose (mcg/kg/min) + |
|  | 100 x | Epinephrine dose (mcg/kg/min) + |
|  | 10 x | Milrinone dose (mcg/kg/min) + |
|  | 10,000 x | Vasopressin dose (U/kg/min) + |
|  | 100 x | Norepinephrine dose (mcg/kg/min) |

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id |  |
| taken_time | Time medication doses recorded |
| taken_hour | Time medication doses recoded, rounded to hour |
| dopa | Dopamine infusion rate (mcg/kg/min) |
| dobut | Dobutamine infusion rate (mcg/kg/min) |
| epi | Epinephrine infusion rate (mcg/kg/min) |
| norepi | Norepinephrine infusion rate (mcg/kg/min) |
| mil | Milrinone infusion rate (mcg/kg/min) |
| vaso | Vasopressin infusion rate (U/kg/min) |
| score | VIS score |

## Concepts for Study Findings

### Study Findings (core.study_finding)

One row for each study finding evaluated in corresponding study.

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| order_proc_id | Order identifier. UNIQUE |
| proc_code | Imaging code |
| finding_id | Study finding ID |
| finding_value | Study finding value |
| finding_num | Numeric value of `finding_value`, if applicable. |
| finding_comment | Study finding comment |
| version | Version information for study finding algorithm used |
| dt | Time study finding was computed. |

## Concepts for vitals

### Fever/Hypothermia Durations (core.fever_dur)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| fever_seq | Sequence of this duration (partitioned by patient) |
| any_fever | ‘1’ if this duration contains fever |
| any_hypothermia | ‘1’ if this duration contains hypothermia, ‘0’ otherwise |
| start_time | Starting time for this duration |
| stop_time | Stop time for this duration |
| max_temp | Maximum temperature during this duration |
| min_temp | Minimum temperature during this duration |
| thresh | Fever threshold (38.3 for immunocompromised patients, 38.5 otherwise) Repository location: concepts/vitals/{fever-dur,fever-dur-tmpl}.sql |

### Vitals (base.vitals_data)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| recorded_time | Time vital observation was made. |
| cat | Type of vital observed.  One of: - ‘pulse’ – heart-rate - ‘resp’ – respiratory rate - ‘map’, ‘sbp’, and ‘dbp’ – mean, systolic, and diastolic blood pressure, measured non-invasively - ‘map-art’, ‘sbp-art’, ‘dbp-art’ – mean, systolic, and diastolic blood pressure, measured via arterial cannula - ‘temp’ – temperature (in Celsius) - ‘spo2’ – arterial O2 saturation, measured via pulse oximetry - ‘weight’ – patient weight (most recently measured) - ‘dosing-weight’ – patient weight used for medication dosing - ‘etco2’ – end-tidal CO2 - ‘gcs’ – Glasgow Coma Score |
| meas_value | Value of observation, from EPIC, as string. |
| num_value | Numeric value of observation. Units transformed for cat = ‘weight’, ‘dosing-weight’, and ‘temp’. May be NULL if ‘meas_value’ is not a properly formatted number. For cat = ‘weight’ or ‘dosing-weight’, num_value is the weight in kilograms.  meas_value will retrain the string value of the weight in ounces. For cat = ‘temp’, num_value is the temperature in Celsius.  Meas_value will retain the string value of the temperature in degree Fahrenheit. |
| meas_id | Flowsheet meas_id that vital entry was generated from.  Links to the d_flowsheet table. Clustered index: osler_id, recorded_time |

## Concepts for Organ Support Devices

### ECMO Durations (core.ecmo_dur)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq |  |
| start_time |  |
| stop_time |  |
| dur_hr |  |
| VA | ‘1’ if VA ECMO settings documented during duration, ‘0’ otherwise. |
| VV | ‘1’ if VV ECMO settings documented during duration, ‘0’ otherwise. |
| ECPR | ‘1’ if ECPR documented during duration, ‘0’ otherwise. |
| QC_num_entries |  |
| QC_num_hour |  |
| QC_num_itime |  |
| QC_num_start |  |
| qC_num_end |  |
| QC_min_hour |  |
| QC_max_hour |  |
| QC_gap_hr |  |

### ECMO Settings (core.ecmo_set)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| recorded_time |  |
| type |  |
| hour |  |
| itime |  |
| start_date |  |
| end_date |  |
| flow |  |
| flow_mkm |  |
| blender |  |
| sweep |  |
| rpm |  |
| svo2 |  |
| c_nirs |  |
| s_nirs |  |
| P2 |  |
| P3 |  |
| capped |  |
| VA |  |
| VV |  |
| ECPR |  |
| fs_count |  |

### O2 Device (core.o2_device)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| recorded_time |  |
| meas_id | Flowsheet `meas_id` of setting (useful when evaluating provenance of setting, or when multiple settings recorded simultaneously) |
| meas_value |  |
| min_level |  |
| max_level |  |
| count |  |

### Ventilator Durations (core.vent_dur)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | Sequence of ventilator duration within encounter |
| level | Level of respiratory support during this duration: - 1 = Room Air (RA) - 2 = Supplementary oxygen - 3 = Regular nasal cannula (NC) - 4 = High-flow nasal cannula (HFNC) - 5 = Non-invasive positive pressure ventilation (NIPPV) - 6 = conventional mechanical ventilation (CMV) - 7 = high-frequency oscillation or jet ventilation (HFOV/HFJV) |
| start_time | Start time of respiratory support duration |
| stop_time | Stop time of respiratory support duration |
| last_recorded_time | Time of last flowsheet entry for this duration.  Different than stop_time, which occurs with first flowsheet entry for next duration. |
| dur_hr | Length of duration (stop_time – start_time), in hours. |
| post_hr | Duration between final documented setting of this duration and first documented setting of next duration, in hours |
| loc | Location of ventilator duration (by CSN type of documentation) - ‘inpatient’ if entirely documented in inpatient admission CSN - ‘anesthesia’ if entirely documented in anesthesia AN52 CSN - ‘both’ if entirely documented in inpatient and AN52 CSNs - ‘other’ if documented in another CSN type (may include inpatient and AN52 documnetation) |
| qc_num_vent_level | Quality control |
| qc_num_o2_level | Quality control |
| qc_count | Number of flowsheet entries for this duration. |
| qc_num_csn | Number of CSNs spanned by duration Clustered index on osler_id, start_time |

### Ventilator Mode (core.vent_mode)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | Sequence number of ventilator mode for this patient (continuous across encounters) |
| level | Level of respiratory support during this mode duration: - 1 = Room Air (RA) - 2 = Supplementary oxygen - 3 = Regular nasal cannula (NC) - 4 = High-flow nasal cannula (HFNC) - 5 = Non-invasive positive pressure ventilation (NIPPV) - 6 = conventional mechanical ventilation (CMV) - 7 = high-frequency oscillation or jet ventilation (HFOV/HFJV) |
| mode | Ventilator mode. For level 6-7, this is the documented ventilator mode, mapped into canonical name (eg ‘SIMV Vol’ is mapped to ‘VC’).  Common modes include: - ‘VC’ – volume control - ‘PC’ – Pressure control - ‘PS’ – pressure support - ‘Spont Vent’ – spontaneous ventilation (frequently documented in OR) - ‘APRV’ - ‘MMV’ - ‘VENT’ – if mode not determined from settings For level 5, this is one of: - ‘BIPAP’ - ‘CPAP’ - ‘NPPVg’ – if mode not determined from settings For levels 1-4, this is fixed by level - ‘RA’ for level = 1 - ‘Oxy’ for level = 2 - ‘NC’ for level = 3 - ‘HFNC’ for level = 4 |
| start_time | Start time of respiratory support mode duration |
| stop_time | Stop time of respiratory support mode duration |
| qc_count | Number of flowsheet entries documenting this mode duration. * - note there is no way to reliably distinguish between pressure-cycled dual control (aka PRVC or autoflow) and flow-cycled traditional volume control. |

### DEPRECATED -- PICU Ventilator Durations (core.picu_vent_dur)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| pat_enc_csn_id | Encounter identifier |
| seq | Sequence of ventilator duration within encounter |
| level | Level of respiratory support during this duration: - 1 = Room Air (RA) - 2 = Supplementary oxygen - 3 = Regular nasal cannula (NC) - 4 = High-flow nasal cannula (HFNC) - 6 = conventional mechanical ventilation (CMV) - 7 = high-frequency oscillation or jet ventilation (HFOV/HFJV) |
| start_time | Start time of respiratory support duration |
| stop_time | Stop time of respiratory support duration |
| last_recorded_time | Time of last flowsheet entry for this duration.  Different than stop_time, which occurs with first flowsheet entry for next duration. |
| dur_hr | Length of duration (stop_time – start_time), in hours. |
| num_vent_level | Quality control |
| num_o2_level | Quality control |
| count | Number of flowsheet entries for this duration. |

### DEPRECATED -- Ventilator Settings (core.picu_vent_set)

| Data Element | Notes |
| --- | --- |
| osler_id | Patient identifier, links to accm_patient table |
| recorded_time | Time of setting observations (derived from flowsheet recorded_time) |
| vss | Vent start/stop (not documented in pediatrics) |
| level | Level of respiratory support (see Ventilator Duration concept) |
| simple_level | Simple level of respiratory support - 0 = Non-invasive support (RA through NIPPV) - 1 = Invasive mechanical ventilation (CMV or HFOV) |
| name | Name of respiratory support device |
| nppv_mode | Non-invasive positive pressure mode.  Includes: - ‘BiPAP’ - ‘CPAP’ - ‘SiPAP’ - ‘S/T’ 27 different values, including NULL. |
| vtype | Invasive ventilation type.  One of: - ‘CMV’ = conventional mechanical ventilation - ‘HFOV’ = high-frequency oscillatory ventilation - ‘HFJV’ = high-frequency jet ventilation - ‘HFOV;Convetional’ - ? May be NULL |
| vmode | Ventilator mode.  Includes: - ‘PC’ = pressure control - ‘VC’ = volume control - ‘APRV’ = - ‘MMV’ = mandatory minute ventilation - ‘CPAP’ = - ‘PS’ = pressure support 14 different values, including NULL |
| flow | Set liter flow (L/m) for NC and HFNC |
| fio2 | Set inspired fraction of O2 |
| pip | Peak inspiratory pressure (for NIPPV, CMV) |
| vol |  |
| pc |  |
| peep |  |
| rate |  |
| ps |  |
| hvof_map |  |
| o2_name | Name of respiratory support from ‘O2 Device’ concept |
| o2_level | Level of respiratory support from ‘O2 Device’ concept |
| o2_id | Flowsheet meas_id used for ‘O2 Device’ concept |
| pat_enc_csn_id |  |
| in_picu |  |
| department_id |  |
| department_name |  |

## Reference Tables

Not patient data tables loaded from external reference sources (such as CMS, AHRQ, etc)

### 2018 ICD-10-PCS General Equivalence Mappings (GEMS) (ref.gem_19pcs_2018)

Based on the "2018 General Equivalence Mappings (GEMS) - Updated August 03, 2017 (ZIP)" [1] located [2]
Links
[1] https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2018-ICD-10-PCS-General-Equivalence-Mappings.zip
[2] https://www.cms.gov/Medicare/Coding/ICD10/2018-ICD-10-PCS-and-GEMs

| Data Element | Notes |
| --- | --- |
| icd9cm | ICD-9-CM Code [source] |
| icd10pcs | ICD-10-PCS Code [target] |
| flags | 5 digit flag: - flag[0]: “approximate” 0/1 - flag[1]: “No Map” 0/1 - flag[2]: “Combination” 0/1 - flag[3]: “Scenario” 0-9 - flag[4]: “Choice List” 0-9 (ref/cms/2018-ICD-10-PCS_GEMS/…) |

### 2022 ICD-10-CM (ref.icd10cm_2022)

2022 ICD-10-CM codes plus descriptions, from cms.gov [1]
[1] https://www.cms.gov/medicare/icd-10/2022-icd-10-cm

| Data Element | Notes |
| --- | --- |
| order | Code “order number”, used to determine which ICD-10-CM/PCS code comes first in an official document |
| code | ICD-10-CM code with dot (if applicable). |
| code_nodot | ICD-10-CM code without dot. |
| valid | - ‘0’ if code is a “header” – not valid for HIPAA-covered transactions - ‘1’ if code is valid for submission for HIPAA-covered transactions. |
| abbr | Short description (up to 60 characters) |
| name | Long description. |

## Meta Tables

### Table Info (meta.table_info)

| Data Element | Notes |
| --- | --- |
| table_name |  |
| dt |  |
| osler_dt |  |
| cohort_dt |  |
| sql_file_hash |  |
| size_hash |  |
| final_hash |  |

### Osler Version Info (meta.osler)

| Data Element | Notes |
| --- | --- |
| dt | Osler date |
| osler_id | Osler used on ‘dt’ |
| mrn | EMRN used on date ‘dt’ |
| mrnstatus | Status or EMRN used on date ‘dt’ Cluster index on osler_id. Source: base/meta/osler.sql |

## AQI Tables

Tables in the ‘aqi’ schema with the prefix ‘ref_’ are copies from the AQI database.

### Intraoperative Blood Units (aqi.ref_intraop_bloodunits)

Copy of AQI_NEW.dbo.aqi_intraop_bloodunits.

| Data Element | Notes |
| --- | --- |
| an_episode_id (EpisodeID) |  |
| order_id |  |
| blood_unit_num |  |
| blood_product_code |  |
| blood_start_instant |  |
| blood_end_instant |  |
| display_name |  |
| units |  |
| Category |  |

### Minimum Dataset (aqi.ref_minimumdataset)

Copy of AQI_NEW.dbo.aqi_minimumdataset

| Data Element | Notes |
| --- | --- |
| EpisodeID | Equivalent to an_episode_id |
| StaffID |  |
| AnProvName |  |
| StaffRole |  |
| StaffTitle |  |
| NPI |  |
| SurgeonID |  |
| SurgeonName |  |
| ServiceArea |  |
| DateOfService |  |
| AnesthesiaStartTime |  |
| AesthesiaEndTime |  |
| Gender |  |
| DOB |  |
| ASA_PhysicalStatus |  |
| PaymentCode |  |
| HSP_ACCOUNT_ID |  |
| LOG_ID |  |
| PatientClass |  |
| PrimaryAnesthesiaType |  |
| PAT_MRN_ID |  |
| PAT_ENC_CSN_ID |  |
| AN_PROC_NAME |  |
| FacilityID |  |
| Hospital |  |
| Age |  |
| LOC_NAME |  |
| ProcStatus |  |
| HOSP_ADMSN_TIME |  |
| HOSP_DISCH_TIME |  |
| ETHNICITY |  |
| STATE |  |
| ZIP |  |
| DISCHARGE_DISPOSITION |  |
| DISCHARGE_DESTINATION | FirstRace … FifthRace |
| MultiRacial |  |
| DeathDate |  |
| WEIGHT_Kgs |  |
| Status |  |

## Comments

…
