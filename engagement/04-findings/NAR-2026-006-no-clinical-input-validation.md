# Finding: No validation of clinical values — medically impossible data accepted into patient records

- **ID**: NAR-2026-006
- **Date found**: 2026-10-11 (IST)
- **Severity**: Medium
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N` → **7.5** (as long as NAR-2026-001 stands; Low once auth exists)
- **CWE**: CWE-20 (Improper Input Validation)

## Affected asset
`POST /api/HourlyVitals/confirm` → `Models/ConfirmHourlyEntryRequest.cs`

## Summary
The request DTO has **zero validation attributes** (no `[Range]`, `[Required]`, `[RegularExpression]`) and the controller binds every field directly into the database entity. Entity-side constraints are only `[MaxLength]` strings. Therefore the API accepts medically absurd or hostile values, e.g. `HeartRate: -1`, `SpO2: 99999`, `Temperature: 9999.9` (precision 5,1 allows it), arbitrary strings into `Hour`/`PatientIdentifier` (up to 50 chars), or future-dated `EntryDate`.

## Impact
- Silent corruption of clinical charts. A clinician glancing at a dashboard showing `HR: 999999` may dismiss it — or worse, act on subtly falsified-but-plausible values injected by an attacker (see NAR-2026-001).
- Breaks any downstream analytics/alerting built on this data.
- Patient-safety integrity issue in a medical device-adjacent system.

## Steps to reproduce (harmless variant)
Send `ConfirmHourlyEntryRequest` with `HeartRate: 999` for a **test patient ID you own/control only**; observe 200 OK persisted. Do not touch real patient records.

## Remediation
1. Add `[Range]` constraints with physiologically sensible bounds (HR 0–300, SpO2 0–100, Temp 25.0–45.0, RR 0–200, etc.).
2. Validate `Hour` format, `EntryDate` not in future, `PatientIdentifier` against known patients server-side.
3. Return 422 with field-level errors; reject, don't clamp.
4. Add server-side audit fields (who/when/what-changed) — currently none exist, and deletes are hard-deletes, so tampering is undetectable.

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
