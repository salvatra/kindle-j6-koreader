# J6 → Kindle → KOReader

[![Checks](https://github.com/salvatra/kindle-j6-koreader/actions/workflows/ci.yml/badge.svg)](https://github.com/salvatra/kindle-j6-koreader/actions/workflows/ci.yml)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg)](LICENSE)

Use a **Yiser-J6 Bluetooth remote to turn pages in KOReader**, with everything running
on the Kindle. Once set up, reading needs no laptop, phone, Wi-Fi network, internet
or terminal commands.

This companion project preserves a working setup, a small mapper compatibility fix,
and the evidence behind it. It builds on Lucas Zampieri's
[Kindle HID Passthrough](https://github.com/zampierilucas/kindle-hid-passthrough),
[Kindle Button Mapper](https://github.com/zampierilucas/kindle-button-mapper-rs), and
[KOReader](https://github.com/koreader/koreader).

> **Status — 19 September 2026:** setup and maintenance cleanup are complete. Page turning,
> offline use, reconnection, manual reboot startup and actual suspend are confirmed:
> **12 of 16 full acceptance cases pass.** The owner accepts the reading routine and
> observed battery use, reporting unchanged displayed charge overnight. Controlled battery
> comparisons and complete feature-disable/rollback tests were not performed.
> See the [final setup record](docs/final-record.md) and [complete results](docs/validation.md).

## What is new here?

The J6's LEFT and RIGHT controls produce **complete touch swipes**, not ordinary arrow
keys. On the tested Kindle, its input node exposes `BTN_TOUCH` and `ABS_X/Y`, but lacks
the direct-touch and multitouch properties expected by the mapper's normal event loop.
The bundled recorder could save the gestures, yet normal presses initially did nothing.

The patch lets that node use the mapper's **existing** gesture matcher when it has
explicit gesture bindings. It preserves the previous handling of direct/multitouch
devices and ordinary button remotes, and re-evaluates the opt-in when mappings reload.
Only `src/main.rs` changes production behavior. Three added tests replay six observed
swipes and check the classification boundaries. [Fixture provenance](docs/fixtures.md)
explains their origin and limits.

| Component | Where it comes from |
| --- | --- |
| Bluetooth ownership, pairing, reconnect and UHID input | Upstream Kindle HID Passthrough |
| Gesture recorder/matcher, mapping UI and action delivery | Upstream Kindle Button Mapper |
| Reading application and bundled loopback integration | KOReader and upstream KHP plugin |
| Single-touch gesture opt-in, three regression tests and sanitized fixtures | This project's patch |
| Capture/recovery helpers, reproduction recipe and setup evidence | This project |

We have not rewritten the Bluetooth stack or replaced the bundled KOReader plugin.
The new public helper configuration is covered by host tests; it has **not** been
deployed to the reference Kindle. [Attribution and licensing](NOTICE.md).

## Tested combination

| Item | Observed version or setting |
| --- | --- |
| Kindle | Paperwhite 5 / Paperwhite 11th generation, ARMv7 |
| Amazon firmware | 5.18.1; kernel 4.9.77-lab126 |
| Reading software | KOReader **v2026.07.1** |
| Jailbreak / launcher | Véra; existing KPM 0.2.2 and search-bar/scriptlet workflow; no KUAL |
| Remote | Yiser-J6, original swipe mode, BLE |
| Bluetooth package | Kindle HID Passthrough **v3.16.0**, commit `966037ee3d9c81792793b8c684b0c420d4ee3ef5` |
| Bundled mapper | v1.6.0, commit `fa3a851ef1d26f3045ef27c7dc3465e45d56de14`, plus this patch |
| Development host | Arch Linux x86_64 |

The actual KOReader application version differs from the KPM package version; record
both rather than assuming they are interchangeable. Other Kindles, firmwares and J6
revisions need their own checks. **J8 has not been tested.**

## How pages travel

```mermaid
flowchart LR
    J6["J6 LEFT / RIGHT"] -->|BLE| KHP["Kindle HID Passthrough"]
    KHP -->|UHID events| M["Patched bundled mapper"]
    M -->|"completed gesture → local action"| K["KOReader plugin, 127.0.0.1:8323"]
    K --> B["Previous / next page"]
```

All boxes after the remote run on the Kindle. Loopback HTTP stays on the device; it
does not require Wi-Fi or HTTP Inspector. SSH is a maintenance tool, not part of reading.

KOReader 2026.07's native keyboard hotplug path is useful for keyboard remotes. It did
not remove the need to recognize this J6's touch gestures. [Technical explanation](docs/design.md).

## Start here

**Already using this exact working setup?** Follow [daily use](docs/daily-use.md).
Do not reinstall it to match this repository.

**Setting it up again?** Read [installation](docs/setup.md), including recovery and
package ownership, before changing the Kindle. This repository neither jailbreaks
devices nor updates Amazon firmware. There is no one-command hardware installer.

**Reviewing or rebuilding the fix?** On an x86_64 Linux development host with Python
3.11+, Git, a C compiler/linker, binutils and normal development headers:

```sh
git clone https://github.com/salvatra/kindle-j6-koreader.git
cd kindle-j6-koreader
python3 -m unittest discover -s tests -v
python3 tools/check_repo.py
python3 tools/reproduce.py
```

The reproducer downloads checksum-pinned official Rust/Cargo 1.98.1 components and the
pinned upstream source into ignored local directories. It installs no host packages
and never contacts a Kindle. It verifies the expected **42 pass / 3 fail** baseline,
then **45 pass / 0 fail** with the patch, and cross-builds a static ARMv7 binary.
See [build inputs and outputs](docs/build.md), including checksum limitations.

## Reading and restarting

With services running, open a KOReader book and turn on the J6 if needed. It reconnects
automatically: **RIGHT → next page; LEFT → previous page**. Use the Kindle's normal
power button for sleep. Tested menu, no-book and native-library contexts do nothing.

After a Kindle reboot, enable **HID Passthrough daemon** in BT Manager, then open
**Button Mapper → Device → Start** from the native Kindle library. Reopen the book.
Both boot autostarts remain disabled in the recorded setup. No terminal or re-pairing
was needed for that manual startup check. [Details and remaining limits](docs/daily-use.md).

## Guides and evidence

| Guide | Purpose |
| --- | --- |
| [Installation](docs/setup.md) | Ordered recovery, KPM, patch and mapping procedure |
| [Build](docs/build.md) | Exact source/toolchain pins, tests, ARM output and provenance |
| [Recovery](docs/recovery.md) | Optional key-only maintenance shell and its limits |
| [Installed components](docs/installed-layout.md) | What stays on Kindle, what runs while reading, and maintenance cleanup |
| [Troubleshooting / rollback](docs/troubleshooting.md) | Identify a failing layer and preserve a working setup |
| [Battery and sleep](docs/battery.md) | Accepted observations, measured suspend and comparison limits |
| [Final setup record](docs/final-record.md) | Dated cleanup result, retained runtime and evidence |
| [Validation](docs/validation.md) | What passed, what did not, and what was actually measured |
| [Experiment history](docs/history.md) | Sanitized account of the setup, failed baseline and targeted fix |

The [example configuration](examples/j6-config.ini) contains a **synthetic Bluetooth
address**. Record gestures on your own remote where possible; never overwrite existing
device mappings with the example. Captures default to ignored `private/captures/`.

## Updates and contributions

This is a local patch to a KHP-owned mapper binary. A package update may overwrite it.
Review newer upstream fixes, exact bundled versions and your original binary backup
before upgrading. The pinned versions are a reproducible historical baseline, not a
recommendation to downgrade a different working installation.

Contributions should be small and evidence-driven. Follow [CONTRIBUTING](CONTRIBUTING.md)
and avoid uploading credentials, bonds, books or raw personal logs. The initial
publication contains source and documentation, **no prebuilt release binary**.
