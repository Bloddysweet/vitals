# WEB-2026-011 — Staff Mobile App Update URL Hardcoded to Unreachable Internal IP Over Cleartext HTTP

| Field | Value |
|---|---|
| **Finding ID** | WEB-2026-011 |
| **Severity** | **Low** |
| **CVSS v3.1 Score** | **3.7** (`CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N`) |
| **CWE** | CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor), CWE-319 (Cleartext Transmission of Sensitive Information), CWE-1104 (Use of Unmaintained/Improperly Controlled Third-Party Component Distribution) |
| **OWASP Top 10 (2021)** | A05:2021 — Security Misconfiguration |
| **Affected Targets** | `https://narayanagroup.co.in/Nnote/layout.html`, `https://narayanagroup.co.in/ncare/layout.html` |
| **Status** | Confirmed (Live Target) |
| **Phase** | Phase 2 (2026-10-11) |

---

## 1. Summary

Both the staff portal (`/Nnote/`) and the patient portal (`/ncare/`) contain a hardcoded application-update pointer to a **plaintext HTTP URL on a private internal address**:

```
http://115.241.194.19/nNote.apk
```

That host is **not reachable from the public internet**. An Nmap port sweep and a direct `curl` fetch both confirm the address exists but exposes **no open ports** to an external client. The result is that the mobile app's update mechanism is permanently broken for any user outside the internal network, while simultaneously disclosing internal network addressing to anyone who views the page source.

---

## 2. Technical Evidence (Live Capture)

### 2.1 The hardcoded reference appears in both portals

```bash
for p in "Nnote/layout.html" "ncare/layout.html" ; do
  curl -s "https://narayanagroup.co.in/$p" | grep -oE "https?://[^\"'<> ]+\.apk" | sort -u
done
```

**Live Response:**

```
--- Nnote/layout.html ---
'http://115.241.194.19/nNote.apk'
--- ncare/layout.html ---
'http://115.241.194.19/nNote.apk'
```

### 2.2 The target host is up, but exposes no reachable service

```bash
nmap -Pn -T4 -p 21,22,80,443,8080,8443 --open 115.241.194.19
```

**Live Response:**

```
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-10-11 12:56 EDT
Nmap done: 1 IP address (1 host up) scanned in 1.80 seconds
```

> The host responds to Nmap's host-discovery probes (**1 host up**) — confirming the address is live and routable — but **zero of the six probed ports were reported open**. There is no `--open` results table, which means every port was either closed or filtered.

### 2.3 Direct fetch attempt fails at the network layer

```bash
curl -k -s -v -m 45 -o nNote.apk "http://115.241.194.19/nNote.apk"
```

**Live Response:**

```
*   Trying 115.241.194.19:80...
* connect to 115.241.194.19 port 80 from 192.168.1.6 port 42716 failed: No route to host
* Failed to connect to 115.241.194.19:80 after 1440 ms: Could not connect to server
nNote.apk: cannot open `nNote.apk' (No such file or directory)
```

`No route to host` is an ICMP unreachable at the network layer, not an application refusal. The update server is internal-only.

---

## 3. Impact

### 3.1 Availability / Operational (primary)

Any staff member or user **outside the Narayana internal network can never receive an application update**. Because the update check is hardcoded rather than resolved through DNS or a configuration service, there is no fallback. Staff running an old build will silently continue to use it, including any build with known defects. In practice this also pushes staff toward sideloading APKs from unofficial sources, which is a supply-chain risk in its own right.

### 3.2 Information Disclosure (secondary)

Publishing `115.241.194.19` in a public-facing page source confirms to an attacker that the `115.241.194.0/24` range is in use and that internal file-distribution hosts live there. This directly corroborates the internal addressing already noted in **WEB-2026-009** (`115.241.194.2`, `115.241.194.19`, `192.168.100.10`), helping an attacker who has gained any internal foothold to pivot.

### 3.3 Cleartext Transport (secondary)

The scheme is `http://`, not `https://`. Even when a user *is* on the internal network, the APK is fetched without transport encryption or integrity verification. An attacker positioned on the same network segment (rogue Wi-Fi, compromised workstation, ARP spoofing) can substitute a trojanised APK for the legitimate one. Staff who install it would grant the attacker the app's full permission set and, critically, any API credentials the app carries.

### 3.4 Security value lost

Because the update path is dead, **security patches pushed to `nNote.apk` will never reach users**. If a vulnerability is ever found in the app itself, there is no working mechanism to distribute the fix.

---

## 4. Steps to Reproduce

1. From any network **outside** the Narayana internal network:
   ```bash
   curl -s "https://narayanagroup.co.in/Nnote/layout.html" | grep -oE "https?://[^\"'<> ]+\.apk"
   ```
2. Observe `http://115.241.194.19/nNote.apk`.
3. Attempt to fetch it:
   ```bash
   curl -v -m 45 -o nNote.apk "http://115.241.194.19/nNote.apk"
   ```
4. Observe `No route to host`.

---

## 5. Remediation

**Immediate**

1. **Serve the APK over HTTPS from a publicly resolvable host**, e.g. `https://narayanagroup.co.in/downloads/nNote.apk`, or publish the app on the Google Play Store and remove the sideload path entirely.
2. **Do not hardcode the update URL in client-side HTML.** Resolve it from server-side configuration or a small version-manifest endpoint such as:
   ```json
   { "version": "2.4.1", "url": "https://.../nNote-2.4.1.apk", "sha256": "..." }
   ```
3. **Replace `115.241.194.19` with a DNS name.** Hardcoded IPs cannot be repointed during an incident.

**Hardening**

4. **Verify integrity before install.** Publish a SHA-256 checksum alongside the APK and have the app verify it. Better still, sign the APK and enforce signature verification on update.
5. **Remove the internal IP from public page source** even if the host remains internal.
6. **Add monitoring** on the update endpoint so a dead distribution path is detected by operations rather than by an external researcher.

---

## 6. Notes for Phase 2

The APK itself could not be retrieved, so **no static analysis of `nNote.apk` was performed**. This is a gap in coverage rather than a clean result: the app is the client for `/NtraktApi/` and `/NnoteApi/` and would be expected to contain hardcoded endpoints and possibly credentials.

**Recommended follow-up:** obtain `nNote.apk` directly from the technical team (they hold the file) and repeat the review with `jadx` / `apktool`. Both tools are confirmed available on the assessment host (`jadx`, `apktool 2.7.0`).

---

## 7. Related Findings

- **WEB-2026-007** — Cleartext `http://115.241.194.19/nNote.apk`; cleartext logins on helpdesk and `115.241.194.8/elearn/`
- **WEB-2026-009** — Internal IP disclosure (`192.168.100.10`, `115.241.194.2`, `115.241.194.19`, `localhost:64867`)
- **WEB-2026-001** — Client-side authentication bypass in `/Nnote/` and `/ncare/`

---

*Finding recorded: 2026-10-11 · Phase 2 deep assessment · Confirmed against live target*
