# WEB-2026-022 — Unauthenticated Retrieval of Employee Photographs by Employee ID (Scanned Identity Documents With EXIF Metadata)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-022 |
| **Severity** | **HIGH** |
| **CVSS v3.1 Score** | **7.5** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`) |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-359 (Exposure of Private Personal Information) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control |
| **Affected Targets** | `https://narayanagroup.co.in/NtraktApi/api/User/ShowPicture/{id}` |
| **Status** | ✅ **CONFIRMED — photographs retrieved, viewed and hash-verified** |
| **Verified Instances** | 3 distinct employee photographs, 3 distinct SHA/MD5 hashes |
| **Phase** | Phase 2 (2026-10-12) |

---

## 1. Summary

`/NtraktApi/api/User/ShowPicture/{id}` returns an **employee photograph** with no authentication, where `{id}` is the 8-digit `EmployeeId`.

Three separate employee IDs returned three **different** photographs — confirmed by MD5 hash and by differing file sizes and pixel dimensions. The images were opened and visually verified during testing.

The photographs carry **EXIF metadata** identifying the scanner hardware and scan timestamp, indicating they were **batch-scanned from physical identity documents**.

This chains directly with **WEB-2026-016** (`employee/hodlist`), which supplies the `EmployeeId` values together with each employee's name, date of birth, mobile number, department and designation. Together the two endpoints yield a complete staff dossier: **photograph + full name + date of birth + mobile + job title + department**, for every employee whose ID is known — with no authentication at any point.

---

## 2. Technical Evidence

### 2.1 Request

```bash
curl -s -o photo.jpg "https://narayanagroup.co.in/NtraktApi/api/User/ShowPicture/45605236"
```

**Result:** HTTP `200 OK`, `Content-Type: image/jpeg`, 13,626 bytes. No credentials.

### 2.2 Three distinct photographs retrieved

| `{id}` | Bytes | Format | Dimensions | DPI | MD5 |
|---|---|---|---|---|---|
| `45605236` | 13,626 | JPEG | 190 × 255 | 150 | `3ebbe43690fa9c325fa50e23abb15f99` |
| `45604917` | 76,879 | JPEG | 411 × 526 | 300 | `a545766927ff2d2b628e95f14f30637d` |
| `45604916` | 63,915 | JPEG | 410 × 527 | 300 | `5f802a23ef5c240823c9f189831806cc` |

**Three different hashes, three different sizes, three different pixel dimensions — three different people.** No photograph is stored or reproduced in this report; the hashes are recorded so the client can verify against their own records.

### 2.3 EXIF metadata

The photograph for `45605236` carries:

```
Manufacturer : Canon
Model        : CanoScan LiDE 120
Software     : IJ Scan Utility
DateTime     : 2024/01/22 18:26:27
Orientation  : upper-left
```

This is forensically informative:

- The images are **scans of physical documents**, not digital photographs
- They were **batch-scanned on 22 January 2024** using a flatbed scanner
- The organisation therefore maintains a **physical archive of employee identity documents**, the digitised copies of which are exposed here

The same scanner model (`Canon CanoScan`) appears in the `EmpPhoto` data covered by WEB-2026-002, indicating a common digitisation process across the estate.

### 2.4 ✅ Control result — the placeholder is NOT a leak

Two other endpoints were tested and **correctly ruled out**:

| Endpoint | Result | Verdict |
|---|---|---|
| `api/StudentAvailability/{id}` | Returns an identical 7,155-byte 220×220 PNG for **every** ID tested — `1`, `2`, `3`, `5`, `10`, `100`, `1000`, `3334024`, `45605236`, `99999999` | ❌ **Not a finding.** Placeholder avatar |
| `api/User/ShowPicture/3334024` | 7,155-byte PNG, **MD5 identical to the placeholder above** (`cac0548b3c83a8ff9fd292d6da1b21f1`) | ❌ **Not a finding.** Same placeholder |

This negative result is recorded deliberately. An earlier draft of this assessment characterised `StudentAvailability` as a "potential enumerable photograph endpoint"; hash comparison proved it returns a fixed default image regardless of input. **It is not a vulnerability and is not reported as one.**

### 2.5 The correct identifier space

`ShowPicture/{id}` takes the **8-digit `EmployeeId`**, not the short employee number:

| Identifier | Result |
|---|---|
| `1` | 0 bytes — empty |
| `3334024` (short employee number) | placeholder avatar |
| `45605236` (8-digit EmployeeId) | **real photograph** |

