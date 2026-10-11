# WEB-2026-004 — Payment Gateway Client-Side Hidden Field Manipulation (Amount, Fine, & Bank Account Number), Unauthenticated Student PII Lookup, & Cleartext HTTP Link (`CreateOrderNew.aspx`)

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-004 |
| **Severity** | **High** |
| **CVSS v3.1 Score** | **8.2** (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`) |
| **CWE** | CWE-472 (External Control of Assumed-Immutable Web Parameter), CWE-319 (Cleartext Transmission of Sensitive Information), CWE-639 (IDOR) |
| **OWASP Top 10 (2021)** | A04:2021 — Insecure Design / A02:2021 — Cryptographic Failures |
| **Affected Target** | `https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx` (linked on homepage as `http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx`) |
| **Status** | Confirmed (Live Target) |

---

## 1. Summary

The online student fee payment portal (`CreateOrderNew.aspx`) exhibits three compounding security flaws:
1. **Cleartext HTTP Link on Main Portal:** The homepage `https://narayanagroup.co.in/` links to the payment page via unencrypted HTTP (`href="http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx"`), and port 80 times out / fails to redirect cleanly.
2. **Unauthenticated Student PII & Fee Lookup by Registration Number:** Any unauthenticated user can enter a 13-character Student Registration Number (`txtRegno`) and trigger `lnkbtnSearch` to retrieve the student's full name, father's name, mother's name, mobile number, email address, home address, biometric ID (`hidBioId`), and fee balances.
3. **Financial & Bank Routing Parameters Stored in Client-Modifiable Hidden HTML Inputs:** Critical payment parameters—including the **destination bank account number (`hinaccountno`)**, **bank branch (`hinbranchname`)**, **payment amount (`hinamount`)**, **fine amount (`hdnfineamt`)**, and **fee balances (`hidCollegeBal`, `hidHostelBal`, `hidBusBal`, `hidTotDue`)**—are rendered as unencrypted `<input type="hidden">` fields submitted back to `./CreateOrderNew.aspx` on POST.

---

## 2. Technical Evidence (Live Capture)

### 2.1 Cleartext HTTP Link in `https://narayanagroup.co.in/`

```html
href="http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx"
```

### 2.2 Hidden Financial & PII Input Fields in `CreateOrderNew.aspx`

```html
<form method="post" action="./CreateOrderNew.aspx" id="ctl01">
<input name="ctl00$MainContent$txtRegno" type="text" maxlength="13" id="txtRegno" placeholder="Registration No" />
<input name="ctl00$MainContent$txtSname" type="text" id="txtSname" placeholder="Student Name" />
<input name="ctl00$MainContent$txtFname" type="text" id="txtFname" placeholder="Father Name" />
<input name="ctl00$MainContent$txtMname" type="text" id="txtMname" placeholder="Mother Name" />
<input name="ctl00$MainContent$txtMobileNo" type="text" maxlength="10" id="txtMobileNo" placeholder="Mobile No" />
<input name="ctl00$MainContent$txtEmail" type="text" maxlength="80" id="txtEmail" placeholder="Email" />
<input name="ctl00$MainContent$txtCourse" type="text" id="txtCourse" placeholder="Course/Year/Sem" />
<input type="hidden" name="ctl00$MainContent$hidCourse" id="hidCourse" />
<input type="hidden" name="ctl00$MainContent$hidCourseSlno" id="hidCourseSlno" />
<input type="hidden" name="ctl00$MainContent$hidYear" id="hidYear" />
<input type="hidden" name="ctl00$MainContent$hidDept" id="hidDept" />
<input type="hidden" name="ctl00$MainContent$hidAddress" id="hidAddress" />
<input type="hidden" name="ctl00$MainContent$hidBioId" id="hidBioId" />
<input type="hidden" name="ctl00$MainContent$hidFeeData" id="hidFeeData" />
<input type="hidden" name="ctl00$MainContent$campusname" id="campusname" />
<input type="hidden" name="ctl00$MainContent$hidIsHostel" id="hidIsHostel" />
<input type="hidden" name="ctl00$MainContent$hidIsBus" id="hidIsBus" />
<input type="hidden" name="ctl00$MainContent$hidCollegeBal" id="hidCollegeBal" />
<input type="hidden" name="ctl00$MainContent$hidHostelBal" id="hidHostelBal" />
<input type="hidden" name="ctl00$MainContent$hidBusBal" id="hidBusBal" />
<input type="hidden" name="ctl00$MainContent$hidTotDue" id="hidTotDue" />
<input type="hidden" name="ctl00$MainContent$hinbranchname" id="hinbranchname" />
<input type="hidden" name="ctl00$MainContent$hinaccountno" id="hinaccountno" />
<input type="hidden" name="ctl00$MainContent$hinlname" id="hinlname" />
<input type="hidden" name="ctl00$MainContent$hinamount" id="hinamount" />
<input type="hidden" name="ctl00$MainContent$hdnfineamt" id="hdnfineamt" value="0" />
<input type="hidden" name="ctl00$MainContent$hdnHeadSplit" id="hdnHeadSplit" />
<input type="hidden" name="ctl00$MainContent$isPrvDues" id="isPrvDues" />
<input type="hidden" name="ctl00$MainContent$hdnPrePercentage" id="hdnPrePercentage" />
```

### 2.3 Cookie Configuration Anomalies on `CreateOrderNew.aspx`

```http
Set-Cookie: ASP.NET_SessionId=kgdoecl45sauil32ljn243tx; path=/; secure; HttpOnly; SameSite=Lax
Set-Cookie: ASP.NET_SessionId=kgdoecl45sauil32ljn243tx; path=/; secure; HttpOnly; SameSite=Lax
Set-Cookie: __AntiXsrfToken=b255c9a35813429f87fb8fcce49d1eb0; path=/; secure; HttpOnly; SameSite=None
```

---

## 3. Impact

- **Fee / Fine Tampering:** If the ASP.NET postback handler reads `hinamount`, `hdnfineamt`, `hidTotDue`, or `hinaccountno` from `Request.Form` (the hidden input controls) when creating the Razorpay order, an attacker can zero out fines (`hdnfineamt=0`), reduce payable fees (`hinamount=1`), or alter fee head splits via browser DevTools or Burp Suite.
- **Mass Student & Parent PII Harvesting:** Any attacker can iterate registration numbers to scrape student names, parents' names, phone numbers, emails, physical addresses, and biometric IDs without authentication.

---

## 4. Remediation

1. **Authenticate Student Fee Lookups:** Require a second factor (e.g., Date of Birth or OTP sent to registered mobile) or student portal login before returning student PII and fee balances.
2. **Calculate Amounts & Bank Routing Strictly Server-Side:** Never store or read `hinaccountno`, `hinamount`, `hdnfineamt`, or fee balances from hidden HTML inputs. Retrieve the authoritative fee amount and merchant settlement account from the database on the server immediately before calling the Razorpay Orders API.
3. **Update Homepage Link to HTTPS:** Change `http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx` to `https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx` and set `SameSite=Lax` or `Strict` on `__AntiXsrfToken`.
