# What's New in v1.9.0

**Release date:** November 8, 2026
**Type:** Feature release
**Breaking changes:** None ✅
**Requires:** RS90 **Standard MQTT** firmware (tested on 4.2), Home Assistant 2024.8+ (the dashboard needs 2026.5+)

---

## 🎯 Top Features

### 1. A ready-made remote dashboard 📺

No more YAML or hand-made cards: the integration ships its own **Haptique RS90 dashboard**.
**Settings → Dashboards → Add dashboard → Haptique RS90**, and you're done.

- **One tab per device** (TV, amplifier, Kodi…), laid out like a real remote: power, navigation pad, volume & channels, playback, keypad, inputs
- **An RS90 tab** to start macros (green when ON), sequences and apps in one tap, plus the remote's status
- **Always up to date**: add, rename or remove a device, macro or app on the RS90 and the dashboard follows on its own
- **Only the buttons you use**: in the integration options, choose per device between all commands, only the ones you tick (with **Tick all / Untick all** shortcuts), or none to hide the device

### 2. The RS90 asleep? Home Assistant wakes it up 😴

Off its dock, the RS90 goes to sleep and stops listening to MQTT. Enter its IP address in the integration options:

- a **Wake up** button wakes it up on demand
- with **auto-wake**, it is woken up automatically before macros, apps, device commands, RGB ring light and Sync, without touching the remote
- only the IP is needed: it works with the RS90's random Wi-Fi MAC (give the RS90 a fixed IP in your router)
- buttons pressed while it wakes up are kept and sent one by one once it is ready

### 3. See what happens 🔎

Every command sent, every wake-up and every macro result now shows in Home Assistant's **Activity**, with icons:
- `Commands - KODI → DOWN sent`
- `Wake up → woke up in 8 s`, `did not wake up`, `already awake`
- `KODI → ON: executed`

Filter the **Activity** panel on the RS90, or on a single entity (e.g. **Commands - AMPLI**), to check whether a command left Home Assistant.

### 4. And also ✨

- **Sync** button: asks the RS90 to publish its devices, commands, macros, sequences and apps again. Lists are also refreshed when the RS90 wakes up (at most every 5 minutes)
- **Last Reported App** keeps its value while the RS90 sleeps
- Sequences get their own icons, distinct from macros

---

## 🐛 Fixes

- Renaming the remote no longer wipes the other options
- After an update, browsers load the new dashboard instead of a cached one

---

## ⚠️ Known firmware limitations

Reported to Haptique, not fixable in the integration (some fixes are planned for firmware 4.3):
- Right after a wake-up, a command sent to a network device (e.g. Kodi) can be missed when several are pressed in a row. Infrared devices are not affected
- If a device has two commands with the same name (e.g. two `POWER`), only one can be sent: rename one in the Haptique app
- A sequence run by a macro has no ON/OFF state until it has been started on its own once
- A macro started **from the RS90 screen** is not published over MQTT, and when switching macros the previous one can stay **ON**

---

## 🚀 Upgrade

- **Marketplace** (Home Assistant 2026.11+): Settings → Marketplace → Haptique RS90 → **Update**
- **HACS** (older versions): open HACS → Haptique RS90 → **Update**
- **Manual**: download [v1.9.0](https://github.com/daangel27/haptique_rs90/releases/tag/v1.9.0), replace `custom_components/haptique_rs90/`

Then restart Home Assistant and refresh your browser (Ctrl+F5). To use the new features:
1. **Dashboard**: Settings → Dashboards → Add dashboard → **Haptique RS90**
2. **Wake-up**: Settings → Devices & services → Haptique RS90 → **Configure** → Wake the RS90 up

---

## 🙏 Credits

- **Claude** (Anthropic), AI pair programmer on this release: code, tests, reviews and documentation
- [@ccs777](https://github.com/ccs777) / WillisD and **Haptique** for the Standard MQTT firmware and the quick feedback

**Enjoy v1.9.0!** 🎉
