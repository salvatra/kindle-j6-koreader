# Gesture fixture provenance

The public patch creates two fixture files in the pinned upstream source tree:

| File after applying the patch | Origin and role |
| --- | --- |
| `fixtures/e03-abs-xy-events.txt` | Six complete project-recorded Arch gestures, projected to the relevant Kindle event types |
| `fixtures/e20-kindlemappings.ini` | Saved J6 gesture templates and mapper settings; device address replaced with a synthetic value |

The successful E03 capture started on **18 September 2026 at 16:22:17 UTC**. The remote
was in its original swipe mode. Prompts requested three brief LEFT presses followed by
three brief RIGHT presses. The earlier interrupted capture was not used. The later E05
alternate-mode capture is also not the regression source: it included a missed third
RIGHT press and offered no useful keyboard input. E06 checked restoration of swipe mode.

The numeric fixture contains ordered `(event type, code, value)` rows. It retains
`EV_KEY/BTN_TOUCH`, `EV_ABS/ABS_X`, `EV_ABS/ABS_Y`, and synchronization frames needed for
the existing stroke matcher. Timestamps, event-node paths, host names, addresses and
unrelated event fields are excluded. Values and retained frame order are unchanged.
The six strokes are stored sequentially in one text file, not six separate raw logs.
The expected completed matches are LEFT, LEFT, LEFT, RIGHT, RIGHT, RIGHT.

This is an **Arch-derived projection**, not a raw Kindle recording. A separate Kindle
capability observation established `BTN_TOUCH` plus `ABS_X/Y`, without DIRECT or
multitouch-X properties. The replay checks that this representation reaches the
existing gesture matcher and emits matches only on completed release. It does not
simulate Bluetooth timing, connection loss, physical input acquisition or sleep.

The E20 templates were recorded through the upstream mapper on the Kindle and retained
unchanged. The only fixture redaction in the public patch is the Bluetooth address,
replaced by `02:00:00:00:00:06`. This is why its patch checksum differs from the original
deployed patch. Both hashes are in [sources.json](../provenance/sources.json).
The standalone [example config](../examples/j6-config.ini) adds an explanatory header.

The stationary contact in the regression test is a **synthetic negative control**, not
a seventh recorded press. Other classification assertions also use synthetic capability
combinations to protect ordinary and unconfigured remotes. Original private captures
remain outside this repository; no unredacted log or manufacturer manual is published.
