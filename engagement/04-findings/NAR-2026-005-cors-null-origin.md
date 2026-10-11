# Finding: Misconfigured CORS policy permits the "null" origin with any method/header

- **ID**: NAR-2026-005
- **Date found**: 2026-10-11 (IST)
- **Severity**: Medium
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N` → **6.5**
- **CWE**: CWE-942 (Permissive Cross-domain Policy with Untrusted Domains)

## Affected asset
`Program.cs` — CORS policy "AllowFrontendDev", applied globally via `app.UseCors(...)`.

## Summary
The policy whitelists origins `http://localhost:5500`, `http://127.0.0.1:5500` **and the literal string `"null"`**, with `AllowAnyHeader()` + `AllowAnyMethod()`. Browsers send `Origin: null` from sandboxed iframes (`<iframe srcdoc>`, `sandbox` attribute) and certain redirect/data-URI contexts. An attacker page can therefore embed a null-origin iframe that makes cross-origin requests to this API **and reads the responses**.

Today the practical impact is masked by NAR-2026-001 (the API answers to everyone anyway), but the moment authentication is added via ambient credentials (cookies), this misconfiguration becomes a direct data-theft vector from logged-in clinicians' browsers. It must be fixed *before* shipping auth, not after.

## Steps to reproduce (safe)
Host a page containing:
```html
<iframe sandbox="allow-scripts" srcdoc="<script>
fetch('https://<host>/api/Patients/lookup/TEST').then(r=>r.text()).then(t=>parent.postMessage(t,'*'));
</script>"></iframe>
```
Observe the API responds with `Access-Control-Allow-Origin: null`. (Harmless lookup value; no data harvested.)

## Evidence (source)
```csharp
policy.WithOrigins("http://localhost:5500", "http://127.0.0.1:5500", "null")
      .AllowAnyHeader()
      .AllowAnyMethod();
```

## Remediation
1. Remove the `"null"` origin entirely; restrict dev origins to Development environment only (build-time conditional).
2. Never combine permissive CORS with cookie-based auth; use explicit production origin allowlists from configuration.

## Timeline
| Date | Event |
|---|---|
| 2026-10-11 | Found (code review) |
