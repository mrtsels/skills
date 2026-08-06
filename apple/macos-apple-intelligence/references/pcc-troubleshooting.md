# Private Cloud Compute (PCC) Troubleshooting

## CRITICAL: Diagnose Before Acting

**Do NOT follow the README's "reset pool" advice blindly.** But also: **do NOT assume 32080 with `clientCacheSize>0` is permanent hardware rejection** — it may be database corruption from a botched deletion attempt.

Before any action, run the complete diagnostic sequence:

```
1. fm available (from user's Terminal.app — NOT Hermes TUI)
   ├── Both available → PCC is working. UI issue or rate limiting.
   │   See references/pcc-troubleshooting.md §Cross-References.
   │
   └── PCC not available from Terminal.app too → real issue.
       Proceed to step 2.

2. Check PCC log signals:
   └─ sudo log show --last 3m --predicate 'process == "privatecloudcomputed"'
        | grep -iE "didn.t receive|attestationsExist:"
   
   ├── "attestationsExist: clientCacheSize=0" → pool genuinely empty.
   │   Action: Reset pool + idle 15-30 min.
   │
   ├── "didn't receive any inline attestations" + clientCacheSize≥1
   │   → Could be database corruption from prior botched deletion OR
   │     legitimate server rejection.
   │   Action: Check if db.sqlite has been deleted/truncated while daemon held
   │     it open (check unified log for "BUG IN CLIENT OF libsqlite3.dylib").
   │     If corruption found → proper reset (kill → verify dead → delete → wait).
   │     If no corruption and clean rebuild still fails → hardware limitation.
   │
   └── Neither signal seen → daemon may not be running.
       Action: Trigger PCC request from Terminal.app to start it.
```

**Trap**: The log signal `didn't receive any inline attestations` with `clientCacheSize=40` was initially misinterpreted as "server-side SEP hardware rejection — permanent and unfixable." In reality, the attestation pool had been corrupted by deleting `db.sqlite` while the daemon still held SQLite WAL/SHM file handles from a prior session. The `libsqlite3 BUG` error confirmed corruption. After a proper clean rebuild (kill daemon → verify dead → delete → idle 15 min), PCC worked on the same CH/A hardware. This was proven by `fm respond --model pcc` from the user's Terminal.app returning "The capital of France is Paris."

| Signal | Possible Meaning | Action |
|--------|-----------------|--------|
| `didn't receive any inline attestations` | Server-side rejection OR database corruption | Check for libsqlite3 BUG first. If corruption → proper reset + idle. If clean → hardware limit. |
| `attestationsExist: clientCacheSize=0` | Local pool empty | Reset + idle 15-30 min |
| `BUG IN CLIENT OF libsqlite3.dylib: vnode unlinked while in use` | Deleted db.sqlite while daemon held file handles | Kill daemon proper, re-delete, restart fresh |

---

## Server-Side Attestation Rejection (CH/A Hardware Limitation)

### Key Log Signal

```
didn't receive any inline attestations
```

Preceded by:
```
attestationsExist: clientCacheSize=40  ← daemon HAS enough attestations
returning 2 attestations               ← sends them to PCC server
```

### Full Evidence Pattern

```
16:12:09  expectedAttestations:=40
16:12:09  attestationsExist: clientCacheSize=40   ← has cached proofs
16:12:09  returning 2 attestations                ← sends them to server
16:12:09  adding prefetched attestation for node  ← attaching to request
16:12:09  didn't receive any inline attestations  ← SERVER REJECTS
16:12:17  Node substreams task finished successfully  ← computation ran fine
16:12:17  Ropes request finished successfully          ← computation succeeded
16:12:17  IncomingUserDataReader shutdown Code=32080   ← attestation fails, results blocked
16:12:17  releasePowerAssertion                        ← daemon gives up
```

### What Actually Happened (Real Session Retrospective)

In a real debugging session on a Mac16,8 (CH/A, macOS 27.0), the 32080 error with `clientCacheSize=40` and `didn't receive any inline attestations` was initially misdiagnosed as permanent SEP hardware rejection. The actual cause was **database corruption from improper file deletion during a prior pool reset attempt**:

