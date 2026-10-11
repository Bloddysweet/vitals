# WEB-2026-014 — Unauthenticated Bulk Retrieval of Patient Prescriptions Including Aadhaar Numbers, Mobile Numbers and Clinical Complaints

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-014 |
| **Severity** | **CRITICAL** |
| **CVSS v3.1 Score** | **9.1** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information to an Unauthorized Actor), CWE-312 (Cleartext Storage of Sensitive Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control · A02:2021 — Cryptographic Failures |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/Prescription/GetPatientPrescription/{type}` |
| **Status** | **Confirmed (Live Target) — ACTIVE DATA EXPOSURE** |
| **Data Categories** | Patient identifiers, **Aadhaar numbers**, mobile numbers, date of birth, gender, clinical complaints, full prescription detail |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

The patient-facing API endpoint `/NnoteApi/api/Prescription/GetPatientPrescription/{type}` requires **no authentication of any kind**. A single unauthenticated `GET` request returns **39 complete prescription records**, each containing the patient's name, date of birth, age, gender, mobile number, **Aadhaar number**, admission date, treating department and doctor, **the presenting clinical complaint**, and the full prescribed-drug detail (molecule, brand, dosage, regimen, duration, quantity).

This is not a single-record leak. It is **bulk retrieval of a live clinical dataset**, and it includes **Aadhaar** — India's national identity number, which is subject to specific statutory protection.

**This finding represents active, ongoing disclosure of regulated personal data and should be treated as a live incident, not a report item.**

---

## 2. Technical Evidence (Live Capture)

### 2.1 The request

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Prescription/GetPatientPrescription/1"
```

**Result:** HTTP `200 OK` — **22,951 bytes** — no authentication header, no session cookie, no token, no redirect.

### 2.2 Response structure

```json
{ "data": [ ... 39 items ... ] }
```

### 2.3 Field inventory returned per record (39 records)

| Field | Category | Sensitivity |
|---|---|---|
| `Name` | Identity | 🔴 Direct identifier |
| **`Aadhar`** | National ID | 🔴🔴 **Statutorily protected identifier** |
| `DOB` | Identity | 🔴 Direct identifier |
| `Age`, `AgeType` | Identity | 🟠 |
| `Gender` | Identity | 🟠 |
| **`MobileNo`** | Contact | 🔴 Direct identifier |
| `RegNo` | Hospital registration no. | 🔴 Internal identifier |
| `IPNo` | Inpatient number | 🔴 Internal identifier |
| `AdmitDate` | Clinical | 🟠 |
| `Department`, `DeptCode` | Clinical | 🟠 |
| `DoctorCode`, `DoctorName` | Clinical | 🟠 |
| **`ChiefComplaints`** | Clinical notes | 🔴🔴 **Free-text clinical narrative** |
| `Content`, `TypeDesc`, `TypeId` | Prescription | 🟠 |
| `molecuelid`, `molecueldesc` | Drug | 🟠 Prescribed molecule |
| `brandid`, `brandname` | Drug | 🟠 Prescribed brand |
| `itemcode`, `itemdesc` | Drug | 🟠 |
| `regimenid`, `regimendosage` | Drug | 🟠 Dosage |
| `diettypeid`, `diettypedesc` | Clinical | 🟠 |
| `durationid`, `durationtype` | Drug | 🟠 |
| `startdurationid`, `startdurationtype` | Drug | 🟠 |
| `prescp_id`, `userid`, `Qty` | Administrative | 🟠 |

Field names were extracted programmatically. **Record values were deliberately not captured, stored or transmitted** during verification.

### 2.4 Corroborating exposure

The same controller exposes `api/Prescription/savepatientprescription` and `api/Prescription/PatientPrescriptionList/{Date}/{DocCode}`, confirming that the prescription subsystem is reachable in its entirety without authentication. `PatientPrescriptionList/{Date}/{DocCode}` allows retrieval of every prescription issued by a given doctor on a given date — meaning the dataset can be walked doctor-by-doctor and day-by-day.

---

## 3. Impact

### 3.1 Aadhaar exposure — statutory and regulatory

`Aadhar` is present in the response. Aadhaar numbers are governed by the **Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and Services) Act, 2016**, which restricts collection, use and disclosure, and by the **Digital Personal Data Protection Act, 2023**, which classifies Aadhaar-linked personal data as sensitive and imposes obligations on data fiduciaries.

