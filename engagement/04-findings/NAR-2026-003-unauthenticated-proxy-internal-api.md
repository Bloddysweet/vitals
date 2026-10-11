# Finding: Unauthenticated public proxy into internal hospital patient system (NMIS) over plaintext HTTP

- **ID**: NAR-2026-003
- **Date found**: 2026-10-11 (IST)
- **Severity**: High
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N` → **8.6**
- **CWE**: CWE-200 (Exposure of Sensitive Information), CWE-319 (Cleartext Transmission), CWE-918-adjacent (confused-deputy proxying)

## Affected asset
- `Services/HospitalPatientService.cs` → hardcoded `http://115.241.194.2/nmis_api/api/Patient/ipdetails`
- Exposed via `GET /api/Patients/lookup/{id}`

## Summary
The public API acts as an unauthenticated relay from the internet into the hospital's internal patient-management system ("NMIS"), which:
1. Speaks **plaintext HTTP** (patient data in cleartext on the wire — trivially intercepted on any shared/compromised network segment).
2. Is addressed by a **hardcoded internal IP**, disclosed in source, narrowing any attacker's reconnaissance.
3. Requires **no credentials** — the VitalsApi forwards arbitrary caller-supplied `input` values (URL-encoded, so no injection, but unlimited lookups) and returns the full patient record: name, sex, age, bed, department, treating doctor, admission date, case type.

Because NAR-2026-001 means `/api/Patients/lookup` needs no auth, **anyone on the internet can query the hospital's in-patient registry through this API** even if `115.241.194.2` itself is firewalled off from the internet.

## Impact
- Directory of in-patients (who is admitted, where, under which doctor) — high-value information for targeted scams/social engineering against patients' families, and a DPDP Act 2023 breach.
- Cleartext transmission of PHI between the two systems.
- The API becomes a pivot point: compromise of the Vitals host exposes the internal 115.241.0/24 segment topology.

## Steps to reproduce (safe)
1. `GET https://<host>/api/Patients/lookup/<id>` returns demographics with no authentication.
2. Source confirms the upstream is `http://115.241.194.2/nmis_api/...` with no auth header ever attached.

## Evidence (source)
```csharp
private const string BaseUrl = "http://115.241.194.2/nmis_api/api/Patient/ipdetails";
...
var url = $"{BaseUrl}?input={Uri.EscapeDataString(input)}";
var response = await _httpClient.GetAsync(url, cancellationToken);
```
No credentials, no client certificate, no mTLS anywhere in the project.

## Remediation
1. Move NMIS integration to authenticated service-to-service calls (API key / mTLS), with the calling identity logged.
2. Enforce TLS (`https`) for the internal API; no cleartext PHI on the wire.
3. Rate-limit and audit every lookup; alert on enumeration patterns.
4. Do not hardcode internal infrastructure addresses in application source — use configuration/secret store.

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