Valid `EmployeeId` values are supplied by `api/employee/hodlist/{id}` (WEB-2026-016) in the `EmployeeId` field, meaning **no guessing is required** — the two endpoints chain directly.

---

## 3. Impact

### 3.1 Complete staff identity package

Combined with WEB-2026-016, an unauthenticated caller can assemble for each employee:

```
photograph · full name · date of birth · mobile number · employee number
department · designation · date of joining
```

That is sufficient for **identity fraud**, **account-recovery attacks** against the employee's other accounts, and **convincing impersonation**.

### 3.2 Physical impersonation

A photograph plus name and job title allows an attacker to **create a convincing fake ID badge** and enter hospital premises. Hospital staff rarely challenge a badge bearing a real name, real department and a genuine photograph of the person carrying it.

### 3.3 Biometric and facial-recognition risk

Facial images are biometric data under most modern privacy regimes. Once disclosed they cannot be revoked, and they enable:
- Cross-matching against social media and public image sets
- Watchlist building
- Deepfake or synthetic-identity construction for video-call fraud

### 3.4 Targeted social engineering

With a photograph, an attacker can pose as a specific named employee in video calls or in person — a materially stronger attack than impersonation without an image.

### 3.5 Enumeration and scale

`EmployeeId` values are served in bulk by `employee/hodlist` (17 records per request). An attacker can enumerate employees and retrieve each photograph in turn. There is **no rate limiting and no logging**, so bulk harvesting would be neither throttled nor detectable.

### 3.6 Document-origin risk

Because the images originate from scanned **identity documents** (per the EXIF), the exposed files may contain more than a facial image — potentially document borders, printed names, ID numbers or signatures captured in the scan. This raises the sensitivity above that of a casual staff photograph.

---

## 4. Steps to Reproduce

```bash
# 1. Obtain valid EmployeeId values (no auth)
curl -s "https://narayanagroup.co.in/NtraktApi/api/employee/hodlist/3334024"

# 2. Retrieve that employee's photograph (no auth)
curl -s -o photo.jpg "https://narayanagroup.co.in/NtraktApi/api/User/ShowPicture/45605236"
file photo.jpg
md5sum photo.jpg
```

---

## 5. Remediation

### Immediate

1. **Require authentication and authorisation on `api/User/ShowPicture/{id}`.** Until then, block the path at the reverse proxy or WAF.
2. **Add authorisation scoping.** A caller should retrieve only their own photograph, or photographs within their authorised management scope — not any ID supplied.
3. **Serve images indirectly.** Replace direct ID lookup with an authorisation-checked, non-enumerable, rate-limited endpoint.

### Short term

4. **Strip EXIF metadata on upload or on serve.** Scanner model, software and timestamps have no operational value to a caller and assist attacker reconnaissance.
5. **Rate-limit and log** all photograph retrieval. Bulk image harvesting should be an alertable event.
6. **Re-examine the digitisation process.** A January 2024 batch scan of physical identity documents produced an archive that is now internet-reachable. Whatever store holds the originals should be reviewed with the same rigour as the API.

### Structural

7. **Apply estate-wide authentication** (closes 001, 002, 003, 012, 013, 015, 016, 017, 018, 020, 021, 022).
8. **Treat facial images as restricted data** in the data model, so they cannot be emitted by default.

---

## 6. Testing Ethics and Data Handling

- **Three photographs were retrieved** — the minimum needed to prove that distinct IDs return distinct images.
- The images were **opened and visually confirmed** by the assessor, then **deleted from the working directory**.
- **No photograph is stored in the assessment repository.** Only file sizes, dimensions, formats and MD5 hashes are recorded, so the client can verify against their own records without the images crossing into the report.
- **No bulk enumeration was performed.** No ID range was walked.
- **No data was created, modified or deleted.**
- The negative control (§2.4) was run specifically to avoid reporting a false positive, and is documented as such.

---

## 7. Related Findings

- **WEB-2026-016** — `employee/hodlist` supplies the `EmployeeId` values, names, dates of birth and mobile numbers
- **WEB-2026-002** — `User/Info/{id}` returns `EmpPhoto` (Canon CanoScan EXIF) — the same imagery through a different endpoint
- **WEB-2026-021** — Patient photographs (`PatPhoto`) exposed — the patient-side equivalent
- **WEB-2026-018** — Unauthenticated write access on the same surface

---

*Finding recorded: 2026-10-12 · Phase 2 deep assessment · **Confirmed — photographs retrieved and hash-verified***
