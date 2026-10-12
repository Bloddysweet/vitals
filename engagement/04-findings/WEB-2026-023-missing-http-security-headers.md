# WEB-2026-023 — Absence of All HTTP Security Headers on the Public Application

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-023 |
| **Severity** | **Low** |
| **CVSS v3.1 Score** | **3.7** (`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N`) |
| **CWE** | CWE-693 (Protection Mechanism Failure), CWE-319 (Cleartext Transmission), CWE-1021 (Improper Restriction of Rendered UI Layers) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://narayanagroup.co.in/` and all paths served by Apache/ASP.NET, including `/NnoteApi/` and `/NtraktApi/` |
| **Status** | Confirmed — 2026-10-12 |
| **Phase** | Phase 2 |

---

## 1. Summary

Every HTTP response from the public web application is returned **without any of the six standard browser security headers**. Verified independently by two methods (manual header inspection and nuclei `http-missing-security-headers`), which also identified four further absent headers.

| Header | Status |
|---|---|
| `Strict-Transport-Security` | ❌ absent |
| `Content-Security-Policy` | ❌ absent |
| `X-Frame-Options` | ❌ absent |
| `X-Content-Type-Options` | ❌ absent |
| `Referrer-Policy` | ❌ absent |
| `Permissions-Policy` | ❌ absent |
| `Cross-Origin-Embedder-Policy` | ❌ absent (nuclei) |
| `Cross-Origin-Opener-Policy` | ❌ absent (nuclei) |
| `Cross-Origin-Resource-Policy` | ❌ absent (nuclei) |
| `X-Permitted-Cross-Domain-Policies` | ❌ absent (nuclei) |

## 2. Evidence

### 2.1 Manual header inspection

```bash
curl -k -s -D - -o /dev/null https://narayanagroup.co.in/
```

```
HTTP/1.1 200 OK
Date: Mon, 12 Oct 2026 09:43:47 GMT
Server: Apache
Content-Type: text/html
Last-Modified: Mon, 28 Sep 2026 10:48:35 GMT
Accept-Ranges: bytes
ETag: "1e79a4e9364fdd1:0"
X-Powered-By: ASP.NET
Content-Length: 16137
Vary: Accept-Encoding
```

No security header is present. Note also that `Server: Apache` and `X-Powered-By: ASP.NET` **disclose** technology rather than concealing it.

### 2.2 Nuclei confirmation

```
[http-missing-security-headers:strict-transport-security]
[http-missing-security-headers:content-security-policy]
[http-missing-security-headers:x-frame-options]
[http-missing-security-headers:x-content-type-options]
[http-missing-security-headers:referrer-policy]
[http-missing-security-headers:permissions-policy]
[http-missing-security-headers:cross-origin-embedder-policy]
[http-missing-security-headers:cross-origin-opener-policy]
[http-missing-security-headers:cross-origin-resource-policy]
[http-missing-security-headers:x-permitted-cross-domain-policies]
```

---

## 3. Why this is rated Low and not higher

Stated explicitly so the client can calibrate the response.

**Missing security headers are not directly exploitable.** They are a defence-in-depth layer: their absence does not create a vulnerability, it removes the mitigation that would blunt one. On this specific target, three further factors limit impact:

1. **HSTS is less critical than usual** — no plaintext HTTP service exists (port 80 is closed), so there is no downgrade path for an attacker to exploit.
2. **Clickjacking requires a valuable state-changing action** — the application's sensitive actions are API calls, not framed UI flows.
3. **CSP mitigates XSS** — but see §4; this is the one place where the absence genuinely compounds an existing issue.

Organisations routinely ship without these headers. This is a **hardening gap**, and it should be closed, but it is not of comparable urgency to the authentication failures in WEB-2026-002, 015, 018 or 021.

---

## 4. Aggravating factor — interaction with stored XSS

The unauthenticated write endpoint `POST /NnoteApi/api/Patient/savepatientfeedback` accepts user-controlled content with no authentication (see the write-surface inventory in WEB-2026-018). If that content is later rendered in a staff-facing view, the absence of `Content-Security-Policy` removes the primary browser-side containment.

**This is the reason to fix the headers:** not the headers themselves, but the fact that they are the last layer standing in front of an already-unauthenticated write path.

---

## 5. The capability exists in-house — this is the point

The Sophos UTM protecting this very site presents **every one of these headers**, correctly configured:

```
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src https: data: ws: wss: blob: 'unsafe-inline'
                         'unsafe-eval'; worker-src 'self' blob:;
                         frame-ancestors 'self'; object-src 'none';
Server: xxxx                     ← deliberately obfuscated
```

**The team that configured the appliance knows exactly how to set these headers.** The same standard was simply never applied to the application tier behind it. This is not a knowledge problem and not a tooling problem — it is a configuration gap on one specific server.

---

## 6. Remediation

Add to the Apache configuration (or to the ASP.NET `web.config` / `Global.asax`):

```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
Header always set Cross-Origin-Opener-Policy "same-origin"
Header always unset X-Powered-By
```

`Content-Security-Policy` should be added **after** the application's own scripts are inventoried, since an over-strict policy will break the site. Deploy it in `Content-Security-Policy-Report-Only` first.

The Sophos UTM in front of the site can also inject these headers at the edge if changing the application server is inconvenient.

---

## 7. Related

- WEB-2026-009 — information disclosure (`Server`, `X-Powered-By`, `X-AspNet-Version: 4.0.30319`)
- WEB-2026-018 — unauthenticated write endpoints, including the stored-XSS candidate
- `07-phase2/infrastructure-assessment.md` §5 — the appliance-vs-application comparison
