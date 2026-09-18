# Diagnose one layer at a time

Preserve a working baseline. Change one condition, use bounded observations, and stop on
unexpected state. Do not reinstall, clear bonds or reboot repeatedly without new evidence.

| Symptom | Narrow next check |
| --- | --- |
| J6 connects to the laptop instead | Disconnect/block only that remote on the host; preserve its bond and unrelated devices |
| Paired icon but no actions | Check KHP HID readiness, actual associated node, mapper job and device bindings |
| Recorder works, normal swipes do nothing | Compare capabilities and exact mapper version with the [classification gap](design.md) |
| Worked before reboot | Enable BT Manager's HID daemon, then Button Mapper → Device → Start |
| Empty input trace | Identify all composite nodes and existing exclusive grabs before concluding no input |
| Two turns per press | Check duplicate owners/mappers or raw-plus-mapped delivery; do not map every motion sample |
| Works only in native reader | Inspect whether Favorites/auto fallback was selected instead of explicit KOReader actions |
| KOReader page endpoint absent | Verify bundled plugin/config and active app; do not enable HTTP Inspector reflexively |
| Recovery SSH times out | Check current Kindle IPv4 versus gateway, client DHCP address, configured single-client allowance and listener |
| Wi-Fi networks disappear | Preserve logs/counters and report the condition; avoid destroying sleep evidence with an unnecessary reboot |

The tested Kindle did encounter missing Wi-Fi networks once and was rebooted. Its cause
was not established. Afterward, an independently confirmed stale recovery client-IP rule
was corrected. These are distinct observations; neither proves a general KHP Wi-Fi defect.

## Safe maintenance observations

Use existing logs sparingly and redact before sharing. Match input nodes by remote
identity/capabilities, never a copied event number. `/var/log/kindle-button-mapper.log`
contains gesture/action evidence and `/var/log/hid_passthrough.log` contains host evidence.
Do not grab Kindle touchscreen/power nodes. Stop diagnostics before a battery trial.

One-shot reads of the current boot ID, existing `/sys/kernel/debug/suspend_stats`, and
timestamped PM entry/exit lines can corroborate suspend. Do not create a debug mount or
keep polling just to get a number. A changed boot ID invalidates before/after counter
comparison. Raw battery current/charge units have not been calibrated by this project.

## Mapper-only rollback

Before any rollback, confirm access through the independently tested recovery path and
identify the exact mapper job/process and current files. Keep an unused, hash-verified
copy of the installed binary, config and job from before the change.

1. Check that no capture is active and that stopping the mapper's existing Upstart job
   cannot unmount an unrelated `/usr/share/X11/xkb/symbols/us` override.
2. Stop only an identity/argv-verified mapping helper and the `kindle-button-mapper` job.
   Never kill every process with a broad loader or helper-name pattern.
3. Stage the original binary, verify its saved checksum and execute permissions, then
   atomically replace the patched binary on the same filesystem.
4. Start the same job and verify its identity/state, normal power settings and recovery.
   Preserve the user's current mappings and pairing; do not restore stale config blindly.

The original bundled mapper hash is recorded in [sources.json](../provenance/sources.json).
For this J6, restoring that original binary also restores the known classification gap;
it is a software rollback, not a promise that page turning continues. Failure rollback
was prepared during the original deployment but a complete binary rollback was **not
actually needed or tested**.

## Full feature disable / package removal

This acceptance case is still pending. The available UI toggles can stop the mapper and
suspend the HID daemon, but a KHP control process may remain. Releasing/re-enabling native
Bluetooth ownership needs verification on the actual Kindle. A software-disabled battery
reference must document which host, mapper, helper, listener and startup components remain.

KPM owns the original package. Review the exact installed uninstall hooks and current
process matches before removal; upstream broad loader-pattern kills can affect unrelated
programs. Preserve pairing/configuration and consistent private backups. Do not replace
whole app/package databases over later unrelated changes. Restore only recorded state,
verify root RO and normal sleep, and test native Bluetooth if it was taken over.

No factory reset, firmware update, kernel replacement or re-jailbreak is a rollback step.
If the observed state differs from the reviewed plan, stop and diagnose through recovery.
