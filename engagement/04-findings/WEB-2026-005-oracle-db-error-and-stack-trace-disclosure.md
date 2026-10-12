# WEB-2026-005 — Raw Oracle Database Exceptions (`ORA-01403`, `ORA-01722`), Internal Schema (`MOBIDB`), & Full Server Stack Trace Disclosure (`/NtraktApi/api/*`)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-005 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-209 (Generation of Error Message Containing Sensitive Information), CWE-215 (Insertion of Sensitive Information Into Debugging Code) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/Attendance/Current/{id}`, `https://narayanagroup.co.in/NtraktApi/api/User/Info/{id}` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

The production ASP.NET Web API service at `/NtraktApi/api/` has detailed exception serialization enabled (`IncludeErrorDetailPolicy.Always` or `customErrors mode="Off"`). When an invalid or non-matching parameter is supplied to unauthenticated endpoints, the server returns raw **Oracle Database error messages (`ORA-01403`, `ORA-01722`, `ORA-06512`)**, internal Oracle schema and stored procedure names (`MOBIDB.GET_USERATTENDANCE_LATEST`, `MOBIDB.GET_USERINFO`), exact PL/SQL line numbers, internal C# class/method signatures, and full Windows filesystem build paths (`d:\NtraktApi\NtraktApi\...`).

---

## 2. Technical Evidence (Live Capture)

### 2.1 Oracle `ORA-01403` & Stack Trace on `/NtraktApi/api/Attendance/Current/4029038`

```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/Attendance/Current/4029038"
```

**Live Response:**
```json
{
  "Message": "An error has occurred.",
  "ExceptionMessage": "ORA-01403: no data found\nORA-06512: at \"MOBIDB.GET_USERATTENDANCE_LATEST\", line 10\nORA-06512: at line 1\n",
  "ExceptionType": "System.Exception",
  "StackTrace": "   at NtraktApi.Models.AttendanceModel.GetUserAttendance_CurrentDay(String userid) in d:\\NtraktApi\\NtraktApi\\Models\\AttendanceModel.cs:line 173\r\n   at NtraktApi.Controllers.AttendanceController.<>c__DisplayClass2.<GetUserAttendance_CurrentDay>b__1() in d:\\NtraktApi\\NtraktApi\\Controllers\\AttendanceController.cs:line 26\r\n   at System.Threading.Tasks.Task`1.InnerInvoke()\r\n   at System.Threading.Tasks.Task.Execute()\r\n--- End of stack trace from previous location where exception was thrown ---\r\n   at System.Runtime.CompilerServices.TaskAwaiter.ThrowForNonSuccess(Task task)\r\n   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)\r\n   at NtraktApi.Controllers.AttendanceController.<GetUserAttendance_CurrentDay>d__4.MoveNext() in d:\\NtraktApi\\NtraktApi\\Controllers\\AttendanceController.cs:line 0"
}
```

### 2.2 Oracle Type Conversion Error (`ORA-01722`) & Stack Trace on `/NtraktApi/api/User/Info/1'`

```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/1'"
```

**Live Response:**
```json
{
  "Message": "An error has occurred.",
  "ExceptionMessage": "ORA-01722: invalid number\nORA-06512: at \"MOBIDB.GET_USERINFO\", line 34\nORA-06512: at line 1\n",
  "ExceptionType": "System.Exception",
  "StackTrace": "   at NtraktApi.Models.UserModel.GetUserById(String userid) in d:\\NtraktApi\\NtraktApi\\Models\\UserModel.cs:line 113\r\n   at NtraktApi.Controllers.UserController.<GetUserInfo>d__4a.MoveNext() in d:\\NtraktApi\\NtraktApi\\Controllers\\UserController.cs:line 181"
}
```

---

## 2A. Phase 2 Estate-Wide Error-Disclosure Sweep (2026-10-12)

Every endpoint returning `200` during the estate sweep (108 endpoints across both APIs) was re-requested with a single quote appended to its identifier segment, and each response was compared against a clean baseline.

**15 endpoints emitted a raw database error.** All responses were `ORA-01722: invalid number` or `ORA-06502: PL/SQL: numeric or value error: character to number conversion error`.

### 2A.1 Complete stored-procedure inventory disclosed to date

