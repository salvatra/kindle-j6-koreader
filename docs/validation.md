# Validation record

As of **18 September 2026**. One Yiser-J6 in original swipe mode, one PW5/Amazon 5.18.1,
KOReader 2026.07.1, KHP 3.16.0 and the historical locally patched mapper build. Hardware
results are reported manual observations, corroborated by device metadata where noted.
No published claim covers arbitrary remotes, firmware or Kindle models.

## Hardware: 11 passed, 5 pending

| ID | Case | Status | Evidence / limit |
| --- | --- | --- | --- |
| F01 | 20 next-page presses | PASS | 20 separate RIGHT presses confirmed manually |
| F02 | 20 previous-page presses | PASS | 20 LEFT presses and round trip confirmed manually |
| F03 | Hold/release | PASS | No reported runaway; exact hold turn counts unrecorded |
| F04 | Two quick presses | PASS | Both directions confirmed |
| F05 | Scope/unintended actions | PASS | Tested menu, no-book, native-library and other brief-control contexts |
| R01 | Remote off/on | PASS | Three automatic reconnect cycles; exact seconds unrecorded |
| R02 | Reading pause/idle | PASS | Combined five-minute pause trial reported successful; exact awake state unrecorded |
| R03 | KOReader relaunch | PASS | Actions restored; no reported stale page replay |
| R04 | Normal sleep / actual suspend | PENDING | Three physical sleep/wake cycles worked; reboot lost the corresponding kernel-counter comparison |
| R05 | Kindle reboot/manual startup | PASS | BT Manager daemon enabled, native mapper Start, then both pages worked |
| O01 | Computer off/no phone relay | PASS | Standalone reading and reconnect reported successful |
| O02 | Wi-Fi off/Bluetooth retained | PASS | Offline page actions/reconnect reported successful |
| B01 | Matched reading battery | PENDING | Enabled observation prepared; no measured comparison or accepted tradeoff |
| B02 | Matched overnight battery | PENDING | Actual elapsed comparison and retained suspend evidence needed |
| U01 | Final daily routine acceptance | PENDING | Reading/startup steps confirmed; complete stop routine and acceptance outstanding |
| S01 | Full disable/recovery/rollback | PENDING | Independent working-OS recovery and its cleanup tested; complete feature rollback untested |

The finish line is reliable standalone reading, normal suspend, acceptable **measured**
drain, a short accepted on-device routine, and a reviewed disable/recovery path. Do not
turn pending rows into passes because the source looks correct or CI is green.

## Software checks

The exact old classification with the added regressions produces **42 passed, 3 failed**.
The public patch produces **45 passed, 0 failed**. Six labeled recorded Arch gesture
projections match the saved templates only on completed release. The stationary negative
case and ordinary/unconfigured remote cases are included. These are offline tests.

The fresh public recipe cross-builds an ELF32 ARM EABI hard-float static executable with
VFPv3-D16 and no interpreter/dynamic dependencies. The first public build differs in
checksum from the historical device binary. [Build details](build.md) and
[host verification snapshot](../provenance/public-verification.json) record this explicitly.

The generalized helper tests simulate exact target selection, invalid inputs, partial
composite devices, interruption cleanup, address validation, and recovery start/stop
against fake processes/firewall/server commands. **No real input node, signal target,
firewall or Kindle is used.** These helper changes are not newly hardware-tested.

CI re-runs host tests, repository-content checks, baseline/patched tests and ARM inspection.
It does not deploy, pair, infer sleep, estimate energy or upload release binaries.
The clean CI build passed all these checks. Its binary checksum differs from the local
Arch build; both are recorded as software-only results, with no byte-identity claim.
Current results are available in [GitHub Actions](https://github.com/salvatra/kindle-j6-koreader/actions/workflows/ci.yml).

## Updating results

Add a dated observation, versions, method, actual elapsed conditions, and uncertainty.
Keep failed or superseded experiments in history with their resolution. A no-change
battery percentage is below display resolution, not proof of zero cost. User acceptance
must accompany the measured battery tradeoff before declaring the project complete.
