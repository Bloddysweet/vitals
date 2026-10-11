# WEB-2026-020 — Unauthenticated Staff Duty Roster: 170 Records With Shift Times, Work Location and Mobile Numbers

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-020 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NnoteApi/api/Roster/Departments` and 7 sibling `api/Roster/*` endpoints |
| **Status** | **CONFIRMED (Live Target) — ACTIVE DATA EXPOSURE** |
| **Scale** | **170 records · 32 fields per record · 90,382 bytes** |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

`/NnoteApi/api/Roster/Departments` returns the organisation's **staff duty roster** with no authentication: **170 records totalling 90 KB**, each containing **32 fields**.

The roster identifies each employee by name and ID, and records **which department they are assigned to, which shift they are working, on which dates, at what times, and at which work location** — together with their gender and mobile number.

This is distinguishable from the staff directory in WEB-2026-016 (`employee/hodlist`). A directory says *who works here*; a roster says **who is on duty, where, and when**. That combination is materially more useful for physical intrusion, targeted social engineering and executive targeting.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The request

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Roster/Departments"
```

**Result:** HTTP `200 OK` — **90,382 bytes** — no authentication required.

### 2.2 Response shape

```
data:
  [list: 170 records]
```

### 2.3 Complete field inventory (32 fields)

| Group | Fields |
|---|---|
| **Identity** | `Name`, `EmpId`, `AlternateEmpId`, `Gender`, 🔴 **`Mobile`** |
| **Assignment** | `Department`, `DepartmentCode`, `Designation`, `ServiceCode`, `ServiceName`, 🔴 **`WorkLocation`**, `officeTypeSlno`, `DeptTypeSlno` |
| **Schedule** | 🔴 `ShiftDate`, `ShiftTime`, `ShiftType`, `ShiftSlno`, `ShiftSlNo`, `FromDate`, `ToDate` |
| **Attendance** | 🔴 `InTime`, `OutTime`, `inDate` |
| **System** | `UserId`, `Code`, `ShowName`, `Type` |
| **Free text** | `Remarks`, `Content`, `Header`, `Footer`, `itemDetails` |

**Field names extracted programmatically. No record values were captured, stored or transmitted.**

### 2.4 The wider Roster surface (8 endpoints, all unauthenticated routes)

```
api/Roster/Alternate/Employees/{empid}
api/Roster/Departments
api/Roster/DutyDates/Change          ← write endpoint
api/Roster/DutyDates/{empid}
api/Roster/DutyTimes/{empid}/{dutydate}
api/Roster/Employee/Shift/{empid}
api/Roster/Schedule
api/Roster/Schedule/N
```

`api/Roster/DutyDates/Change` is a **write endpoint** and is therefore also in scope for WEB-2026-018 — an attacker who can change duty dates can alter the recorded staffing of a ward.

---

## 3. Impact

### 3.1 Physical security — the primary concern

A roster discloses the **staffing level of every department at every hour**. This supports:

- **Timing an intrusion** for a period when a target department is minimally staffed
- **Identifying unattended areas** — a ward, laboratory, pharmacy or cash-handling office with no assigned staff
- **Targeting the pharmacy.** `api/nPharmacy/getpharmcyindent/{deptcode}` and `api/nPharmacy/getdeptcode` (40 records, confirmed live) sit in the same API. Combining pharmacy department codes with roster coverage identifies when controlled-drug storage is least observed.
- **Night-shift targeting**, where skeleton staffing is typical

### 3.2 Targeted social engineering

`WorkLocation` plus `ShiftTime` tells an attacker **where a named employee is and whether they are on duty**. An impersonation call or visit can be timed to a moment when the real employee is known to be elsewhere — defeating the natural verification step of "let me check with them."

### 3.3 Executive and key-holder targeting

`Designation` and `ServiceName` allow filtering for administrators, finance staff, and those holding keys or approval authority. Combined with `Mobile` and the shift pattern, this supports highly targeted pretexting.

### 3.4 Identity fraud

Name + mobile + employee ID + department supports account-recovery attacks against the employee's other accounts, particularly where the mobile number is used for OTP delivery.

### 3.5 Corroboration of WEB-2026-016

Two independent, unauthenticated endpoints now expose staff data with live attendance (`employee/hodlist` → `InTime`/`OutTime`; `Roster/Departments` → `InTime`/`OutTime` + `ShiftTime`). This confirms the absence of authentication is **systemic across controllers**, which strengthens the case for the single estate-wide fix recommended throughout this report.

---

## 4. Steps to Reproduce

```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Roster/Departments" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print(len(d),'records;',len(d[0]),'fields')
print(', '.join(d[0].keys()))
"
```

Observed: `170 records; 32 fields`.

---

## 5. Remediation

### Immediate

1. **Require authentication on all `api/Roster/*` endpoints.**
2. **Remove `Mobile` from roster responses.** A roster does not require staff mobile numbers.
3. **Restrict `WorkLocation`, `ShiftTime`, `InTime` and `OutTime`** to callers with an explicit operational need — ideally only the roster owner and their manager.
4. **Authenticate and authorise `api/Roster/DutyDates/Change` immediately** (see WEB-2026-018).

### Short term

5. **Strip internal keys** (`officeTypeSlno`, `DeptTypeSlno`, `ShiftSlno`) from responses.
6. **Scope by caller** — an employee should retrieve their own roster entry and, if a manager, their team's; not the whole organisation.
7. **Log and rate-limit** roster queries. Bulk retrieval of staffing levels is a reconnaissance precursor and should be alertable.

### Structural

8. **Apply estate-wide authentication** (closes 001, 002, 003, 012, 014, 015, 016, 017, 018, 019, 020).
9. **Adopt response DTOs with field allow-lists.**

---

## 6. Related Findings

- **WEB-2026-016** — Unauthenticated staff directory with live attendance (`employee/hodlist`) — the companion exposure
- **WEB-2026-012** — Internal surrogate keys exposed in staff responses
- **WEB-2026-018** — Unauthenticated write endpoints, including `Roster/DutyDates/Change`
- **WEB-2026-013** — Public API documentation advertising all 8 `Roster` routes

---

## 7. Disclosure Handling

Verification used **a single unauthenticated request**. Field names and the record count were recorded; **no record values were captured, stored or transmitted.** The temporary response file was deleted immediately after processing.

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
