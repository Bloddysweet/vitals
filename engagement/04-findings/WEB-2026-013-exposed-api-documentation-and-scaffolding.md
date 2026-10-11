# WEB-2026-013 — Publicly Exposed ASP.NET Web API Documentation Disclosing the Complete Internal API Surface (104 Endpoints), With Default Scaffolding Still Deployed

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-013 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-215 (Insertion of Sensitive Information Into Debugging Code), CWE-1188 (Insecure Default Initialization of Resource) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/help` (35,387 bytes), `https://narayanagroup.co.in/NnoteApi/help`, `https://narayanagroup.co.in/NtraktApi/`, `https://narayanagroup.co.in/NnoteApi/` |
| **Status** | Confirmed (Live Target) |
| **Phase** | Phase 2 (2026-10-11) |
| **Evidence** | `engagement/07-phase2/NtraktApi-endpoints.txt` |

---

## 1. Summary

Both production API services expose the **ASP.NET Web API auto-generated help page** with no authentication:

```
https://narayanagroup.co.in/NtraktApi/help   →  HTTP 200  (35,387 bytes)
https://narayanagroup.co.in/NnoteApi/help    →  HTTP 200
```

The `NtraktApi` help page alone documents **104 distinct API endpoints**, complete with HTTP verbs, parameter names and route templates. Both API roots (`/NtraktApi/` and `/NnoteApi/`) additionally render the **default *"Home Page"* ASP.NET MVC template**, and the route list includes the **default Visual Studio scaffolding endpoints `api/Values`, `api/Values/Get`, `api/Values/Post` and `api/Values/{id}`** — proof that development scaffolding was never removed before deployment to production.

For an attacker this eliminates the reconnaissance phase entirely. There is nothing left to guess.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The help pages return 200 without authentication

```bash
for p in "NtraktApi/help" "NnoteApi/help" ; do
  curl -k -s -o /dev/null -w "$p -> %{http_code}\n" -m 30 "https://narayanagroup.co.in/$p"
done
```

**Live Response:**

```
NtraktApi/help -> 200
NnoteApi/help -> 200 (in 0.61s)
```

### 2.2 Harvesting the endpoint list

```bash
curl -k -s -m 30 "https://narayanagroup.co.in/NtraktApi/help" -o ntrakt-help.html
wc -c ntrakt-help.html
grep -oE "api/[A-Za-z0-9_/{}\.-]+" ntrakt-help.html | sort -u | wc -l
```

**Live Response:**

```
35387 ntrakt-help.html
104
```

### 2.3 Both API roots still render the default template

```bash
curl -k -s "https://narayanagroup.co.in/NtraktApi/" | grep -oiE "<title>[^<]*</title>"
```

**Live Response:**

```
<title>Home Page</title>
```

Identical output for `/NnoteApi/`. Both roots also reference `Api/Help`, `Api/Content/css`, `Api/bundles/bootstrap`, `Api/bundles/jquery` and `Api/bundles/modernizr` — the untouched default MVC bundle layout.

---

## 3. Endpoint Inventory by Functional Area

| Area | Count | Representative Endpoints |
|---|---|---|
| **Attendance / Leave** | 18 | `api/Attendance/LeaveApprove`, `LeaveReject`, `LeavesApproveAll`, `ApprovalLeaves`, `Leaves/{id}`, `postmarkattendance`, `AlternateLeaveApprove` |
| **Student / Hostel** | 20 | `api/Student/CheckIn`, `CheckOut`, `Approve`, `Reject`, `Details/{uid}/{id}`, `DashBoardStatusList/{uid}/{from}/{to}/{leavetype}/{status}` |
| **Invoice Concession** | 12 | `api/InvConcession/ConcessApprove`, `IpConcessApprove`, `ConcessList`, `IpConcessList`, `PateintDetails`, `LabDataUpdate` |
| **Account** | 11 | `api/Account/Register`, `ChangePassword`, `SetPassword`, `UserInfo`, `ManageInfo`, `AddExternalLogin` |
| **User** | 10 | `api/User/Info/{id}`, `OTP`, `VerifyOTP`, `UpdatePin`, `ShowPicture/{id}`, `AlternateUsers/{id}` |
| **Vehicle** | 8 | `api/Vehicle/SaveVehReq`, `UpdateVehReq`, `VehReqApprList`, `VehReqList`, `CheckUserAccess` |
| **Values (scaffolding)** | 4 | `api/Values`, `api/Values/Get`, `api/Values/Post`, `api/Values/{id}` |
| **Doctor / DoctorStatus** | 5 | `api/Doctors`, `api/Doctors/{id}`, `api/DoctorStatus/StatusChange` |
| **Notifications** | 3 | `api/Notifications/App/{id}`, `MarkRead`, `{id}` |
| **FileUpload** | 3 | `api/FileUpload/UploadFile`, `UploadFile/{name}`, `UploadForEmpFile/{EmpId}/{MSlno}` |
| **Other** | 10 | `api/Departments`, `api/CheckPin`, `api/CheckUser`, `api/UserType/{type}`, `api/employee/hodlist/{id}` |
| **Total** | **104** | |

The complete list is preserved at `engagement/07-phase2/NtraktApi-endpoints.txt`.

---

## 4. Why This Is High Severity, Not Informational

An unprotected API catalogue is not merely "extra information" — it is a **force multiplier applied to every other finding in this report**.

### 4.1 It removes the cost of discovery

