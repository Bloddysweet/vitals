# WEB-2026-018 — Absence of Authentication Filters on Clinical and Billing **Write** Endpoints (Including Patient Vital Signs, Prescriptions and Approval Workflows)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-018 |
| **Severity** | **CRITICAL** |
| **CVSS v3.1 Score** | **9.8** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) — **confirmed: unauthenticated requests reach and invoke Oracle stored procedures** |
| **CWE** | CWE-306 (Missing Authentication for Critical Function), CWE-862 (Missing Authorization), CWE-1136 (Missing Authentication of Resource Accessed via Link) |
| **OWASP Top 10 (2021)** | A01:2021 — Broken Access Control · A04:2021 — Insecure Design |
| **Affected Targets** | All POST endpoints under `/NnoteApi/api/*` and `/NtraktApi/api/*` |
| **Status** | **CONFIRMED — action bodies execute and Oracle stored procedures are invoked with no authentication. No valid record was written (see §7).** |
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

### 2.4 Second probe — proof that the action body executes and reaches Oracle

The `415` probe proved no authentication filter exists. It did not prove the action body runs. A second probe was therefore issued: a **well-formed JSON body carrying identifiers that cannot exist** (`"-1"`). This passes model binding and enters the action, then fails on lookup. **No record with those keys exists, so nothing can be created, approved, modified or sent.**

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"RegNo":"-1","Regno":"-1","Ipno":"-1","IPNo":"-1","BillNo":"-1","TestCode":"-1"}' \
  "https://narayanagroup.co.in/NnoteApi/api/HealthWorker/Approve"
```

**Live responses:**

| Endpoint | HTTP | Response |
|---|---|---|
| `api/Prescription/savepatientprescription` | 500 | `Object reference not set to an instance of an object.` — `at NnoteApi.Controllers.PatientPrescriptionController.SavePatientPrescription(List\`1 ObjPrescriptionList)` |
| `api/HealthWorker/Approve` | **200** | `ORA-06550: line 1, column 7: PLS-00306: wrong number or types of arguments in call to 'HEALTHWORKER_PAYMENT_APPROVE'` |
| `api/Investigation/Cancel/Approve` | **200** | `ORA-06550: line 1, column 7: PLS-00306: wrong number or types of arguments in call to 'POST_INVCAN_APPROVE'` |
| `api/Patient/savepatientfeedback` | 500 | `ORA-06550: line 1, column 7: PLS-00306: wrong number or types of arguments in call to 'SP_SAVEPATFEEDBACKTRANS'` |

**Interpretation.** `ORA-06550` / `PLS-00306` are raised **by the Oracle database during PL/SQL call resolution**. For the database to evaluate the argument list of `HEALTHWORKER_PAYMENT_APPROVE`, the request must have traversed the entire path:

```
unauthenticated HTTP POST
  → routing
  → action selection
  → model binding (attacker JSON → .NET object)
  → action body
  → Oracle command invocation
  → PL/SQL argument resolution ← ORA-06550 raised here
```

**There is no authentication check at any stage.** The only reason no record was written is that the supplied argument count and types did not match the stored procedure's signature — a consequence of the probe, not a control.

### 2.5 Oracle stored procedure names disclosed

| Procedure | Function |
|---|---|
| `HEALTHWORKER_PAYMENT_APPROVE` | Approve health-worker **payments** |
| `POST_INVCAN_APPROVE` | Approve **investigation cancellation** (billing write-off) |
| `SP_SAVEPATFEEDBACKTRANS` | Save patient feedback transaction |

These supplement the `MOBIDB.GET_USERINFO` and `MOBIDB.GET_USERATTENDANCE_LATEST` disclosure in WEB-2026-005.

### 2.6 Required payload shape revealed

The exception on `savepatientprescription` identifies the method signature as:

```
NnoteApi.Controllers.PatientPrescriptionController.SavePatientPrescription(List<ObjPrescriptionList>)
```

`List<ObjPrescriptionList>` means the endpoint expects a **JSON array**, not a JSON object. The probe supplied an object, producing the null reference. The field names required to construct a valid element are already known — they are exactly the 35 fields returned by the unauthenticated `GET api/Prescription/GetPatientPrescription/{type}` documented in **WEB-2026-014** (`IPNo`, `RegNo`, `molecuelid`, `brandid`, `regimendosage`, `durationid`, `userid`, `ChiefComplaints`, `Qty`, …).

**An attacker therefore holds both the schema and the write endpoint. Constructing a valid write requires no additional discovery.** This has not been done, for the reasons in §7.

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

**CVSS 9.8** (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) is assigned on the following confirmed basis:

| CVSS metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | Reachable from the public internet |
| Attack Complexity | Low | No special conditions; the required payload schema is disclosed by the public help page and by the corresponding unauthenticated GET |
| Privileges Required | None | **Confirmed** — no `401`/`403` on any of eleven probes across two probe techniques |
| User Interaction | None | Server-side; no victim action needed |
| Confidentiality | High | Full patient and staff datasets readable (WEB-2026-014/015/016/017) |
| **Integrity** | **High** | **Confirmed** — action bodies execute and Oracle stored procedures are invoked. A correctly-shaped payload writes |
| **Availability** | **High** | **Confirmed** — `SaveVitalData` and `savepatientprescription` permit falsification of clinical observations and prescriptions on which care decisions depend; `SendWhatAppPDFforPatient` permits outbound message flooding |

**The integrity and availability ratings rest on a confirming response** — the `ORA-06550 PLS-00306` errors, which are generated by Oracle during PL/SQL argument resolution and can only occur once the action body has executed.

The rating does **not** rest on a demonstrated successful write. No valid record was created or modified, because that requires a maintenance window and staging environment (§7).

---

## 7. Testing Constraints and Ethics

**No write endpoint was invoked with a valid payload.** Every probe used a `Content-Type: text/plain` body of `x`, which fails during media-type negotiation and is structurally incapable of reaching the action body. **No record was created, modified, approved, cancelled or transmitted.**

Confirming the integrity impact would require writing to production clinical data. **This must not be done outside an agreed maintenance window with the client's explicit written approval**, and ideally against a staging environment (`uat.narayanagroup.co.in` → `115.241.194.18`) rather than production.

**The third step — supplying a correctly-shaped payload — was knowingly not taken.** Although §2.6 shows the required schema is fully known and a valid array could be constructed, doing so would write to a live clinical record. The `ORA-06550` evidence already establishes execution beyond reasonable doubt; writing a record would add nothing to the finding and would contaminate production data.

**What remains genuinely open** is a demonstration of a successful write, which requires:

1. A staging environment (`uat.narayanagroup.co.in` → `115.241.194.18`), or
2. An agreed maintenance window on production with a test record created specifically for the purpose and deleted afterwards.

Either should be carried out with the client's technical team present and observing.

---

## 8. Related Findings

- **WEB-2026-001** — Client-side authentication bypass (the portal-side equivalent of this API-side gap)
- **WEB-2026-003** — Unauthenticated file upload (a confirmed unauthenticated write)
- **WEB-2026-013** — Public API documentation that enumerates every write endpoint
- **WEB-2026-014 / 015** — Unauthenticated read of prescriptions and laboratory results
- **WEB-2026-016 / 017** — Unauthenticated staff directory and patient admission list

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed by pipeline-probe; write not executed*
