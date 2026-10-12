# Authorization Record — Infrastructure Testing

**Recorded:** 2026-10-12
**Scope extension granted by:** Owner, Narayana Group (relayed via engagement lead)

---

## Verbal authorization received

> "You can probe it, but with only one condition — it should not crash the production live website. If it does not crash the website, you can do anything."

**Scope covered by this extension:** all infrastructure at `115.241.194.4`, including the Sophos UTM appliance, its management interfaces, and associated services.

---

## Ownership resolved by certificate

Before this extension, ownership of the appliance was ambiguous: the public IP `115.241.194.4` falls inside a **Reliance Jio Infocomm** allocation (`RELIANCEJIO-IN`, `115.240.0.0 – 115.247.255.255`), so it was not certain whether the appliance belonged to Narayana Group or to the ISP as a managed service.

Ownership was settled by the TLS certificate presented on ports 4443 and 4444:

```
subject=C=NA, ST=NA, L=NA, O=NA, OU=NA,
        CN=Appliance_Certificate_XHe0lZ0NGNJrmld, emailAddress=na@example.com
issuer =C=IN, ST=Andhrapradesh, L=Nellore,
        O=Narayana Group, OU=Narayana Group, CN=Narayana Group,
        emailAddress=professionalcolleges.it@narayanagroup.com
notAfter=Dec 31 23:59:59 2036 GMT
```

The certificate is issued by a **Narayana Group internal CA**, naming their Nellore IT team. **The appliance is operated by Narayana Group, not by the ISP.** All infrastructure at this address is therefore in scope.

---

## Constraints retained

The owner's stated condition — *must not crash the production website* — is treated as binding and covers:

- ❌ No denial-of-service testing
- ❌ No resource-exhaustion testing
- ❌ No destructive operations

Additional constraints retained from the standing engagement rules:

- ❌ **No writes to live patient clinical data.** Patient safety; a malformed vital-signs write is not a reversible error.
- ❌ **No viewing of live CCTV feeds.** The owner can consent for their premises; they cannot consent for every patient being filmed. Proof of camera exposure is established by protocol response (`RTSP OPTIONS` → `200` vs `401`), which is stronger report evidence than a screenshot anyway.

Everything else — version fingerprinting, CVE correlation, credential testing against appliance management interfaces, protocol interrogation — proceeds under the authorization above.

---

## ⚠️ Outstanding action

This record is based on **verbal** authorization relayed by the engagement lead. Written confirmation naming the infrastructure and the Sophos appliance should be obtained and filed here to complete the record.
