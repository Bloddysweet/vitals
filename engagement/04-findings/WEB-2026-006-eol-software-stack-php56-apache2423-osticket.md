# WEB-2026-006 — Severely End-of-Life Software Stack Across Subdomains & Portals (PHP 5.6.25, Apache 2.4.23, osTicket v1.10, ASP.NET 2.0, jQuery 1.10–1.12, Bootstrap 3.3.7)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-006 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **8.1** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L`) |
| **CWE** | CWE-1104 (Use of Unmaintained Third Party Components), CWE-1395 (Dependency on Vulnerable Third-Party Component) |
| **OWASP Top 10 (2021)** | A06:2021 — Vulnerable and Outdated Components |
| **Affected Targets** | `http://helpdesk.narayanagroup.co.in`, `https://narayanagroup.co.in/`, `https://narayanagroup.co.in/patient/`, `https://narayanagroup.co.in/MedicalNarayanaPayroll/`, `https://narayanagroup.co.in/onlinefeepay/` |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

Multiple internet-facing portals under `narayanagroup.co.in` run severely outdated, End-of-Life (EOL) server and client software stacks containing dozens of publicly known Critical and High CVEs:

| Asset | Component & Version | Release / EOL Status | Key Known CVEs |
|---|---|---|---|
| `helpdesk.narayanagroup.co.in` | **PHP 5.6.25** (Win64) | Released Aug 2016; **EOL Dec 2018** | CVE-2016-7479, CVE-2016-10158, CVE-2017-11144, CVE-2019-9637 (RCE, Deserialization, Heap Overflow) |
| `helpdesk.narayanagroup.co.in` | **Apache HTTP Server 2.4.23** (Win64) | Released Jul 2016 | **CVE-2017-9798** (Optionsbleed), **CVE-2017-7679** (mod_mime buffer overread), **CVE-2017-3167** (auth bypass), **CVE-2016-8743** (HTTP request smuggling) |
| `helpdesk.narayanagroup.co.in` (`117.206.80.205`) | **osTicket v1.10** (`?901e5ea`) + **jQuery 1.11.2** + **jQuery UI 1.10.3** | Released Nov 2016 | CVE-2020-24881 (SSRF), CVE-2020-14008 (XSS), CVE-2017-15580 (SQLi), CVE-2021-41182/3/4 (jQuery UI XSS) |
| `uat.narayanagroup.co.in` (`115.241.194.18`) | **Apache 2.4.41 (Win64) + OpenSSL 1.1.1c + PHP 7.3.11** | Released 2019; **EOL Dec 2021** | **CVE-2021-40438** (Apache mod_proxy SSRF), **CVE-2020-11984** (RCE), **CVE-2021-3711** (OpenSSL SM2 buffer overflow) |
| `narayanagroup.co.in/patient/` | **ASP.NET 2.0.50727** | **EOL Apr 2011 / 2016** | Legacy .NET 2.0 cryptographic & deserialization weaknesses |
| `narayanagroup.co.in/MedicalNarayanaPayroll/` | **Visual Studio .NET 7.1 (2003)** / VB.NET 7.1 | **EOL** (23-year-old build toolchain) | Legacy ASP.NET 1.1/2.0 WebForms architecture |
| `narayanagroup.co.in/inventory/` & `/nmconline/` | **Classic ASP (`.asp`, 2010)** (`WIMS` & `WHIS`) | **Legacy** | Client-side-only JS login filtering (`chkName`), unencrypted `ASPSESSIONID` without `HttpOnly`/`Secure` |
| `dms.narayanagroup.co.in/dms` | **jQuery v3.2.1** | EOL | **CVE-2019-11358** (Prototype Pollution), **CVE-2020-11022/11023** (DOM XSS) |
| `narayanagroup.co.in/` | **jQuery v1.12.4** | EOL | **CVE-2020-11022**, **CVE-2020-11023** (DOM XSS), **CVE-2019-11358** (Prototype Pollution) |
| `narayanagroup.co.in/` | **Bootstrap v3.3.7** | EOL | **CVE-2018-14040**, **CVE-2018-14041**, **CVE-2018-14042**, **CVE-2019-8331** (XSS in data attributes) |
| `narayanagroup.co.in/onlinefeepay/` & `/zoomreports/` | **jQuery v1.10.2** | EOL | CVE-2015-9251, CVE-2019-11358, CVE-2020-11022, CVE-2020-11023 |
| `narayanagroup.co.in/NIS/` | **jQuery v1.11.3** | EOL | CVE-2015-9251, CVE-2019-11358, CVE-2020-11022, CVE-2020-11023 |
| `narayanagroup.co.in/ncare/` | **jQuery UI v1.12.1** + **PhoneGap 1.1.0** | EOL | CVE-2021-41182, CVE-2021-41183, CVE-2021-41184 (DOM XSS) |

---

## 2. Technical Evidence (Live Capture)

### 2.1 `helpdesk.narayanagroup.co.in` HTTP Response & HTML

```http
HTTP/1.1 200 OK
Date: Sun, 11 Oct 2026 09:45:54 GMT
Server: Apache/2.4.23 (Win64) PHP/5.6.25
```
```html
<link rel="stylesheet" href="/helpdesk/css/osticket.css?901e5ea" media="screen"/>
<link type="text/css" href="/helpdesk/css/ui-lightness/jquery-ui-1.10.3.custom.min.css?901e5ea" rel="stylesheet" media="screen" />
<script type="text/javascript" src="/helpdesk/js/jquery-1.11.2.min.js?901e5ea"></script>
```

### 2.2 `narayanagroup.co.in/patient/` & `/MedicalNarayanaPayroll/`

```http
HTTP/1.1 302 Found
Location: /patient/Reports/Patient_Login.aspx
X-AspNet-Version: 2.0.50727
X-Powered-By: ASP.NET
```
```html
<title>:: Narayana Payroll System :: </title>
<meta content="Microsoft Visual Studio .NET 7.1" name="GENERATOR">
<meta content="Visual Basic .NET 7.1" name="CODE_LANGUAGE">
```

### 2.3 Main Portal JS Libraries (`narayanagroup.co.in/assets/js/`)

```javascript
/*! jQuery v1.12.4 | (c) jQuery Foundation | jquery.org/license */
/*! Bootstrap v3.3.7 (http://getbootstrap.com) */
```

---

## 3. Remediation

1. **Upgrade or Isolate `helpdesk.narayanagroup.co.in` Immediately:** Migrate osTicket to the latest supported release (v1.18.x) running on supported PHP 8.2+ and Apache 2.4.62+, and place it behind HTTPS.
2. **Migrate Legacy ASP.NET 2.0 Applications:** Upgrade `/patient/` and `/MedicalNarayanaPayroll/` to a supported .NET runtime or restrict access to internal hospital VPN/intranet only.
3. **Upgrade Frontend Libraries:** Update jQuery to `v3.7.1` (already present in `/NHIS/`) and Bootstrap to `v5.3.3` (already present in `app.narayanagroup.co.in`) across all portals.
