# Changelog - Haptique RS90 Home Assistant Integration

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.9.0] - Unreleased

### ✨ New Features
- **Haptique RS90 dashboard** (dashboard strategy shipped with the integration, Home Assistant 2026.5+ lists it under *Community dashboards*):
  - RS90 view: macros as ON/OFF buttons (green = ON), sequences, apps and status
  - One view per RS90 device, commands grouped like a remote (power, navigation pad, volume & channels, playback, keypad, inputs, more), 3D style with card-mod
  - Rebuilt every time it opens, so new, renamed or removed devices, macros and apps show up by themselves; removed macros and apps are left out
- **Wake the RS90 up**: enter its IP address in the options to get a **Wake up** button, and optionally wake it up automatically before macros, apps and device commands (UDP packets to its IP until it reports online, up to 20 s; works with the RS90's random MAC address)
- With auto-wake, the RGB ring light and **Sync** buttons also wake the RS90 up, and **Last Reported App** keeps its last value while the RS90 sleeps
- Commands pressed while the RS90 wakes up are sent one by one once it is ready (4 s after it reports online), so none is lost
- The device **Activity** shows, with an icon, each device command sent (e.g. `RS90 KODI → DOWN sent`) and each wake-up (`wake-up sent`, `woke up in 18 s` or `did not wake up`)
- **Sync** button (configuration entity): asks the RS90 to publish its devices, commands, macros, sequences and apps again, plus battery and macro states, without using an action
- When the RS90 wakes up, the integration asks for its lists again (at most every 5 minutes), so changes made while it slept are picked up
- **Integration options** become a menu: rename the remote, or choose the command buttons shown for each device (all by default, none hides the device)

### 🐛 Fixes
- Renaming the remote no longer wipes the other options
- The dashboard script URL carries a hash of the file, so browsers load the new version after an update

---

## [1.8.1] - 2026-11-07

Maintenance release: no change in behaviour.

### 🐛 Fixes
- Drop the unused `aiomqtt` requirement (Home Assistant no longer installs it)
- Minimum Home Assistant version set to **2024.8** (oldest version the test suite passes on)

### 📚 Documentation
- Device buttons card template rewritten: only the sensor to replace, RS90 and device IDs found automatically, duplicate commands removed, `perform-action` syntax, correct 4-step procedure (render in Developer tools → Template, then paste the result in a Manual card), new KODI example
- Installation through the Home Assistant **Marketplace** (2026.11+), with the HACS steps kept for older versions
- README: new screenshots, finding IDs with the Info Summary sensor, minimum Home Assistant version badge

---

## [1.8.0] - 2026-11-07

Requires the RS90 **Standard MQTT** firmware (tested on 4.1.2 / 4.2).

### ✨ New Features

#### Standard MQTT macros and sequences (PR #38, thanks @ccs777)
- Macros and sequences are discovered separately (`macro/list`, `sequence/list`) and triggered by **stable ID**
- Macro state (ON/OFF/UNKNOWN) comes from firmware feedback (`macro/<id>/status`), no optimistic state
- New actions: `haptique_rs90.trigger_sequence`, `haptique_rs90.query_status`
- Existing macro switches keep their entity IDs when a macro becomes a sequence or is renamed

#### Installed apps (PR #39, thanks @ccs777)
- One launch button per installed RS90 app (`app/list`), **disabled by default**
- New action: `haptique_rs90.launch_app`
- New sensor **Last Reported App**: shows the app label (e.g. `Kore`), package ID in `app_package_id`
  - Also resolves apps opened on the RS90 screen, which the firmware reports by label instead of package ID

#### Last Macro Result sensor and event
- New sensor **Last Macro Result**, e.g. `CANAL · OFF · skipped (already_in_requested_state)`
  - Attributes: `target_name`, `target_id`, `target_kind`, `action`, `status`, `error`, `timestamp`
  - Every result also gets its own logbook entry, even when identical to the previous one, attached to the macro/sequence switch
  - Last value is restored after a Home Assistant restart
- New event `haptique_rs90_macro_result` with the same data, for automations (e.g. notify on `skipped` / `failed`)
- Retained results replayed on reconnect are not reported as new runs

#### Integration icon and logo
- New icon and logo (light and dark), shipped in `brand/` so Home Assistant 2026.3+ shows them; the old root `icon.png` was never used by Home Assistant

### 🐛 Fixes
- Replace deprecated `DeviceEntry.config_entries` with `config_entry_id` (breaks in HA 2027.10), with fallback for older HA
- Remove hard-coded `sw_version: 1.0` (device page showed "Firmware: 1.0" whatever the RS90 version)
- Rename `• RGB Ring Light` to `RGB Ring Light`
- French translation placeholders (`{name}`) no longer break service descriptions
- Remove deprecated `device_registry.async_get_device` call from the Info Summary sensor (stops working in HA 2027.8), fixes #37

---

## [1.7.0] - 2026-01-27

### ✨ New Features

#### Event-Based Key Press Detection
- **Fire events on every button press**, including repeated presses of the same button
- New event: `haptique_rs90_key_pressed` with data: `remote_id`, `device_id`, `button`, `timestamp`
- Enables **dual functionality**: RS90 macro execution + Home Assistant automation from single button press
- Solves issue where pressing the same button twice didn't trigger automations

**Example usage:**
```yaml
automation:
  trigger:
    - platform: event
      event_type: haptique_rs90_key_pressed
      event_data:
        button: 13
```

#### Device Triggers for Native UI Support
- **24 button triggers** (1-24) available in Home Assistant automation UI
- No manual YAML needed - fully visual automation builder compatible
- Select RS90 device and button directly from dropdown menus

**Example (UI-generated):**
```yaml
trigger:
  - platform: device
    device_id: [your_rs90]  # From sensor.rs90_info_summary → rs90_id
    domain: haptique_rs90
    type: button_pressed
    button: 13
```

#### Macro Status Synchronization
- **New MQTT topic**: Subscribe to `macro/{MacroName}/status` for state feedback
  - ⚠️ **Requires updated RS90 firmware** (upcoming release from Haptique - check with Haptique support for availability)
- **Proper state tracking** when macros are triggered from RS90 remote
- Switch entities now accurately reflect macro state regardless of trigger source
- Clean MQTT architecture: Commands (`/trigger`) separated from state (`/status`)

**Technical details:**
- Command topic: `macro/{MacroName}/trigger` (retain=False, ephemeral)
- Status topic: `macro/{MacroName}/status` (retain=True by RS90, authoritative state)
- No synchronization loops or duplicate commands

#### MQTT RemoteID Exposure
- Added `rs90_remote_id` attribute to `sensor.rs90_info_summary`
- Makes MQTT RemoteID easily discoverable for debugging and manual MQTT operations

**Example attributes:**
```yaml
sensor.rs90_info_summary:
  rs90_id: "9b974dab9a7649e13baeb921d4c9bb85"  # HA Device ID
  rs90_remote_id: "3d5d95aa3a7f7b20"  # MQTT RemoteID (new!)
  rs90_device_name: "RS90"
  devices: {...}
  macros: {...}
```

### 🔧 Improvements

#### Battery Refresh Optimizations
- **Automatic refresh on reconnection**: Battery level requested immediately when RS90 wakes from sleep
- **Optimized for sleep/wake cycles**: Up to 6x more frequent updates when RS90 is off charging dock
- **Throttle protection**: Minimum 5 minutes between refreshes to prevent spam during unstable connections
- **Reduced timer interval**: Periodic refresh every 30 minutes (was 60 minutes)

**Refresh frequency:**
- On charging dock (always online): Every 30 minutes
- Off dock (sleep/wake ~10 min): Every ~10 minutes on wake
- Unstable connection (<5 min disconnect/reconnect): Throttled to max 1 refresh per 5 minutes

#### Battery Refresh in `refresh_lists` Service
- Service `refresh_lists` now also requests battery level update
- Useful for manual refresh without waiting for automatic intervals

### 🐛 Bug Fixes

- Fixed macro state not updating when triggered from RS90 remote
- Fixed potential MQTT publish loops during macro state synchronization
- Fixed battery level not updating during RS90 sleep/wake cycles

### 📝 Documentation

- Added comprehensive examples for event-based automations
- Documented device trigger usage in automation UI
- Explained macro status synchronization architecture
- Added battery refresh behavior documentation

### ⚠️ Breaking Changes

**None** - This release is fully backward compatible with v1.5.1.

### 🙏 Credits

- **Macro status synchronization**: Special thanks to **Haptique Support** for implementing the `/status` topic and providing excellent collaboration!
- **Event detection issue**: Reported and validated by @Benz63Amg in issue #35

### 📋 Requirements

- **RS90 Firmware**: Macro status synchronization requires updated RS90 firmware with `/status` topic support
  - This feature will be available in an upcoming firmware release
  - Contact Haptique support for firmware availability and update instructions
  - All other features work with current firmware versions
- **Home Assistant**: 2024.1.0 or newer
- **MQTT**: Configured and working

---

## [1.5.1] - 2025-12-27

### Previous stable release

See GitHub releases for details: https://github.com/daangel27/haptique_rs90/releases

---

## Links

- [GitHub Repository](https://github.com/daangel27/haptique_rs90)
- [Issue Tracker](https://github.com/daangel27/haptique_rs90/issues)
- [Documentation](https://github.com/daangel27/haptique_rs90/blob/main/README.md)
