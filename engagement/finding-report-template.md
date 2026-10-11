# Finding: <short title, e.g. "Reflected XSS on /search">

- **ID**: NAR-2026-001
- **Date found**: YYYY-MM-DD (IST)
- **Severity**: Critical | High | Medium | Low | Info
- **CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` → score __ (use https://www.first.org/cvss/calculator/3.1)
- **CWE**: CWE-___ (e.g. CWE-79)
- **Status**: New | Reported | Confirmed by client | Fixed | Retested

## Affected asset
- URL / endpoint / IP / parameter

## Summary
One paragraph: what the bug is and why it matters.

## Impact
What an attacker could do. Business terms, not just technical.

## Steps to reproduce
1. Step one
2. Step two (keep steps minimal and deterministic; a junior dev must be able to follow them)

## Evidence
- Raw request (from Burp → "copy to file" or curl)
- Raw response (trimmed to relevant parts)
- Screenshot(s): filename(s), stored in `04-findings/evidence/`

```
PUT RAW REQUEST/RESPONSE HERE
```

## Proof of concept (non-destructive only)
Safe PoC — e.g., `alert(1)` for XSS, `SELECT version()` style proof without dumping data.
Never demonstrate with real user data.

## Remediation
- Concrete fix (code/config level)
- Defense-in-depth notes
- References: OWASP link, vendor docs

## Timeline
| Date | Event |
|---|---|
| | Found |
| | Reported to client |
| | Client confirmed |
| | Fix deployed |
| | Retested — PASS/FAIL |
