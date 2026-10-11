# WEB-2026-017 — Unauthenticated Patient Admission, Billing and Health-Worker Consultation List

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-017 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/HealthWorker/List`, `api/HealthWorker/List/{regno}` |
| **Status** | **Confirmed (Live Target) — ACTIVE DATA EXPOSURE** |
| **Records Observed** | 17 records from a single unauthenticated request |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

`/NnoteApi/api/HealthWorker/List` requires no authentication and returns **17 patient records** combining identity, clinical timeline, consultation detail, billing and insurer information.

Each record includes the patient's name, age, sex, **registration number (`Regno`)** and **inpatient number (`Ipno`)**, admission date, discharge date, consultation date, the assigned health worker, **the billed amount**, the patient's **company/insurer**, bill number and date, and the user account that created the entry.

The `Regno` and `Ipno` values returned by this endpoint are **directly usable as input to the other unauthenticated patient endpoints** documented in this report — making this a chaining primitive that turns scattered single-record leaks into systematic enumeration.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The request

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/HealthWorker/List"
```

**Result:** HTTP `200 OK` — **6,537 bytes** — no authentication required.

### 2.2 Response shape

```
data:
  [list: 17 items]
    Regno, Ipno, Name, Age, AgeType, Sex, Adate, Ddate, ConsultationDate,
    HealthWorkerName, Amount, Company, BillNo, BillDate, UserId, UserName, Type
```

### 2.3 Field sensitivity

| Field | Sensitivity |
|---|---|
| `Name` | 🔴 Direct identifier |
| `Age`, `Sex` | 🟠 |
| **`Regno`** | 🔴🔴 **Chaining key** — feeds `Patient/Info/{regno}`, `Patient/AdmissionDetails/{regno}`, `Prescription/GetAdmissionDetails/{regno}/{opatientid}`, `LabReport/GetPatientTestDetails/{RegNo}/...` |
| **`Ipno`** | 🔴🔴 **Chaining key** — inpatient identifier |
| `Adate`, `Ddate` | 🟠 Admission / discharge dates |
| `ConsultationDate` | 🟠 |
| `HealthWorkerName` | 🟠 Staff identifier |
| **`Amount`** | 🔴 Financial — billed value |
| **`Company`** | 🔴 Insurer / corporate sponsor — reveals employer or insurance provider |
| `BillNo`, `BillDate` | 🔴 Billing identifiers, usable against `Investigation/Cancel/Bill/{regno}/{billno}/{cbillno}` |
| `UserId`, `UserName` | 🟠 Staff account identifiers — supports account targeting |
| `Type` | ⚪ |

Field names extracted programmatically. **Record values were not captured, stored or transmitted.**

---

## 3. Impact

### 3.1 Chaining primitive — the most serious aspect

This endpoint does not merely leak 17 records. It **supplies the identifiers needed to query every other patient endpoint systematically**:

```
HealthWorker/List  →  Regno
                        ├─→ Patient/Info/{regno}
                        ├─→ Patient/AdmissionDetails/{regno}
                        ├─→ Patient/ConsultDetails/{regno}
                        ├─→ Patient/IsInPatient/{regno}
                        ├─→ Prescription/GetAdmissionDetails/{regno}/{opatientid}
                        └─→ LabReport/GetPatientTestDetails/{RegNo}/{TestCode}/{BillNo}
```

An attacker no longer needs to guess registration numbers. They can enumerate the patient population from this list and then retrieve the full clinical record for each.

### 3.2 Financial and insurance profiling

`Amount`, `Company` and `BillNo` reveal what each patient was billed and who is paying — insurer, employer, or self-funded. This supports:

- **Insurance fraud** — knowledge of policy and treatment value.
- **Targeted financial phishing** — referencing a real bill number and amount.
- **Socio-economic profiling** — identifying wealthy or well-insured patients for extortion.

### 3.3 Clinical timeline reconstruction

`Adate`, `Ddate` and `ConsultationDate` establish when a person was hospitalised. Combined with `Company` and `Amount`, this allows inference about the seriousness and cost of treatment even without a diagnosis field.

### 3.4 Staff targeting

`HealthWorkerName`, `UserId` and `UserName` expose staff identities and their account names, supporting the social-engineering and account-takeover attacks described in WEB-2026-016.

---

## 4. Steps to Reproduce

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/HealthWorker/List" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(len(d),'records'); print(list(d[0].keys()))"
```

Observed: `17 records` with the field list in §2.2.

---

## 5. Remediation

### Immediate

1. **Require authentication and authorisation on `api/HealthWorker/List` and `api/HealthWorker/List/{regno}`.**
2. **Note that `api/HealthWorker/Approve` is a sibling write endpoint.** If it is also unauthenticated, an attacker may be able to approve health-worker records. This should be verified and, if confirmed, treated as a Critical integrity finding.

### Short term

3. **Remove `Amount`, `Company`, `UserId` and `UserName` from the list response** unless a specific authorised caller requires them.
4. **Do not return internal chaining keys** (`Regno`, `Ipno`, `BillNo`) to callers who are not authorised to use them.
5. **Add authorisation scoping** so a caller retrieves only the patients within their care relationship.
6. **Log and rate-limit** all patient-list queries.

### Structural

7. **Apply estate-wide authentication** across both APIs (closes 001, 002, 003, 012, 014, 015, 016, 017).
8. **Adopt response DTOs with field allow-lists** and automated sensitive-field tests.

---

## 6. Related Findings

- **WEB-2026-002** — Unauthenticated patient IDOR (`Patient/Info/{regno}`) — the endpoint this list feeds
- **WEB-2026-014** — Unauthenticated patient prescriptions with Aadhaar
- **WEB-2026-015** — Unauthenticated laboratory results by date range
- **WEB-2026-016** — Unauthenticated staff directory with live attendance
- **WEB-2026-013** — Public API documentation advertising this endpoint

---

## 7. Disclosure Handling

Verification used **a single unauthenticated request**. Field names and the record count were recorded; **record values were not captured, stored or transmitted.**

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
