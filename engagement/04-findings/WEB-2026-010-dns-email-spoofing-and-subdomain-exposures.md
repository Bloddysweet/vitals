# WEB-2026-010 — Domain-Wide Email Spoofing (Missing SPF & DMARC Records), Misdirected DNS A-Record (`online.narayanagroup.co.in` → `15.241.194.25`), & Unhardened `uat` / `nmc` Subdomains

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-010 |
| **Severity** | **Medium** |
| **CVSS v3.1 Score** | **6.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`) |
| **CWE** | CWE-290 (Authentication Bypass by Spoofing), CWE-350 (Reliance on Reverse DNS Resolution / Misdirected DNS), CWE-16 (Configuration) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `narayanagroup.co.in` (DNS / Email), `online.narayanagroup.co.in`, `uat.narayanagroup.co.in` (`115.241.194.18`), `nmc.narayanagroup.co.in` (`115.241.194.13`) |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

Full subdomain and DNS reconnaissance across `*.narayanagroup.co.in` (authoritative nameservers `dion.ns.cloudflare.com` and `grace.ns.cloudflare.com`) identified four domain/subdomain-level security issues:

1. **Complete Absence of SPF and DMARC Records (`narayanagroup.co.in`):** Neither an SPF `TXT` record on `narayanagroup.co.in` nor a DMARC `TXT` record on `_dmarc.narayanagroup.co.in` is configured. Any external attacker can send spoofed phishing or billing emails appearing to originate from `@narayanagroup.co.in`.
2. **Misdirected / Typo DNS A-Record on `online.narayanagroup.co.in` (`15.241.194.25`):** While Narayana Group's IP block is `115.241.194.0/24`, the DNS A-record for `online.narayanagroup.co.in` points to **`15.241.194.25`** (missing the leading `1` — an external IP address in the `15.0.0.0/8` range). Any traffic, cookies, or credentials sent to `online.narayanagroup.co.in` are routed to an untrusted third-party IP outside Narayana Group's network.
3. **UAT Subdomain (`uat.narayanagroup.co.in` → `https://115.241.194.18`) Exposes Internal Server Running EOL Software:** `uat.narayanagroup.co.in` (`3.33.251.168`) issues a `301` redirect to `https://115.241.194.18`, which discloses `Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11` (all End-of-Life since 2019–2021).
4. **Default Unhardened IIS Server on `nmc.narayanagroup.co.in` (`115.241.194.13`):** Serves the default `IIS Windows Server` welcome page over both plaintext HTTP and HTTPS with `Server: Microsoft-IIS/10.0` and `X-Powered-By: ASP.NET` headers and zero security headers.

---

## 2. Technical Evidence (Live Capture)

### 2.1 Missing SPF & DMARC Records

```text
$ dig +short NS narayanagroup.co.in
dion.ns.cloudflare.com.
grace.ns.cloudflare.com.

$ dig +short TXT narayanagroup.co.in
(empty)

$ dig +short TXT _dmarc.narayanagroup.co.in
(empty)
```

### 2.2 Misdirected DNS A-Record on `online.narayanagroup.co.in`

```text
$ dig +short online.narayanagroup.co.in
15.241.194.25
```
*(Compare with legitimate Narayana subnet `115.241.194.4`, `115.241.194.8`, `115.241.194.11`, `115.241.194.12`, `115.241.194.13`, `115.241.194.18`, `115.241.194.19`.)*

### 2.3 `uat.narayanagroup.co.in` Redirect to `115.241.194.18` (EOL Apache/OpenSSL/PHP)

```http
HTTP/2 301 
location: https://115.241.194.18
server: ip-100-74-5-26.eu-west-2.compute.internal

HTTP/1.1 403 Forbidden
Date: Sun, 11 Oct 2026 13:21:45 GMT
Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11
```

### 2.4 `nmc.narayanagroup.co.in` (`115.241.194.13`)

```http
HTTP/2 200 
etag: "75cae461e0a8d91:0"
server: Microsoft-IIS/10.0
x-powered-by: ASP.NET
<title>IIS Windows Server</title>
```

---

## 3. Remediation

1. **Publish SPF and DMARC DNS TXT Records:**
   - If `narayanagroup.co.in` does not send mail directly, publish a strict null-SPF policy:
     ```
     narayanagroup.co.in. IN TXT "v=spf1 -all"
     _dmarc.narayanagroup.co.in. IN TXT "v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s;"
     ```
   - If authorized mail servers exist, list only their IPs/includes and set `~all` or `-all` with a `p=quarantine`/`p=reject` DMARC policy.
2. **Remove or Correct `online.narayanagroup.co.in` Immediately:** Delete the erroneous `15.241.194.25` A-record in Cloudflare DNS (or update it to `115.241.194.25` if still in use) so traffic is never routed to a third-party IP.
3. **Restrict `uat.narayanagroup.co.in` (`115.241.194.18`) and `nmc.narayanagroup.co.in` (`115.241.194.13`):** Remove public DNS records for unused/UAT environments or upgrade `Apache/2.4.41 OpenSSL/1.1.1c PHP/7.3.11` on `115.241.194.18`.
