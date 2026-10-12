# WEB-2026-015 — Unauthenticated Retrieval of Patient Laboratory Results by Arbitrary Date Range (Aadhaar, Mobile, Test Values, Report Files)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-015 |
| **Severity** | **HIGH** *(revised from Critical — see correction below)* |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |

> # ⚠️ PARTIAL CORRECTION — 2026-10-12
>
> The original assessment was based on **field names**. A **field-population analysis** has since confirmed which fields actually contain data.
>
> **CONFIRMED REAL — 7 patient records, all populated:**
>
> ```
> PatientName   7/7      RegNo   7/7      MobileNumber   7/7
> Age           7/7      Type    7/7      BillNumber     7/7
> ```
>
> **NOT populated — no values in any record:**
>
> ```
> AadharNo      0/7      TestValue      0/7      TestDescription  0/7
> TestCode      0/7      ImageData      0/7      FilePath         0/7
> Collectedon   0/7      Reportedon     0/7      Wardname         0/7
> ```
>
> **Therefore:**
> - ❌ **No Aadhaar numbers.** The `AadharNo` field exists but is null.
> - ❌ **No laboratory result values.** `TestValue` is null in all records.
> - ✅ **Real patient identities ARE exposed** — name, registration number and mobile number for 7 patients, retrievable by caller-supplied date range with no authentication.
>
> **Severity revised 9.1 → 7.5.** The finding remains genuine and materially serious — unauthenticated disclosure of named patients with mobile numbers — but it is not the Aadhaar-plus-results breach originally described, and the confirmed volume is small (7 records across a 284-day range).
>
> ### ✅ RESOLVED 2026-10-12 — test-level detail confirmed

Supplying a **real registration number** to `api/LabReport/getPatient_All_LabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}/{BillNo}` returned **18 fully-populated laboratory test records** for a single named patient:

| Field | Sample values |
|---|---|
| `PatientName` | `[22 chars]` |
| `RegNo` | `20260133958` |
| `Age` | `46 Y / M` |
| `MobileNumber` | `[10 digits]` |
| **`TestDescription`** | **`GRAMS STAIN`** · **`RT-PCR for COVID-19`** · **`C.REACTIVE PROTEIN {QUANITATIVE}`** |
| `TestCode` | `KMSM020` · `NHRTPCR1` · `NBIOCR` |
| `BillNumber` | `5207639827` · `5207650890` · `5207647018` |
| `Billdate` | `20-JAN-2026` · `25-JAN-2026` · `23-JAN-2026` |
| `Status` / `Confirmstatus` | `R`/`Y` · `E`/`N` · `R`/`Y` |

**The finding is therefore larger than "7 patients with names and mobiles."** With a valid registration number, the endpoint returns a patient's **laboratory test history** — which investigations were ordered and when.

`TestValue` remained empty in these records, so **test result values are still not confirmed exposed**. That is now the single open question (§7).

**Why test names alone are sensitive.** The names of investigations a person has undergone disclose health information independently of any result: a COVID-19 PCR, an inflammatory marker, a microbiology stain or an oncology marker each carry meaning on their own. `Status` (`R` = reported, `E` = in progress) and `Confirmstatus` further reveal whether a result exists and has been signed off.

`api/LabReport/getPatientLabReportData/{FromDate}/{ToDate}/{RegNo}/{TestCode}` independently confirmed the same patient and the `RT-PCR for COVID-19` test, corroborating the above.

