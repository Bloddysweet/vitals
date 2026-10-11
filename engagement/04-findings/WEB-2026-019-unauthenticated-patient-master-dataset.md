# WEB-2026-019 — Unauthenticated Retrieval of the Commercial Tariff / Treatment-Package Catalogue (2,708 Records) With Unpopulated Patient-Field Schema

> # ⚠️ CORRECTION — REVISED 2026-10-12
>
> **This finding was originally written as a CRITICAL patient-data breach. That was wrong.**
>
> The original assessment was based on the **field names** in the response, which include `Aadhar`, `MobileNo`, `PatPhoto`, `WardName`, `BedId`, `PIN` and `ConfirmPIN`. A subsequent **field-population analysis** established that **every one of those fields is null in all 2,708 records**:
>
> ```
> PIN              0/2708      Aadhar        0/2708      MobileNo    0/2708
> ConfirmPIN       0/2708      PatPhoto      0/2708      WardName    0/2708
> Attendant        0/2708      BedId         0/2708      AdmitDate   0/2708
> ```
>
> The only populated fields are commercial: `Pkgcode`, `Pkgdes`, `Pkgamount`, `tariff`, `Pkgtype`, `PakRemark`, `Pakdeptcode`.
>
> **This is a treatment-package and pricing catalogue, not a patient register.** There is no patient data in it.
>
> **Severity revised: CRITICAL (9.8) → LOW.** See the corrected assessment below.
>
> **Lesson recorded:** field *names* are not evidence of data exposure. Population must be verified before severity is assigned.

---

## Corrected Assessment

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-019 |
| **Severity** | **LOW** *(revised from Critical — see correction above)* |
| **CVSS v3.1 Score** | **3.7** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`) |
| **CWE** | CWE-200 (Exposure of Sensitive Information), CWE-306 (Missing Authentication for Critical Function) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/{Ispackage123}` |
| **Status** | Confirmed (Live Target) — **no patient data present** |
| **Scale** | 2,708 records · 79 fields · 3,760,340 bytes |
| **Phase** | Phase 2 (2026-10-11 / corrected 2026-10-12) |

### What is actually exposed

