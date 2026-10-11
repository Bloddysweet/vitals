# Finding: Unauthenticated access to entire patient-vitals API (read, modify, delete medical records + PII)

- **ID**: NAR-2026-001
- **Date found**: 2026-10-11 (IST)
- **Severity**: Critical
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` → **9.8**
- **CWE**: CWE-306 (Missing Authentication for Critical Function), CWE-862 (Missing Authorization)
- **Status**: New (code review — requires live confirmation)
- **Method**: Source-code review of `VitalsApi` (.NET / ASP.NET Core, Oracle backend)

## Affected asset
All API endpoints of the VitalsApi service:
- `POST /api/HourlyVitals/confirm` — create/overwrite patient vital-sign records
- `GET  /api/HourlyVitals/patient/{patientIdentifier}/date/{date}` — read any patient's hourly vitals
- `DELETE /api/HourlyVitals/{entryId}` — delete any vital-sign record
- `GET  /api/Patients/lookup/{id}` — retrieve patient PII (name, sex, age, bed, department, doctor, admission date)
- `POST /api/Vitals/extract` — image upload → paid third-party AI API

## Summary
The application registers `app.UseAuthorization()` in `Program.cs` but configures **no authentication scheme whatsoever** — no `[Authorize]` attributes, no JWT/API-key/session middleware, no filters. Every controller action is anonymously reachable by anyone who can reach the service. There is no role concept (nurse/doctor/admin) anywhere in the codebase.

## Impact
This is a **patient-safety and medical-privacy** failure, not just a data breach:
1. **Confidentiality**: any internet user can enumerate patient identifiers and read full ICU charts (vitals, medications incl. vasopressor infusions, ventilation settings, GCS) and demographic PII.
2. **Integrity**: any internet user can **falsify** a patient's vitals or medication records (e.g., overwrite heart rate, insulin, adrenaline dosage fields). Clinicians relying on this dashboard could make treatment decisions on attacker-manipulated data — direct risk of patient harm.
3. **Availability**: any internet user can delete medical records (see NAR-2026-002).
4. Regulatory exposure under India's DPDP Act 2023 and medical-record confidentiality norms.

## Steps to reproduce (against deployed instance — safe, read-only)
1. `GET https://<host>/api/HourlyVitals/patient/<known-or-guessed-id>/date/2026-10-11`
2. Observe HTTP 200 with full chart data returned with no credentials, cookies, or tokens.
3. `GET https://<host>/api/Patients/lookup/<id>` returns patient demographics likewise.
> ⚠️ Do NOT exercise POST/DELETE for confirmation — code path is unambiguous; live confirmation of read access is sufficient evidence.

## Evidence (source)
- `Program.cs`: pipeline is `UseCors → UseAuthorization → MapControllers` with zero authentication services registered; no `AddAuthentication(...)` call exists anywhere in the project.
- `Controllers/HourlyVitalsController.cs`, `Controllers/PatientsController.cs`, `Controllers/VitalsController.cs`: no `[Authorize]`/`[AllowAnonymous]` attributes; all actions public.
- Frontend `wwwroot/icu-dashboard.html` calls all endpoints with plain `fetch()`, sending no credentials.

## Remediation
1. Implement authentication immediately (ASP.NET Core Identity / JWT bearer / API gateway auth) and mark all controllers `[Authorize]`.
2. Add role-based authorization: read-only roles vs. clinical-write roles; enforce that a user can only access patients under their care unit (fix the IDOR, NAR-2026-002).
3. Require re-authentication/MFA for destructive operations (DELETE) and for medication fields.
4. Until auth ships: take the API off the public internet (firewall/VLAN allow-list for hospital network only).

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
| | Reported to client |
