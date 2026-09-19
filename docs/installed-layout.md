# Installed components and maintenance

This is the layout of the tested PW5 setup: KHP 3.16.0, its bundled mapper 1.6.0 with
the J6 patch, and KOReader 2026.07.1. KPM owns the base package. The mapper executable
is the one documented local override; a package upgrade can replace it.

## Files to retain

| Location on Kindle | Purpose |
| --- | --- |
| `/mnt/us/kindle_hid_passthrough/` | Upstream Bluetooth host, compatible runtime, configuration and private pairing data |
| `/mnt/us/kindle-button-mapper/` | Patched mapper, gesture configuration, scripts and mapping UI |
| `/mnt/us/koreader/plugins/hidpassthrough.koplugin/` | Upstream KOReader controls and local page-action endpoint |
| `/mnt/us/documents/BTManager.sh` | Native-library Bluetooth management launcher |
| `/mnt/us/documents/MapperManager.sh` | Native-library Button Mapper launcher |
| `/etc/upstart/kindle-button-mapper.conf` | Existing mapper service, configured for manual startup |
| `/etc/udev/rules.d/99-hid-keyboard.rules` and `99-kindle-button-mapper-pointer.rules` | Package-owned input integration |
| `/mnt/us/kindle-remote-recovery/` | Separate on-demand recovery runtime, private authentication material and controller |
| `/mnt/us/documents/Start-Remote-Recovery.sh` and `Stop-Remote-Recovery.sh` | Native-library maintenance shortcuts |

Keep private backups of the original mapper, saved mapping configuration, service job
and affected package/application-registration state. The tested setup retains these in
`/var/local/kindle-remote-E21/` (original mapper, configuration and service job),
`/var/local/kindle-remote-E15/` (package/application-registration state) and
`/var/local/kindle-remote-E28/` (earlier recovery configuration), with supporting host
backups. They are recovery material, not running services. Do not upload their contents or restore
whole databases over newer unrelated changes.

The recovery controller installed during setup uses a restricted client address. The
generalized controller in this repository was tested with host mocks and is a separate
source artifact; it has not silently replaced the working installed controller. If the
computer's address changes, follow [recovery](recovery.md) and [troubleshooting](troubleshooting.md)
instead of widening access to the whole network.

## What runs during reading

| Component | Normal state |
| --- | --- |
| KHP Bluetooth host | Enabled; manages its sleep/wake behavior |
| Button Mapper | Running with the saved J6 gestures |
| KOReader and bundled action endpoint | Active while reading; page actions delivered locally |
| KHP control endpoint, port 8321 | Loopback only |
| KOReader action endpoint, port 8323 | Loopback only; required for this mapping |
| Mapper settings helper, port 8322 | On demand for configuration; closed after maintenance |
| KOReader SSH, port 2222 | Off outside maintenance |
| Separate recovery SSH, port 2223 | Off outside maintenance |
| HTTP Inspector, port 8080 | Not required; off |

Leaving a launcher or recovery binary installed does not mean its server is running.
The settings UI may start its helper again when opened. Do not remove the local reading
endpoints while trying to close maintenance servers.

Both automatic boot starts remain disabled. After a reboot, enable the HID daemon in
BT Manager, then use **Button Mapper → Device → Start**. Ordinary sleep/wake does not
require repeating that sequence. See [daily use](daily-use.md).

## Verified cleanup — 19 September 2026

Both SSH servers were stopped, with their own temporary firewall rules and PID files
removed. No settings-helper or HTTP Inspector listener remained. The original temporary
diagnostic launcher/reports and installation staging were confirmed already absent.
The Bluetooth host and mapper stayed running; ports 8321 and 8323 remained loopback-only.
No reading binary, mapping, pairing, power setting or boot policy changed. Recovery files
and rollback backups were retained. See the [final setup record](final-record.md).

## Cleanup rules

Completed diagnostics and transfer staging can be removed after verifying their exact
ownership and preserving needed evidence. The original setup removed the temporary
Kindle Remote Check launcher/report and the KHP installation staging directory. Do not
delete whole userstore directories or everything matching a broad filename pattern.

Close maintenance processes by their executable and arguments, remove only their own
PID files and firewall rules, and close the active recovery connection last. Keep the
Bluetooth host, mapper, gesture configuration and pairing intact for remote reading.
Turn Wi-Fi off through the normal on-device control after maintenance is finished.

On the development computer, keep this source repository and private recovery backups.
The ignored `.cache/` and `build/` directories are reproducible downloads/build outputs;
they are not needed for reading. Captures and detailed session records stay private.

## Before a future update

Record the current package, application and mapper versions; preserve the working
binary/configuration and prove maintenance access. Review the update's actual bundled
mapper before applying this patch again. The pinned patch is for one exact source
commit, not every later release. Check page turning, reconnect and ordinary sleep after
an intentional update, and retain the [rollback procedure](troubleshooting.md).
