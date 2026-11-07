# What's New in v1.8.0

**Release date:** November 7, 2026
**Type:** Feature release
**Breaking changes:** None ✅ (existing macro switches keep their entity IDs)
**Requires:** RS90 **Standard MQTT** firmware (tested on 4.1.2 and 4.2), Home Assistant 2024.8+

---

## 🎯 Top Features

### 1. Macros and sequences, the Standard MQTT way 🎛️

Thanks to [@ccs777](https://github.com/ccs777) (PR #38), macros and sequences are now discovered separately and triggered by their **stable ID**.

- One switch per macro and one per sequence
- The state is the one **confirmed by the RS90** (`ON` / `OFF` / unknown), never guessed
- New actions `haptique_rs90.trigger_sequence` and `haptique_rs90.query_status` (re-read a state without running anything)
- Your existing switches and automations keep working: entity IDs are preserved, even when a macro becomes a sequence

### 2. Launch RS90 apps 📱

Also from [@ccs777](https://github.com/ccs777) (PR #39):

- One button per app installed on the RS90, **disabled by default**: enable only the ones you want in Settings → Entities
- New action `haptique_rs90.launch_app`
- New sensor **Last Reported App**: the last app the RS90 reported, shown by its name (e.g. `Kore`), even when the app was opened on the RS90 screen

### 3. Know what your macros really did 📊

New sensor **Last Macro Result**:

```
CANAL · OFF · skipped (already_in_requested_state)
```

- Macro name, action, status and error in one line, full details in attributes
- **One logbook entry per result**, even when the same result repeats, shown on the macro's own logbook too
- Survives Home Assistant restarts
- New event `haptique_rs90_macro_result` for automations, e.g. get notified when a macro is skipped or fails (see the [README](README.md#macro-results))

### 4. A real icon 🎨

The integration finally shows its own icon and logo (light and dark themes) in Home Assistant **2026.3+**.

---

## 🐛 Fixes

- Ready for the next Home Assistant releases: deprecated device-registry calls replaced (would break in HA 2027.8 and 2027.10, #37)
- The device page no longer shows a fake "Firmware: 1.0"
- `• RGB Ring Light` renamed to `RGB Ring Light`
- Action descriptions no longer break in French

---

## ⚠️ Known firmware limitations

Reported to Haptique, not fixable in the integration:
- A macro started **from the RS90 screen** is not published over MQTT
- When switching macros, the previous one can stay **ON**, and turning it off later returns `skipped`
- Leaving an app is not reported, so Last Reported App keeps the last opened app
- Off its dock, the RS90 sleeps and goes offline: commands can't reach it until it wakes up

---

## 🚀 Upgrade

- **HACS**: open HACS → Haptique RS90 → **Update**, then restart Home Assistant
- **Manual**: download [v1.8.0](https://github.com/daangel27/haptique_rs90/releases/tag/v1.8.0), replace `custom_components/haptique_rs90/`, restart

New app buttons are disabled: enable the apps you want in **Settings → Devices & services → Entities**.

---

## 🙏 Credits

- [@ccs777](https://github.com/ccs777) for PR #38 and #39
- **Claude** (Anthropic), AI pair programmer on this release: code, tests, reviews, documentation and icon
- **Haptique Support** for the Standard MQTT firmware

**Enjoy v1.8.0!** 🎉