1. The agent tried to reset the pool by running `rm -f "$DIR"/db.sqlite*` **before verifying the daemon was dead**
2. The daemon still held SQLite WAL/SHM file handles from a prior session
3. Deleting live files triggered: `BUG IN CLIENT OF libsqlite3.dylib: vnode unlinked while in use`
4. The sequel established a **corrupt** database (40 "cached" attestations that were actually invalid SQLite pages)
5. The daemon tried to serve these corrupt attestations → server rejected them → "didn't receive any inline attestations"
6. After a **proper** reset (kill → VERIFY DEAD → delete → idle 15 min), PCC worked: `fm respond --model pcc` returned "The capital of France is Paris."

**Key lesson**: `didn't receive any inline attestations` with `clientCacheSize>0` does NOT automatically mean permanent hardware rejection. It may mean the database was corrupted by a prior improper deletion. Always check for `libsqlite3 BUG` errors in the unified log before concluding hardware limitation.

### Why Pool Reset Does NOT Help

The pool was never empty — it had 40 attestations. The attestations were built correctly but rejected server-side. Resetting the pool just causes the daemon to rebuild the same kind of attestations, which get rejected again. This creates a vicious cycle where each rebuild triggers new prefetch activity but never makes progress.

### Is It Fixable?

**Usually, yes.** The 32080 error with `didn't receive any inline attestations` is most often caused by pool corruption from improper deletion, not permanent hardware limitation. A proper clean rebuild (kill daemon → verify dead → delete → idle 15-30 min) resolves it in most cases.

Only if a **clean rebuild** (no libsqlite3 BUG, confirmed fresh db.sqlite) still produces the same error should you suspect a genuine hardware-level limitation. Even then, verify by:
1. Running `fm available` from the user's Terminal.app (not Hermes TUI) — if PCC shows available, it's not hardware-limited
2. Running `fm respond --model pcc "What is the capital of France?"` from Terminal.app — if it responds, PCC works

**End-side Apple Intelligence** (proofreading, summarization, Genmoji, Writing Tools basic features) works regardless and doesn't depend on PCC attestation.

---

## Local Pool Staleness (Fixable)

### Key Log Signal

```
attestationsExist: clientCacheSize=0
```

Also look for `failed prefetch attestations: Code=32022` in the log, which indicates the daemon couldn't prefetch a fresh pool.

### Log Pattern

Repeating 3-second cycle without any successful PCC requests:

```
outgoingUserDataWriter ended due to cancellation, error=...Code=32080
Data substream task finished successfully
Ropes request finished successfully
IncomingUserDataReader transitions from shutdown to finish state. ...32080
```

### Common Triggers

- Recent region change (CH/A → LL/A via RegionSpoof kext) — daemon needs to rebuild attestations for the new region context
- AMFI was previously disabled and re-enabled
- System was restored from backup
- Daemon crash during attestation pool refresh
- First boot after kext installation

### Error 32022 During Prefetch

When the local pool is empty, you may see:
```
failed prefetch attestations: Error Domain=PrivateCloudComputeError Code=32022
```

This is a **secondary symptom**, not a root cause. The daemon tried to prefetch attestations but couldn't. This usually means:
- No cached nodes available (nodesReceived.log is empty or stale)
- The daemon hasn't had time to contact Apple's attestation service
- Network constraints preventing the attestation fetch

Fix: this resolves automatically after the daemon sits idle long enough to rebuild. The 32022 is informational — focus on getting the pool rebuilt.

### Reset Procedure

