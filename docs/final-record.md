# Final setup record — 19 September 2026

The owner accepted the working remote-reading routine and observed battery use, then
requested setup closure with the Bluetooth host and mapper left enabled. Maintenance
cleanup completed successfully. No additional hardware experiments are scheduled.

## Retained baseline

| Component | Final state |
| --- | --- |
| Device | Kindle Paperwhite 5 / 11th generation; Amazon 5.18.1, kernel 4.9.77-lab126 |
| Reader | KOReader v2026.07.1, existing Véra/KPM 0.2.2/scriptlet workflow |
| Remote | Yiser-J6 in original swipe mode; RIGHT next / LEFT previous |
| Bluetooth host | KHP v3.16.0, running |
| Mapper | Bundled v1.6.0 plus the opt-in J6 classification fix, running |
| Startup | Both boot autostarts disabled; tested manual on-device sequence after reboot |
| Sleep | Normal power control; `preventScreenSaver=0`, mapper keep-awake disabled |
| Maintenance | Setup/recovery SSH stopped; helper and HTTP Inspector absent |

The final inventory verified the deployed mapper SHA-256:

```text
f3a5f7951fab9cd07aeaeb1e3c709003b555dc5b759411488d1ac162aa8caf55
```

The bundled KOReader integration files were also identified:

| File in `hidpassthrough.koplugin` | SHA-256 |
| --- | --- |
| `main.lua` | `5f64afcc1650743bf256b2a487eb53793ca51a01d938f6d67b571803e68c2af8` |
| `eventserver.lua` | `f632ad966d4b91e984fb55e1dbf37a932fbe0ab37cbeabc8e1a784df2610f3c0` |

These are historical installed identities, not a promise of byte-identical rebuilds.
[Source, package, patch and toolchain pins](../provenance/sources.json) and
[build verification](build.md) preserve the reproduction details. The public helper
configuration was host-tested and has not been deployed to this Kindle.

## Final checks and cleanup

A bounded authenticated inventory compared the running services, deployed files,
configuration and original mapper backups with their recorded identities. All matched.
It found the root filesystem read-only, no sleep inhibitor, and the original manual
startup policy intact. Temporary diagnostic launchers, reports and transfer staging
were already absent; the final cleanup did not delete books or broad directories.

Independent key-only recovery authentication succeeded before the setup channel was
closed. The shutdown checked exact process ownership, stopped the two maintenance
servers, removed only their own firewall rules/PID files, then verified:

- No SSH listeners on 2222/2223, settings helper on 8322 or HTTP Inspector on 8080.
- No remaining setup SSH process or maintenance listener; the final recovery command
  was the sole remaining session and ended normally with a successful return.
- Bluetooth host and mapper still running, with unchanged mapping configuration.
- Control/action endpoints retained on loopback at 8321/8323.
- `preventScreenSaver=0` and the root filesystem still read-only.

Recovery runtime, shortcuts, pairing and rollback backups remain installed. A failed
preflight prevented an unnecessary client-address change; the existing recovery
configuration stayed intact. An intermediate shutdown stopped when Dropbear removed its
own PID file; a state-checked continuation verified the first server was fully closed
before stopping the second. [History](history.md) retains these limits and resolutions.

Turning Wi-Fi off through the normal Kindle control is the final owner step. Its state
after the maintenance connection ended was not remotely verified. Bluetooth remains
needed for page turning. No SSH, terminal or computer belongs in the daily reading path.

## Acceptance and remaining limits

Twelve full functional/lifecycle cases pass. Earlier physical sleep/wake checks are now
supported by a same-boot increase from zero to seven successful kernel suspends, no
failures, and paired PM timestamps including about 8 h 36 min suspended.

The owner reports unchanged displayed battery percentage overnight and minimal,
sustainable usage. Exact battery endpoints, elapsed battery-test hours and a matched
software-disabled comparison were not recorded. These observations establish owner
acceptance, not zero energy cost or a quantified added-drain rate. No performance
comparison, complete feature-disable/native-Bluetooth restoration or binary rollback
was executed at closure. Recovery authentication and maintenance shutdown were tested;
failed-boot recovery is not promised.

Use [daily reading](daily-use.md), the [installed component catalog](installed-layout.md)
and [recovery/rollback guidance](troubleshooting.md) for future reference. Detailed
acceptance statuses and measurement limits remain in [validation](validation.md) and
[battery observations](battery.md).
