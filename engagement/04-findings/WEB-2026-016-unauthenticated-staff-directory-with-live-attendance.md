# WEB-2026-016 — Unauthenticated Staff Directory With Live Attendance (`InTime`/`OutTime`), Date of Birth and Mobile Numbers

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-016 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/employee/hodlist/{id}` |
| **Status** | **Confirmed (Live Target) — ACTIVE DATA EXPOSURE** |
| **Records Observed** | 17 records from a single unauthenticated request |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

`/NtraktApi/api/employee/hodlist/{id}` returns a **complete staff roster** with no authentication. A single request returned **17 employee records**, each containing the employee's name, employee number, date of joining, department, designation, **gender**, **date of birth**, **mobile number**, and — distinctively — **`InTime` and `OutTime`, the employee's live attendance punch times for the day**.

The `{id}` parameter is enumerable: different values return different record sets (`3334024` → 17 records; `45605236` → 1 record), and employee identifiers were observed in the 8-digit range (e.g. `45605236`).

This is a **second, independent unauthenticated staff-data endpoint**, separate from `api/User/Info/{id}` (WEB-2026-002 / WEB-2026-012). It confirms that the missing authentication is controller-wide rather than endpoint-specific.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The request

```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/employee/hodlist/3334024"
```

**Result:** HTTP `200 OK` — **5,655 bytes** — no authentication required.

### 2.2 Response shape

```
RECORDS: 17
FIELDS: EmployeeSlno, EmployeeId, EmployeeNo, DateOfJoining, DepartmentSlno,
        Department, DesignationSlno, Designation, EmployeeName, Gender,
        DateOfBirth, MobileNo, InTime, OutTime
```

### 2.3 Field sensitivity

| Field | Sensitivity |
|---|---|
| `EmployeeName` | 🔴 Direct identifier |
| `MobileNo` | 🔴 Direct identifier |
| `DateOfBirth` | 🔴 Direct identifier — irreversible |
| `Gender` | 🟠 |
| **`InTime`, `OutTime`** | 🔴🔴 **Live physical presence — security relevant** |
| `EmployeeNo`, `EmployeeId`, `EmployeeSlno` | 🔴 Internal identifiers |
| `DateOfJoining` | 🟠 |
| `Department`, `DepartmentSlno` | 🟠 Internal key |
| `Designation`, `DesignationSlno` | 🟠 Internal key |

Field names extracted programmatically. **Record values were not captured, stored or transmitted.**

### 2.4 Enumeration behaviour

| `{id}` | HTTP | Bytes | Records |
|---|---|---|---|
| `1` | 200 | 11 | 0 |
| `100` | 200 | 11 | 0 |
| `1,000` | 200 | 11 | 0 |
| `10,000` | 200 | 11 | 0 |
| `100,000` | 200 | 11 | 0 |
| `1,000,000` | 200 | 11 | 0 |
| **`3,334,024`** | 200 | **5,655** | **17** |
| **`45,605,236`** | 200 | 347 | 1 |

The endpoint never returns an error or an authentication challenge — it returns `{"data":[]}` for unknown identifiers and full records for valid ones. **This is a clean existence oracle as well as a data leak.**

---

## 3. Impact

### 3.1 Physical security exposure

`InTime` and `OutTime` reveal **which staff are physically on site at any given moment**, and when specific individuals arrive and leave. This supports:

- **Burglary and physical intrusion** — an attacker can determine when a department is unstaffed, or when a specific individual is working late.
- **Targeted stalking or harassment** of a named employee, using their known shift pattern.
- **Social engineering timing** — impersonating a colleague or manager at a moment when the real one is known to be off-site.

### 3.2 Identity fraud and account takeover

Name + date of birth + mobile number + employee number is a strong identity-fraud kit, and is frequently sufficient to defeat knowledge-based authentication at banks and telecoms providers. Date of birth in particular is a common password component and security-question answer.

### 3.3 High-fidelity spear-phishing

Knowing an employee's department, designation, joining date and live attendance pattern allows an attacker to craft a message that is extremely difficult to distinguish from a genuine internal communication — for example contacting a department while its head is known to be absent, purporting to be that head.

### 3.4 Reconnaissance for privilege escalation

`DepartmentSlno` and `DesignationSlno` are internal database keys (see WEB-2026-012). Combined with the department and designation names, an attacker can map the organisational structure and identify high-value targets — payroll staff, system administrators, approval authorities.

### 3.5 Scale

The endpoint returns **whole teams per request**, not one record at a time. Harvesting the staff directory is dramatically faster here than via `User/Info/{id}`, which is single-record.

---

## 4. Steps to Reproduce

```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/employee/hodlist/3334024" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(len(d),'records'); print(list(d[0].keys()))"
```

Observed: `17 records` with the field list in §2.2.

---

## 5. Remediation

### Immediate

1. **Require authentication on `/NtraktApi/api/employee/*`.**
2. **Remove `DateOfBirth`, `MobileNo`, `InTime` and `OutTime` from the response.** No roster-listing caller requires an employee's date of birth or live punch times.
3. **Strip `DepartmentSlno` and `DesignationSlno`** — internal surrogate keys must not cross the API boundary (see WEB-2026-012).

### Short term

4. **Add authorisation, not just authentication.** A caller should see only their own record, or records within their authorised management scope.
5. **Return a consistent response for unknown identifiers.** Distinguishing "no such employee" from "no access" turns the endpoint into an enumeration oracle.
6. **Rate-limit and log** all directory queries. Staff-directory access should be an auditable event.

### Structural

7. **Apply estate-wide authentication** across both APIs (closes 001, 002, 003, 012, 014, 015, 016, 017).
8. **Adopt response DTOs with field allow-lists**, and add an automated test that fails the build if sensitive fields appear in a response.

---

## 6. Related Findings

- **WEB-2026-002** — Unauthenticated staff PII IDOR (`User/Info/{id}`)
- **WEB-2026-012** — `User/Info` schema expansion exposing internal surrogate keys
- **WEB-2026-013** — Public API documentation advertising this endpoint
- **WEB-2026-017** — Unauthenticated patient admission and billing list

---

## 7. Disclosure Handling

Verification used **one request per identifier across eight identifiers**. Field names and record counts were recorded; **record values were not captured, stored or transmitted.** No bulk enumeration was performed.

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
