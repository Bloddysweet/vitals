# WEB-2026-012 — Expansion of Unauthenticated Staff PII Response (13 → 28 Fields) Now Leaking Internal Database Surrogate Keys

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-012 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-213 (Exposure of Sensitive Information Due to Incompatible Policies), CWE-639 (Authorization Bypass Through User-Controlled Key) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/User/Info/{id}` |
| **Status** | Confirmed (Live Target) — **worsened since WEB-2026-002 was recorded** |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

WEB-2026-002 recorded that `/NtraktApi/api/User/Info/{id}` returns **13 fields** of staff PII with no authentication. A re-test in Phase 2 shows the response has **expanded to 28 fields — more than double** — and now includes:

- Additional personal data: `Gender`, `PhoneNo`, `Status`, `StatusDate`, `StatusType`, `UserStatus`
- **Internal infrastructure detail: `UserHostAddress`** (server-side host address)
- A parallel internal identifier: `BioEmpNo` (biometric/attendance employee number)
- **Four internal Oracle database surrogate keys: `DepartmentSlno`, `DesignationSlno`, `OfficeTypeSlno`, `BranchSlno`**

The endpoint is still fully unauthenticated. The response has therefore become **more sensitive, not less**, and it now publishes the primary-key values of the organisation's internal reference tables.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The endpoint still requires no authentication

```bash
curl -s -i "https://narayanagroup.co.in/NtraktApi/api/User/Info/3334024" | head -n 12
```

**Live Response:** HTTP `200 OK`, no `WWW-Authenticate` challenge, no redirect to a login page, and no session cookie required. The login pages continue to set `set-cookie: 0`, confirming **no authentication control has been added anywhere in the estate since Phase 1**.

### 2.2 Fields newly exposed since WEB-2026-002

| Field | Example Value | Why It Matters |
|---|---|---|
| `Gender` | `M` | Personal characteristic; enables demographic profiling |
| `PhoneNo` | *(second contact number)* | A **second** contact number beyond the `MobileNo` already exposed |
| `OfficeType` | `HOSPITAL` | Reveals organisational structure |
| `OfficeTypeSlno` | `10` | **Internal DB surrogate key** for the office-type reference table |
| `Status` | `1` | Employment status |
| `StatusDate` | *(date)* | Effective date of employment status |
| `StatusType` | `ACTIVE` | Confirms current employment |
| `UserStatus` | *(value)* | Account state — useful for targeting active accounts |
| `UserHostAddress` | *(host address)* | **Internal infrastructure detail** |
| `BioEmpNo` | `3334024` | Biometric/attendance identifier — a second pivot key into the attendance subsystem |
| `DepartmentSlno` | `72` | **Internal DB surrogate key** for the department reference table |
| `DesignationSlno` | `157` | **Internal DB surrogate key** for the designation reference table |
| `BranchSlno` | `456` | **Internal DB surrogate key** for the branch reference table |

### 2.3 Full confirmed record for one employee

Retrieved unauthenticated in a single GET request:

| Attribute | Value |
|---|---|
| Name | **Yepuri N V K Meerendra Balu** |
| Employee No | `NES3334024` |
| Mobile | *(redacted — confirmed present)* |
| Date of Birth | **15/AUG/1991** |
| Date of Joining | **01/MAY/2025** |
| Department | `HARDWARE` |
| Designation | `INCHARGE` |
| Branch | `PRO-GHA-HL` |
| Gender | `M` |
| Status | `ACTIVE` |
| Employee Photo | **49,276-byte Base64-encoded JPEG** (Canon CanoScan EXIF metadata) |

---

## 3. Why the Surrogate Keys Matter

This is the significant part of the finding. `DepartmentSlno`, `DesignationSlno`, `OfficeTypeSlno` and `BranchSlno` are **not business identifiers** — they are the internal numeric primary keys of the backend Oracle reference tables.

Exposing them converts the API into a **structure reconnaissance tool**:

- **Precise enumeration.** An attacker can walk `BranchSlno` 1…N and `DepartmentSlno` 1…N to reconstruct the complete internal organisational chart — every branch, department and designation in the group — without ever guessing a name.
- **Write-path targeting.** Any endpoint that accepts these values as parameters (for example a record update or a create/transfer action) can be addressed **directly by key**, bypassing any name-based validation.
- **Cross-reference correlation.** Because the same keys are returned by other endpoints, records from different subsystems can be joined into a single profile of an employee.
- **Injection surface.** Numeric key parameters are frequently concatenated into dynamic SQL elsewhere in an application even when the read path is parameterised. Their exposure tells an attacker exactly which numeric parameters exist to probe.

---

## 4. Impact

- **Aggregated insider profile.** A single unauthenticated request now yields name, date of birth, gender, two phone numbers, employee number, biometric ID, employment dates, department, designation, branch, employment status, account status, internal host address and a photograph.
- **High-fidelity social engineering.** Date of birth, gender, join date, designation and a staff photograph are exactly the credentials a caller needs to impersonate HR or IT convincingly. The photograph in particular makes a pretexting call to a colleague highly credible.
- **Physical and biometric targeting.** `BioEmpNo` identifies the employee within the biometric attendance system — the system that governs physical access to hospital premises.
- **Enumeration at scale.** `Assignee/{id}` was already confirmed enumerable (`{1..5}` tested). Combined with the surrogate keys, the entire staff directory of the group is retrievable record by record.

---

## 5. Remediation

**Immediate**

1. **Require authentication on `/NtraktApi/api/User/Info/{id}`** and re-test. This single control also closes WEB-2026-001, WEB-2026-002 and WEB-2026-003.
2. **Do not serialise whole entity objects.** Replace `return dbEntity;` with an explicit allow-list DTO containing only the fields the caller actually needs. Auto-serialising the ORM entity is what caused this schema to grow silently from 13 to 28 fields.
3. **Strip internal keys from all responses.** `DepartmentSlno`, `DesignationSlno`, `OfficeTypeSlno`, `BranchSlno` and `UserHostAddress` must never cross the API boundary.
4. **Remove `EmpPhoto`** unless a specific caller requires it. If it is required, serve it from an authenticated, authorised, rate-limited endpoint.

**Structural**

5. **Add a contract test** that fails the build when the response schema changes. The 13 → 28 growth went unnoticed precisely because nothing asserts the shape of the response.
6. **Apply the same review to every other endpoint.** `User/Info` is the one that grew; it is unlikely to be the only one serialising whole entities.
7. **Add authorisation, not just authentication.** An authenticated caller should only be able to read their own record, or records within their authorised scope — not `{id}` for any value of `id`.

---

## 6. Related Findings

- **WEB-2026-002** — Unauthenticated IDOR: staff PII + photo, and patient PHI (parent finding; this finding documents the escalation)
- **WEB-2026-001** — Client-side authentication bypass across `/Nnote/` and `/ncare/`
- **WEB-2026-005** — Raw Oracle exceptions disclosing `MOBIDB` schema and stored procedure names
- **WEB-2026-013** — Publicly exposed ASP.NET Web API help pages documenting all 104 endpoints

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
