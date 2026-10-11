/* ============================================================================
   SPEAKER NOTES — keyed by slide index (0-based).
   Press N during the presentation to show/hide these.
   Each note includes a time budget for a 90-minute slot.
   ========================================================================== */
var NOTES = {

/* ---------- OPENING ---------- */
0: `[0:00-2:00] OPENING.
Open with the headline, not with yourself: "By the end of this session you will have watched
me read live patient data out of your systems using a web browser and no password."
Then say clearly that this is authorised, non-destructive, and aimed at fixing it.
Set the tone: serious, not accusatory. Nobody in this room built this deliberately.`,

1: `[2:00-2:30] GROUND RULES.
Do not skip this slide. It protects you and it protects the room. Say the words
"written authorisation from the owner" out loud — it settles everyone.`,

2: `[2:30-4:00] SCOPE.
Stress the right column. Several people will be bracing for a blame session; defuse it early.
"If your team built part of this, this is not about you."`,

3: `[4:00-5:00] SAFETY.
This slide earns you credibility with the security team. Walk the list.
The payment-point caveat at the bottom is important: be transparent that you read HTML every
visitor receives — and that this is not an attack.`,

/* ---------- MINDSET ---------- */
4: `[5:00-5:20] SECTION 02.
"Before any code, let us talk about how the other side thinks."`,

5: `[5:20-8:00] THE KILL CHAIN.
Land one idea: steps 2 and 3 are the same action here. There is no payload, no malware,
no exploit kit. The vulnerability IS the request. That is why it is so dangerous.
If you only get one point across in this whole session, make it this one.`,

6: `[8:00-10:00] WHY HOSPITALS.
This slide is for management. The economics point: a stolen card dies in hours,
a stolen identity lasts decades. Health data is the premium product on criminal markets.
The last card — "nobody is watching" — is the one that should worry the security team most.`,

7: `[10:00-12:00] THE TOOLKIT.
Make the Rs 0 point. Then the uncomfortable one: this is not a person, it is a script
running against ten thousand domains a day. You are simply in the list.
Ask the room: "How many of you have curl installed right now?"`,

8: `[12:00-13:00] THE PLAN.
Preview only — do not explain each step yet. "This is the next twenty minutes."
Everything on this slide succeeded. Say that line and pause.`,

/* ---------- RECON ---------- */
9: `[13:00-13:20] SECTION 03.
Transition: "Now let us actually do it. Minute zero."`,

10: `[13:20-15:00] 29 DOORS.
The point is not the number, it is that nobody has an inventory. Ask the room:
"Can anyone here name the owner of all 29?" Expect silence. That silence is the finding.`,

11: `[15:00-17:00] SUBDOMAIN DISCOVERY.
Run this live if the network is up — it is fast and safe.
Emphasise that nmc, uat and online were NOT linked from the website. They were found in
public records. Ask: "Who owns these three?"`,

12: `[17:00-19:00] BANNERS.
The max-age=0 line is the money shot. Most people assume HSTS is present; it is
actively disabled. And the placeholder CORS value proves no config review happened.
Developers usually react audibly here.`,

13: `[19:00-22:00] READING THE JAVASCRIPT.
SLOW DOWN. This is where everything unravels. Read the code out loud.
"window.location = layout.html?empid= ..." — that is the entire login.
Then: "There is no lock here. Only the appearance of one."`,

14: `[22:00-25:00] FINDING THE APIS.
Explain IDOR in one sentence: "Change the number, get a different person."
It is the hotel-key analogy if anyone looks blank: keys numbered 1,2,3 and nobody
asks who you are.`,

15: `[25:00-26:00] RECON COMPLETE.
End on the two questions. Especially: "How would you know if someone already did this?"
Let that hang. You will come back to it in section 09.`,

/* ---------- MASTER ATTACK ---------- */
16: `[26:00-26:30] SECTION 04.
"The next twenty minutes are the whole breach, start to finish."`,

17: `[26:30-28:00] THE CHAIN.
Walk left to right at a steady pace. Then say clearly: step 8 was NOT executed, and why.
That statement demonstrates discipline and keeps you inside authorisation.`,

18: `[28:00-30:00] STEP 1 — LIVE.
Run it. Expect nothing to come back. Then show what a normal login would return.
Say: "This is the root cause. Not a broken check — the check does not exist."`,

19: `[30:00-32:00] STEP 2 — LIVE.
Two commands, very visual. Explain base64 in one line: "It is not encryption,
it is a reversible code. Any free website decodes it."`,

20: `[32:00-34:00] STEP 3 — LIVE. THE PEAK OF THE TALK.
Run it. Let the 200 OK sit on screen in silence for a good five seconds.
Then: "200 means here you go. For any employee number. For any patient number.
From anywhere in the world. At three in the morning. Forever."
If you get a reaction from the room, this is where it happens.`,

21: `[34:00-36:00] STEP 4 — LIVE.
Show the loop. Point out there is no rate limit: five pages in under a second.
Then CheckOperator confirming which IDs are real.`,

22: `[36:00-39:00] STEP 5 — LIVE.
Read the fields out loud, slowly: name, mobile, date of birth, joining date, department,
branch, employee number... and a scanned passport photograph.
"This is a complete identity kit." Mention the Canon CanoScan EXIF detail — it proves
these are scanned identity documents, not casual snapshots.`,

23: `[39:00-42:00] STEP 6 — LIVE. THE MOST SERIOUS SLIDE.
Say plainly: "This is the one that matters." A named patient, her age, her mobile number,
and the specific clinical test she had. That is a health record.
Note the Aadhaar and PIN fields are present in the schema even when null — they should
never be returned by an API at all.`,

24: `[42:00-44:00] STEP 7.
Shift from privacy to money. "This is not just theft. This is an attacker taking a
business action in your name." Then: nothing is logged, so the audit trail will not
say who approved it.`,

25: `[44:00-47:00] STEP 8 — NOT EXECUTED.
Be explicit and repeat it: no file was uploaded. Show the shell only so they understand
severity. Walk the five-step path. The Web.config line at the end gets developers'
attention — that is where the Oracle connection string lives.`,

26: `[47:00-49:00] WHAT THEY OWN.
Eight boxes. Read them. Then the bottom line: none of it was logged, alerted, or
rate limited. "They could have been doing this for months."`,

27: `[49:00-50:00] TIMELINE.
Seven minutes. Then the closing question, aimed at the security team:
"If this takes seven minutes and you have no detection, how long has it been happening?"
Hand straight over to section 05.`,

/* ---------- WEB-001 ---------- */
28: `[50:00-50:20] SECTION 05.
"Let me show the developers exactly what is wrong and exactly what to change."`,

29: `[50:20-53:00] ANATOMY.
This is the key teaching slide. The golden rule: anything running in the browser is a
suggestion, not a control. Security decisions belong on the server — the only computer
you actually own. Point at the [Authorize] attribute on the right. It is one line.`,

30: `[53:00-56:00] LIVE DEMO.
Run the four commands. Pause after number three. Narrate the expected result before
each one so you look in control even if output is slow.`,

31: `[56:00-58:00] DETECT & FIX.
Note item 5 under detect: today you have none of these. "That is finding zero."
Hand the fix list to the lead developer by name if you can.`,

/* ---------- WEB-002 ---------- */
32: `[58:00-58:20] SECTION 06.
"Same root cause, worse consequence."`,

33: `[58:20-61:00] CHAIN A.
Show the twelve-line script. Say: "I ran the enumeration. I did not run the download.
This is what a real attacker writes." Twelve lines of shell.`,

34: `[61:00-63:00] CHAIN B.
Three HTTP requests between a stranger and a named patient's clinical test.
Say it in those words.`,

35: `[63:00-66:00] MONETISATION.
The phone-call scenario is the one that lands with non-technical people. Act it out:
"Madam, this is Narayana billing, your CROSS MATCHING test payment of Rs 1,400 failed,
please confirm your card." She knows she had that test. She believes it.
Then the DPDP Rs 250 crore line — for management.`,

36: `[66:00-68:00] DETECT & FIX.
Highlight the before/after code. The [Authorize] + IsInRole + Log.Access pattern is
what they should copy into every controller.`,

/* ---------- HIGH FINDINGS ---------- */
37: `[68:00-68:20] SECTION 07.
"Five High findings. Each is a breach path on its own."`,

38: `[68:20-70:00] 003 UPLOAD.
Point at {fname} in the URL. Explain why attacker-controlled filenames are catastrophic.
Repeat: nothing was uploaded.`,

39: `[70:00-71:30] 003 FIX.
The code sample is the whole fix — generate the filename server-side, never trust the client.`,

40: `[71:30-73:30] 004 PAYMENT.
Explain hidden fields properly: "Hidden means invisible on screen. It does not mean
secret. Press F12 and you can edit every one of them."`,

41: `[73:30-75:00] 004 FIX.
The fix is architectural: the server computes the price. Never trust a price from a browser.
Add the daily reconciliation — that is how you catch tampering that already happened.`,

42: `[75:00-77:00] 005 ERRORS.
ORA-01722 is the important part. It is the system admitting that input reaches the
database unvalidated. "Attackers read these the way you read a menu."`,

43: `[77:00-78:30] 005 FIX.
Cheapest high-value fix in the report: two config lines plus parameterised queries.
Fifteen minutes for the first part.`,

44: `[78:30-80:00] 006 EOL.
Name the CVEs. Say: "Public working exploit code exists. Attacker downloads it and runs it.
No skill required."`,

45: `[80:00-81:30] 006 FIX.
Helpdesk first. Then the upgrade/replace/retire decision for the legacy estate.
Push the monthly patching routine — it prevents most breaches, not just these.`,

46: `[81:30-83:00] 007 APK.
Widest blast radius of any finding: one substituted file reaches every device that updates.`,

47: `[83:00-84:30] 007 FIX.
Signing the APK is the real fix. Play Store distribution is easiest.
Plus force HTTPS and HSTS — config only.`,

/* ---------- MEDIUM ---------- */
48: `[84:30-84:45] SECTION 08.
"Three Medium findings. Lower severity individually, but two are two-minute fixes."`,

49: `[84:45-86:00] 008 PACS.
max-age=0 disables HSTS — say that explicitly, people misread it.
Placeholder CORS proves the server was deployed straight from the manual.
Best answer: VPN only.`,

50: `[86:00-87:30] 010 DNS/EMAIL.
The fastest fix in the whole report: the online DNS typo. Two minutes in Cloudflare.
Say: "This is currently pointing part of your brand at somebody else's server."`,

51: `[87:30-89:00] 009 HEADERS.
Free defence. One config change for six headers.
Cookies without HttpOnly turn any small XSS into instant account theft.`,

/* ---------- DETECTION ---------- */
52: `[89:00-89:20] SECTION 09.
For the security team. Shift tone from "here is the attack" to "here is how you would
have seen it".`,

53: `[89:20-91:00] THE LOG GAP.
Six gaps. The hardest line in the deck: because none of this is logged, nobody can tell
you whether someone else already did it. Treat that as an open incident until proven
otherwise. You will repeat this in section 12.`,

54: `[91:00-93:00] SIEM QUERIES.
Hand these to whoever runs the SIEM. Query 1 is the single most valuable: any 200 with
no session cookie on those API paths is a Critical incident, full stop.`,

55: `[93:00-95:00] CLOUDFLARE.
Be honest: this is a seatbelt, not a cure. It buys time. It does not fix the missing
authentication. Say both halves — you do not want anyone treating this as the fix.`,

/* ---------- REMEDIATION ---------- */
56: `[95:00-95:20] SECTION 10.
"Everything so far was the problem. This is the plan."`,

57: `[95:20-97:00] THE ONE THING.
If they remember one slide, make it this one. One change, one day, closes three findings.
Give the fallback too: if developers are unavailable today, the Cloudflare IP allow-list
takes ten minutes.`,

58: `[97:00-98:30] DEV-OWNED.
Hand this table to the lead developer. Total about two developer-weeks.
Point out that items 4, 5 and 8 are hours, not days.`,

59: `[98:30-100:00] OPS-OWNED.
Six of these ten take under an hour. Say: "There is no reason for any of these to still
be open on Friday."`,

60: `[100:00-102:00] VERIFICATION.
Book the re-test now, in the room. Around a third of first fixes are incomplete.
Verify with the attack, not with a code review.`,

61: `[102:00-104:00] ROADMAP.
Walk the five rows. Exit criteria are stated — use them.
Close with: "Book the re-test before you close the ticket."`,

/* ---------- RUNBOOK ---------- */
62: `[104:00-104:20] SECTION 11.
"If you want to reproduce any of this yourself, here is exactly how."`,

63: `[104:20-106:00] DEMO SCRIPT.
Give the team this script. Every command is read-only.
Tip: 18pt font minimum on the projector, pause after step 3.`,

64: `[106:00-107:30] CONTINGENCY.
Non-negotiable: read-only. No uploads, no PIN changes, no bill approvals — on stage or off.
That is what keeps this authorised and safe.`,

/* ---------- Q&A ---------- */
65: `[107:30-107:45] SECTION 12.
Open the floor.`,

66: `[107:45-112:00] Q&A PREP.
Rehearse these eight. The first — "has this already been exploited?" — is the one you
will definitely be asked. Answer honestly: we cannot know, because there is no logging.
If you do not know an answer, say you will verify in writing. That is stronger than a guess.`,

67: `[112:00-115:00] THE OPEN INCIDENT.
Save this for last if you can. Close the door first, investigate second.
Preserve logs before rotation. Take advice on DPDP notification.
"Do not let this become a scheduled maintenance item."`,

68: `[115:00-117:00] CLOSE.
End on the one thing: server-side authentication on the two APIs. One day of work.
Thank the room. Offer the re-test in writing.`,

/* ---------- APPENDIX ---------- */
69: `[APPENDIX] COMMAND REFERENCE.
Copy-paste for the developers. Everything used during the assessment, in one place.`,

70: `[APPENDIX] FINDINGS INDEX.
Quick reference during questions.`,

71: `[APPENDIX] MONDAY MORNING.
If the room does nothing else: these four things, in this order, today.`

};
