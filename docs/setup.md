# Setup on the tested Kindle combination

This is an ordered reproduction guide for the [tested versions](../README.md#tested-combination).
It is not a universal installer. The repository build does **not** deploy anything.
For an already working installation, preserve it and use [daily use](daily-use.md).

## 1. Inventory and establish recovery

Record the actual Kindle model, Amazon firmware, kernel/ABI, KOReader `git-rev`, package
ownership and launcher stack. The reference device used PW5, firmware 5.18.1, kernel
4.9.77-lab126, Upstart 0.6.6, Véra and existing KPM 0.2.2. It did not require KUAL.
Do not re-jailbreak, upgrade firmware or install another package manager for this guide.

Test maintenance access that remains available after **fully exiting KOReader**. A copy
of userstore or KOReader's own SSH server is not that test. The optional [recovery guide](recovery.md)
describes the separately copied Dropbear/scriptlet method used here. It still requires a
working Kindle OS and Wi-Fi; it does not guarantee recovery from failed boot or frozen OS.

Back up affected files and consistent package/app-registration database state privately.
Record which target paths were absent, the native Bluetooth service state and boot policy.
Do not copy whole databases, keys or books into this Git repository. For every device
change, write its exact commands, target, expected effects, bounds and rollback first.

## 2. Review and install the pinned upstream baseline

Use KHP **v3.16.0**, commit `966037ee3d9c81792793b8c684b0c420d4ee3ef5`, and the exact
`kindle-hid-passthrough.kpkg` asset in [sources.json](../provenance/sources.json).
Download from the pinned [release](https://github.com/zampierilucas/kindle-hid-passthrough/releases/tag/v3.16.0)
and verify SHA256 **before transferring and again on Kindle**:

```text
5ad0c96f7d44362833b11e327a3548f1915c1c88a2bc130963cc4e6ba26e69b0
```

Inspect its install/uninstall hooks without running them. This package owns KHP, the
mapper, bundled KOReader plugin, native library launchers, udev rules and the mapper
Upstart job. The installer remounts root temporarily and starts services; it also has
broad process-name stop patterns. Before executing it, confirm those patterns cannot
match unrelated programs. Review `/dev/uhid`, native uinput and automatic module loading
for the actual kernel. Do not load a bundled module for a different kernel/Kindle.

The reference installation had no conflicting existing package/files. It used the
**existing KPM local-file install** rather than mixing a manual install with ownership.
The recorded form, after all prerequisites and private backups, was:

```sh
# KINDLE maintenance shell — reference form, not an automatic repository action.
# First stage/hash-verify the asset at this chosen path and close KOReader.
timeout -s TERM 90 /var/local/kmc/bin/kpm -y install \
  file:///mnt/us/kindle-j6-stage/kindle-hid-passthrough.kpkg
```

KPM may refresh its existing indexes. Do not add repositories or upgrade unrelated
packages. If a timeout/failure occurs, inspect remaining owned processes and the log;
do not blindly repeat the installer. This command alone is **not** the complete setup.

Preseed only newly absent configuration: KHP `protocol=ble`, `media_remote=false`;
mapper `keep_awake=false`, `log_buttons=false`, initially no device bindings. Preserve
other existing settings. The reference left main KHP boot autostart **off** and made
the mapper job manual by removing only its `start on ...` stanza in
`/etc/upstart/kindle-button-mapper.conf`, retaining stop/respawn/start logic. On this old
Upstart version, a modern override-file recipe was not substituted. Back up and verify
the exact job before a bounded root-RW edit, then restore root RO. Expected original
job SHA256: `40f97234cfc9d39742164c365c32c4eca145852755dfa8a0807665d64177cc54`.
The recorded manual job hash is `95f50cad7be9098866766e8014a3fb6fe42902b0794ef36f7253d6493e0c25ca`.
Keep boot startup disabled until your recovery and sleep behavior are established.

Verify ownership, actual mapper/plugin hashes, root RO, normal power settings and only
one Bluetooth owner. KHP's control API must bind to loopback `127.0.0.1:8321`. An early
connection-refused response can be a startup race: inspect status/logs before reinstalling.

## 3. Identify and move the remote

Use one remote and one changed condition at a time. The working J6 mode is the original
single-touch swipe mode. Do not switch to its alternate mode to seek arrow keys: that
mode offered no such benefit on this unit. J8 is outside the tested setup.

Optional development-host capture, after separately identifying/pairing **your** J6 and
installing Arch's evtest through your normal package workflow:

```sh
python3 tools/capture-j6.py --address YOUR:J6:ADDRESS:HERE --output-dir private/captures
```

Replace the placeholder with six actual hex octets. Run as your normal user in a terminal;
the helper requests sudo there for two bounded evtest grabs. It checks the exact address,
names, vendor/product and capabilities, emits six short-press cues, and releases both
readers on interruption. Unexpected interfaces/capabilities stop it. No keyboard/touchpad
node should be supplied manually. Optional `--other-mode` and `--restore-mode` cues are
experimental and do not establish restoration without reviewing the trace.

Before pairing on Kindle, disconnect/block only this remote on the host to prevent
competing auto-connections; preserve the bond and unrelated devices. In KOReader's
**Settings → Network → BT Manager - HID Passthrough**, enable the daemon, scan and pair
the identified J6. Do not infer the correct device from a marketing name alone. Confirm
BLE/HID readiness and the associated input node(s).

## 4. Build and apply the targeted mapper fix

Build locally using [the pinned recipe](build.md). The original bundled mapper binary
has SHA256 `2fb64c8fcff3dceaa34009f932d71351d24dcbf4a72dc5b596f2be6254fbef28`.
If your binary/base differs, stop and review that version; do not blindly patch over it.

Deployment is a separately bounded maintenance operation:

1. Transfer the fresh ARM binary to an **unused staging filename** next to the installed
   mapper, verify its generated checksum, then check its inert `--version` branch with a
   short timeout. Do not run the daemon from staging.
2. Keep tested independent recovery open. Back up the original mapper, current config
   and Upstart job into a new private on-device directory. Hash and preserve originals.
3. Identify the real mapper job and any `--waf-helper` process by executable **and argv**;
   stop only the helper and exact `kindle-button-mapper` Upstart job. Check no input capture
   is active and no unrelated XKB override mount is affected by its post-stop hook.
4. Atomically rename the checksum-verified binary over
   `/mnt/us/kindle-button-mapper/kindle-button-mapper`, retain execute permissions, and
   start the same manual job. Preserve KHP, pairing, mappings and plugin.
5. Verify version, running process, saved configuration hash, normal power state and
   recovery access. On failure restore the hash-verified original binary and same job;
   do not overwrite later mappings with an old configuration snapshot.

Bound each transfer/start/stop and inspect on unexpected output. A power loss can interrupt
shell cleanup; independent recovery and original files are prerequisites. A KPM update
can overwrite this locally patched package-owned binary. No firmware/kernel change or
Bluetooth-stack replacement is part of this step.

## 5. Record and map whole gestures

The native **Button Mapper** library app is the full mapping UI. Its **Device** tab
controls the mapper daemon; the **Bindings** tab contains **Save & Apply**. KOReader's
BT Manager also exposes **Key mappings** for the paired device.

Record one complete brief LEFT stroke, bind it to the explicit **KOReader Previous page**
action, then record RIGHT and bind **KOReader Next page**. Select the KOReader-specific
actions, not Favorites/auto fallback. Keep the mapper owning the J6 exclusively and do
not forward its raw input. Inspect the saved configuration for:

```ini
[device.yiser_j6]
name = Yiser-J6
uniq = 02:00:00:00:00:06
grab = true
passthrough = false

[device.yiser_j6.gestures]
j6_left = /mnt/us/kindle-button-mapper/scripts/koreader.sh prev_page
j6_right = /mnt/us/kindle-button-mapper/scripts/koreader.sh next_page
```

The address above is synthetic. The complete [example](../examples/j6-config.ini) includes
the recorded templates and settings. Prefer your own recordings; merge only the relevant
device/template sections, never overwrite unrelated mappings. A successful Save & Apply
message does not establish page turning. Open a book, test one RIGHT and LEFT, then run
the functional/offline/reconnect cases in [validation](validation.md).

## 6. Finish through observation

Test normal Kindle sleep, actual suspend, on-device restart, scope/no-op behavior, and
[matched battery trials](battery.md). Close maintenance SSH, helper UIs and captures
before battery intervals. Keep Wi-Fi off while retaining Bluetooth. Do not use sleep
inhibitors, fake touches, wake locks or a screen-off substitute for suspend.

The reference owner accepted observed battery use and requested setup closure. Controlled
battery comparisons and full feature-disable/rollback checks remain unperformed, as
recorded in the [final setup record](final-record.md). Recreating its successful page
actions does not establish the sleep or battery behavior of a different installation.
