# Haptique RS90 Integration - Release v1.2.6

## 📦 Release Package

**Version**: 1.2.6  
**Release Date**: December 11, 2025  
**Type**: Maintenance Release  
**Package**: haptique_rs90_v1.2.6.tar.gz (18 KB)

---

## 📝 Release Summary

Version 1.2.6 is a **maintenance release** focused on documentation updates and consistency improvements for 2025. There are **no functional changes** from version 1.2.5.

### What's Updated
- ✅ Documentation dates (2024 → 2025)
- ✅ Version badges and references
- ✅ Copyright year (2025)
- ✅ Minor formatting improvements

### What's Unchanged
- ✅ All code functionality
- ✅ Integration behavior
- ✅ Configuration requirements
- ✅ Service definitions
- ✅ Entity creation

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
├── icon.png                 # Integration icon
├── manifest.json            # Version 1.2.6
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

---

## 🚀 Installation Instructions

### Via HACS (Recommended)
1. Open HACS → Integrations
2. Find "Haptique RS90"
3. Click "Update" (if already installed)
   OR
   Click "Download" (if new installation)
4. Restart Home Assistant

### Manual Installation
1. Download [haptique_rs90_v1.2.6.tar.gz](haptique_rs90_v1.2.6.tar.gz)
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

## 📊 Feature Set (from v1.2.5)

All features from v1.2.5 are preserved in v1.2.6:

### Sensors & Controls
- 🔋 **Battery Sensor**: Monitor battery level (0-100%)
- 🔌 **Connection Status**: Real-time online/offline detection
- 🎮 **Key Detection**: Last pressed key sensor
- 📱 **Device List**: Number of configured devices
- 📋 **Device Commands**: Diagnostic sensors showing available commands
- 🎛️ **Macro Switches**: Visual ON/OFF state with blue/gray coloring

### Architecture
- ⚡ **100% Event-Driven**: No polling, instant MQTT updates
- 🎯 **QoS Optimized**: QoS 0 for monitoring, QoS 1 for commands
- 🔄 **Real-time Updates**: Event-based subscription system
- 🚀 **Auto-Discovery**: Automatic remote ID detection
- 🌍 **Multi-Language**: English and French support

### Services
- `haptique_rs90.trigger_macro` - Manually trigger a macro
- `haptique_rs90.trigger_device_command` - Send command to a device

---

## 🔄 Upgrading from v1.2.5

### Migration Steps
**None required!** This is a documentation-only release.

1. Update via HACS or manually
2. Restart Home Assistant
3. Done! ✅

### What to Expect
- No configuration changes needed
- All entities remain the same
- All automations continue working
- All services unchanged

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
- [WHATS_NEW.md](WHATS_NEW.md) - What's new in v1.2.6

### Français
- [README_FR.md](README_FR.md) - Documentation principale
- [CHANGELOG_FR.md](CHANGELOG_FR.md) - Journal complet
- [WHATS_NEW_FR.md](WHATS_NEW_FR.md) - Nouveautés de la v1.2.6

### Guides
- [GUIDE_DEVICE_ID.md](documentation/GUIDE_DEVICE_ID.md) - How to find device_id
- [Templates](templates/) - Dashboard templates for device buttons

---

## 🔧 Technical Details

### MQTT Protocol (Unchanged from v1.2.5)
- **QoS 0**: status, battery_level, keys, lists, commands (monitoring)
- **QoS 1**: macro triggers, device triggers (control)
- **Retained**: Only on monitoring topics
- **Not Retained**: Control topics (macro/device triggers)

### Architecture
- Event-driven updates via MQTT callbacks
- No periodic polling
- Single source of truth: MQTT retained messages
- Proper subscription lifecycle management

---

## ✅ Verification Checklist

After installation, verify:
- [ ] Integration appears in Settings > Devices & Services
- [ ] Haptique logo is visible
- [ ] Remote is auto-discovered
- [ ] All entities are created
- [ ] Macro switches show blue (ON) / gray (OFF)
- [ ] Connection sensor shows correct status
- [ ] Device command sensors are present
- [ ] Services work correctly

---

## 🙏 Acknowledgments

- [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) - Creators of the Haptique RS90
- Home Assistant team - Excellent platform
- Haptique community - Support and feedback

---

## 📞 Support

- 🐛 [Report a bug](https://github.com/daangel27/haptique_rs90/issues)
- 💡 [Request a feature](https://github.com/daangel27/haptique_rs90/issues)
- 💬 [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

---

**Author**: daangel27  
**Repository**: https://github.com/daangel27/haptique_rs90  
**License**: MIT  
**Home Assistant Version**: 2024.1.0+  
**Languages**: English, Français  
**Release Type**: Maintenance  
**Breaking Changes**: None
