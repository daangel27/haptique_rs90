# Haptique RS90 - Home Assistant Integration

[![Version](https://img.shields.io/badge/version-1.1.5-blue.svg)](https://github.com/daangel27/haptique_rs90/releases)
[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Home Assistant integration for the **Haptique RS90** universal remote via MQTT.

**English** | [Français](README.md)

## ✨ Features

- 🎛️ **Macro switches**: Control your macros with visible ON/OFF state
- 🔋 **Battery sensor**: Monitor remote battery level
- 🔌 **Connection status**: Real-time online/offline detection
- 🎮 **Key detection**: Last pressed key sensor
- 📱 **Device list**: View all configured devices
- 💾 **Persistent states**: States preserved after Home Assistant restart
- 🔄 **MQTT retained**: States available immediately on reconnection
- 🚀 **Auto-discovery**: Automatic Remote ID detection

## 📋 Requirements

- Home Assistant 2024.1.0 or higher
- Configured MQTT broker (Mosquitto recommended)
- Haptique RS90 remote connected to the same MQTT network

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add URL: `https://github.com/daangel27/haptique_rs90`
6. Category: `Integration`
7. Click "Add"
8. Search for "Haptique RS90"
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest version from [Releases](https://github.com/daangel27/haptique_rs90/releases)
2. Extract contents to `/config/custom_components/haptique_rs90/`
3. Restart Home Assistant

## ⚙️ Configuration

### 1. Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Haptique RS90**
4. Integration will automatically detect your remote
5. Give it a name (optional, default: "Haptique RS90")
6. Click **Submit**

### 2. MQTT Configuration

Ensure your Haptique RS90 remote publishes to the following topics:

```
Haptique/{RemoteID}/status          # Online/offline status
Haptique/{RemoteID}/battery_level   # Battery level (0-100)
Haptique/{RemoteID}/keys            # Pressed keys
Haptique/{RemoteID}/macro/list      # Macro list
Haptique/{RemoteID}/device/list     # Device list
Haptique/{RemoteID}/macro/{name}/trigger  # Macro state (on/off)
```

## 📊 Created Entities

### Sensors

| Entity | Description | Values |
|--------|-------------|---------|
| `sensor.{name}_battery` | Battery level | 0-100% |
| `sensor.{name}_last_key_pressed` | Last pressed key | Key name |
| `sensor.{name}_running_macro` | Running macro | Macro name or "Idle" |
| `sensor.{name}_device_list` | Device list | Number of devices |

### Binary Sensors

| Entity | Description | States |
|--------|-------------|-------|
| `binary_sensor.{name}_connection` | Connection status | ON (online) / OFF (offline) |

### Switches

| Entity | Description | Actions |
|--------|-------------|---------|
| `switch.{name}_macro_{macro_name}` | Macro control | ON / OFF / TOGGLE |

**Switch features:**
- ✅ Visible state (ON = macro active, OFF = macro inactive)
- ✅ Native toggle
- ✅ Dynamic icon (▶️ / ⏹️)
- ✅ Persistent states after restart

## 🎯 Usage Examples

### Dashboard

```yaml
type: entities
title: Living Room Remote
entities:
  - entity: binary_sensor.rs90_connection
    name: Connection
  - entity: sensor.rs90_battery
    name: Battery
  - entity: switch.rs90_macro_watch_tv
    name: Watch TV
  - entity: switch.rs90_macro_cinema_mode
    name: Cinema Mode
```

### Automation

```yaml
automation:
  - alias: "Auto TV on arrival"
    trigger:
      - platform: state
        entity_id: person.me
        to: "home"
    condition:
      - condition: state
        entity_id: binary_sensor.rs90_connection
        state: "on"
      - condition: state
        entity_id: switch.rs90_macro_watch_tv
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.rs90_macro_watch_tv
```

### Script

```yaml
script:
  cinema_scene:
    alias: "Cinema Scene"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.rs90_macro_cinema_mode
      - service: light.turn_off
        target:
          entity_id: light.living_room
      - delay:
          seconds: 2
      - service: media_player.play_media
        target:
          entity_id: media_player.tv
```

## 🔧 Available Services

### `haptique_rs90.trigger_macro`

Manually trigger a macro.

```yaml
service: haptique_rs90.trigger_macro
data:
  device_id: "your_device_id"
  macro_name: "Watch TV"
  action: "on"  # or "off"
```

### `haptique_rs90.trigger_device_command`

Send a command to a device.

```yaml
service: haptique_rs90.trigger_device_command
data:
  device_id: "your_device_id"
  device_name: "Samsung TV"
  command_name: "power_on"
```

### `haptique_rs90.refresh_data`

Manually refresh data.

```yaml
service: haptique_rs90.refresh_data
data:
  device_id: "your_device_id"
```

### `haptique_rs90.get_diagnostics`

Display diagnostics in logs.

```yaml
service: haptique_rs90.get_diagnostics
data:
  device_id: "your_device_id"
```

## 🐛 Troubleshooting

### Remote not detected

1. Verify MQTT is configured and working
2. Check that remote is publishing to MQTT topics
3. Use MQTT Explorer to view messages
4. Enable debug logs:

```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### Switches don't reflect correct state

1. Verify `macro/{name}/trigger` topics publish with `retained=True`
2. Check `.storage/haptique_rs90_*_states.json` file
3. Restart Home Assistant

### Battery always shows 0

1. Verify remote responds to `battery/status` topic
2. Enable debug logs and search for "Battery level updated"
3. Test manually:

```bash
mosquitto_pub -h localhost -t "Haptique/YOUR_ID/battery/status" -m ""
mosquitto_sub -h localhost -t "Haptique/YOUR_ID/battery_level"
```

## 📁 File Structure

```
custom_components/haptique_rs90/
├── __init__.py           # Integration entry point
├── manifest.json         # Integration metadata
├── config_flow.py        # Configuration interface
├── coordinator.py        # MQTT coordinator
├── const.py             # Constants
├── sensor.py            # Sensors
├── binary_sensor.py     # Binary sensors
├── switch.py            # Macro switches
├── services.yaml        # Service definitions
├── strings.json         # English translations
└── translations/
    └── fr.json          # French translations
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant team for the excellent platform
- Haptique community for support

## 📞 Support

- 🐛 [Report a bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Request a feature](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

**Version:** 1.1.5  
**Author:** daangel27  
**Last updated:** December 2025
