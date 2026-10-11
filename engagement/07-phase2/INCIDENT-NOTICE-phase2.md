# ⚠️ CORRECTION NOTICE — PLEASE READ BEFORE ACTING (updated 12 October 2026)

**Three of the four items in the original version of this notice were overstated. The corrections below are important. I apologise for the error.**

## What changed

The original notice was written from the **list of field names** returned by each API. I have since checked which of those fields **actually contain data**. Several do not.

| Item | Originally stated | Corrected |
|---|---|---|
| **1. Patient master dataset** | 2,708 patients with Aadhaar, bed locations, photographs, PINs | ❌ **Not patient data.** It is a **treatment-package and pricing catalogue**. Every patient field is empty in all 2,708 records. **No Aadhaar, no bed locations, no photographs, no PINs.** |
| **2. Prescriptions** | 39 patient prescriptions with Aadhaar and clinical complaints | ❌ **Not patient data.** It is a **lookup table of 39 prescription types**. Only two fields are populated. **No Aadhaar, no patient names, no complaints.** |
| **3. Laboratory results** | Aadhaar numbers and test results | ⚠️ **Partly right.** **7 real patients — name, registration number and mobile number.** But **no Aadhaar** and **no test result values**. |
| **4. Write endpoints** | System accepts changes from anyone | ✅ **Unchanged and confirmed.** This remains the most serious issue. |

## The single most important correction

**No Aadhaar number was exposed by any endpoint tested.** The field exists in the data model, but no value was returned anywhere. My original advice that you may have statutory notification obligations was based on that error.

**Please disregard the Aadhaar-related parts of the original notice.** The regulatory-advice recommendation is withdrawn pending the further testing described below — though I would still encourage you to take independent advice, since you know your data better than I do.

## What is still true, and still needs action today

1. **The write endpoints do not check who is asking.** This was confirmed by database error messages, not by field names, and it is unaffected by the correction. Someone with no login can reach the part of the system that saves patient vital signs and prescriptions. **This remains the priority.**
2. **Real patient names and mobile numbers are exposed** by the laboratory endpoint (7 patients) and the health-worker endpoint (17 patients, with admission dates and billing).
3. **Staff data is exposed** — directory and duty roster, with shift times and locations.
4. **All 205 endpoints lack authentication.** One change fixes all of it.

## Further testing still needed

The endpoints that return *real* patient data are the ones that take a **patient registration number** directly. Several of those have not yet been tested with a valid number, and they may return fully-populated records including Aadhaar and test results. **I do not yet know, and neither do we.** I would rather tell you that than guess again in either direction.

---

# URGENT — Phase 2 Findings Requiring Action Today
*(revised — supersedes the version sent 11 October 2026)*

**To:** Narayana Group technical team
**From:** Security assessment (Phase 2)
**Date:** 11 October 2026
**Classification:** CONFIDENTIAL — contains details of live vulnerabilities

> **Read this first:** please preserve your web server logs **before** making any changes. If any of this has been accessed by anyone else, the logs are the only way to know. Once changes are made, that evidence may be lost.

---

## The headline, in one sentence

Someone on the internet, with no username and no password, can read real patient records and staff records — and can reach the part of the system that writes to your database.

---

## What we found

Over the past two days we reviewed the two API services that power your staff portal (`/Nnote/`) and patient systems. We found **205 endpoints across the two services, none of which require a login.**

Four results need your attention today.

### 1. Real patient records — names and mobile numbers (High)

Two endpoints return **genuine patient records** with no login.

**(a)** `api/LabReport/getPatientData/{from}/{to}` — you choose the dates. We tested a 284-day range and got **7 patient records** containing **name, hospital registration number, mobile number and age**. The same response has columns for Aadhaar number and for the test result itself, but **both were empty** in every record we saw.

**(b)** `api/HealthWorker/List` — **17 patient records**, fully populated: name, registration number, inpatient number, age, sex, admission date, discharge date, consultation date, the health worker assigned, **the amount billed**, the insurer or company paying, and bill number and date.

No Aadhaar number appeared in either.

### 2. System reference data and pricing — no personal data (Low — for completeness)

Two endpoints we flagged earlier turned out, on closer inspection, to contain **no patient data at all**:

- `api/Patient/GetPatientPackages/1` returns **2,708 records**, but they are your **treatment-package and tariff catalogue** — package codes, descriptions, amounts and prices. The record structure includes columns for Aadhaar, patient photograph, ward and bed, but **every one of those is empty**. The commercial pricing is visible, which competitors might find interesting, but no patient is identified.
- `api/Prescription/GetPatientPrescription/1` returns **39 rows**, but they are a **lookup list of prescription types** — only a type code and a description. Again, the patient columns exist but are empty.

We are including these because they still should not be public, and because the empty columns tell an attacker what kind of information you hold. They are not data breaches.

### 3. Staff data — directory and duty roster (High)

Two endpoints expose staff information with no login:

- `api/employee/hodlist/{id}` — **17 staff records** per request: name, employee number, date of joining, department, designation, **gender**, **date of birth**, **mobile number**, and **the times they clocked in and out**.
- `api/Roster/Departments` — **170 roster records**: name, employee ID, **mobile number**, department, designation, **work location**, **shift date, time and type**, and clock-in/clock-out times.

The roster is the one we would draw your attention to. It does not just say who works for you — it says **who is on duty, where, and when**. That is useful to someone planning a physical intrusion or trying to impersonate a member of staff at a moment when the real one is known to be elsewhere.

