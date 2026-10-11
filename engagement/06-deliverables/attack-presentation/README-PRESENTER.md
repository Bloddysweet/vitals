# Presenter quick-start

**File:** `Narayana-Security-Attack-Presentation.html` — one self-contained file, no internet
needed. Double-click it, or drag it into Chrome/Edge/Firefox.

---

## Keyboard

| Key | Action |
|---|---|
| `→` / `Space` / `Enter` / click | Next slide |
| `←` / `Backspace` | Previous slide |
| `N` | **Show/hide speaker notes** (72 slides, all have them) |
| `O` | Overview grid — jump to any slide |
| `F` | Fullscreen |
| `T` | Start/stop a running timer (top-left) |
| `Home` / `End` | First / last slide |
| `0`–`9` | Jump to that fraction of the deck |

The slide number is in the bottom-right; the current section is bottom-left.

---

## 90-minute running order

| Time | Slides | Section |
|---|---|---|
| 0:00–5:00 | 1–4 | Ground rules, scope, safety |
| 5:00–13:00 | 5–8 | Attacker mindset, kill chain, toolkit |
| 13:00–26:00 | 9–15 | Reconnaissance (public data only) |
| 26:00–50:00 | 16–27 | **The master attack** — 0 to full compromise |
| 50:00–68:00 | 28–36 | WEB-2026-001 and WEB-2026-002 (Critical) |
| 68:00–84:30 | 37–47 | The five High findings |
| 84:30–89:00 | 48–51 | The three Medium findings |
| 89:00–95:00 | 52–55 | Detection engineering |
| 95:00–104:00 | 56–61 | Remediation plan |
| 104:00–107:30 | 62–64 | Live demo runbook |
| 107:30–117:00 | 65–68 | Q&A prep and close |
| — | 69–71 | Appendix (command reference, findings index) |

**If you run short:** cut slides 48–51 (Medium findings) and 69–71 (appendix) and go
straight from slide 47 to 52. The two Criticals and the five Highs are the story.

---

## The live demo

`LIVE-DEMO-RUNBOOK.sh` is ready to run:

```bash
chmod +x LIVE-DEMO-RUNBOOK.sh
./LIVE-DEMO-RUNBOOK.sh
```

- 14 steps, each pauses for Enter so you can narrate.
- **Every command is read-only** (GET requests and DNS lookups only).
- Nothing is uploaded, changed, downloaded or stored.

### Before you present

1. Run it once end-to-end. Confirm each step returns the expected result.
2. Screenshot each step into `01.png` … `14.png` as a **fallback** if the network dies.
3. Set your terminal font to **18pt or larger**; the room is bigger than your screen.
4. Test the connection 15 minutes before you start (run step 3).

### Contingency

- Network down? Present from the slides — every terminal block in the deck is the real,
  verbatim output. Nothing is lost.
- Phone hotspot as a backup connection; the requests are tiny.
- Something unexpected happens? Stop. Say "that is unexpected, I will verify offline and
  report back." Never improvise against production.

---

## Three moments to land

1. **Slide 20 (step 3)** — the `200 OK` when you skip the login. Let it sit in silence.
2. **Slide 23 (step 6)** — a named patient, her mobile number, and the clinical test she had.
   Say: *"This is the one that matters."*
3. **Slide 57 (the one fix)** — server-side authentication closes three findings in one day.

---

## The one thing they must remember

> Add server-side authentication to `/NtraktApi/api/*` and `/NnoteApi/api/*`, deny by
> default. That closes both Critical findings and the unauthenticated file upload.
>
> If the developers are unavailable today: restrict those two paths to known Narayana IP
> ranges in Cloudflare. Ten minutes.

---

## Rebuilding

```bash
python3 build.py          # regenerates the single-file HTML from src/
```

Sources: `src/template.html` (engine + CSS), `src/slides.js` (content),
`src/notes.js` (speaker notes).

---

## Related deliverables

- `../Narayana-Group-Website-Security-Assessment-Client-Report.pdf` — 42-page plain-English
  report for the owner (no technical background assumed).
- `../../04-findings/WEB-2026-*.md` — the ten individual developer-ready findings.
- `../../05-reports/narayanagroup-website-security-assessment.md` — the technical master report.
