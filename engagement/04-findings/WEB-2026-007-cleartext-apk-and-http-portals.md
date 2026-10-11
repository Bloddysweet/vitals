# WEB-2026-007 — Cleartext HTTP Distribution of Hospital Android APK (`http://115.241.194.19/nNote.apk`) & Cleartext Authentication Portals (`helpdesk.narayanagroup.co.in`, `115.241.194.8/elearn/`)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-007 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H`) |
| **CWE** | CWE-494 (Download of Code Without Integrity Check), CWE-319 (Cleartext Transmission of Sensitive Information) |
| **OWASP Top 10 (2021)** | A08:2021 — Software and Data Integrity Failures / A02:2021 — Cryptographic Failures |
| **Affected Targets** | `http://115.241.194.19/nNote.apk` (referenced in `/Nnote/layout.html` & `/ncare/layout.html`), `http://helpdesk.narayanagroup.co.in/helpdesk/login.php`, `http://115.241.194.8/elearn/` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

1. **Cleartext HTTP Android APK Delivery (`http://115.241.194.19/nNote.apk`):** Both `/Nnote/layout.html` and `/ncare/layout.html` instruct users to download the hospital's mobile application (`nNote.apk`) over unencrypted HTTP from a raw IP address (`http://115.241.194.19/nNote.apk`). Any attacker on a shared Wi-Fi or ISP network path can intercept the download and substitute a trojanized APK.
2. **Cleartext HTTP Login Portals:** Both the IT Helpdesk (`http://helpdesk.narayanagroup.co.in/helpdesk/login.php` and staff panel `/helpdesk/scp/login.php`) and the E-Learning portal (`http://115.241.194.8/elearn/`) are linked from `https://narayanagroup.co.in/` over plaintext `http://` and serve `200 OK` without redirecting to HTTPS.

---

## 2. Technical Evidence (Live Capture)

### 2.1 Cleartext APK Download in `/Nnote/layout.html` & `/ncare/layout.html`

```javascript
// Source: https://narayanagroup.co.in/Nnote/layout.html & /ncare/layout.html
function ShowAppUpdate() {
    $.get(apiURL + 'Notifications/App/4029038', function (response) {
        $('#download').click(function () {
            $(this).attr('href', 'http://115.241.194.19/nNote.apk');
        });
    });
}
```

### 2.2 Cleartext HTTP Portals Linked on Homepage (`https://narayanagroup.co.in/`)

```html
href="http://115.241.194.8/elearn/"
href="http://helpdesk.narayanagroup.co.in"
href="http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx"
```

Live probe confirmation:
```text
http://115.241.194.8/elearn/ -> 200 (redirect: )
http://helpdesk.narayanagroup.co.in -> 200 (redirect: )
```

---

## 3. Impact

- **Mobile Device Compromise via APK MITM:** Because `http://115.241.194.19/nNote.apk` is fetched over plaintext HTTP and requires sideloading ("Install Unknown Apps") on Android, an attacker on hospital/public Wi-Fi can replace the APK in transit with spyware.
- **Credential & Session Sniffing:** Staff and students logging into `http://helpdesk.narayanagroup.co.in` or `http://115.241.194.8/elearn/` transmit their usernames, passwords, and session cookies (`OSTSESSID` / `PHPSESSID`) in cleartext.

---

## 4. Remediation

1. **Serve All APK Downloads & Portals Strictly Over HTTPS:** Host mobile apps on the official Google Play Store or serve them over `https://narayanagroup.co.in/` with a published SHA-256 checksum.
2. **Enforce 301 HTTP-to-HTTPS Redirects Across All Hosts:** Configure TLS certificates and mandatory HTTPS redirects on `helpdesk.narayanagroup.co.in` and the E-Learning server.
3. **Add `upgrade-insecure-requests` CSP Directive:** Prevent mixed-content and accidental `http://` navigation from `https://narayanagroup.co.in/`.
