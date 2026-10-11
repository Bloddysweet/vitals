# Security Testing Engagement — Charter

> Fill this in and store it in `00-admin/` together with the signed authorization letter
> BEFORE any active testing begins. This is the document that makes everything legal.

## 1. Parties

| Role | Name | Organization | Contact (phone/email) |
|---|---|---|---|
| Client / asset owner | | Narayana Group | |
| Authorized tester | | | |
| Emergency contact (client side) | | | |

## 2. Authorization

- Written authorization document: ____________ (filename in this folder, e.g. `authorization.pdf`)
- Signed by (name + title, must be someone with authority over the assets): ____________
- Date signed: ____________
- Validity window: **from** ____________ **to** ____________

## 3. Scope

**In scope (test these):**
- `https://narayanagroup.co.in`
- `*.narayanagroup.co.in` (all subdomains owned/operated by Narayana Group)
- IP(s) operated by Narayana Group hosting the above: `115.241.194.4` (confirm + add others during recon)
- APIs/admin panels belonging to the above hosts

**Out of scope (do NOT test; report only if found):**
- Third-party services (email/SMTP providers, payment gateways, CDN/WAF providers, analytics, social media integrations)
- DoS / stress testing of any kind
- Social engineering, phishing, physical security
- Employee devices and internal networks not listed above
- Destructive operations (deleting/modifying production data)

## 4. Rules of engagement

1. Testing performed only from tester's machines; tester's source IP(s): ____________ (give to client so traffic is attributable).
2. Testing window: ____________ (e.g., "any time" or "weekdays 10:00–18:00 IST").
3. Scanner intensity: low-to-moderate; no aggressive rate settings against production.
4. Stop-on-demand: client may halt testing at any time via the emergency contact; tester complies immediately.
5. Data handling: any sensitive data accessed is logged minimally, never copied off the engagement machines, and destroyed at handover.
6. Critical findings (RCE, SQLi with data access, auth bypass): notify client emergency contact **within 24h**, full write-up within 72h.
7. Public disclosure: not permitted without written client approval (or per agreed disclosure policy: ____).

## 5. Deliverables

- [ ] Findings log (`04-findings/`, one file per finding)
- [ ] Final report with remediation guidance (`05-reports/`)
- [ ] Raw evidence archive
- [ ] Handover call / presentation (optional)

## 6. Logbook

| Date | Activity | Tools | Notes |
|---|---|---|---|
| | | | |
