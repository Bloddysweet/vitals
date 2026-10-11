# Finding: No rate limiting — patient-data enumeration + AI-cost abuse ("wallet DoS")

- **ID**: NAR-2026-004
- **Date found**: 2026-10-11 (IST)
- **Severity**: Medium (High when combined with NAR-2026-001/002)
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L` → **6.5**
- **CWE**: CWE-770 (Allocation of Resources Without Limits or Throttling)

## Affected asset
All endpoints; most critically `POST /api/Vitals/extract` and `GET /api/Patients/lookup/{id}`.

## Summary
No rate limiting exists anywhere (`AddRateLimiter` is absent from `Program.cs`).

Two concrete abuses:
1. **Enumeration amplifier**: NAR-2026-002's IDOR becomes a bulk-harvest at network speed — thousands of patient lookups/second limited only by the backend.
2. **Wallet DoS**: `/api/Vitals/extract` forwards every 10 MB upload to a **paid third-party vision model** (`openrouter.ai`, model `google/gemma-3-27b-it`). An attacker can burn the company's OpenRouter credits with scripted junk uploads (or exhaust memory — the handler copies the full stream into a `MemoryStream` per request with no concurrency cap).

## Impact
- Financial loss (per-call AI billing), service degradation for real clinical users, and mass data exfiltration when chained with the IDOR findings.

## Steps to reproduce (non-abusive)
Code inspection: no `Microsoft.AspNetCore.RateLimiting` registration, no `[EnableRateLimiting]`, no upstream evidence of WAF/limits in this project. Confirm live later: issue 50 rapid `GET /api/Patients/lookup/x` requests; expect all 200/404 with zero throttling. (50 requests is well within benign bounds.)

## Remediation
1. Add ASP.NET Core rate limiter (`AddRateLimiter`, fixed-window + concurrency policies) per IP and per endpoint class; strict limits on `/extract` and `/lookup`.
2. Put an upstream gateway/WAF with bot protection in front.
3. Set budget alerts on the OpenRouter account; cache/queue extraction jobs.

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