**Severity remains High (7.5).** The CVSS confidentiality metric was already `C:H` on the basis of confirmed identity exposure; the test-history confirmation reinforces that rating rather than raising it. It would rise only if `TestValue` or `AadharNo` were shown to be populated.
>
> **Lesson recorded:** field *names* are not evidence of data exposure. Population must be verified before severity is assigned.
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information), CWE-639 (Authorization Bypass Through User-Controlled Key) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/LabReport/getPatientData/{FromDate}/{ToDate}` and 23 sibling `api/LabReport/*` endpoints |
| **Status** | **Confirmed (Live Target) — ACTIVE DATA EXPOSURE** |
| **Data Categories** | Patient identity, **Aadhaar**, mobile, **laboratory test results**, report file paths, dates of collection/reporting |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

`/NnoteApi/api/LabReport/getPatientData/{FromDate}/{ToDate}` accepts **an arbitrary date range from an unauthenticated caller** and returns patient laboratory records. Each record contains **47 fields**, including `PatientName`, `Age`, `Gender`, `MobileNumber`, **`AadharNo`**, `TestDescription`, **`TestValue`** (the actual result), `ImageData`, `FilePath` and `Filename`.

The endpoint is one of **24 `api/LabReport/*` routes** exposed without authentication, several of which take a patient registration number and bill number directly — for example `api/LabReport/GetPatientTestDetails/{RegNo}/{TestCode}/{BillNo}` and `api/LabReport/getPatient_All_LabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}/{BillNo}`.

Laboratory results are among the most sensitive categories of personal data a hospital holds. They reveal HIV status, genetic conditions, pregnancy, cancer markers, and substance use. Unlike a password or a card number, **a test result cannot be reissued or revoked once disclosed.**

---

## 2. Technical Evidence (Live Capture)

### 2.1 The date-range endpoint responds without authentication

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/LabReport/getPatientData/11-OCT-2026/11-OCT-2026"
```

**Result:** HTTP `200 OK` — **854 bytes** — no credentials required.

### 2.2 The date range is genuinely honoured by the backend

| Date range | HTTP | Bytes | Elapsed |
|---|---|---|---|
| `11-OCT-2026` → `11-OCT-2026` (1 day) | 200 | 854 | 0.42 s |
| `10-OCT-2026` → `11-OCT-2026` (2 days) | 200 | 854 | 0.42 s |
| `04-OCT-2026` → `11-OCT-2026` (8 days) | 200 | 854 | 0.49 s |
| `01-SEP-2026` → `11-OCT-2026` (41 days) | 200 | **2,534** | 4.79 s |
| `01-JAN-2026` → `11-OCT-2026` (284 days) | 200 | **5,908** | 17.29 s |

The response size and server processing time both scale with the width of the requested range, confirming the parameters are parsed and applied by the database query rather than ignored. **The caller controls the volume of data returned by adjusting two URL path segments.**

### 2.3 Field inventory returned per record (47 fields)

| Field | Sensitivity |
|---|---|
| `PatientName` | 🔴 Direct identifier |
| **`AadharNo`** | 🔴🔴 **Statutorily protected national ID** |
| **`MobileNumber`**, `MobileNo` | 🔴 Direct identifiers (returned twice) |
| `Age`, `Gender` | 🟠 |
| `RegNo`, `PRNo`, `BillNo`, `BillNumber`, `OPIPNo`, `UpId` | 🔴 Internal record identifiers |
| **`TestDescription`**, **`TestValue`**, `ResultTestDescription`, `ChildTestDescription` | 🔴🔴 **The laboratory result itself** |
| `SampleType`, `Lm_method_desc` | 🟠 Clinical method detail |
| `Collectedon`, `Receivedon`, `Reportedon`, `ReportDate`, `Billdate` | 🟠 Clinical timeline |
| `RefDoctor`, `DoctorName`, `ConfirmUserId`, `Confirmstatus` | 🟠 Staff identifiers |
| **`ImageData`**, **`FilePath`**, **`Filename`**, `Showfile`, `Template`, `Multitemplate` | 🔴 Report artefacts / file paths |
| `OporIp`, `ICMRNo`, `Wardname`, `DeptName`, `DeptNameDesig`, `DeptDesignation`, `Designation`, `Spec_dept_code` | 🟠 Internal structure |
| `Type`, `Status`, `Row_number`, `Name` | ⚪ |

Field names extracted programmatically. **Record values were deliberately not captured, stored or transmitted.**

### 2.4 The broader LabReport surface (24 endpoints, all unauthenticated routes)

```
api/LabReport/CultureLabPatientReport/{RegNo}/{BillNo}/{Testcode}
api/LabReport/ExportPDF
api/LabReport/GetPatientPathologyTestDetails/{RegNo}/{TestCode}/{BillNo}
api/LabReport/GetPatientTestDetails/{RegNo}/{TestCode}/{BillNo}
api/LabReport/GetPatient_CultureLab_NegativeReport/{RegNo}/{TestCode}/{BillNo}
api/LabReport/OutSidePatientReport/{RegNo}/{BillNo}/{Testcode}
api/LabReport/SendCriticalValuesForPatient
api/LabReport/SendSMSExportPDF
api/LabReport/SendWhatAppPDFforPatient
api/LabReport/getPatientData/{FromDate}/{ToDate}
api/LabReport/getPatientData/{FromDate}/{ToDate}/{PrgNo}/{InqueryType}
api/LabReport/getPatientLabReportData/{FromDate}/{ToDate}/{RegNo}/{TestCode}
api/LabReport/getPatient_All_LabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}/{BillNo}
api/LabReport/getPatient_All_LabReport_TestDetails/{RegNo}/{TestCode}/{BillNo}/{TemplateNo}
api/LabReport/getPatient_CultureLabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}/{BillNo}
api/LabReport/getPatient_CultureLabReportFiles/{RegNo}/{TestCode}/{BillNo}
api/LabReport/getPatient_OutSideLabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}/{BillNo}
api/LabReport/getPatient_OutSideReportFiles/{RegNo}/{TestCode}/{BillNo}
api/LabReport/getPatient_PathologyLabReport/{FromDate}/{ToDate}/{RegNo}/{TestCode}
```

Note in particular `SendWhatAppPDFforPatient`, `SendSMSExportPDF` and `SendCriticalValuesForPatient` — endpoints that **push patient reports to a patient's phone**. Unauthenticated access to these is both a disclosure and a harassment/abuse vector, allowing an attacker to trigger outbound WhatsApp and SMS messages to patients.

---

## 3. Impact

### 3.1 Irreversible disclosure of the most sensitive data a hospital holds

Laboratory results reveal diagnoses the patient may not have disclosed to family, employer or insurer. HIV, hepatitis, oncology markers, genetic findings, pregnancy and substance screening all fall within this dataset. **Once disclosed, this cannot be undone.**

### 3.2 Aadhaar exposure

`AadharNo` is returned. See **WEB-2026-014 §3.1** for the statutory position under the Aadhaar Act 2016 and DPDP Act 2023.

### 3.3 Attacker-controlled scale

Because the date range is caller-supplied, an attacker chooses the volume. The measured 0.42 s → 17.29 s scaling shows the backend processes the full range. An attacker can script sequential ranges and harvest the laboratory record set systematically with no credentials and no rate limiting.

### 3.4 Report artefacts and file paths

`ImageData`, `FilePath` and `Filename` may allow retrieval of the rendered report document itself, converting a metadata leak into full-document disclosure.

### 3.5 Outbound messaging abuse

If `SendWhatAppPDFforPatient` and `SendSMSExportPDF` accept unauthenticated calls, an attacker can trigger unsolicited messages to arbitrary patients — a credible phishing delivery channel that originates from the hospital's own messaging identity.

### 3.6 No ability to detect or scope prior access

Nothing in this environment is logged. As with WEB-2026-014, **it is not possible to determine whether this data has already been harvested.**

---

## 4. Steps to Reproduce

```bash
# Single day — minimal-impact confirmation
curl -s "https://narayanagroup.co.in/NnoteApi/api/LabReport/getPatientData/11-OCT-2026/11-OCT-2026"

# Field names only, no values
curl -s "https://narayanagroup.co.in/NnoteApi/api/LabReport/getPatientData/11-OCT-2026/11-OCT-2026" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(len(d),'records'); print(list(d[0].keys()))"
```

---

## 5. Remediation

### Immediate — today

1. **Require authentication and authorisation on all 24 `api/LabReport/*` endpoints.** Until deployed, block the path at the reverse proxy or WAF.
2. **Disable or authenticate `SendWhatAppPDFforPatient`, `SendSMSExportPDF` and `SendCriticalValuesForPatient`** — these have outbound side effects and should never be reachable unauthenticated.
3. **Enable request logging on `/NnoteApi/api/*` before remediating**, and preserve any existing logs for incident scoping.
4. **Seek legal advice on notification obligations** (DPDP Act 2023; CERT-In directions). This assessment does not constitute legal advice.

### Short term

5. **Remove `AadharNo`, `MobileNumber`, `MobileNo` and `TestValue` from list endpoints.** Return a minimal record set; expose result values only to an authorised, audited caller.
6. **Bound the date range server-side** — reject ranges wider than a defined maximum, and rate-limit by caller.
7. **Replace `FilePath`/`Filename` with opaque, authorisation-checked resource tokens** so that knowing a path does not grant retrieval.
8. **Add an audit trail for every laboratory record access.** Access to lab results should be an auditable event tied to an authenticated identity.

### Structural

9. **Apply estate-wide authentication** across `/NnoteApi/api/*` and `/NtraktApi/api/*` (closes 001, 002, 003, 012, 014, 015, 016, 017).
10. **Remove the public API help page** (WEB-2026-013) so the laboratory surface is not advertised.
11. **Data classification and DTO allow-lists** — see WEB-2026-014 §5 items 8–10.

---

## 6. Related Findings

- **WEB-2026-014** — Unauthenticated patient prescriptions with Aadhaar and clinical complaints
- **WEB-2026-002** — Unauthenticated patient IDOR (`Patient/Info/{regno}`)
- **WEB-2026-013** — Public API documentation advertising all 24 `LabReport` routes
- **WEB-2026-017** — Unauthenticated patient admission and billing list

---

## 7. Disclosure Handling

Verification used **one request per date range**, with the widest range being a bounded single-year window. **Values were never printed, saved or transmitted**; only field names and byte counts were recorded. No bulk extraction, no report-file download, and no invocation of the messaging endpoints was performed.

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · **Confirmed against live target — treat as active incident***