| Schema | Stored procedure | Line | Endpoint |
|---|---|---|---|
| `MOBIDB` | `GET_USERINFO` | 34 | `NtraktApi/api/User/Info/{id}` |
| `MOBIDB` | `GET_USERLEAVES` | 5 | `NtraktApi/api/Attendance/LeavesHold/{id}` |
| `MOBIDB` | `GET_USERLEAVES_ALTERNATE` | 3 | `NtraktApi/api/User/AlternateUsers/{id}` |
| `MOBIDB` | `GET_USERATTENDANCE_LATEST` | — | `NtraktApi/api/Attendance/Current/{id}` |
| `WHISPROD` | `SP_INPATIENTDETAILS` | 3 | `NnoteApi/api/Patient/AdmissionDetails/{id}` |
| `WHISPROD` | `SP_OUTPATIENTDETAILS` | 5 | `NnoteApi/api/Patient/ConsultDetails/{id}` |
| `WHISPROD` | `SP_GET_VITALDATA_API` | 5 | `NnoteApi/api/Patient/GetOPPatient/{id}` |
| `WHISPROD` | `GET_TRANS_DROPDOWN` | — | `NnoteApi/api/Patient/Transport/GetCommontronsportddl/{id}` |
| `WHISPROD` | `GET_EMP_SHIFTDATES` | 3 | `NnoteApi/api/Roster/DutyDates/{id}` |
| `WHISPROD` | `GET_EMPSHIFT_DTLS` | 3 | `NnoteApi/api/Roster/Employee/Shift/{id}` |
| `WHISPROD` | `GET_PATIENT_FEEDBACK_RPT` | 51 | `NnoteApi/api/Patient/Report/Feedback/…` |
| `WHISPROD` | `GET_DENTALPATIENT_FEEDBACK_RPT` | 42 | `NnoteApi/api/Patient/DentalReport/DentalFeedback/…` |
| `WHISPROD` | `GET_DUTYROSTER_ALTERNATE_EMP` | — | (earlier capture) |

Endpoints erroring without naming a procedure: `NnoteApi/api/Patient/Info/{id}`, `NnoteApi/api/Patient/FeedbackTeam/{id}`, `NnoteApi/api/Prescription/GetPatientPrescription/{id}` (`ORA-24338`), `NnoteApi/api/PrescriptionRpt/PatientData/{id}`, `NnoteApi/api/PrescriptionRpt/PrescriptionData/{id}`, `NnoteApi/api/Investigation/Cancel/Bill/…`.

### 2A.2 ✅ SQL injection specifically tested for and NOT found

The `ORA-01722` signature initially suggests injectable string concatenation. **It is not.** Differential testing was performed against five representative endpoints (`Patient/Info`, `Roster/Employee/Shift`, `User/Info`, `Patient/ConsultDetails`, `Patient/GetOPPatient`) using seven payloads each:

| Payload | Result |
|---|---|
| `1` (control, valid number) | no error, 0 records, 11 bytes |
| `abc` (non-numeric, **no quote**) | ORA-01722 / ORA-06502 |
| `1'` | **identical** response |
| `1' OR '1'='1` | **identical** response |
| `1' UNION SELECT NULL FROM DUAL--` | **identical** response |
| `1 AND 1=1` | **identical** response |
| `1 AND 1=2` | **identical** response |

**Every non-numeric payload produced a byte-identical response** — same error code, same byte count (e.g. 1,981 bytes for all six payloads against `Roster/Employee/Shift`).

**Three conclusions:**

1. **`abc` — containing no quote whatsoever — triggers the identical error.** The response is driven by the input being non-numeric, not by a quote breaking SQL syntax.
2. **No boolean injection.** `1 AND 1=1` and `1 AND 1=2` are indistinguishable.
3. **No union injection.** `UNION SELECT … FROM DUAL` changes nothing.

Genuine string concatenation would instead produce `ORA-00933: SQL command not properly ended`. **That error was never observed.**

**Root cause of the error:** parameters are passed to stored procedures as `VARCHAR` bind variables; the PL/SQL body performs an implicit conversion to `NUMBER`, which fails on any non-numeric input. **Parameters are bound, not concatenated.**

> **Recorded as a verified negative.** SQL injection is not present on these endpoints. Do not re-test without new evidence. This is worth stating to the client explicitly: the vulnerability class was searched for across the whole estate and ruled out by differential testing, not by absence of attempt.

### 2A.3 ⚠️ Deprecated Oracle driver identified

Error responses carry the exception type:

```json
"ExceptionType": "System.Data.OracleClient.OracleException"
```

`System.Data.OracleClient` is Microsoft's **legacy** ADO.NET provider for Oracle. It was **deprecated in .NET Framework 4.0 (2010)** and receives no security updates. The supported replacement is Oracle's own ODP.NET (`Oracle.ManagedDataAccess`).

Worth flagging as a technology-lifecycle issue: even once error disclosure is remediated, the underlying data-access library remains out of support.

---

## 3. Impact

- **Database Reconnaissance & Error-Based Injection Oracle:** Exposes the backend DBMS (Oracle), schema name (`MOBIDB`), stored procedure names (`GET_USERATTENDANCE_LATEST`, `GET_USERINFO`), and exact PL/SQL line numbers where inputs are processed, enabling targeted error-based SQL/PLSQL injection attacks.
- **Server Filesystem & Architecture Disclosure:** Confirms the application root path (`d:\NtraktApi\NtraktApi\`) and internal controller/model structure.

---

## 4. Remediation

1. **Disable Detailed Web API Exceptions in Production:**
   - In `WebApiConfig.Register`: set `config.IncludeErrorDetailPolicy = IncludeErrorDetailPolicy.Never;`
   - In `Web.config`: set `<customErrors mode="On" />` and `<compilation debug="false" />`.
2. **Catch Database Exceptions Server-Side:** Log `OracleException` details to an internal server log and return a generic `400 Bad Request` or `500 Internal Server Error` message (`{"error": "An unexpected error occurred"}`) to the client.
