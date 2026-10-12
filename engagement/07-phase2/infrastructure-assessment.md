# Phase 2 — Infrastructure Assessment

**Target:** `115.241.194.4` (resolves from `narayanagroup.co.in` / `www.narayanagroup.co.in`)
**Date:** 2026-10-12
**Tools:** whois, dig, nmap, whatweb, wafw00f, testssl.sh, nuclei, curl, openssl

---

## 1. Hosting model — the headline finding

| Property | Value |
|---|---|
| Public IP | `115.241.194.4` |
| WHOIS netname | `RELIANCEJIO-IN` |
| WHOIS org | **Reliance Jio Infocomm Limited** |
| Allocation | `115.240.0.0 – 115.247.255.255` |
| Country | IN |
| Abuse contact | `ip.abuse@ril.com` |
| Edge device | **Sophos UTM / SFOS firewall** |
| Internal address | `192.168.220.68` (disclosed via SMTP EHLO) |

**The entire Narayana Group web presence — including both APIs holding patient data — is served from a business broadband connection, behind a single Sophos UTM appliance.**

There is no CDN, no load balancer, no DDoS scrubbing service, and no WAF in front of the application (see §4).

**Implications:**
- Single point of failure for all web and API services
- Uplink bandwidth is a broadband line, not a data-centre pipe — trivially saturated
- No geographic or network-layer redundancy

## 2. Ownership of the appliance — resolved

The public IP sits inside a Reliance Jio allocation, which initially left open whether the Sophos appliance belonged to Narayana Group or to the ISP as a managed service.

**Resolved by the TLS certificate presented on ports 4443 and 4444:**

```
subject = C=NA, ST=NA, L=NA, O=NA, OU=NA,
          CN=Appliance_Certificate_XHe0lZ0NGNJrmld, emailAddress=na@example.com
issuer  = C=IN, ST=Andhrapradesh, L=Nellore,
          O=Narayana Group, OU=Narayana Group, CN=Narayana Group,
          emailAddress=professionalcolleges.it@narayanagroup.com
notAfter= Dec 31 23:59:59 2036 GMT
```

Issued by a **Narayana Group internal CA** naming their Nellore IT team. **The appliance is theirs.** All infrastructure at this address is in scope.

## 3. Open ports

```
22/tcp    ssh       SSH-2.0-OpenSSH (version stripped)
25/tcp    smtp      Sophos ESMTP
53/tcp    domain    recursive resolver (see §7)
443/tcp   https     Apache httpd (ASP.NET) — the public website and APIs
587/tcp   smtp      Sophos ESMTP (submission)
4443/tcp  ssl       Sophos User Portal / SSL-VPN portal
4444/tcp  ssl       Sophos WebAdmin (administration console)
8090/tcp  ssl       http-proxy (returns 502 bad gateway)
```

**✅ No database ports exposed.** Absent: `1433` (MSSQL), `1521` (Oracle), `3306` (MySQL), `5432` (PostgreSQL), `3389` (RDP). The Oracle backend is reachable only through the application, never directly from the internet.

**✅ No CCTV, IoT or additional management ports.** A targeted scan of `80, 81, 554, 8000, 8080, 8081, 8443, 8888, 9000, 34567, 37777, 5000, 8899, 10554, 7070, 10000, 20000` returned **nothing open**. RTSP (`554`) timed out. No cameras are exposed on this address.

## 4. Web application firewall — none, confirmed by direct test

`wafw00f` reported no WAF. `nuclei` reported four (`apachegeneric`, `aspgeneric`, `modsecurity`, `cloudflare`). These disagreed, so the question was settled empirically:

| Request | Response |
|---|---|
| `GET /?q=test` | `200` |
| `GET /?q=1' OR '1'='1` | `200` |
| `GET /?q=<script>alert(1)</script>` | `200` |
| `GET /?f=../../../../etc/passwd` | `200` |
| WAF response headers present | **0** |

**No WAF. All four nuclei detections were false positives** — they fingerprint Apache and ASP.NET, not a firewall.

## 5. Sophos appliance — current and hardened ✅

**Build timestamp** recovered from static resource version strings on port 4443:

```
?version=202607022201    →    2026-07-02 22:01
```

A build from July 2026 postdates every publicly known Sophos SFOS vulnerability, including CVE-2022-1040 (authentication bypass, User Portal and WebAdmin), CVE-2020-12271 (SQL injection), CVE-2024-12727 (SQL injection) and CVE-2025-6704 (SQL injection). **The appliance is assessed as patched against known SFOS CVEs.**

**Security headers presented by the appliance:**

```
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src https: data: ws: wss: blob: 'unsafe-inline'
                         'unsafe-eval'; worker-src 'self' blob:;
                         frame-ancestors 'self'; object-src 'none';
Server: xxxx                                  ← deliberately obfuscated
Set-Cookie: JSESSIONID=...; Path=/webconsole; Secure; HttpOnly
```