Unauthenticated exposure of Aadhaar numbers at scale is materially more serious than exposure of ordinary contact details. It creates a **permanent, non-revocable identifier** for every affected patient — a phone number can be changed, an Aadhaar number cannot.

### 3.2 Clinical harm

`ChiefComplaints` is free-text clinical narrative. Combined with name, age, gender, doctor and department, it permits reconstruction of a patient's presenting condition. Exposure of a person's medical complaints carries risks of **discrimination, stigma, and loss of employment or insurance prospects** — harms that cannot be remediated after the fact.

### 3.3 Identity fraud and financial crime

Name + Aadhaar + mobile + date of birth is a **complete identity-fraud kit**. This combination is sufficient to pass knowledge-based authentication at banks, telecoms providers and government portals, and to conduct SIM-swap and account-takeover attacks against the affected individuals.

### 3.4 Targeted phishing at scale

With patient name, mobile number, treating department, doctor and admission date, an attacker can send convincing, individually-addressed messages — *"Regarding your admission on 4 October under Dr. X, please settle your outstanding bill at [link]"* — with a hit rate far above generic phishing.

### 3.5 Integrity risk

The presence of `api/Prescription/savepatientprescription` in the same unauthenticated surface means prescription data is not merely readable but potentially **writable**. Malicious alteration of prescribed dosage or brand is a direct patient-safety risk.

### 3.6 Acknowledged likelihood of prior exploitation

Because these endpoints require no credentials and are documented on a public help page (**WEB-2026-013**), and because **nothing in this environment is logged** (see the master report), it is **not possible to determine whether this data has already been harvested**. The correct working assumption is that it may have been.

---

## 4. Steps to Reproduce

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Prescription/GetPatientPrescription/1" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(len(d),'records'); print(list(d[0].keys()))"
```

Observed: `39 records` with the field list in §2.3.

---

## 5. Remediation

### Immediate — today

1. **Require authentication and authorisation on the entire `/NnoteApi/api/Prescription/` controller.** Until that is deployed, take the endpoint offline at the reverse proxy or WAF rather than leaving it live.
2. **Preserve logs before remediating.** Enable request logging on `/NnoteApi/api/*` and retain what already exists. If this data has been harvested, the access logs are the only way to know.
3. **Assess notification obligations.** Exposure of Aadhaar numbers and clinical data may trigger obligations under the **DPDP Act 2023** and **CERT-In** incident-reporting directions. The client should obtain legal advice promptly — this assessment does not constitute legal advice.

### Short term

4. **Remove `Aadhar` from every API response.** No caller in this application requires the Aadhaar number to render a prescription. If a downstream process needs it, that process should be authenticated, audited and justified.
5. **Remove `MobileNo` and `ChiefComplaints`** unless a specific, authorised caller requires them.
6. **Implement response DTOs.** Serialising the ORM entity is what placed 35 fields — including Aadhaar — into an unauthenticated response.
7. **Scope data by caller.** An authenticated caller should retrieve only records they are authorised to see, not all records for a given `{type}`.

### Structural

8. **Apply a single authentication filter across `/NnoteApi/api/*` and `/NtraktApi/api/*`.** This one control closes WEB-2026-001, 002, 003, 012, 014, 015, 016 and 017 simultaneously.
9. **Add an automated test that fails if any endpoint returns a field from a sensitive-data blocklist** (`Aadhar`, `AadharNo`, `MobileNo`, `MobileNumber`, `ChiefComplaints`, `TestValue`, `DateOfBirth`).
10. **Classify data at design time.** Aadhaar and clinical narrative should be tagged as restricted in the data model so that exposure is impossible by default rather than prevented by review.

---

## 6. Related Findings

- **WEB-2026-002** — Unauthenticated IDOR on patient data (`Patient/Info/{regno}`) — the single-record precursor to this bulk exposure
- **WEB-2026-013** — Public API documentation that advertises this endpoint
- **WEB-2026-015** — Unauthenticated laboratory results by date range (same estate, same root cause)
- **WEB-2026-016** — Unauthenticated staff directory with live attendance
- **WEB-2026-017** — Unauthenticated patient admission and billing list

---

## 7. Disclosure Handling

Verification was performed with a **single unauthenticated request per endpoint**. Response **field names** were extracted programmatically; **record values were not captured, stored, or transmitted**, and no bulk extraction was performed. No data was written, modified or exfiltrated.

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · **Confirmed against live target — treat as active incident***
