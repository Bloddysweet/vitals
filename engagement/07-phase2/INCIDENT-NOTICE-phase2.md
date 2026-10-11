# URGENT — Phase 2 Findings Requiring Action Today

**To:** Narayana Group technical team
**From:** Security assessment (Phase 2)
**Date:** 11 October 2026
**Classification:** CONFIDENTIAL — contains details of live vulnerabilities

> **Read this first:** please preserve your web server logs **before** making any changes. If any of this has been accessed by anyone else, the logs are the only way to know. Once changes are made, that evidence may be lost.

---

## The headline, in one sentence

Someone on the internet, with no username and no password, can download your entire patient list — including Aadhaar numbers and **which ward and bed each patient is in right now** — and can reach the part of the system that writes to your database.

---

## What we found

Over the past two days we reviewed the two API services that power your staff portal (`/Nnote/`) and patient systems. We found **205 endpoints across the two services, none of which require a login.**

Four results need your attention today.

### 1. The full patient list — with live ward and bed locations (Critical) — **most urgent**

One web request with no login returns **2,708 patient records, 3.7 MB**. Each record has 79 fields, including:

- Patient name, date of birth, age, gender, mobile number, **Aadhaar number**
- 🔴 **Which ward and bed the patient is in right now** — `WardName`, `BedId`, `BedDescription`
- 🔴 **A photograph of the patient**
- 🔴 **Two fields called `PIN` and `ConfirmPIN`**
- Name and mobile number of the patient's attendant or family member
- Admission and discharge dates, department, doctor, patient status
- Full billing detail — tariff, package amount, itemised charges

Address: `/NnoteApi/api/Patient/GetPatientPackages/1`

**Two things in that list need action today, before anything else:**

**(a) The `PIN` fields.** Your patient portal logs patients in with a PIN. If `PIN` and `ConfirmPIN` in this response are those portal PINs — and the fact that there is a *confirm* field suggests they are — then this response provides working login details for 2,708 patient accounts. **Please check this immediately.** A safe way to tell, without reading anyone's PIN, is to check how long the values are: if they are all exactly 6 digits they are probably postcodes; if the lengths vary they are probably credentials.

**(b) Ward and bed locations.** Anyone can see exactly where a named patient is in the hospital, in real time. For patients admitted under safeguarding, domestic-violence or VIP arrangements, this is a safety-of-life issue, not just a privacy one.

A second address, `/NnoteApi/api/Patient/Camp/getcamppatientlist/…`, returns the same 79 fields for camp patients, for any date range you give it.

### 2. Patient prescriptions — readable by anyone (Critical)

A single web request with no login returns **39 patient prescription records**. Each record contains:

- Patient name, date of birth, age, gender
- **Aadhaar number**
- Mobile number
- **The doctor's notes on why the patient came in** (`ChiefComplaints`)
- The full drug prescription — molecule, brand, dosage, how long to take it

Address: `/NnoteApi/api/Prescription/GetPatientPrescription/1`

### 3. Laboratory results — readable by anyone, for any date range (Critical)

A request with no login returns patient laboratory records. Each record contains **47 fields**, including patient name, mobile number, **Aadhaar number**, the test description and **the test result itself**, plus the file path to the report document.

The caller picks the date range. A one-day range returned one record; a nine-month range returned more, and the server took 17 seconds to gather it. An attacker can walk through your laboratory records date by date.

Address: `/NnoteApi/api/LabReport/getPatientData/01-JAN-2026/11-OCT-2026`

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

1. **Aadhaar numbers are involved.** Aadhaar is protected under the Aadhaar Act 2016 and the Digital Personal Data Protection Act 2023. You may have legal obligations to notify. **We are not lawyers and cannot advise you on this — please take advice promptly.**

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

1. **Check whether `PIN` / `ConfirmPIN` are patient portal PINs.** This is the single most important question arising from this review. See §1(a) above for how to check it safely. If they are credentials, every patient portal PIN needs to be reset and patients need to be told.
2. **Turn on request logging** for `/NnoteApi/` and `/NtraktApi/`. Keep whatever logs already exist.
3. **Block all POST, PUT and DELETE requests at your firewall or reverse proxy** for both API paths, while allowing GET. This is a ten-minute change and it stops the most serious issue immediately. Your portals use GET for reading, so this should not break anything users do.
4. **Take `SaveVitalData` and `savepatientprescription` offline entirely** — these are the patient-safety ones.
5. **Block or authenticate `GetPatientPackages` and `getcamppatientlist`.** These are the two largest exposures, at 3.7 MB and 237 KB per request.

### In the next few days

4. **Add a single login requirement across both APIs.** One change in `WebApiConfig.cs` covers all 205 endpoints at once. Then open up only the few that genuinely must be public.
5. **Remove Aadhaar numbers from all API responses.** Nothing in these applications needs the Aadhaar number to display a prescription or a lab result.
6. **Remove the public API documentation pages** at `/NtraktApi/help` and `/NnoteApi/help`. These publish a complete list of all 205 endpoints, including every write endpoint, to anyone who asks.

### In the next few weeks

7. **Add permission checks, not just login checks.** Knowing who someone is, is not the same as knowing what they are allowed to do. A receptionist should not be able to approve a payment.
8. **Add an audit trail** for anything that touches patient records — who, when, and what changed from what.
9. **Get legal advice** on whether this needs to be reported.

---

## Documents attached / available

| Document | Contents |
|---|---|
| **`WEB-2026-019`** | **Patient master dataset — 2,708 records, Aadhaar, bed location, PIN fields. Most urgent.** |
| **`WEB-2026-018`** | **Unauthenticated write endpoints — full technical detail, including the Oracle evidence (CVSS 9.8)** |
| `WEB-2026-014` | Patient prescriptions and Aadhaar — full technical detail |
| `WEB-2026-015` | Laboratory results by date range — full technical detail |
| `WEB-2026-013` | Publicly exposed API documentation (all 205 endpoints listed) |
| `WEB-2026-016` | Staff directory with live attendance times |
| `WEB-2026-017` | Patient admission and billing list |
| `WEB-2026-020` | Staff duty roster — shifts, work locations, mobile numbers |
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
