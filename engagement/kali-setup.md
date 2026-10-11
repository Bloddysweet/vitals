# Kali Linux Setup — Narayana Group Engagement

Target: `narayanagroup.co.in` (+ authorized subdomains)
Status: authorized test — keep `00-admin/authorization.pdf` (or equivalent) in this project at all times.

---

## 0. VMware prep (do this FIRST)

1. **Snapshot now**: VM menu → Snapshot → Take Snapshot → name it `pre-engagement-baseline`.
2. Resources: ≥ 2 vCPUs, ≥ 4 GB RAM (8 GB recommended for nuclei/httpx), ≥ 60 GB disk.
3. Network mode: **NAT is fine** for external web testing. Your VM's public IP will be visible to the target — give that IP + your testing window to the client so they can distinguish your traffic from a real attack.
4. Clipboard/file sharing: `sudo apt install -y open-vm-tools-desktop` (then reboot) — needed for copy/paste and dragging evidence to the host.

## 1. Update the base system

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt autoremove -y
sudo timedatectl set-ntp true
sudo timedatectl set-timezone Asia/Kolkata     # log everything in IST
```

## 2. Install the toolchain

Kali ships most of what you need. One command:

```bash
sudo apt install -y \
  subfinder amass httpx-toolkit nuclei katana naabu dnsx tlsx \
  dalfox arjun xsstrike sqlmap jwt-tool \
  gau waybackurls anew qsreplace unfurl \
  ffuf feroxbuster gobuster wfuzz nikto \
  nmap masscan wafw00f whatweb testssl.sh eyewitness \
  seclists jq curl wget git unzip golang
```

> Note: on Kali the probing tool is packaged as `httpx-toolkit` (avoids a name clash); the binary is still called `httpx`.

Update nuclei templates (do this now, and weekly):

```bash
nuclei -ut
```

### If apt can't find a tool — install from GitHub via Go

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/sensepost/gowitness@latest
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.zshrc
source ~/.zshrc
```

### Wordlists

```bash
ls /usr/share/seclists/                     # Seclists is your main wordlist repo
sudo gzip -dk /usr/share/wordlists/rockyou.gz   # only if you need rockyou
```

## 3. Verify the install

```bash
for t in subfinder httpx nuclei katana naabu dnsx tlsx dalfox ffuf nmap; do
  printf '%-12s ' "$t"; $t --version 2>/dev/null | head -1 || echo MISSING
done
```

## 4. Browser + proxy setup

1. Firefox (preinstalled) → add **FoxyProxy** extension → proxy `127.0.0.1:8080`.
2. Start Burp Suite (Community is fine): create a **named project**, enable saving to `~/engagement/narayana/03-manual/burp/`.
3. Burp → Proxy → Proxy settings → make sure it listens on 127.0.0.1:8080.
4. Import Burp's CA cert into Firefox (http://burp → download CA, import as trusted).
5. In Burp → Target → Scope: add `narayanagroup.co.in` and `*.narayanagroup.co.in`, enable "Use advanced scope" and keep "And not the following" empty. **Work only within scope.**

## 5. Project directory + logging (documentation!)

```bash
mkdir -p ~/engagement/narayana/{00-admin,01-recon,02-scans,03-manual,04-findings,05-reports,logs}
cd ~/engagement/narayana
```

- `00-admin/` — authorization letter, signed scope, contacts (copy the templates from the repo `engagement/` folder and fill them in BEFORE any scanning)
- `01-recon/` — subdomains, live hosts, ports, tech stack
- `02-scans/` — nuclei/nikto/testssl output
- `03-manual/` — Burp project files, manual test notes
- `04-findings/` — one markdown file per confirmed finding (use `finding-report-template.md`)
- `05-reports/` — final client report
- `logs/` — session logs

**Log every session** (full terminal record, timestamped):

```bash
script -af ~/engagement/narayana/logs/session-$(date +%F_%H%M).log
# ... do your testing; every command + output is recorded ...
exit    # stop recording
```

## 6. Recon workflow (run AFTER the charter in 00-admin is filled in)

```bash
cd ~/engagement/narayana/01-recon
D=narayanagroup.co.in

# passive subdomains
subfinder -d $D -all -recursive -o subs_raw.txt
# resolve + dedupe
dnsx -l subs_raw.txt -o subs_resolved.txt
sort -u subs_resolved.txt -o subs.txt

# probe live hosts + tech detection
httpx -l subs.txt -o live.txt -status-code -title -tech-detect -follow-redirects -silent

# screenshots for eyeballing
gowitness file -f live.txt -P screenshots/

# crawl the main site for endpoints/params
katana -u https://$D -d 3 -jc -kf all -ct -o katana_$D.txt

# ports (main IP only; add other in-scope IPs as you confirm them)
nmap -sV -sC -T3 -p- 115.241.194.4 -oN ports_main.txt
```

## 7. Scanning phase (low-noise first)

```bash
cd ~/engagement/narayana/02-scans

# security headers + TLS
for u in $(cat ../01-recon/live.txt); do curl -sSI "$u" > headers_$(echo $u | md5sum | cut -c1-8).txt; done
testssl.sh narayanagroup.co.in 2>&1 | tee testssl_main.txt

# nuclei: misconfig, exposures, tech detection first (NOT the everything profile yet)
nuclei -l ../01-recon/live.txt -t misconfiguration/ -t exposures/ -t technologies/ \
  -severity medium,high,critical -o nuclei_pass1.txt

# directory brute force on the main host (moderate noise — client already approved)
ffuf -u https://narayanagroup.co.in/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -mc 200,301,302,403 -o ffuf_main.txt -of json
```

## House rules for this engagement

- Stay inside scope (`narayanagroup.co.in` + its subdomains). Anything else you discover (CDNs, email providers, payment gateways): **report, don't test**.
- No DoS, no brute-forcing real user accounts, no data deletion/modification, no social engineering.
- If you hit real user data (PII): capture minimum proof, stop, notify the client contact immediately.
- Every finding needs: timestamp, raw request/response, reproduction steps. That's what `script` + Burp history are for.
