# Battery and actual sleep: results pending

No measured reading/overnight difference or acceptable battery allowance has been
established. The enabled trial was prepared with the final reading runtime active and
temporary SSH/helper listeners closed.

## Matched conditions

Compare ordinary reading with the feature enabled against ordinary touch reading with
the relevant remote software disabled. Turning only J6 off is not that baseline. Review
and test the full stop/start and native radio restoration procedure before the disabled
run; record any component that remains rather than calling a partial shutdown complete.

Keep duration, brightness/warmth, font/layout/book format, approximate page workload,
charger state, Wi-Fi state, room conditions and starting charge range reasonably similar.
Use actual reported durations. Do not add fake input, keep-awake settings or wake locks
to force a “reading” interval. A short or interrupted run is preliminary data.

For the first enabled observation:

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

## Worksheet

| Condition | Point | Date/time | Battery % | Settings / workload / interruptions |
| --- | --- | --- | --- | --- |
| Enabled | Before reading | pending | pending | pending |
| Enabled | After reading | pending | pending | pending |
| Enabled | Before sleep | pending | pending | J6 left on |
| Enabled | After wake, before Wi-Fi | pending | pending | pending |
| Disabled | Before reading | pending | pending | match above |
| Disabled | After reading | pending | pending | pending |
| Disabled | Before sleep | pending | pending | documented software-off state |
| Disabled | After wake, before Wi-Fi | pending | pending | pending |

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

Record the measured difference and uncertainty, then decide whether the drain is acceptable.
Extend/repeat only if the data cannot resolve that decision. Until then, B01/B02 and
objective R04 remain pending; the successful page-turning results remain valid.
