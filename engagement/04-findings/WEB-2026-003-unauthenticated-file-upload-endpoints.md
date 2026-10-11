# WEB-2026-003 — Unauthenticated File Upload Endpoints Exposed on Staff & Patient APIs

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-003 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **8.6** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`) |
| **CWE** | CWE-434 (Unrestricted Upload of File with Dangerous Type), CWE-306 (Missing Authentication for Critical Function) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control / A04:2021 — Insecure Design |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/FileUpload/UploadForEmpFile/{empid}/{Mslno}`, `https://narayanagroup.co.in/NnoteApi/api/FileUpload/UploadFile/{n}/{cslno}`, `https://narayanagroup.co.in/NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}` |
| **Status** | Confirmed via Live Client Source Inspection |

---

## 1. Summary

Client-side source code on the live production server reveals three unauthenticated file upload API endpoints used for employee attendance attachments (`Nnote/markattendance.html`) and patient/staff service complaint attachments (`ncare/request.html`). None of these endpoints require authentication tokens, CSRF tokens, or session cookies, and one route (`/FileUpload/UploadFile/mobile/{fname}/{cslno}`) accepts a user-controlled filename parameter directly in the URL path.

---

## 2. Technical Evidence (Live Capture)

### 2.1 Staff Attendance File Upload (`https://narayanagroup.co.in/Nnote/markattendance.html`)

```javascript
// Source: https://narayanagroup.co.in/Nnote/markattendance.html
var apiURL = '../../NtraktApi/';
$.ajax({
    url: apiURL + 'api/FileUpload/UploadForEmpFile/' + $("#hempid").val() + '/' + Mslno,
    ...
});
$.ajax({
    url: apiURL + 'api/FileUpload/UploadForEmpFile/' + $('#hfname').val() + '/' + Mslno,
    ...
});
```

### 2.2 Complaint / Request Attachment Upload (`https://narayanagroup.co.in/ncare/request.html`)

```javascript
// Source: https://narayanagroup.co.in/ncare/request.html
var apiURL = '../../NnoteApi/api/';
$.ajax({
    url: apiURL + 'FileUpload/UploadFile/' + n + '/' + cslno,
    ...
});
$.ajax({
    url: apiURL + 'FileUpload/UploadFile/mobile/' + $('#hfname').val() + '/' + cslno,
    ...
});
```

*(Note: Per Rules of Engagement, no destructive or executable payloads were uploaded to the production IIS server.)*

---

## 3. Impact

- **Remote Code Execution (RCE) / Web Shell Risk:** Because the backend runs on Windows IIS (`Microsoft-IIS/10.0` / ASP.NET 4.0), if uploaded files are written inside a web-accessible directory without strict server-side extension allowlisting (`.aspx`, `.ashx`, `.asmx`, `.config`) or path traversal sanitization on `{fname}`, an attacker can achieve unauthenticated Remote Code Execution.
- **Stored XSS & Malware Hosting:** Uploading `.html`, `.svg`, or malicious binaries under `narayanagroup.co.in` allows stored XSS or trusted-domain malware delivery.
- **Disk Exhaustion (DoS):** Unauthenticated callers can fill the server's `d:\` drive by uploading large files in a loop.

---

## 4. Remediation

1. **Enforce Authentication & Authorization:** Require a valid authenticated session before accepting any file upload.
2. **Validate File Type & Content Server-Side:** Allow only specific image formats (`.jpg`, `.png`) verified by magic bytes (file signature) and re-encode images before saving.
3. **Never Trust Client-Supplied Filenames or Paths:** Generate a random UUID filename on the server (`Guid.NewGuid()`) and store uploaded files outside the IIS web root (or in object storage with `Content-Disposition: attachment` and script execution disabled).
