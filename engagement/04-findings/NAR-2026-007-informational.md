# Finding: Informational / hardening items

- **ID**: NAR-2026-007
- **Date found**: 2026-10-11 (IST)
- **Severity**: Low / Informational
- **CWE**: various
- **Status**: New

## Items

1. **Patient identifier logged at INFO level** — `HourlyVitalsController` logs `"Confirmed hourly entry for Patient {PatientIdentifier}, {Date} {Hour}"` and deletes by ID. PHI in plain log files violates minimization principles; log a pseudonymous reference instead. (CWE-532)

2. **OpenAPI/Swagger UI exposed in Development** — `MapOpenApi()` + `UseSwaggerUI()` are gated on `app.Environment.IsDevelopment()`. **Verify live**: if the deployment runs with `ASPNETCORE_ENVIRONMENT=Development` (common mistake), full API documentation is published at `/openapi/v1.json` and `/swagger`. Check on the deployed instance once access is restored.

3. **No audit trail on medical records** — `HourlyVitalEntry` has only `ConfirmedAt`; no created-by/updated-by, no soft delete. Deletion is a hard `Remove()`. Medical records should be append-mostly with immutable audit history.

4. **Upload content-type is client-asserted only** — `/api/Vitals/extract` trusts the `Content-Type` header; no magic-byte validation. Impact is low here (bytes go to a third-party model, not to disk/DB), but add image-format sniffing and consider resizing server-side before forwarding. (CWE-434-adjacent)

5. **launchSettings binds `0.0.0.0` on plaintext HTTP :5245** — fine for local dev, but verify production hosting serves HTTPS only (the app does call `UseHttpsRedirection`; confirm the 443 binding exists on the deployed host).

6. **Memory-buffering of uploads** — `ExtractVitalsAsync` copies up to 10 MB per request into a `MemoryStream` with no concurrency cap; combined with NAR-2026-004 this is a memory-exhaustion lever.

## Verified ABSENT (for the report's completeness)
- ✅ No hardcoded secrets/API keys/connection strings in source (OpenRouter key + Oracle connection string are expected via user-secrets/config — confirm production uses a secret store).
- ✅ No SQL injection: all data access through EF Core LINQ (parameterized); no raw SQL anywhere.
- ✅ No public GitHub leakage: `gh search repos narayanagroup` + code search for the domain returned no source/secret exposure as of 2026-10-11.
