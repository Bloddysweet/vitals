# WEB-2026-009 — Missing Security Headers (Clickjacking, HSTS, CSP), Insecure Session Cookies, & Internal Network IP / Infrastructure Disclosure

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-009 |
| **Severity** | **Medium** |
| **CVSS v3.1 Score** | **5.8** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`) |
| **CWE** | CWE-1021 (Improper Restriction of Rendered UI Layers or Frames), CWE-614 (Sensitive Cookie in HTTPS Session Without 'Secure' Attribute), CWE-200 (Information Exposure) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://narayanagroup.co.in/`, `https://narayanagroup.co.in/NHIS/`, `https://dms.narayanagroup.co.in/dms`, `https://app.narayanagroup.co.in/login` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

1. **Clickjacking & Missing Security Headers on Main Portal (`narayanagroup.co.in`) and `app.narayanagroup.co.in`:** Neither `https://narayanagroup.co.in/` nor `https://app.narayanagroup.co.in/login` sends `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, or `Permissions-Policy`. All login pages under `narayanagroup.co.in/*` can be framed inside an attacker-controlled site for UI redressing (Clickjacking).
2. **Session & Anti-CSRF Cookies Missing `HttpOnly`, `Secure`, and `SameSite` Flags:**
   - `https://narayanagroup.co.in/nmconline/` (WHIS — Web-based Hospital Management System) and `/inventory/` (WIMS — Web-based Inventory Management System) set Classic ASP session cookies (`ASPSESSIONIDQCQRQDSB=...; path=/`) **without `HttpOnly`, `Secure`, or `SameSite` attributes**, allowing session theft via any XSS or plaintext HTTP request across `narayanagroup.co.in`.
   - `https://narayanagroup.co.in/NHIS/` sets `ASP.NET_SessionId` **without the `Secure` flag** (`Set-Cookie: ASP.NET_SessionId=...; path=/; HttpOnly; SameSite=Lax`), allowing the session cookie to be leaked over any plaintext HTTP request to `narayanagroup.co.in` (such as the plaintext `CreateOrderNew.aspx` link).
   - `https://dms.narayanagroup.co.in/dms` sets `__RequestVerificationToken_L2Rtcw2` **without `Secure` or `SameSite` flags**.
   - `https://app.narayanagroup.co.in/login` (Narayana Lab Runners Application) submits credentials via `POST /login` without any anti-CSRF token or session cookie initialization.
3. **Internal Network IPs, Localhost Ports, & Server Version Banners Leaked:**
   - Homepage `https://narayanagroup.co.in/` contains a hardcoded RFC 1918 private IP link: `href="https://192.168.100.10/"` and an ASP.NET error redirect path `Login.aspx?aspxerrorpath=/EngineeringAcademics/home.aspx`.
   - `/Nnote/` and `/ncare/` scripts leak internal server IPs `http://115.241.194.2/NtraktApi/api/`, `http://115.241.194.19/NnoteApi/api/`, and internal developer localhost ports `localhost:64867` and `localhost:6491`.
   - Response headers across the estate disclose exact framework and server versions: `X-AspNet-Version: 4.0.30319`, `X-AspNet-Version: 2.0.50727`, `X-AspNetMvc-Version: 5.2`, `X-Powered-By: ASP.NET`, `Server: Microsoft-IIS/10.0`, `Server: nginx/1.24.0 (Ubuntu)`, and `Server: Apache/2.4.23 (Win64) PHP/5.6.25`.

4. **Username Enumeration on Classic ASP Hospital & Inventory Portals (`CWE-204`):**
   - Submitting a login attempt to `/inventory/commonfiles/asp/InnerHome.asp` (WIMS) or `/nmconline/commonfiles/asp/InnerHome.asp` (WHIS) redirects to `default.asp?logInFlag=0` and renders `<FONT COLOR=RED>There is no such Login Id</FONT>`, allowing unauthenticated attackers to enumerate valid hospital Login IDs distinct from invalid passwords (in addition to `/NtraktApi/api/CheckOperator/{empid}` returning `{"data":"Success"}`).

---

## 2. Technical Evidence (Live Capture)

### 2.1 Missing Security Headers on `https://narayanagroup.co.in/`

```http
HTTP/1.1 200 OK
Date: Sun, 11 Oct 2026 09:18:24 GMT
Server: Apache
Content-Type: text/html
Last-Modified: Mon, 28 Sep 2026 10:48:35 GMT
Accept-Ranges: bytes
ETag: "1e79a4e9364fdd1:0"
X-Powered-By: ASP.NET
Content-Length: 16137
Vary: Accept-Encoding
```

### 2.2 Insecure Cookies on `/nmconline/`, `/inventory/`, `/NHIS/`, and `dms.narayanagroup.co.in`

```http
# https://narayanagroup.co.in/nmconline/commonfiles/asp/InnerHome.asp (WHIS Hospital Management) & /inventory/ (WIMS)
Set-Cookie: ASPSESSIONIDQCQRQDSB=OLHNJDIBHPLLGGEDLGEFOAJH; path=/

# https://narayanagroup.co.in/NHIS/
Set-Cookie: ASP.NET_SessionId=litdpe253pehz15jb1ghiqj5; path=/; HttpOnly; SameSite=Lax

# https://dms.narayanagroup.co.in/dms
set-cookie: __RequestVerificationToken_L2Rtcw2=VVt1HQZb...; path=/; HttpOnly
```

### 2.3 Hardcoded Private/Internal IPs in Production HTML/JS

```html
<!-- https://narayanagroup.co.in/ -->
href="https://192.168.100.10/"
href="http://115.241.194.8/elearn/"

<!-- https://narayanagroup.co.in/Nnote/index.html & registration.html -->
//var apiURL = 'http://115.241.194.2/NtraktApi/api/';
//var apiURL = 'http://115.241.194.19/NtraktApi/api/';
//var apiURL = 'http://localhost:64867/api/';
//var apiURL = 'http://localhost:6491/api/Nnote/';
```

---

## 3. Remediation

1. **Add Standard Security Response Headers across IIS / Apache / Nginx:**
   ```http
   Strict-Transport-Security: max-age=31536000; includeSubDomains
   X-Frame-Options: SAMEORIGIN
   X-Content-Type-Options: nosniff
   Referrer-Policy: strict-origin-when-cross-origin
   Permissions-Policy: camera=(), microphone=(), geolocation=()
   Content-Security-Policy: frame-ancestors 'self'; upgrade-insecure-requests
   ```
2. **Enforce `requireSSL="true"` on All ASP.NET Cookies:** In `Web.config`, configure `<httpCookies httpOnlyCookies="true" requireSSL="true" sameSite="Lax" />`.
3. **Strip Version Headers & Internal IP Comments:** Remove `X-Powered-By`, `X-AspNet-Version`, and `X-AspNetMvc-Version` (`enableVersionHeader="false"`), and remove internal IP addresses (`192.168.100.10`, `115.241.194.2`, `115.241.194.19`) from production HTML/JS files.
