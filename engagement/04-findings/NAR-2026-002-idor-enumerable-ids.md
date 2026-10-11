# Finding: IDOR — enumerable sequential IDs expose/delete any patient's records

- **ID**: NAR-2026-002
- **Date found**: 2026-10-11 (IST)
- **Severity**: High
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L` → **8.6** (High; escalates with NAR-2026-001)
- **CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)
- **Status**: New (code review — requires live confirmation)

## Affected asset
- `DELETE /api/HourlyVitals/{entryId}` — `entryId` is a sequential database integer (`ValueGeneratedOnAdd`, `int`)
- `GET /api/HourlyVitals/patient/{patientIdentifier}/date/{date}` — `patientIdentifier` is a user-controlled string with no ownership check
- `GET /api/Patients/lookup/{id}` — hospital PR/IPatient numbers are typically sequential or guessable

## Summary
Object references are direct, sequential, and fully attacker-controlled, and there is no ownership/authorization check anywhere. Combined with no authentication (NAR-2026-001):
- Record IDs start near 1 and increment by 1 → the entire table can be walked with a loop (`for id in 1..N: DELETE ...`).
- Patient identifiers from the hospital system (PR numbers) can be enumerated via the lookup endpoint.

## Impact
- Mass deletion of ICU charts (availability + potential destruction of legal medical records).
- Mass harvesting of patient PII and clinical data (privacy breach at scale).
- Attack is trivially scriptable and low-noise (small GET/DELETE requests).

## Steps to reproduce (safe demonstration only)
1. Retrieve any entry (e.g., via the dashboard while logged in as intended user, or via NAR-001 read access).
2. Note the integer `entryId` in the JSON response.
3. `GET /api/HourlyVitals/patient/<other-patient-id>/date/<today>` succeeds for a *different* patient — proof of missing ownership check.
> ⚠️ Do NOT actually call DELETE during testing. The authorization-absence is fully evidenced by source; destructive PoC is prohibited by the engagement RoE.

## Evidence (source)
- `VitalsDbContext.cs`: `entity.Property(e => e.EntryId).ValueGeneratedOnAdd();` (sequential int PK)
- `HourlyVitalsController.DeleteEntry(int entryId)`: looks up purely by caller-supplied ID, no user/ownership context exists at all.
- `GetEntriesForDate(string patientIdentifier, ...)`: caller supplies any identifier; no scoping to an authenticated clinician.

## Remediation
1. Fix NAR-2026-001 first (auth).
2. Enforce authorization on every access: clinician ↔ patient care-unit mapping; reject out-of-scope patient IDs with 403/404.
3. Replace sequential public IDs with non-guessable references (GUIDs) for anything exposed over the wire; never expose raw DB keys.
4. Rate-limit lookups (NAR-2026-004) to blunt enumeration.

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
