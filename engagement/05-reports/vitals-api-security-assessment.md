# Security Assessment — VitalsApi (Narayana Group)

- **Assessment date**: 2026-10-11
- **Method**: Static source-code review (full codebase of `VitalsApi` .NET 10 solution) + passive OSINT (GitHub exposure check)
- **Target system**: VitalsApi — ICU patient-vitals capture/dashboard API (ASP.NET Core, Oracle DB, OpenRouter vision model integration, NMIS hospital-system integration)
- **Assessor**: (your name), authorized engagement per `00-admin/` authorization document
- **Status note**: Findings are code-review confirmed. Items marked *requires live confirmation* need a single safe verification request against the deployed instance (see §4) before client submission.

---

## 1. Executive summary

The VitalsApi service exposes **hospital patient data and clinical chart write/delete operations with no authentication of any kind**. Any person on the network where this API is reachable can read ICU charts, look up in-patient demographics from the hospital's internal NMIS system, falsify vital-sign and medication entries, and delete records. There is no authorization model, no rate limiting, and a misconfigured CORS policy. Because this is a **clinical system**, the integrity failures carry direct patient-safety risk, and the confidentiality failures constitute a breach under India's DPDP Act 2023.

**Headline result: 1 Critical, 3 High, 2 Medium, 1 Informational.**

## 2. Findings register

| ID | Title | Severity | CVSS | Status |
|---|---|---|---|---|
| NAR-2026-001 | Unauthenticated access to entire patient-vitals API | **Critical** | 9.8 | live confirmation needed |
| NAR-2026-002 | IDOR — enumerable sequential IDs (read/delete any record) | High | 8.6 | live confirmation needed |
| NAR-2026-003 | Unauthenticated proxy into internal NMIS over cleartext HTTP | High | 8.6 | live confirmation needed |
| NAR-2026-004 | No rate limiting → enumeration + AI-cost ("wallet DoS") abuse | Medium–High | 6.5 | code-confirmed |
| NAR-2026-005 | CORS policy permits `null` origin with any method | Medium | 6.5 | code-confirmed |
| NAR-2026-006 | No validation of clinical values accepted into records | Medium | 7.5* | code-confirmed |
| NAR-2026-007 | Informational: PHI in logs, Swagger dev-gate, no audit trail, etc. | Low/Info | — | mixed |

\* escalates with NAR-2026-001 present.

Full per-finding detail (impact, reproduction, evidence, remediation, timeline) in `04-findings/NAR-2026-00X-*.md`.

## 3. Priority remediation roadmap

**Immediately (before next business day):**
1. Take VitalsApi off the public internet or firewall it to the hospital network only (mitigates NAR-001/002/003 instantly).
2. Rotate/protect the OpenRouter API key; set spend alerts.

**This sprint:**
3. Implement authentication (JWT/Identity) + `[Authorize]` everywhere (NAR-001).
4. Authorization model: clinician ↔ patient scope; non-guessable IDs; block cross-patient access (NAR-002).
5. Authenticated + TLS service-to-service call to NMIS; remove hardcoded IP (NAR-003).

**Next sprint:**
6. Rate limiting + WAF (NAR-004); CORS cleanup (NAR-005); clinical-range validation + audit trail (NAR-006/007).

## 4. Live-verification checklist (to run when test machine is back)

All of these are **single safe GET requests** — zero risk, zero data modification:

```bash
H=https://<deployed-host>            # confirm where VitalsApi actually runs first
curl -sI  $H/                        # security headers: HSTS/CSP/XFO absent?
curl -s   $H/openapi/v1.json -o /dev/null -w '%{http_code}\n'   # 200 = dev docs exposed (NAR-007.2)
curl -s   $H/swagger -o /dev/null -w '%{http_code}\n'
curl -s   "$H/api/Patients/lookup/<test-id>"                    # 200 w/ data, no auth = NAR-001/003 confirmed
curl -s   "$H/api/HourlyVitals/patient/<test-id>/date/2026-10-11"  # read-only confirmation of NAR-001
```
Rules: use only test/dummy patient IDs; **never** POST/DELETE during verification; capture responses as evidence into `04-findings/evidence/`.

## 5. Open questions for the client

1. Where is VitalsApi deployed (narayanagroup.co.in? a subdomain? hospital LAN only?) — this determines the exposure level of every finding above.
2. Is `ASPNETCORE_ENVIRONMENT=Development` on the production host?
3. How is the OpenRouter key stored in production?

---
*Report compiled 2026-10-11. Raw evidence: source review of VitalsApi solution (git rev: see repo), GitHub OSINT pass (no leaks found).*