```bash
# Step 1: Find attestation store path
DIR="$(sudo lsof -c privatecloudcomputed -Fn 2>/dev/null | sed -n 's/^n//p' | grep -m1 -oE '.*/attestationstore_v3')"
echo "DIR=$DIR"

# Step 2: Kill daemon FIRST
# launchctl kill KILL system/com.apple.privatecloudcomputed does NOT work
# on macOS 27 — the service label is not registered under launchd.
# Kill by PID instead:
PID="$(pgrep -f privatecloudcomputed)"
sudo kill -KILL "$PID"

# CRITICAL: Verify daemon is dead before deleting
# If you delete db.sqlite while the daemon still has it open (from a prior
# session's WAL/SHM), you get:
#   BUG IN CLIENT OF libsqlite3.dylib: database integrity compromised
#   by API violation: vnode unlinked while in use
ps aux | grep privatecloudcomputed   # should show nothing

# Step 3: Delete stale attestation database + node cache
rm -f "$DIR"/db.sqlite*
rm -f "$(dirname "$DIR")"/nodesReceived.log

# Verify: ls "$DIR"/ should show empty dir (only . ..)
```

### Critical: Attestation Pool Builds Only During Idle Time

**The daemon builds attestations in the background when NOT serving requests.** This is the most commonly misunderstood step.

After deleting the pool and killing the daemon:
1. The daemon auto-restarts via XPC **only when a PCC request triggers it** (on-demand).
2. Once running, the daemon builds attestations during **idle CPU cycles** — when it is sitting idle, not actively handling requests.
3. **Do NOT use PCC features for 15-30 minutes after reset.** If you make a PCC request immediately, the daemon tries to use the empty pool → fails with 32080 → the daemon spends its time serving failing requests instead of idle-building attestations. This creates a vicious cycle: every attempt fails, and the pool never accumulates.
4. Let the daemon sit idle. It auto-reaches out to Apple's PCC attestation service when it has bandwidth.
5. Verify with:
```bash
sudo log show --last 3m --predicate 'process == "privatecloudcomputed"' \
  | grep -iE 'finished successfully|32080' | tail -15
```
6. Healthy state = multiple `Ropes request finished successfully` with zero 32080 errors.

---

## Error 32001 — Rate Limiting

Log includes `RetryAfterDate` with a future timestamp. Apple throttles when:
- Too many PCC requests in quick succession (especially failed ones)
- Too many attestation pool rebuilds
- Suspicious error patterns

Fix: stop clicking, wait the duration indicated in RetryAfterDate (typically hours).

## Error 32010 — Rate Limiting (Alternate Code)

Same as 32001 — `Ropes request failed` with `AppleIntelligenceRetryAfterDate`. Indicates Apple's PCC backend has temporarily blocked the device. Same fix: stop all PCC activity, wait several hours.

## Error 32057 + NWError / Network Errors

PCC can't reach Apple's backend at all. Causes:
- Proxy/VPN routing to a non-supported region (HK, CN, etc.)
- DNS failure for PCC domains
- Firewall blocking ports

Fix: route through a supported region node (US/JP), check DNS, verify general connectivity.

## Error 32080 + 32010 Mixed Pattern

```
32010 → 32080 → 32010 → 32080 → ...
```

User hammered PCC features, got rate-limited (32010), then after the rate limit cooled briefly, the pool was stale → 32080. Each 32080 triggers another rate-limit cycle. Fix: full reset (kill daemon + delete pool), then **idle 15-30 min** without touching PCC.

## Error: libsqlite3 BUG — vnode unlinked while in use

```
BUG IN CLIENT OF libsqlite3.dylib: database integrity compromised
by API violation: vnode unlinked while in use:
  .../attestationstore_v3/db.sqlite
  .../attestationstore_v3/db.sqlite-wal
  .../attestationstore_v3/db.sqlite-shm
```

**Cause**: Deleted `db.sqlite` (or the entire `attestationstore_v3/` directory) while the privatecloudcomputed daemon still had the SQLite files open. The daemon from a prior session may hold WAL/SHM file handles even after being killed — if you delete the files before the process fully exits, the OS warns of the violation.

**Fix**:
1. Kill the daemon (`sudo kill -KILL $(pgrep -f privatecloudcomputed)`)
2. **Wait** — confirm dead with `ps aux | grep privatecloudcomputed`
3. THEN delete the attestation files
4. The libsqlite3 BUG message itself is cosmetic — it doesn't prevent the pool from being rebuilt. Just don't make it a habit.

## Proxy/Routing Notes

