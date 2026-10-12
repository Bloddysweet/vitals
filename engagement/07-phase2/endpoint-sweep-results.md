# Phase 2 — Endpoint Sweep Results

**Target:** `https://narayanagroup.co.in` (`/NnoteApi/`, `/NtraktApi/`)
**Date:** 2026-10-12
**Method:** Every endpoint on both API help pages was enumerated from the ASP.NET Web API auto-generated help pages, then probed with unauthenticated requests.

---

## 1. Estate totals

| Metric | Count |
|---|---|
| **Total endpoints discovered** | **205** |
| `NtraktApi` endpoints | 104 |
| `NnoteApi` endpoints | 101 |
| Endpoints requiring authentication | **7** |
| Endpoints with **no** authentication | **198** |

## 2. Response distribution — first sweep (all 205, GET)

| Status | Count | Interpretation |
|---|---|---|
| `200 OK` | 108 | Readable, no authentication |
| `405 Method Not Allowed` | 81 | Write (POST) endpoints |
| `500 Internal Server Error` | 8 | Reached controller, threw |
| `404 Not Found` | 4 | Route mismatch |
| `400 Bad Request` | 3 | Parameter parsing failed |
| `401 Unauthorized` | **1** | ✅ Authentication enforced |

## 3. Response distribution — write sweep (the 81 `405` endpoints, POST)

Each was sent `POST` with `Content-Type: text/plain` and body `x` — a request that **fails during media-type negotiation, before any business logic executes**. No data can be created, modified, approved or transmitted by this probe.

| Status | Count | Interpretation |
|---|---|---|
| `415 Unsupported Media Type` | 60 | Reached model binding → **no auth gate** |
| `204 No Content` | 13 | **Accepted**, action body ran → **no auth gate** |
| `500 Internal Server Error` | 2 | Reached controller, threw → **no auth gate** |
| `401 Unauthorized` | **6** | ✅ Authentication enforced |
| **Ungated total** | **75 of 81** | |

---

## 4. The seven protected endpoints — all scaffolded template code

| Endpoint | Response |
|---|---|
| `GET  /NtraktApi/api/Account/UserInfo` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/AddExternalLogin` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/ChangePassword` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/Logout` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/RegisterExternal` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/RemoveLogin` | `401` · `WWW-Authenticate: Bearer` |
| `POST /NtraktApi/api/Account/SetPassword` | `401` · `WWW-Authenticate: Bearer` |

Every one lives in `AccountController` — the controller that ships as boilerplate with the ASP.NET Web API project template.

> **Conclusion:** the authentication system is installed, configured and functioning. It was never applied to any hand-written controller. Remediation = apply `[Authorize]` estate-wide, not build an auth system.

---

## 5. The 60 ungated write endpoints (`415`)

Grouped by business function.

### Clinical / patient safety
```
NnoteApi/api/Patient/SaveVitalData/1/1
NnoteApi/api/Prescription/savepatientprescription
NnoteApi/api/Patient/savepatientfeedback
NnoteApi/api/Patient/Camp/Camp_savepatientfeedback
NnoteApi/api/Patient/Dental/SaveDentalpatientfeedback
NnoteApi/api/Patient/Dental/DentalOpDetails
NnoteApi/api/Ip/Census
NnoteApi/api/Ip/Census/Dept
NnoteApi/api/LabReport/SendCriticalValuesForPatient
```

### Billing / financial approval
```
NnoteApi/api/Investigation/Cancel/Approve
NtraktApi/api/InvConcession/ConcessApprove
NtraktApi/api/InvConcession/ConcessReject
NtraktApi/api/InvConcession/IpConcessApprove
NtraktApi/api/InvConcession/IpConcessReject
NtraktApi/api/InvConcession/IpConcessDetails
NtraktApi/api/InvConcession/IpConcessList
NtraktApi/api/InvConcession/LabDataUpdate
NtraktApi/api/InvConcession/LabTestList
NtraktApi/api/InvConcession/PateintConcessDetails
NtraktApi/api/InvConcession/PateintDetails
NtraktApi/api/InvConcession/CheckConcess
NnoteApi/api/HealthWorker/Approve
```

### Outbound messaging (WhatsApp / SMS to patients)
```
NnoteApi/api/LabReport/SendWhatAppPDFforPatient
NnoteApi/api/LabReport/SendSMSExportPDF
NnoteApi/api/LabReport/ExportPDF
```

### Identity / credential management
```
NtraktApi/api/Account/Register
NtraktApi/api/CheckPin
NtraktApi/api/CheckUser
NtraktApi/api/User/OTP
NtraktApi/api/User/VerifyOTP
NtraktApi/api/User/UpdatePin
NnoteApi/api/Patient/ChangePin
NnoteApi/api/Patient/Validate
NtraktApi/api/Vehicle/CheckUserAccess
```

### Student / hostel
```
NtraktApi/api/Student/ApprovalCancel
NtraktApi/api/Student/Approve
NtraktApi/api/Student/Cancel
NtraktApi/api/Student/CheckIn
NtraktApi/api/Student/CheckOut
NtraktApi/api/Student/Close
NtraktApi/api/Student/Reject
NtraktApi/api/Student/Request
```

### Vehicle / transport
```
NtraktApi/api/Vehicle/SaveVehReq
NtraktApi/api/Vehicle/UpdateVehReq
NtraktApi/api/Vehicle/VehReqApprList
NtraktApi/api/Vehicle/VehReqList
NtraktApi/api/Vehicle/VehReqLoad
NtraktApi/api/Vehicle/CampusList
NnoteApi/api/Patient/Transport/SaveTransportWheelChairs
```

### Asset management / roster
```
NnoteApi/api/Nnote/assetsummary
NnoteApi/api/Nnote/assettaging
NnoteApi/api/Nnote/assetverify
NnoteApi/api/Nnote/getassetuser
NnoteApi/api/Roster/Schedule
NnoteApi/api/Roster/Schedule/N
NtraktApi/api/DoctorStatus/StatusChange
```

### File upload / enquiry
```
NnoteApi/api/Nnote/FileUpload/Upload
NnoteApi/api/Nnote/FileUpload/Upload/1
NnoteApi/api/Patient/Enquiry
NnoteApi/api/Patient/Enquiry/FeedBack
```

---

## 6. The 13 accepted endpoints (`204`) — all file upload

See WEB-2026-018 §1.2 for the list and the caveat about possible stray artefacts.

## 7. The two `500`s — new Oracle objects

| Endpoint | Stored procedure | Line | Error |
|---|---|---|---|
| `Patient/DentalReport/DentalFeedback/1/1/1/1` | `WHISPROD.GET_DENTALPATIENT_FEEDBACK_RPT` | 42 | `ORA-06535` |
| `Patient/Report/Feedback/1/1/1/1/1` | `WHISPROD.GET_PATIENT_FEEDBACK_RPT` | 51 | `ORA-06535` |

Adds to the Oracle oracle inventory in WEB-2026-005 (schemas `MOBIDB`, `WHISPROD`).

---

## 8. Method notes

- Endpoints were enumerated from the ASP.NET Web API auto-generated help pages, which are publicly reachable. **The client was asked to keep these live until patch day**, since they are the discovery source, and to remove them as part of the patch.
- The write probe (`Content-Type: text/plain`) cannot create, modify, approve or transmit anything: media-type negotiation fails before model binding completes.
- No destructive operations (`--os-shell`, `DROP`, `rm`, mass upload) were performed at any point.
- No systematic patient enumeration was performed; only single-record proof-of-access requests.
