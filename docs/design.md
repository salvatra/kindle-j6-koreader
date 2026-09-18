# Why the J6 needed a small fix

The manual's phone-oriented LEFT/RIGHT descriptions are not Linux keycodes. Actual
Arch captures showed six repeatable touch swipes. A deliberate alternative-mode trial
produced pinch-like gestures and no useful keyboard path; the original mode was restored.
No AB Shutter3 keycodes or arbitrary screen coordinates were copied.

On the Kindle the linked J6 exposes one merged UHID node with `BTN_TOUCH`, `ABS_X/Y`,
properties `0`, and no `ABS_MT_POSITION_X`. Arch exposes two interfaces. Input event
numbers can change, so diagnostics use address/name/capabilities, not fixed event paths.

The pinned mapper's runtime classified touch from `INPUT_PROP_DIRECT` or multitouch X.
Its recorder had a different admission check. This explains the observed sequence:
successful Bluetooth/HID link, successful gesture recording, saved bindings, mapper
exclusive grab, available KOReader listener, and no page turn or gesture-match log.

The patch keeps the original branches and additionally allows:

```text
BTN_TOUCH present AND ABS_X/Y present AND explicit gesture bindings configured
```

That opt-in matters: a button remote using BTN_TOUCH must not automatically become a
touchscreen. Whole paths still go through upstream matching and are delivered once on
completed release. A motion sample or contact transition is not independently mapped
to a page action. Binding reloads re-evaluate the opt-in.

The three regressions cover classification, ordinary/unconfigured remotes and binding
changes, and six recorded gesture projections plus a synthetic stationary negative case.
The projection is from Arch to the observed Kindle capabilities; it is explicitly **not
a raw Kindle event trace**.

The J6 mapping uses `grab=true`, `passthrough=false`, and KOReader-specific `koreader.sh`
previous/next actions. `keep_awake=false` and `log_buttons=false` are preserved. The
upstream KHP plugin serves the action endpoint on loopback `127.0.0.1:8323`; HTTP Inspector
is not needed. Upstream delivery code and reconnect policy are unchanged.

KOReader v2026.07 added keyboard input hotplug support, but touch gestures are not native
arrow-key input. The upstream plugin's **“KOReader only” device-ownership mode** also
differs from a **KOReader-only action**: handing this node away from the mapper can
prevent gesture bindings from running. Favorites/auto actions may fall back to native
reader taps, so they are not the chosen mapping.

There is no API/schema migration or new radio stack. A different architecture would
need an observed defect and measurable advantage over this small change. Sleep and
battery are measured separately from page delivery.