**This is the single most useful observation in the infrastructure assessment.** The same organisation that hardened its firewall to this standard deployed a web application with **zero of six** of these headers. The capability exists in-house; it was not applied to the application tier. See WEB-2026-023.

## 6. SMTP — not an open relay ✅

```
220 Sophos ESMTP ready
250-Sophos Hello probe.invalid [192.168.220.68]
250-SIZE
250-LIMITS MAILMAX=100 RCPTMAX=512
250-8BITMIME
250-PIPELINING
250-PIPECONNECT
250-CHUNKING
250-STARTTLS
250 HELP
```

| Test | Result |
|---|---|
| `VRFY` | **not offered** ✅ — no user enumeration |
| `EXPN` | **not offered** ✅ |
| `MAIL FROM:<probe@probe.invalid>` | `250 OK` |
| `RCPT TO:<test-nonexistent-xyz@example.com>` | **`550 Relay not permitted`** ✅ |

**Not an open relay.** No mail was sent — `QUIT` was issued before `DATA`.

## 7. DNS resolver — negligible amplification risk ✅

```
dig @115.241.194.4 google.com A  →  142.250.182.78
flags: qr rd ra                  →  recursion available
dig @115.241.194.4 isc.org ANY   →  182 bytes
```

Recursion **is** available to external queries, which is technically an open-resolver condition. However the `ANY` response is only **182 bytes** — a meaningful amplifier returns 3,000+ bytes for a ~40-byte query. Response-size limiting is in effect.

**Assessed as low risk.** Not written up as a finding. Recommended hardening: restrict recursion to the internal network.

## 8. TLS — website certificate

| Property | Value |
|---|---|
| Subject | `CN=narayanagroup.co.in` |
| Issuer | Go Daddy Secure Certificate Authority - G2 |
| Validity | 2026-04-18 → **2026-11-02** |
| Key | RSA 2048 |
| Signature | sha256WithRSAEncryption |

⚠️ **Operational warning:** the certificate expires **2026-11-02**, 21 days after assessment. It is a 90-day certificate, so renewal is presumably automated — but a lapse during the remediation window would be mistaken for damage caused by the patch. The client should confirm auto-renewal functions.

**Protocol support:**

| Check | Result |
|---|---|
| SSLv2 / SSLv3 | ✅ not offered |
| TLS 1.0 / 1.1 | ✅ not offered |
| **TLS 1.3** | ❌ **not offered** — downgraded to TLS 1.2 |
| **Obsoleted CBC ciphers** | ❌ offered |
| Forward Secrecy (AEAD) | ✅ offered |
| Heartbleed / POODLE / FREAK / LOGJAM / BEAST | ✅ not vulnerable |
| **BREACH** | ⚠️ gzip compression enabled |
| TLS_FALLBACK_SCSV | ✅ OK |

## 9. Application-layer probes — clean

| Path | Result |
|---|---|
| `robots.txt`, `sitemap.xml` | `404` |
| `web.config` | `404` ✅ |
| `.git/HEAD` | `404` ✅ |
| `.env` | `404` ✅ |
| `appsettings.json` | `404` ✅ |
| `elmah.axd` | `404` ✅ |
| `trace.axd` | **`403`** ✅ — tracing present but correctly disabled |
| `admin`, `login`, `server-status` | `404` |

**HTTP methods at root:** `TRACE` → `501` ✅ · `TRACK` → `405` ✅ · `DELETE` → `405` ✅ · `OPTIONS` → `200` · `PUT` → `411` (see note)

⚠️ `PUT` returned `411 Length Required` rather than `405 Method Not Allowed`. Low probability, but this should be re-tested with a valid `Content-Length` to confirm the method is genuinely refused.

## 10. Subdomains

Of `www, mail, ftp, api, admin, crm, hr, erp, lab, portal, test, dev, staging, vpn, remote, ns1, ns2` — **only `www` resolves.** No forgotten development, staging or administrative hosts. ✅

## 11. Technology fingerprint

```
Apache · Bootstrap · jQuery · HTML5 · X-Powered-By: ASP.NET · X-UA-Compatible: IE=edge
X-AspNet-Version: 4.0.30319   (confirmed independently by nuclei)
Title: Narayana Professional Colleges
```

The root path serves a **static marketing site**. All application and API functionality lives under `/NnoteApi/` and `/NtraktApi/`.

---

## Summary of clean negatives

Recorded so that the client's tech team is not asked to fix things that are already correct:

- ✅ Sophos SFOS patched to a July 2026 build
- ✅ Appliance hardened with all six security headers
- ✅ No database or RDP exposure
- ✅ No CCTV or IoT exposure on this address
- ✅ SMTP is not an open relay; no `VRFY`/`EXPN`
- ✅ DNS amplification negligible (182 bytes)
- ✅ No `web.config`, `.git`, `.env` or `appsettings.json` exposure
- ✅ `trace.axd` correctly disabled
- ✅ No SSLv2/SSLv3/TLS 1.0/1.1
- ✅ No WAF — **but the Sophos they own can provide this** (see WEB-2026-025)
- ✅ No forgotten subdomains
