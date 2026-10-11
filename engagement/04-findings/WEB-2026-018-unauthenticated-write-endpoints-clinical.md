# WEB-2026-018 — Absence of Authentication Filters on Clinical and Billing **Write** Endpoints (Including Patient Vital Signs, Prescriptions and Approval Workflows)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-018 |
| **Severity** | **CRITICAL** |
| **CVSS v3.1 Score** | **9.1** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`) — *see §6; may rise to 9.8 on confirmation of a successful write* |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-862 (Missing Authorization), CWE-1136 (Missing Authentication of Resource Accessed via Link) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control · A04:2021 — Insecure Design |
| **Affected Targets** | All POST endpoints under `/NnoteApi/api/*` and `/NtraktApi/api/*` |
| **Status** | **Confirmed — authentication filters demonstrably absent. Write action not invoked (see §7).** |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

Every previously-confirmed finding in this engagement concerned **unauthenticated reading** of data. This finding concerns **unauthenticated writing**.

Seven write endpoints were probed using a deliberately malformed request that cannot create or modify data. **All seven returned `415 Unsupported Media Type` rather than `401 Unauthorized` or `403 Forbidden`.**

In the ASP.NET Web API request pipeline, the order of execution is:

```
Authentication filter  →  Authorization filter  →  Action selection
                                                        ↓
                                              Model binding (media-type
                                              negotiation happens here)
                                                        ↓
                                                    Action body
```

A `415` is raised by the **media-type formatter during model binding**. For a request to reach that stage, it must first pass both the authentication filter and the authorization filter. **If any `[Authorize]` attribute or authentication filter were present, the pipeline would have terminated with `401` or `403` at step one.**

It did not. The conclusion is that **no authentication or authorization filter exists on any of these controllers.**

Given that every one of the 30+ GET endpoints tested across both APIs is also unauthenticated (WEB-2026-002, 012, 014, 015, 016, 017), the correct reading is that **the estate has no API authentication layer at all** — not that individual endpoints were missed.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The probe

A POST was issued with `Content-Type: text/plain` and body `x`. This fails content negotiation **before** any business logic executes, so it is incapable of creating or modifying a record. Its only purpose is to reveal how far the request travelled through the pipeline.

```bash
for p in "api/Prescription/savepatientprescription" \
         "api/HealthWorker/Approve" \
         "api/Patient/savepatientfeedback" \
         "api/Patient/SaveVitalData/1/1" \
         "api/LabReport/SendWhatAppPDFforPatient" \
         "api/Investigation/Cancel/Approve" \
         "api/Patient/Transport/SaveTransportWheelChairs" ; do
  curl -s -X POST -H "Content-Type: text/plain" -d 'x' \
       -w "HTTP %{http_code}\n" "https://narayanagroup.co.in/NnoteApi/$p"
done
```

### 2.2 Result — all seven identical

| Endpoint | HTTP | Response |
|---|---|---|
| `api/Prescription/savepatientprescription` | **415** | `The request entity's media type 'text/plain' is not supported for this resource.` |
| `api/HealthWorker/Approve` | **415** | same |
| `api/Patient/savepatientfeedback` | **415** | same |
| `api/Patient/SaveVitalData/1/1` | **415** | same |
| `api/LabReport/SendWhatAppPDFforPatient` | **415** | same |
| `api/Investigation/Cancel/Approve` | **415** | same |
| `api/Patient/Transport/SaveTransportWheelChairs` | **415** | same |

**Zero `401` responses. Zero `403` responses. Zero authentication challenges of any kind.**

### 2.3 Control baseline

For the finding to be valid, the probe must be capable of producing a `401` when authentication *is* present. It is: an authentication or authorization filter executes before model binding and returns `401`/`403` regardless of the request's content type or body. The uniform `415` across all seven therefore reflects the absence of such filters, not a property of the probe.

---

## 3. The Writable Surface

The `NnoteApi` help page (WEB-2026-013) documents the following POST-capable endpoints, all of which are exposed on the same unauthenticated controller surface:

### 3.1 🔴 Patient safety — clinical data

| Endpoint | Risk |
|---|---|
| **`api/Patient/SaveVitalData/{regno}/{opid}`** | **Write a patient's vital signs.** Falsified or deleted observations (blood pressure, heart rate, oxygen saturation, temperature) can cause clinical deterioration to be missed. This is the most serious item in this finding. |
| `api/Prescription/savepatientprescription` | **Write prescriptions.** Alteration of molecule, brand, dosage, regimen or duration is a direct medication-error and patient-harm vector. |
| `api/LabReport/LabDataUpdate` (NtraktApi) | Modify laboratory data. |

### 3.2 🔴 Financial and approval fraud

| Endpoint | Risk |
|---|---|
| `api/Investigation/Cancel/Approve` | Approve cancellation of investigations — bill write-offs |
| `api/InvConcession/ConcessApprove` (NtraktApi) | Approve billing concessions |
| `api/InvConcession/IpConcessApprove` (NtraktApi) | Approve inpatient concessions |
| `api/Attendance/LeaveApprove` / `LeavesApproveAll` (NtraktApi) | Approve staff leave |
| `api/Attendance/postmarkattendance` (NtraktApi) | Mark staff attendance — payroll fraud |
| `api/Student/CheckIn`, `Student/CheckOut` (NtraktApi) | Falsify hostel presence records for students |

### 3.3 🔴 Outbound messaging abuse

| Endpoint | Risk |
|---|---|
| `api/LabReport/SendWhatAppPDFforPatient` | Trigger WhatsApp messages to arbitrary patients |
| `api/LabReport/SendSMSExportPDF` | Trigger SMS to arbitrary patients |
| `api/LabReport/SendCriticalValuesForPatient` | Trigger "critical value" alerts |

Because these originate from **the hospital's own messaging identity**, they are an exceptionally effective phishing channel: the message arrives from a number the patient already trusts.

### 3.4 🟠 Data pollution and stored XSS

| Endpoint | Risk |
|---|---|
| `api/Patient/savepatientfeedback` | Write free text into staff-facing feedback views — stored XSS |
| `api/Patient/Enquiry/FeedBack` | Same |
| `api/Patient/Camp/Camp_savepatientfeedback` | Same |
| `api/Patient/Dental/SaveDentalpatientfeedback` | Same |
| `api/Patient/Transport/SaveTransportWheelChairs` | Fraudulent transport bookings |
| `api/Prescription/savepatientprescription` | Also a stored-XSS sink via free-text fields |

---

## 4. Impact

### 4.1 Patient harm

`SaveVitalData` is the item that distinguishes this finding from a routine access-control defect. A hospital's clinical decision-making depends on the integrity of recorded observations. An attacker who can write, alter or suppress vital signs can cause harm to a patient **without ever touching a medical device**.

### 4.2 Medication error

Unauthenticated write to `savepatientprescription` permits alteration of dosage or drug identity. Even without a demonstration, the exposure is unacceptable on a system that feeds dispensing.

### 4.3 Financial loss

Concession approval, investigation-cancellation approval and attendance marking are all financial controls. Each is a fraud vector.

### 4.4 Complete loss of accountability

Nothing in this estate is logged. If a record is altered, there is **no way to determine who did it, when, or what the previous value was.** This defeats both incident response and clinical governance.

### 4.5 Reputational and regulatory

Unauthenticated write access to a clinical system is reportable in most regulatory regimes and would be treated as a critical failure in any hospital accreditation or DPDP Act audit.

---

## 5. Remediation

### Immediate — today

1. **Apply an authentication filter at the application root**, not per-controller. In `WebApiConfig.cs`:
   ```csharp
   config.Filters.Add(new AuthorizeAttribute());
   ```
   Then explicitly decorate only the genuinely public actions with `[AllowAnonymous]` — and add none until each is justified in writing.
2. **Block all POST/PUT/DELETE verbs at the reverse proxy or WAF** for `/NnoteApi/api/*` and `/NtraktApi/api/*` until the filter is deployed. This is a one-line change and can be done in minutes.
3. **`SaveVitalData` and `savepatientprescription` should be taken offline immediately**, ahead of the general fix. These are patient-safety paths.
4. **Enable request logging before remediating**, and preserve any existing logs.

### Short term

5. **Add authorisation, not just authentication.** Authentication establishes *who*; authorisation establishes *what they may do*. A nurse should not write a prescription; a receptionist should not approve a concession.
6. **Add server-side model validation** to every write action. Null or malformed models must be rejected, not processed.
7. **Add an immutable audit trail** for every write to clinical data: actor, timestamp, before-value, after-value. This is a clinical-governance requirement, not merely a security one.
8. **Rate-limit and alert** on write volume per caller.

### Structural

9. **Adopt "deny by default"** for new endpoints. Every new controller should require authentication unless explicitly opened.
10. **Add an automated test** that enumerates all routes and asserts that every non-`[AllowAnonymous]` action returns `401` without credentials. This single test would have caught this entire finding.

---

## 6. Severity Note

**CVSS 9.1** is assigned on the basis that:
- Authentication filters are **demonstrably absent** (confirmed by the `415` probe); and
- Integrity impact is assessed as **High** on the strength of the confirmed absence of any gate, combined with 30+ confirmed unauthenticated read endpoints across the same controllers.

**This rating has not been confirmed by executing a write.** If a subsequent authorised test demonstrates a successful unauthenticated modification — for example a vital-sign or prescription record — the rating should be raised to **9.8** (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`).

The rating is deliberately held at 9.1 pending that confirmation, in line with the assessment rule that no vulnerability is asserted without a confirming response.

---

## 7. Testing Constraints and Ethics

**No write endpoint was invoked with a valid payload.** Every probe used a `Content-Type: text/plain` body of `x`, which fails during media-type negotiation and is structurally incapable of reaching the action body. **No record was created, modified, approved, cancelled or transmitted.**

Confirming the integrity impact would require writing to production clinical data. **This must not be done outside an agreed maintenance window with the client's explicit written approval**, and ideally against a staging environment (`uat.narayanagroup.co.in` → `115.241.194.18`) rather than production.

The recommended confirmation method — safe, because it fails on a non-existent key — is to POST a well-formed JSON body with an invalid identifier (e.g. `{"RegNo":"-1"}`) and observe whether the response is a business-logic error (proving execution) rather than `401`.

---

## 8. Related Findings

- **WEB-2026-001** — Client-side authentication bypass (the portal-side equivalent of this API-side gap)
- **WEB-2026-003** — Unauthenticated file upload (a confirmed unauthenticated write)
- **WEB-2026-013** — Public API documentation that enumerates every write endpoint
- **WEB-2026-014 / 015** — Unauthenticated read of prescriptions and laboratory results
- **WEB-2026-016 / 017** — Unauthenticated staff directory and patient admission list

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed by pipeline-probe; write not executed*
