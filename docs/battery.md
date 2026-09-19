# Battery observations and measurement limits

On **19 September 2026**, the owner reported minimal, sustainable battery usage and an
**unchanged displayed battery percentage overnight**, and chose to keep the setup ready
for remote reading. This is an accepted practical observation for this device.

| Reported item | Result |
| --- | --- |
| Overnight displayed change | 0 percentage points, reported manually |
| Exact start/end percentage and elapsed hours | Not recorded in the report |
| Reading battery loss | Described as minimal; no numerical endpoints supplied |
| Matched feature-disabled comparison | Not performed |
| Owner's assessment | Acceptable for continued use |

An unchanged integer display does not establish zero energy use, a loss-per-hour rate or
the additional cost of this software. Trial preparation closed SSH and setup helpers;
the report did not separately quantify lighting, workload or other conditions. No
controlled battery benchmark is claimed. The procedure below remains available for
anyone who needs that comparison; it is not a prerequisite for using the accepted setup.

## Actual suspend observed

The same-boot kernel counters rose from **0 to 7 successful suspends**, with **0 failures**,
between preparation on 18 September and inspection on 19 September. Paired PM entry/exit
timestamps include a continuous interval of about **8 hours 36 minutes**. The final
inspection also found `preventScreenSaver=0`; no power-setting change was needed.

This confirms actual suspend during the observation period. That timed interval is
separate from the owner's battery report: its endpoints were not paired with recorded
battery readings, so it cannot supply a missing battery-rate denominator.

## Matched conditions

Compare ordinary reading with the feature enabled against ordinary touch reading with
the relevant remote software disabled. Turning only J6 off is not that baseline. Review
and test the full stop/start and native radio restoration procedure before the disabled
run; record any component that remains rather than calling a partial shutdown complete.

Keep duration, brightness/warmth, font/layout/book format, approximate page workload,
charger state, Wi-Fi state, room conditions and starting charge range reasonably similar.
Use actual reported durations. Do not add fake input, keep-awake settings or wake locks
to force a “reading” interval. A short or interrupted run is preliminary data.

For an enabled observation:

1. Unplug Kindle; turn Wi-Fi and restore-on-resume off. Record time, battery %, lighting
   and page position; read normally with J6 for about 2 hours.
2. Record end time, battery % and approximate page workload. At bedtime, record time/%
   separately if there was a gap after reading.
3. Sleep normally for an ordinary uninterrupted night, aiming for 6–8 hours or longer. Leave
   J6 on untouched for this particular condition; note if it powers itself off.
4. On normal wake record time/% **before Wi-Fi**. Check one next/previous pair and record
   any extra remote power-on or reconnect step.
5. Only afterward enable maintenance Wi-Fi/recovery and read existing suspend counters
   and timestamped PM entries once. If networks disappear, report before rebooting so
   same-boot evidence is not lost.

This condition measures “remote left on”; it is not silently substituted for a remote-off
night. A later different storage policy needs a separately labeled observation. The
computer can remain on: computer-off independence has already passed, and leaving it on
avoids another DHCP-related maintenance change. It does not participate in page delivery.

## Optional comparison worksheet

| Condition | Point | Date/time | Battery % | Settings / workload / interruptions |
| --- | --- | --- | --- | --- |
| Enabled | Before reading | unrecorded | unrecorded | unrecorded |
| Enabled | After reading | unrecorded | unrecorded | unrecorded |
| Enabled | Before sleep | unrecorded | unrecorded | J6 left on |
| Enabled | After wake, before Wi-Fi | unrecorded | unrecorded | unrecorded |
| Disabled | Before reading | unrecorded | unrecorded | match above |
| Disabled | After reading | unrecorded | unrecorded | unrecorded |
| Disabled | Before sleep | unrecorded | unrecorded | documented software-off state |
| Disabled | After wake, before Wi-Fi | unrecorded | unrecorded | unrecorded |

Compute percentage-point loss divided by elapsed hours, separately for reading and
overnight. Compare matched rates, with display resolution and uncontrolled workload
differences stated. Integer battery percentages have roughly one-point granularity;
unchanged display does not mean zero energy use. Avoid relative-percent increases when
the reference loss is effectively zero and do not extrapolate a short run into weeks.

## Suspend evidence and acceptance

Use a before/after boot ID, existing suspend success/failure counters, and PM entry/exit
timestamps. Counter increments alone do not establish time asleep. A reboot invalidates
the same-boot comparison; a sleep-screen image is not actual suspend proof.

No SSH, ping, frequent sampling, input capture, debug UI or HTTP Inspector should remain
during a battery interval. Do not create a monitor that prevents the state being measured.
Leave the required loopback action path intact for the enabled trial.

For a controlled comparison, record the measured difference and uncertainty before
claiming an added-drain rate. Extend/repeat only if the data cannot resolve the decision.
The owner accepted observed usage without that comparison; B01/B02 retain this explicit
measurement limitation. Suspend evidence is recorded separately in [validation](validation.md).
