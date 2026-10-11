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

## 3. Impact

- **Database Reconnaissance & Error-Based Injection Oracle:** Exposes the backend DBMS (Oracle), schema name (`MOBIDB`), stored procedure names (`GET_USERATTENDANCE_LATEST`, `GET_USERINFO`), and exact PL/SQL line numbers where inputs are processed, enabling targeted error-based SQL/PLSQL injection attacks.
- **Server Filesystem & Architecture Disclosure:** Confirms the application root path (`d:\NtraktApi\NtraktApi\`) and internal controller/model structure.

---

## 4. Remediation

1. **Disable Detailed Web API Exceptions in Production:**
   - In `WebApiConfig.Register`: set `config.IncludeErrorDetailPolicy = IncludeErrorDetailPolicy.Never;`
   - In `Web.config`: set `<customErrors mode="On" />` and `<compilation debug="false" />`.
2. **Catch Database Exceptions Server-Side:** Log `OracleException` details to an internal server log and return a generic `400 Bad Request` or `500 Internal Server Error` message (`{"error": "An unexpected error occurred"}`) to the client.