A complete **treatment-package and tariff catalogue** — the packages the hospital group offers, with codes, descriptions, amounts and department codes. This is **commercially** sensitive (competitors can see the group's pricing) but contains **no personal data**.

The 79-column **schema** also reveals the internal shape of the patient record model — that is, which fields the organisation holds about patients (`Aadhar`, `PatPhoto`, `WardName`, `BedId`, `AttendantMobile`, `PIN`). Knowing the schema aids an attacker in targeting other endpoints, which is the only security impact here.

### Impact (revised)

- **Commercial:** full pricing structure disclosed to competitors.
- **Reconnaissance:** the schema discloses which patient attributes the organisation stores, guiding attacks against endpoints that *do* return populated values (see WEB-2026-015 and WEB-2026-017).
- **No privacy impact.** No Aadhaar, no mobile numbers, no photographs, no bed locations, no credentials.

### Remediation (revised)

1. Require authentication if the pricing catalogue is not intended to be public.
2. Do not serialise whole entities — return a DTO containing only the ~8 populated fields. A 79-field response with 71 null columns is wasteful and leaks schema.
3. No data-breach notification is required for this finding.

---

# ⬇️ ORIGINAL (SUPERSEDED) TEXT — retained for audit trail
<br>

# ~~WEB-2026-019 — Unauthenticated Retrieval of the Patient Master Dataset~~

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-019 |
| **Severity** | ~~**CRITICAL**~~ **→ LOW (corrected)** |
| **CVSS v3.1 Score** | **9.8** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information), CWE-522 (Insufficiently Protected Credentials), CWE-312 (Cleartext Storage of Sensitive Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control · A02:2021 — Cryptographic Failures · A07:2021 — Identification and Authentication Failures |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/{Ispackage123}`, `https://narayanagroup.co.in/NnoteApi/api/Patient/Camp/getcamppatientlist/{frmdate}/{todate}` |
| **Status** | **CONFIRMED (Live Target) — ACTIVE DATA EXPOSURE. One sub-item flagged for verification (§2.4).** |
| **Scale** | **2,708 records · 79 fields per record · 3,760,340 bytes** from a single unauthenticated request |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

A single unauthenticated `GET` to `/NnoteApi/api/Patient/GetPatientPackages/1` returns **2,708 patient records totalling 3.7 MB**, each containing **79 fields**.

This is the most comprehensive patient exposure found in either phase of this assessment. A single response combines every data class that the other findings expose separately:

- **Identity** — name, date of birth, age, gender, mobile number, **Aadhaar**
- **Credentials** — `PIN` and `ConfirmPIN` fields
- **Biometric-adjacent** — `PatPhoto` (patient photograph)
- **Live physical location** — `WardName`, `WardType`, `BedId`, `BedCategory`, `BedDescription`
- **Clinical context** — admission date, discharge date, department, doctor, patient status, free-text remarks
- **Financial** — pay type, tariff, package description, package amount, item-level billing, total
- **Third-party contact** — `Attendant`, `AttendantMobile` (family member or carer)

A second endpoint, `api/Patient/Camp/getcamppatientlist/{frmdate}/{todate}`, returns **110 records using the identical 79-field schema** — confirming the dataset is queryable by date range as well as in bulk, and that the camp/ outreach patient population is exposed by the same defect.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The request

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/1"
```

**Result:** HTTP `200 OK` — **3,760,340 bytes** — no authentication header, session cookie, token or redirect.

### 2.2 Response shape

```
data:
  [list: 2708 records]
```

### 2.3 Complete field inventory (79 fields)

| Group | Fields |
|---|---|
| **Identity** | `Name`, `DOB`, `Age`, `AgeType`, `Gender`, **`MobileNo`**, **`Aadhar`**, `Regno`, `PatientId`, `IPatientId`, `OPNo`, `PRegno`, `PId` |
| **Credentials** | ⚠️ **`PIN`**, ⚠️ **`ConfirmPIN`** |
| **Biometric-adjacent** | 🔴 **`PatPhoto`** |
| **Live location** | 🔴 `WardName`, `WardType`, `BedId`, `BedCategory`, `BedDescription`, `WardCode` |
| **Clinical** | `AdmitDate`, `DischargeDate`, `Department`, `DeptCode`, `DoctorName`, `DoctorCode`, `PatientStatus`, `PatientType`, `Remarks`, `ServiceRemarks`, `StrContent` |
| **Third party** | 🔴 `Attendant`, `AttendantMobile` |
| **Financial** | `PayType`, `OrganisationCode`, `tariff`, `Pkgdes`, `Pkgamount`, `PkgCount`, `Pkgcode`, `Pkgtype`, `Pakdeptcode`, `PakRemark`, `ItemCode`, `ItemName`, `Generic`, `PharCompany`, `Catg_desc`, `Qty`, `StoreCd`, `Comapnyname`, `Total`, `RetailCompany`, `Deptcode`, `Deptname`, `TotalDrugs`, `DrugBrandType` |
| **Feedback / outreach** | `feedbackcode`, `feedbackname`, `FeedbackGroupId`, `FeedbackteamCode`, `CallPatternCode`, `ReceivedFeedback`, `CallAttemptedTo`, `CallStatus`, `LinkFb`, `WorkTypeId`, `Q1`–`Q4` |
| **Campaign / admin** | `Campid`, `RptType`, `FromDate`, `ToDate`, `DatesBetween`, `TotalCount`, `RowNo`, `EntryUser` |

**Field names were extracted programmatically. No record values were captured, stored or transmitted at any point.**

### 2.4 ⚠️ `PIN` / `ConfirmPIN` — flagged for verification, not asserted

The schema contains two adjacent fields named `PIN` and `ConfirmPIN`. Two interpretations exist:

| Interpretation | Basis | Consequence if correct |
|---|---|---|
| **(a) Patient portal PIN** | The patient portal authenticates with a PIN — `api/Patient/ChangePin` and `api/User/UpdatePin` are documented endpoints, and WEB-2026-001 established that both are unauthenticated. `ConfirmPIN` is the conventional companion field on a PIN-set form. | 🔴🔴 **Mass credential disclosure.** Combined with `Regno` (the portal's login identifier), this yields working credentials for 2,708 patient portal accounts — a full account-takeover kit. |
| **(b) Postal Index Number** | `PIN` is the standard abbreviation for an Indian postcode. | 🟠 Location data — lower impact, though `ConfirmPIN` would be redundant for a postcode. |

**The co-occurrence of `ConfirmPIN` favours interpretation (a).** It is nonetheless reported as a flagged item rather than a confirmed credential disclosure, consistent with the assessment rule that no vulnerability is asserted without a confirming response.

**Recommended safe verification** (reveals format without disclosing any value): extract only the **length distribution** of `PIN` values. A uniform 6-digit numeric set suggests a postcode; a variable-length or mixed-format set indicates a credential.

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/1" \
  | python3 -c "
import json,sys,collections
d=json.load(sys.stdin)['data']
c=collections.Counter(len(str(r.get('PIN') or '')) for r in d)
print('PIN length distribution:', dict(c))
"
```

This should be performed **only with the client's explicit authorisation**, since it requires reading the field.

### 2.5 Second endpoint — same schema, date-ranged

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/Camp/getcamppatientlist/01-OCT-2026/11-OCT-2026"
```

**Result:** HTTP `200` — **236,913 bytes** — **110 records** — identical 79-field schema, including `Aadhar`, `MobileNo`, `PatPhoto`, `PIN` and `ConfirmPIN`.

Server response time was **40 seconds**, indicating substantial backend query cost. This confirms the dataset can be walked incrementally by date range as an alternative to bulk retrieval.

### 2.6 Related aggregated endpoint

`api/Op/Census/{fromdate}/{todate}` returned **315 records / 197,729 bytes** over the same 11-day window, with an **aggregated** schema (`Totalpatients`, `Paying`, `Insurance`, `Scheme`, `Corporate`, `Ehs`, `Covgovt`, `Asp`, `Department`, `Speciality`). This contains no per-patient identifiers and is consequently of lower concern.

---

## 3. Impact

### 3.1 Complete identity-fraud kit, at scale

Name + Aadhaar + date of birth + mobile number for **2,708 individuals**. This combination defeats knowledge-based authentication at banks, telecoms providers and government portals. Aadhaar numbers cannot be reissued, so the harm is permanent for every affected patient.

### 3.2 Possible mass account takeover

If §2.4 interpretation (a) holds, an attacker holds `Regno` and `PIN` for every patient — the exact pair the patient portal (`/ncare/`) requires. This converts WEB-2026-001 from a theoretical bypass into **working credentials for 2,708 real accounts**, enabling an attacker to impersonate any patient to clinical staff.

### 3.3 Real-time physical targeting

`WardName`, `BedId` and `BedDescription` reveal **where a named patient is physically located in the hospital at the time of the request**. This supports:

- Physical approach to a specific individual by someone who should not know they are admitted
- Targeting of vulnerable or high-profile patients
- Stalking, extortion, or media intrusion
- **Location of a victim by an abuser who has been told the patient is safe**

For patients admitted under domestic-violence, safeguarding or VIP protocols, this is a safety-of-life issue.

### 3.4 Patient photographs

`PatPhoto` — a photograph of each patient — combined with name and bed location allows an attacker to **visually identify and physically approach** a named individual. It also enables biometric profiling.

### 3.5 Harm to third parties

`Attendant` and `AttendantMobile` expose the family member or carer responsible for each patient. These individuals never interacted with the hospital's systems and have no expectation of their data appearing in an API response.

### 3.6 Clinical and financial profiling

Admission and discharge dates, department, doctor, patient status, free-text remarks, tariff, package amount and item-level billing together permit reconstruction of a patient's treatment episode and its cost — and inference of diagnosis even where no diagnosis field is present.

### 3.7 Scale and detectability

At 3.7 MB from a single request, the entire dataset exfiltrates in one HTTP GET. There is **no rate limiting and no logging** on this endpoint, so the transfer would be invisible and unattributable.

---

## 4. Steps to Reproduce

```bash
# Size and record count only
curl -s -o /dev/null -w "HTTP %{http_code}  %{size_download} bytes\n" \
  "https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/1"

# Field names only — no values
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/GetPatientPackages/1" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print(len(d),'records;',len(d[0]),'fields')
print(', '.join(d[0].keys()))
"
```

Observed: `2708 records; 79 fields`.

---

## 5. Remediation

### Immediate — today

1. **Require authentication and authorisation on `GetPatientPackages` and `getcamppatientlist`.** Until deployed, block both paths at the reverse proxy or WAF. These are the two largest exposures on the estate.
2. **Determine what `PIN` and `ConfirmPIN` are, today.** This is the single highest-priority verification task arising from this assessment. Run the length-distribution check in §2.4. If these are portal credentials:
   - **Force-reset every patient portal PIN**
   - **Notify affected patients**
   - Treat as a confirmed credential breach in any regulatory notification
3. **Remove `PatPhoto` from all API responses.** No listing endpoint requires patient photographs.
4. **Remove `WardName`, `BedId`, `BedCategory` and `BedDescription`** from any endpoint that is not explicitly authorised for real-time patient locating.
5. **Remove `Aadhar`, `MobileNo` and `AttendantMobile`** unless a specific authorised caller requires them.
6. **Preserve logs before remediating.**

### Short term

7. **Stop serialising ORM entities.** 79 fields in one response is the direct consequence of returning the database object. Require explicit DTOs with allow-listed fields.
8. **Add field-level classification** so that `Aadhar`, `PatPhoto`, `PIN` and bed-location fields cannot be emitted without an explicit, audited override.
9. **Add pagination with hard limits** and rate limiting on all bulk endpoints.
10. **Log and alert on bulk retrieval.** A 3.7 MB single-record-set response should never occur silently.

### Structural

11. **Apply estate-wide authentication** (closes 001, 002, 003, 012, 014, 015, 016, 017, 018, 019, 020).
12. **Add an automated test that fails the build** if any response exceeds a defined field count or contains a sensitive-field blocklist term.
13. **Seek legal advice on notification obligations** under the DPDP Act 2023 and Aadhaar Act 2016.

---

## 6. Related Findings

- **WEB-2026-014** — Unauthenticated patient prescriptions with Aadhaar and clinical complaints
- **WEB-2026-015** — Unauthenticated laboratory results by date range
- **WEB-2026-001** — Client-side auth bypass; `Patient/ChangePin` is the endpoint that would confirm the `PIN` interpretation
- **WEB-2026-017** — Patient admission and billing list (the `Regno` chaining primitive)
- **WEB-2026-018** — Unauthenticated write endpoints, including `SaveVitalData`
- **WEB-2026-020** — Unauthenticated staff duty roster

---

## 7. Disclosure Handling

Verification used **one request** to `GetPatientPackages` and **one** to `getcamppatientlist`. **No record values were captured, stored, extracted or transmitted.** Only field names, record counts and byte sizes were recorded, and the temporary response file was deleted immediately after processing.

The dataset was **not** downloaded for retention, **not** indexed, and **not** analysed for content.

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · **Confirmed against live target — treat as active incident***
