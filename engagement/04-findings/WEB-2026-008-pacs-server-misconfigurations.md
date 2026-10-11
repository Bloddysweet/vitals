# WEB-2026-008 — Medical Imaging Server (`pacs.narayanagroup.co.in`) Security Misconfigurations (`max-age=0` HSTS Disabling, Placeholder CORS Origin, & Exposed PACS/RIS Web APIs)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-008 |
| **Severity** | **Medium** |
| **CVSS v3.1 Score** | **6.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`) |
| **CWE** | CWE-16 (Configuration), CWE-942 (Permissive Cross-Domain Policy), CWE-200 (Exposure of Sensitive Information) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Target** | `https://pacs.narayanagroup.co.in`, `https://pacs.narayanagroup.co.in/externalConfig.js`, `https://pacs.narayanagroup.co.in/PacsAPI/`, `https://pacs.narayanagroup.co.in/RISAPI/` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

The hospital's **Medsynapse PACS (Picture Archiving and Communication System)** medical imaging portal at `https://pacs.narayanagroup.co.in` suffers from several production security misconfigurations:
1. **HSTS Actively Disabled (`max-age=0`):** The server sends `strict-transport-security: max-age=0; includeSubDomains; preload`, which instructs browsers to **immediately delete/expire** any cached HSTS policy for `pacs.narayanagroup.co.in`, re-exposing clinical imaging traffic to SSL stripping.
2. **Unreplaced Template Placeholders in CORS & CSP Headers:** The server returns `access-control-allow-origin: https://GlobalServerIP:Port` and a Content-Security-Policy containing literal `https://GlobalServerIP`, alongside `'unsafe-inline'`, `'unsafe-eval'`, and wildcard `https://*` in `connect-src`.
3. **Unauthenticated Exposure of `/externalConfig.js`, `/PacsAPI/`, and `/RISAPI/`:** The publicly readable `/externalConfig.js` reveals the internal API routing structure (`/PacsAPI/`, `/PACSMISReportAPI/`, `/RISAPI/`) and custom URI protocol (`MedsynapseLauncher:`). Direct requests to `/PacsAPI/` and `/RISAPI/` return live service banners and version numbers (`Pacs 7.0.0.0 Web API is running`, `Ris 5.1.0.0 Web API is running`) without authentication.

---

## 2. Technical Evidence (Live Capture)

### 2.1 HTTP Response Headers on `https://pacs.narayanagroup.co.in`

```http
HTTP/2 200 
content-type: text/html
server: PACS-SERVER
access-control-allow-methods: GET,PUT,POST,DELETE
access-control-allow-origin: https://GlobalServerIP:Port
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff
x-xss-protection: 1
content-security-policy: default-src 'none';style-src 'self' 'unsafe-inline';script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' blob:;img-src 'self' https://GlobalServerIP data: blob:;font-src 'self' data:;frame-src 'self' data: blob:;frame-ancestors 'self';manifest-src 'self';connect-src 'self' wss://msplchat.medsynaptic.com https://GlobalServerIP 'unsafe-inline' 'unsafe-eval' blob: data: https://*;media-src 'self';worker-src 'self' 'unsafe-inline' 'unsafe-eval' blob:;object-src blob: https://GlobalServerIP;
strict-transport-security: max-age=0; includeSubDomains; preload
```

### 2.2 Exposed `/externalConfig.js` and API Banners

```javascript
// https://pacs.narayanagroup.co.in/externalConfig.js
const externalConfig = {
    BASE_URL: "/PacsAPI/",
    Hub_BASE_URL: '/PacsAPI/',
    URI_PROTOCOL: 'MedsynapseLauncher:',
    PRODUCT_TITLE: "Medsynapse PACS",
    MIS_BASE_URL: "/PACSMISReportAPI/",
    BROKER_BASE_URL: "/RISAPI/",
    ...
}
```
```text
GET https://pacs.narayanagroup.co.in/PacsAPI/ -> "Pacs 7.0.0.0 Web API is running. Culture: en-US"
GET https://pacs.narayanagroup.co.in/RISAPI/  -> "Ris 5.1.0.0 Web API is running. Culture: en-US"
```

---

## 3. Remediation

1. **Fix the HSTS Header:** Replace `max-age=0` with `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
2. **Replace Template Placeholders in CORS & CSP:** Replace `https://GlobalServerIP:Port` with `https://pacs.narayanagroup.co.in` and remove `https://*` from `connect-src`.
3. **Restrict PACS Access:** Place `pacs.narayanagroup.co.in` (and `/PacsAPI/`, `/RISAPI/`) behind hospital VPN/Zero-Trust access or mutual TLS if external radiologist access is required.
