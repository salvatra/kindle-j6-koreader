# Development history

This record follows the setup from the first input capture to the working mapper fix.
It includes failed attempts and the evidence behind each change. Personal identifiers
and unredacted diagnostic logs are excluded.

| Stage | Observation | Decision |
| --- | --- | --- |
| Initial review | New setup; no prior remote work; PW5/5.18.1/KOReader 2026.07.1/Véra identified | Reuse existing KPM/scriptlet stack and reviewed KHP release |
| Original J6 mode | Arch exposes touch plus consumer interfaces; six LEFT/RIGHT gestures observed | Characterize full frames instead of assuming keyboard codes |
| Alternate mode | Three LEFT/two RIGHT pinch-like events; one physical press missed | No keyboard benefit; restore and verify original swipe mode |
| Recovery | Separate copied key-only Dropbear worked with KOReader closed; stop/start cleanup passed | Proceed with independent working-OS maintenance access; no failed-boot guarantee |
| Baseline installation | Exact KHP 3.16.0 package and mapper 1.6.0 installed through existing KPM | Keep both boot starts off; preserve package ownership and private backups |
| First status read | API initially refused connection, then existing process/log showed normal startup | Treat as readiness race; no redundant reinstall |
| Pairing and mapping | J6 released from Arch, paired directly to Kindle; both whole gestures recorded | Exclusive mapper ownership and KOReader-specific page actions |
| First physical page test | No response despite link, stored gestures and local endpoint | Compare recorder/runtime input classification |
| Targeted fix | J6 lacked DIRECT/MT properties; explicit gesture bindings were excluded at runtime | Add opt-in BTN_TOUCH+ABS_X/Y path; retain upstream matcher/transport |
| Software regression | Three new tests fail old classification; all 45 pass with fix | Build official matched Rust toolchain; preserve original mapper binary |
| First ARM build | Distribution compiler and upstream std had incompatible build metadata | Use checksum-verified official compiler/host/ARM std locally; no global toolchain replacement |
| Physical checks | Both directions, 20/20 counts, quick/hold/scope and lifecycle checks passed | Preserve working baseline; no Bluetooth rewrite or repeat tests |
| Offline/sleep batch | Computer/Wi-Fi off, idle and three physical sleep/wake cycles worked | Continue measured suspend/battery validation |
| Maintenance interruption | Wi-Fi networks absent once; Kindle rebooted | Cause unestablished; prior kernel-counter comparison no longer usable |
| Recovery reconnection | Host DHCP address changed; copied server still restricted to old client | Update only allowance/controller manifest; verify access and clean setup SSH |
| Reboot startup | BT Manager enabled, then native Button Mapper Start; page pair worked | Manual on-device startup confirmed; boot policy unchanged |
| Battery preparation | New boot baseline captured; SSH/helper listeners closed | Begin enabled reading/night, then matched disabled comparison; results pending |
| Public packaging | Personal identity present in fixture and local helper configuration | Sanitize fixture, parameterize helpers, preserve code provenance and test separately |

An interrupted early capture and an early diagnostic timeout incompatibility were handled
as failed preparations, not claimed as successful device tests. The final capture worker
has bounded duration and interruption cleanup. Exact event node numbers and process IDs
were never promoted to permanent configuration.

This project used existing upstream components first. Its new runtime contribution is
the classification fix, supported by a before/after failure and recorded gesture replay.
