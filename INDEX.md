# Haptique RS90 Integration - Documentation Index

Welcome to the documentation for the Haptique RS90 Home Assistant integration.

---

## 📚 Main Documentation

### English
- **[README.md](README.md)** - Complete integration documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Full changelog with all versions
- **[WHATS_NEW.md](WHATS_NEW.md)** - What's new in v1.5.0 ✨

### Français
- **[README_FR.md](README_FR.md)** - Documentation complète de l'intégration
- **[CHANGELOG_FR.md](CHANGELOG_FR.md)** - Journal complet avec toutes les versions
- **[WHATS_NEW_FR.md](WHATS_NEW_FR.md)** - Nouveautés de la v1.5.0 ✨

---

## 🚀 Latest Release - v1.5.0

### Release Information
- **[RELEASE_v1.5.0.md](RELEASE_v1.5.0.md)** - Complete v1.5.0 release documentation
- **[SUMMARY_v1.5.0.md](SUMMARY_v1.5.0.md)** - Quick summary of the release package

### Key Features
- ✅ **Ultra-stable entities** - ID-based unique IDs, rename-proof
- ✅ **Enhanced services** - New stable parameters (`macro_id`, `haptique_device_id`)
- ✅ **Automatic rename detection** - Friendly names update instantly
- ✅ **Professional logging** - Clean text-only logs
- ✅ **Updated templates** - Lovelace templates using stable parameters

### Migration
- ⚠️ **No breaking changes** - 100% backwards compatible
- 💡 **Optional migration** recommended for better stability
- 📖 See [WHATS_NEW.md](WHATS_NEW.md) for migration guide

---

## 📖 User Guides

### English
- **[GUIDE_DEVICE_ID.md](documentation/GUIDE_DEVICE_ID.md)** - How to find your Home Assistant device_id
- **[templates/README.md](templates/README.md)** - Lovelace card templates guide

### Français
- **[GUIDE_DEVICE_ID_FR.md](documentation/GUIDE_DEVICE_ID_FR.md)** - Comment trouver votre device_id Home Assistant
- **[templates/README_FR.md](templates/README_FR.md)** - Guide des templates de cartes Lovelace

---

## 🎨 Templates & Examples

### Lovelace Card Templates
- **[device_buttons_card.yaml](templates/device_buttons_card.yaml)** - Generate remote control buttons automatically
- **[example_canal_plus.yaml](templates/example_canal_plus.yaml)** - Complete working example

**New in v1.5.0**: Templates updated to use `haptique_device_id` for rename-proof operation!

---

## 📦 Archive - Previous Releases

### v1.2.8
- Last release before v1.5.0
- Automatic device discovery
- Battery auto-refresh

### v1.2.6
- **[RELEASE_v1.2.6.md](RELEASE_v1.2.6.md)** - v1.2.6 release documentation
- **[SUMMARY_v1.2.6.md](SUMMARY_v1.2.6.md)** - v1.2.6 package summary
- Initial stable release with event-driven architecture

---

## 🔧 Technical Documentation

### For Developers
- **[hacs.json](hacs.json)** - HACS integration configuration
- **[manifest.json](custom_components/haptique_rs90/manifest.json)** - Integration manifest

### MQTT Protocol
- **[CONFORMITE_HAPTIQUE_MQTT.md](documentation/CONFORMITE_HAPTIQUE_MQTT.md)** - MQTT protocol compliance verification
- Full compliance with Haptique RS90 MQTT specification

---

## 📸 Screenshots

All screenshots are located in the [/documentation/screenshots/](documentation/screenshots/) folder:

<table>
<tr>
<td width="50%">
<img src="documentation/screenshots/device_info.png" alt="Device Info" width="100%" />
<p align="center"><strong>Device Information</strong><br/>
Shows device info, controls (macro switches), sensors (battery, connection, etc.), and diagnostic sensors (device commands)</p>
</td>
<td width="50%">
<img src="documentation/screenshots/device_commands.png" alt="Device Commands" width="100%" />
<p align="center"><strong>Device Commands Details</strong><br/>
Detailed view of available commands for a device (example: Canal with 31 commands)</p>
</td>
</tr>
</table>

### Available Screenshots

- **device_info.png** - Device information page showing all entities
- **device_commands.png** - Device commands sensor details with full command list
- **device_buttons_card.png** - Example of Lovelace card template

---

## 🎯 Quick Links

### Installation
1. **Via HACS**: Add custom repository `https://github.com/daangel27/haptique_rs90`
2. **Manual**: Download latest release from [Releases](https://github.com/daangel27/haptique_rs90/releases)

### Support
- [Report a bug](https://github.com/daangel27/haptique_rs90/issues)
- [Request a feature](https://github.com/daangel27/haptique_rs90/issues)
- [Discussions](https://github.com/daangel27/haptique_rs90/discussions)

### Official Resources
- [Haptique MQTT Documentation](https://support.haptique.io/en/articles/mqtt)
- [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions)

---

## 🌟 What's New in v1.5.0

| Feature | Description |
|---------|-------------|
| **Stable Entities** | Unique IDs based on internal Haptique IDs - rename-proof! |
| **Auto Rename** | Friendly names update automatically when renamed in Haptique Config |
| **New Service Params** | `macro_id`, `haptique_device_id` - stable and reliable |
| **Professional Logs** | Text-only logs, no emojis - better for monitoring tools |
| **Updated Templates** | Lovelace templates using stable parameters |
| **Full Compatibility** | 100% backwards compatible - no breaking changes |

---

**Current Version**: 1.5.0  
**Release Date**: December 17, 2025  
**Languages**: English, Français  
**License**: MIT