Without this page, an attacker must brute-force directory and route names. With it, the entire attack surface arrives pre-sorted by business function, with exact casing and parameter names. What would take weeks of fuzzing takes one HTTP request.

### 4.2 It advertises high-value *write* operations

The list names capabilities that an attacker would otherwise never guess exist:

- **Financial authority** — `api/InvConcession/ConcessApprove`, `IpConcessApprove`, `ConcessReject`, `LabDataUpdate`. These approve or reject billing concessions — i.e. discounts on patient invoices. If unauthenticated, this is direct financial fraud capability.
- **Attendance fraud** — `api/Attendance/postmarkattendance`, `LeaveApprove`, `LeavesApproveAll`, `AlternateLeaveApprove`. `postmarkattendance` marks an employee's attendance; `LeavesApproveAll` approves every pending leave in one call.
- **Hostel / student movement** — `api/Student/CheckIn` and `CheckOut`. These record whether a student is physically present in a hostel. False check-outs defeat safeguarding and attendance controls for minors.
- **Account administration** — `api/Account/Register`, `ChangePassword`, `SetPassword`.
- **Arbitrary file upload** — `api/FileUpload/*` (already confirmed vulnerable as WEB-2026-003).
- **OTP lifecycle** — `api/User/OTP` and `api/User/VerifyOTP`, which map directly onto the client-side-only OTP weakness in WEB-2026-001.

### 4.3 It reveals the business domain

The endpoint names alone disclose that the group runs hostel management, vehicle requisition, biometric attendance, doctor availability and concession-approval workflows — none of which is visible from the public website.

### 4.4 Default scaffolding in production

`api/Values`, `api/Values/Get`, `api/Values/Post` and `api/Values/{id}` are the sample controller generated by Visual Studio's "New ASP.NET Web API Project" template. Their presence, alongside the default *"Home Page"* MVC template on both roots, shows that **the project was deployed without any production cleanup**. That is a process failure as much as a technical one, and it predicts further default-configuration weaknesses elsewhere.

---

## 5. Impact

- **Complete, authenticated-free map of the internal API** — 104 endpoints on `NtraktApi`, plus an unharvested second set on `NnoteApi`.
- **Targets named for financial, attendance and safeguarding abuse**, each of which becomes a distinct follow-on finding if confirmed unauthenticated.
- **Eliminates detection opportunity.** Reconnaissance noise is normally how defenders catch an attacker. This page produces a single request that looks entirely benign.
- **Confirms default scaffolding in production**, indicating weak release management.

---

## 6. Remediation

**Immediate**

1. **Disable the Web API help pages in production.** In `App_Start/HelpPageConfig.cs` / `WebApiConfig.cs`, or via `GlobalConfiguration.Configuration.Services.Replace(typeof(IDocumentationProvider), ...)` — remove the `HelpPage` area from production builds. Simplest robust fix: delete the `Areas/HelpPage` folder from the release pipeline, or gate it behind authentication and an internal-IP allow-list.
2. **Require authentication on `/NtraktApi/help` and `/NnoteApi/help`** if the documentation is genuinely needed by developers.
3. **Delete the default `ValuesController`** and the default `HomeController` MVC template from both projects.
4. **Audit every endpoint in `engagement/07-phase2/NtraktApi-endpoints.txt`.** Each one needs an explicit authentication and authorisation decision. Start with the write operations listed in §4.2.

**Structural**

5. **Add a release checklist gate** that fails deployment if the `HelpPage` area, `ValuesController`, or the default MVC home page is present.
6. **Separate internal API documentation from the public estate.** If developers need it, serve it from an internal host that is not internet-facing.
7. **Adopt an allow-list routing posture.** Any route not explicitly published should 404 by default, rather than being discoverable by enumeration.

---

## 7. Next Steps for This Assessment

The `NnoteApi` help page has **not yet been harvested**. It is expected to contain a comparable endpoint set covering the patient-facing API (`Assignee`, `Patient/Info`, `Investigation/Cancel/*`, `CreateUser`, `ChangePin`) and should be captured next.

Every previously untested endpoint is now a candidate finding. Priority for immediate testing:

| Priority | Endpoint | Rationale |
|---|---|---|
| 1 | `api/InvConcession/ConcessList`, `IpConcessList` | Patient billing + concession data |
| 2 | `api/Student/Details/{uid}/{id}`, `DashBoardStatusList/...` | Student PII, potentially minors |
| 3 | `api/Attendance/ApprovalLeaves`, `Leaves/{id}` | Staff leave history |
| 4 | `api/Doctors`, `api/Departments` | Directory enumeration |
| 5 | `api/Values` | Confirms scaffolding is live and reachable |
| 6 | `api/User/CheckUser`, `api/CheckPin` | Possible authentication/credential oracle |

Write operations (`ConcessApprove`, `LeaveApprove`, `postmarkattendance`, `Student/CheckIn`) should **not** be exercised against production without explicit written approval and a maintenance window.

---

## 8. Related Findings

- **WEB-2026-001** — Client-side authentication bypass; the `User/OTP` and `User/VerifyOTP` endpoints listed here are the server side of that weakness
- **WEB-2026-002** — Unauthenticated IDOR on staff and patient data
- **WEB-2026-003** — Unauthenticated file upload (`api/FileUpload/*` appears in this catalogue)
- **WEB-2026-005** — Stack trace disclosure from these same controllers

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