The user's system may have a local HTTP/HTTPS proxy (127.0.0.1:1082) with Apple Intelligence domains in the bypass list:
- `sequoia.apple.com`
- `seed-sequoia.siri.apple.com`
- `*.ls.apple.com`
- `captive.apple.com`

These bypass entries ensure Apple Intelligence traffic goes direct, not through the proxy. If PCC is having network issues, check whether PCC domains (`*.apple.com` via PCC infrastructure) are hitting the proxy. The `Ropes request finished successfully` log indicates the data plane reaches Apple — but the attestation control plane may use different endpoints.

### Shadowrocket Config Location

Shadowrocket stores imported configs in iCloud Drive as SQLite databases:
```
/Users/minimx/Library/Mobile Documents/iCloud~com~liguangming~Shadowrocket/Documents/*.conf-*.db
```

The SQLite schema stores rules in the `config` table (key-value format). Extract rules with:
```bash
sqlite3 "path/to/file.conf-*.db" "SELECT * FROM config" | grep -E 'rule\|'
```

The `skip-proxy` bypass list and custom PROXY/DIRECT rules are both visible in that table. Common custom overrides added for PCC domains:
- `DOMAIN-SUFFIX,sequoia.apple.com,PROXY` — but `skip-proxy` already bypasses this, so it's redundant
- `DOMAIN-SUFFIX,gspe1-ssl.ls.apple.com,PROXY`

## Error 32033 — Unconfirmed Cause

Appears in some user reports alongside 32080/32010. Exact meaning unknown (no public documentation). Some users report it strikes at certain times of day and resolves overnight. No consistent workaround documented.

## Error 32080 + GREYMATTER COUNTRY_LOCATION=2

If `OS_ELIGIBILITY_INPUT_COUNTRY_LOCATION = 2` in the diagnose output, PCC will fail regardless of attestation pool state. The eligibility daemon itself blocks PCC because it detects the device is physically in a non-supported country. Fix: route through a supported-region proxy (US/JP), then `sudo launchctl kickstart -k system/com.apple.eligibilityd` to force a re-check.

## Rate-Limit Cyclical Pattern (from GitHub issues)

Several users report PCC works only during specific windows (e.g. early morning for ~10 minutes). Pattern:
- Successful Ropes requests with zero 32080 for a brief window
- Then back to persistent 32080
- Recurs the next day at same time

Unclear if this is server-side quota rotation, attestation certificate expiry windows, or actual rate limiting. No permanent fix known.

## Log Parsing Commands

```bash
# Full-spectrum grep (covers all known error codes + network signals + privacy relay)
sudo log show --last 3m --predicate 'process == "privatecloudcomputed"' \
  | grep -iE 'finished successfully|3200[0-9]|32033|RetryAfter|retry-after|privacyProxyRateLimited|privacyProxyErrorDomain|private access token|Rate-limited for token issuer|NWError|3205[0-9]|Insufficient inline|32080' | tail -15

# Last 3 min, key signals only
sudo log show --last 3m --predicate 'process == "privatecloudcomputed"' \
  | grep -iE 'finished successfully|3200[0-9]|RetryAfter|NWError|3205[0-9]|Insufficient inline|32080' \
  | tail -15

# Quick diagnostic: cached attestation count vs server rejection
sudo log show --last 3m --predicate 'process == "privatecloudcomputed"' \
  | grep -iE "didn.t receive|attestationsExist: clientCacheSize=|returning.*attestations" | tail -10

# Tail live (useful while testing after reset)
sudo log stream --predicate 'process == "privatecloudcomputed"' \
  | grep -iE 'finished successfully|32080'

# Historical search across wider window
sudo log show --last 12h --predicate 'process == "privatecloudcomputed"' \
  | grep -iE '32080|32010|32001|32022'
```

## Cross-References

- **GitHub Issue #62**: Exact match — CH/A Mac, all eligibility inputs = 3, GREYMATTER=4, persistent 32080 with "didn't receive any inline attestations". No fix found.
- **GitHub Issue #65**: Same 32080, but COUNTRY_LOCATION=2 (different blocker).
- **GitHub Issue #37**: SIP not disabled, different case.
- `references/pcc-model-assets.md` — Reference sizes for model download progress
