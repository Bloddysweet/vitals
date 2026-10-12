# WEB-2026-024 — Firewall Administration Console and SSL-VPN Portal Exposed to the Internet

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-024 |
| **Severity** | **Medium** |
| **CVSS v3.1 Score** | **5.3** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`) |
| **CWE** | CWE-668 (Exposure of Resource to Wrong Sphere), CWE-306 (Missing Authentication for Critical Function — *not applicable; authentication is present, exposure is the issue*) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://115.241.194.4:4443/` (Sophos User Portal / SSL-VPN) · `https://115.241.194.4:4444/` (Sophos WebAdmin) · `115.241.194.4:22` (SSH) |
| **Status** | Confirmed — 2026-10-12 |
| **Phase** | Phase 2 |

---

## 1. Summary

The Sophos UTM appliance protecting the Narayana Group network presents **three administrative interfaces directly to the internet**, unrestricted by source address:

| Port | Service | Exposure |
|---|---|---|
| **4444** | **Sophos WebAdmin — the firewall's administration console** | World-reachable |
| **4443** | Sophos User Portal / SSL-VPN | World-reachable |
| **22** | SSH (`SSH-2.0-OpenSSH`) | World-reachable |

**This is not a vulnerability in the Sophos product.** The appliance is patched to a current build and is otherwise well configured (see §4). The finding is that **the administrative console of the device protecting the entire network is reachable by any host on the internet**, which gives an attacker an unlimited, unmetered authentication surface against the highest-value device in the estate.

---

## 2. Evidence

### 2.1 Port scan

```bash
nmap -sV -sS -T3 -Pn -p 22,25,53,443,587,4443,4444,8090 115.241.194.4
```

```
22/tcp    open  ssh            SSH-2.0-OpenSSH
443/tcp   open  ssl/http       Apache httpd (ASP.NET)
4443/tcp  open  ssl/pharos?
4444/tcp  open  ssl/krb524?
8090/tcp  open  ssl/http-proxy (bad gateway)
Service Info: Device: router
```

> ⚠️ The same scan reported port 22 as `Linksys WRT45G modified dropbear sshd`. **This is a false positive** — the actual banner is `SSH-2.0-OpenSSH`. Recorded here because it is the third tool fingerprint this engagement has had to correct; tool output was verified against banners before use.

### 2.2 Port 4443 — User Portal / SSL-VPN

```
GET https://115.241.194.4:4443/  →  200 OK
Title: VPN Portal
<div id="userportal_link" ...>
1 form, 5 input fields
```

### 2.3 Port 4444 — WebAdmin

```
GET https://115.241.194.4:4444/  →  200 OK
Set-Cookie: JSESSIONID=...; Path=/webconsole; Secure; HttpOnly
/themes/lite1/css/typography.css
```

The cookie path `/webconsole` identifies this as the **Sophos WebAdmin console** — the interface used to configure firewall rules, NAT, VPN and network policy.

### 2.4 Ownership confirmed

```
issuer = C=IN, ST=Andhrapradesh, L=Nellore, O=Narayana Group,
         OU=Narayana Group, CN=Narayana Group,
         emailAddress=professionalcolleges.it@narayanagroup.com
```

Self-signed by a Narayana Group internal CA. **The appliance is theirs**, not ISP-managed equipment — remediation is within their control.

---

## 3. Impact

A world-reachable administration console provides an attacker with:

1. **Unlimited credential-guessing attempts** against the single device that controls all network traffic. Even with rate limiting, the surface is open.
2. **A landing point for future zero-day exploitation.** When the next Sophos SFOS vulnerability is published, an appliance whose console is on the internet is compromised within hours; one restricted to internal addresses is not.
3. **Reconnaissance value.** The login page discloses the product, theme and build timestamp.

If an attacker obtained administrative access to this appliance they could:
- Add firewall rules exposing internal services, including the Oracle database at `192.168.220.68`
- Intercept or modify all traffic to and from the hospital network
- Establish persistent VPN access
- Disable logging

**Note:** no authentication attempt was made during this assessment. The finding is the *exposure*, not a demonstrated authentication bypass.

---

## 4. What is working well — stated for completeness

The appliance is **not** neglected. It is among the better-configured components observed:

| Check | Result |
|---|---|
| SFOS build | **2026-07-02 22:01** — current, postdates all known Sophos CVEs |
| Known SFOS CVEs (2022-1040, 2020-12271, 2024-12727, 2025-6704) | ✅ assessed patched |
| Security headers on appliance | ✅ all six present |
| Server banner | ✅ obfuscated (`Server: xxxx`) |
| Session cookie | ✅ `Secure; HttpOnly` |
| SMTP relay | ✅ `550 Relay not permitted` |
| SMTP `VRFY` / `EXPN` | ✅ not offered |

**The appliance is well built. It is simply standing in the open.**

---

## 5. Remediation

**Primary (recommended):** restrict management access by source address.

On the Sophos UTM, under **Administration → Device Access**, remove `Any` from the permitted source networks for:
- HTTPS **WebAdmin** (4444)
- **User Portal** / SSL-VPN (4443)
- **SSH** (22)

Replace with the specific internal ranges and the static addresses of administrative staff. If remote administration is required, restrict it to the SSL-VPN address pool rather than the internet.

**Compensating controls if the consoles must stay reachable:**

- Enforce multi-factor authentication on all WebAdmin accounts
- Enable administrative lockout after a small number of failed attempts
- Alert on failed administrative logins from external sources
- Restrict SSH to key-based authentication and disable password authentication
- Enable Sophos's own brute-force protection on the user portal

**Priority:** this should be done **in the same maintenance window as the API authentication patch.** It is a configuration change on a device the team already administers competently, not a development task.

---

## 6. Related

- `07-phase2/infrastructure-assessment.md` — full infrastructure assessment
- `07-phase2/AUTHORIZATION-INFRASTRUCTURE.md` — authorization and ownership evidence
- WEB-2026-023 — the contrast between appliance hardening and application hardening