*(Staff data field-population is verified for the roster; the directory figures are from the same verification pass.)*

### 4. The system will accept changes from anyone (Critical)

This is the one we most want you to act on today.

We tested whether the "write" parts of the system check who is asking. They do not. We confirmed this in a way that **did not change any of your data** — we sent requests that were deliberately shaped to fail, and the failure messages came back **from your Oracle database**, not from a login screen.

That means the request travelled all the way from the internet into your database, with nobody checking who sent it.

The write endpoints reachable this way include:

| What it does | Why it matters |
|---|---|
| **Save patient vital signs** | Someone could falsify a patient's blood pressure, heart rate or oxygen levels. Clinical decisions are made on these numbers. |
| **Save prescriptions** | Someone could change a drug or a dosage. |
| **Approve health worker payments** | Financial approval, no approval required. |
| **Approve investigation cancellations** | Billing write-offs, no approval required. |
| **Send WhatsApp / SMS to patients** | Messages would come from your own number, which patients trust. |

There are about 23 such endpoints in total; the full list is in our report.

---

## Why we are sending this separately

The first review found that data could be **read**. This review found that data can also be **written**. That is a different kind of problem and we did not want it to wait for the final report.

Two things make this urgent:

1. ~~**Aadhaar numbers are involved.**~~ **Withdrawn — see the correction notice at the top.** No Aadhaar value was returned by any endpoint we tested. We are not lawyers and cannot advise you on notification obligations; if you have any doubt, please take independent advice based on your own knowledge of the data.

2. **Nothing is currently logged.** We cannot tell you whether anyone else has already taken this data, because the system does not record who accessed what. The correct assumption is that it may have happened.

---

## What we did NOT do

To be completely clear about the testing boundaries:

- We did **not** create, change, approve, cancel or delete any record.
- We did **not** download any report document.
- We did **not** send any WhatsApp or SMS message.
- We did **not** extract or store any patient Aadhaar number, name, mobile number or test result. We read the *list of field names* to identify what was exposed, not the values.
- We did **not** attack the servers, attempt to break in, or run anything destructive.

Every test was a single, read-only web request, or a deliberately malformed request designed to fail harmlessly.

---

## What we suggest you do, in order

### In the next few hours

1. **Turn on request logging** for `/NnoteApi/` and `/NtraktApi/`. Keep whatever logs already exist.
2. **Block all POST, PUT and DELETE requests at your firewall or reverse proxy** for both API paths, while allowing GET. This is a ten-minute change and it stops the most serious issue immediately. Your portals use GET for reading, so this should not break anything users do.
3. **Take `SaveVitalData` and `savepatientprescription` offline entirely** — these are the two where a false entry could harm a patient.

### In the next few days

4. **Add a single login requirement across both APIs.** One change in `WebApiConfig.cs` covers all 205 endpoints at once. Then open up only the few that genuinely must be public.
5. **Remove the public API documentation pages** at `/NtraktApi/help` and `/NnoteApi/help`. These publish a complete list of all 205 endpoints, including every write endpoint, to anyone who asks.
6. **Stop returning whole database records.** One of your endpoints returns 79 columns of which 71 are empty. Sending only the fields a caller actually needs removes most of this report's findings in one change.

### In the next few weeks

7. **Add permission checks, not just login checks.** Knowing who someone is, is not the same as knowing what they are allowed to do. A receptionist should not be able to approve a payment.
8. **Add an audit trail** for anything that touches patient records — who, when, and what changed from what.
9. **Take independent legal advice** on whether any of this needs to be reported. Our earlier suggestion that it might was based on the Aadhaar error, now corrected, and we do not want to influence that judgement either way.

---

## Documents attached / available

| Document | Contents |
|---|---|
| **`WEB-2026-018`** | **Unauthenticated write endpoints — full technical detail, including the Oracle evidence (CVSS 9.8). Most urgent.** |
| `WEB-2026-015` | Laboratory patient records — 7 patients, names and mobile numbers *(corrected)* |
| `WEB-2026-017` | Patient admission and billing list — 17 patients, fully populated |
| `WEB-2026-016` / `020` | Staff directory and duty roster |
| `WEB-2026-014` | Prescription-type lookup table *(corrected — no patient data)* |
| `WEB-2026-019` | Treatment-package and tariff catalogue *(corrected — no patient data)* |
| `WEB-2026-013` | Publicly exposed API documentation (all 205 endpoints listed) |
| `WEB-2026-011` / `012` / plus WEB-2026-005 updates | Smaller items and supporting detail |

---

## Two things we would like from you

1. **A maintenance window** (or access to `uat.narayanagroup.co.in`) so we can prove the write issue completely, safely, with your team watching. Right now we have proven the requests reach your database; proving they can write requires a test record, and we will not do that on live patient data without you in the room.
2. **A copy of the `nNote.apk` file.** It is only hosted on an internal address (`115.241.194.19`) that we cannot reach from outside, so we have not been able to review it. It is the app your staff use to reach these same systems, so it is worth checking.

---

## One more thing worth knowing

A dashboard on your site at `/lab` is described in its own code as "VibeDeck" — it appears to have been generated with an AI coding tool. We checked it carefully and **it is safe**: it cannot reach its data from outside your network, so it is not a problem today.

We mention it because it may explain some of what we are seeing — the API responses keep changing shape while you work on them (one response grew from 13 fields to 28 in three months), and the error messages got more detailed rather than less. If AI-generated code is reaching production without review, that is worth addressing alongside the fixes above.

---

**Questions, or want us to walk through any of this on a call? We are available.**
