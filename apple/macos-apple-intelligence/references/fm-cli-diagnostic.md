# fm CLI — PCC Diagnostic Reference

## CRITICAL: fm Output Depends on Calling Shell

`fm` can report DIFFERENT results from different shells on the SAME machine. This was confirmed in a real session:

| Shell | `fm available` | `fm respond --model pcc` |
|-------|---------------|--------------------------|
| User's Terminal.app (zsh) | Both available ✅ | Worked ✅ |
| Hermes TUI terminal (bash → Python) | PCC not available ❌ | Error ❌ |

**Root cause**: The `fm` binary checks the calling process's XPC bootstrap context. The Hermes terminal tool runs in a process tree (Hermes Python daemon → bash) that has a different XPC audit session than a direct Terminal.app shell. The context mismatch causes `fm` to deny PCC access even though the device and daemon are fully capable.

**Rule: Always verify PCC by running `fm` from the user's own Terminal.app.** The Hermes TUI terminal tool's output is unreliable for `fm available --model pcc` and `fm respond --model pcc`.

If Hermes terminal shows "PCC not available" but the user's Terminal shows "PCC available", the daemon is healthy. The issue is only the tool's XPC context.

## Session Output (CH/A Mac16,8, macOS 27.0)

```
% fm available
Error: PCC inference is not available in this context.
System model available

% fm available --model system
System model available

% fm available --model pcc
Error: PCC inference is not available in this context.

% fm respond --model system --no-stream "Say hello in one word"
Hello

% fm respond --model pcc --stream "where do apple's employees work in the headquarters? what is the address"
Error: PCC inference is not available in this context.
```

The PCC rejection is consistent across `fm available` and `fm respond`, matching the privatecloudcomputed log signal `didn't receive any inline attestations` + error 32080.

## What fm Says vs What the Logs Say

| Layer | fm output | Log signal |
|-------|-----------|------------|
| Model availability | `System model available` | (no log needed) |
| PCC availability | `Error: PCC inference is not available in this context.` | `didn't receive any inline attestations` + Code=32080 |
| Pool state | (not shown by fm) | `attestationsExist: clientCacheSize=40` |
| Compute success | (not reached) | `Ropes request finished successfully` |
| Shutdown | (not reached) | `IncomingUserDataReader shutdown Code=32080` |

## When to Use fm as Diagnostic

1. **First step** before touching anything — `fm available` tells you if PCC is reachable at all
2. **After pool reset** — `fm available --model pcc` confirms whether the pool rebuild worked or if it's a server-side rejection
3. **Before blaming network** — if `fm available --model system` works but `--model pcc` fails, the issue is attestation, not connectivity

## Notes

- fm does NOT do any local pool management — it reaches the same Apple PCC APIs as privatecloudcomputed
- **If `fm` from the user's Terminal.app says PCC unavailable**, the issue is real (server-side attestation rejection or pool issue). Pool resets won't help if attestation is server-rejected.
- **If `fm` from Hermes TUI says PCC unavailable**, verify from the user's own Terminal.app first before concluding there's a device-level problem.
- If `fm` from Terminal.app says PCC available but PCC features fail in the UI, then it's likely a different issue (rate limiting, network routing to specific PCC nodes, eligibility location check, etc.).
