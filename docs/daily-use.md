# Daily reading

These steps describe the tested setup; its measured battery and final full-disable
acceptance remain pending. [Current results](validation.md).

## Ordinary use

1. Wake the Kindle normally and open or resume a book in KOReader.
2. Turn on the J6 if needed; let it reconnect automatically.
3. **RIGHT** advances one page; **LEFT** goes back one page.

No terminal, computer, phone bridge, Wi-Fi network or internet is needed in this path.
Leave the remote in its original swipe mode. The small lower-right button is a mode
control; it is not the RIGHT direction on the ring.

For a break, use the Kindle's normal power button to sleep. Wake it normally afterward.
The remote need not wake a deeply sleeping Kindle. Three physical sleep/wake checks
passed in manual testing; retained kernel proof and measured battery acceptance are pending.
If the remote powered itself off, turn it on; do not re-pair as a routine reconnect step.

## After reboot

1. Enable **HID Passthrough daemon** in BT Manager.
2. In the native Kindle library, open **Button Mapper → Device → Start**.
3. Return to the KOReader book and use the remote.

This sequence passed after a reboot. Both boot autostarts remain disabled; ordinary
wake from sleep does not require repeating it. Exact reconnect seconds were not measured.
If a service is already running, do not toggle it off and on unnecessarily.

## Controls and scope

Twenty separate presses in each direction and quick pairs passed. Hold/release produced
no reported runaway; precise hold turn counts were not recorded and continuous repeat is
not promised. Tested menus, no-book screens, other brief controls and the native Kindle
library did not cause unintended page actions. No native-reader page-turn fallback is
configured. Not every possible modal dialog has been tested.

## Turning the whole feature off

Powering off J6 does not stop the Kindle services. Existing controls include Button
Mapper's Device → Stop and BT Manager's HID daemon toggle, but **the complete disable /
native Bluetooth restoration procedure is still awaiting its bounded test**. Do not
treat an idle control API as proof that all feature processes stopped. See
[troubleshooting and rollback](troubleshooting.md) before a full maintenance shutdown.

Start/Stop Remote Recovery and KOReader SSH are maintenance tools. Leave them off for
ordinary reading and battery observations. The mapping helper can stay after opening
its UI; its targeted cleanup is also a maintenance step, not a page-turn dependency.
