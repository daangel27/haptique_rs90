# Haptique RS90 Integration - Release v1.2.5

## 📦 Release Package

**Version**: 1.2.5
**Release Date**: December 10, 2024
**Package**: [haptique_rs90_v1.2.5.tar.gz](haptique_rs90_v1.2.5.tar.gz) (18 KB)

---

## 📁 Files Included in Release

### Integration Files (in `custom_components/haptique_rs90/`)
```
haptique_rs90/
├── __init__.py              # Entry point, services
├── binary_sensor.py         # Connection status sensor
├── config_flow.py           # Configuration interface
├── const.py                 # Constants
├── coordinator.py           # MQTT coordinator (event-driven)
├── icon.png                 # Integration icon ✨ NEW
├── manifest.json            # Version 1.2.5
├── sensor.py                # All sensors including device commands
├── services.yaml            # Service definitions (EN/FR)
├── strings.json             # English translations
├── switch.py                # Macro switches
└── translations/
    ├── en.json              # English translations
    └── fr.json              # French translations
```

### Documentation Files (in repository root)
```
├── .gitignore               # Git ignore rules
├── CHANGELOG.md             # Complete changelog (EN)
├── CHANGELOG_FR.md          # Complete changelog (FR)
├── hacs.json                # HACS configuration
├── icon.png                 # Repository icon
├── LICENSE                  # MIT License
├── README.md                # Main documentation (EN)
├── README_FR.md             # Main documentation (FR)
├── WHATS_NEW.md             # What's new summary (EN)
└── WHATS_NEW_FR.md          # What's new summary (FR)
```

### Additional Guides
```
├── GUIDE_DEVICE_ID.md       # How to find device_id
├── ICON_GUIDE.md            # Icon setup guide
└── MODIFICATIONS_SERVICES_v1.2.3.md  # Service changes details
```

---

## 🎯 Quick Summary: v1.2.0 → v1.2.5

### ✨ Added
- Device command sensors for each device
- Comprehensive MQTT DEBUG logging
- Multi-language support (EN/FR)
- Integration icon (icon.png)
- Better service documentation
- Visual improvements (colors, icons)

### 🔧 Changed
- **100% event-driven** (removed all polling)
- QoS optimization (QoS 0/1 based on Haptique spec)
- Macro trigger protocol (retain=False)
- Service descriptions (clearer device_id explanation)
- README now in English by default

### 🗑️ Removed
- Refresh Data button and service
- Get Diagnostics service
- Scan Interval slider
- Periodic polling mechanism
- .storage file-based state persistence

### 🐛 Fixed
- Random macro triggers (removed dual state management)
- Subscription leaks (proper cleanup on deletion)
- Retained message cleanup (unsubscribe before delete)
- Race conditions in subscription management

---

## 🚀 Installation Instructions

### Via HACS (Recommended)
1. Add custom repository: `https://github.com/daangel27/haptique_rs90`
2. Search for "Haptique RS90"
3. Click "Download"
4. Restart Home Assistant

### Manual Installation
1. Download [haptique_rs90_v1.2.5.tar.gz](haptique_rs90_v1.2.5.tar.gz)
2. Extract to `/config/custom_components/`
3. Restart Home Assistant

---

## ⚙️ Prerequisites

Before adding the integration:
1. ✅ MQTT broker configured in Home Assistant
2. ✅ RS90 configured to connect to MQTT (via Haptique Config app)
3. ✅ RS90 online and publishing to MQTT

Once these are met, the integration will **auto-discover** your remote!

---

## 📊 Breaking Changes

### Removed Entities
- `button.{name}_refresh_data`
- `number.{name}_scan_interval`

### Removed Services
- `haptique_rs90.refresh_data`
- `haptique_rs90.get_diagnostics`

### Migration Steps
1. Remove these entities from your dashboards
2. Remove automations using removed services
3. Enable DEBUG logs if you used `get_diagnostics`:
   ```yaml
   logger:
     logs:
       custom_components.haptique_rs90: debug
   ```

### What Stays the Same
✅ All macro switches work identically
✅ All sensors function unchanged
✅ Services `trigger_macro` and `trigger_device_command` unchanged
✅ No configuration changes needed

---

## 🌍 Language Support

The integration is fully translated:
- 🇬🇧 **English** (default)
- 🇫🇷 **Français**

All UI elements, services, and documentation are available in both languages.

---

## 📚 Documentation

### English
- [README.md](README.md) - Main documentation
- [CHANGELOG.md](CHANGELOG.md) - Complete changelog
- [WHATS_NEW.md](WHATS_NEW.md) - What's new summary

### Français
- [README_FR.md](README_FR.md) - Documentation principale
- [CHANGELOG_FR.md](CHANGELOG_FR.md) - Journal complet
- [WHATS_NEW_FR.md](WHATS_NEW_FR.md) - Résumé des nouveautés

### Guides
- [GUIDE_DEVICE_ID.md](GUIDE_DEVICE_ID.md) - How to find Home Assistant device_id
- [ICON_GUIDE.md](ICON_GUIDE.md) - Integration icon setup

---

## 🔧 Key Technical Changes

### MQTT Protocol
- **QoS 0**: status, battery_level, keys, lists, commands (monitoring)
- **QoS 1**: macro triggers, device triggers (control)
- **No retained** on control topics (macro/device triggers)
- **Retained** on monitoring topics (status, lists)

### Architecture
- Event-driven updates via MQTT callbacks
- No periodic polling (`update_interval=None`)
- Single source of truth: MQTT retained messages
- Proper subscription lifecycle management

### Code Quality
- Comprehensive DEBUG logging for MQTT operations
- Proper async/await handling
- Race condition fixes
- Memory leak fixes

---

## 🙏 Acknowledgments

- [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) - Creators of the Haptique RS90 remote
- Home Assistant team - Excellent platform
- Haptique community - Support and feedback

---

## 📞 Support

- 🐛 [Report a bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Request a feature](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

## ✅ Verification Checklist

After installation, verify:
- [ ] Integration appears in Settings > Devices & Services
- [ ] Haptique logo is visible (icon.png)
- [ ] Remote is auto-discovered
- [ ] All entities are created
- [ ] Macro switches show blue (ON) / gray (OFF)
- [ ] Connection sensor shows correct status
- [ ] Device command sensors are present
- [ ] Services work correctly

---

**Author**: daangel27
**Repository**: https://github.com/daangel27/haptique_rs90
**License**: MIT
**Home Assistant Version**: 2024.1.0+
**Languages**: English, Français
