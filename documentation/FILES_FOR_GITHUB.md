# Files for GitHub Repository - v1.2.5

## 📦 Package for Release

**Main package**: `haptique_rs90_v1.2.5.tar.gz` (18 KB)

This archive contains the complete integration ready to install in Home Assistant.

---

## 📁 Files to Upload to GitHub Repository Root

### Essential Files
```
.gitignore                    # Git ignore rules
LICENSE                       # MIT License
README.md                     # Main documentation (English - DEFAULT)
README_FR.md                  # Documentation française
hacs.json                     # HACS configuration
icon.png                      # Integration and repository icon
```

### Changelog & Release Notes
```
CHANGELOG.md                  # Complete changelog (English)
CHANGELOG_FR.md               # Journal complet (Français)
WHATS_NEW.md                  # What's new in v1.2.5 (English)
WHATS_NEW_FR.md               # Nouveautés v1.2.5 (Français)
RELEASE_v1.2.5.md             # Complete release documentation
```

### Guides & Documentation
```
GUIDE_DEVICE_ID.md            # How to find device_id (EN/FR)
ICON_GUIDE.md                 # Icon setup guide
CONFORMITE_HAPTIQUE_MQTT.md   # MQTT conformity documentation
```

---

## 📂 custom_components/haptique_rs90/ Directory

Extract `haptique_rs90_v1.2.5.tar.gz` to get:

```
custom_components/haptique_rs90/
├── __init__.py
├── binary_sensor.py
├── config_flow.py
├── const.py
├── coordinator.py
├── icon.png                  ← Integration icon (auto-detected by HA)
├── manifest.json             ← Version 1.2.5
├── sensor.py
├── services.yaml
├── strings.json
├── switch.py
└── translations/
    ├── en.json
    └── fr.json
```

---

## 🎯 GitHub Release Structure

### Release Tag: `v1.2.5`

### Release Title
```
Haptique RS90 Integration v1.2.5 - Event-Driven Update
```

### Release Description (use WHATS_NEW.md content)

```markdown
# 🎉 Major Update: From Polling to 100% Event-Driven

[Copy content from WHATS_NEW.md]
```

### Attached Files
- `haptique_rs90_v1.2.5.tar.gz` (main package)

---

## 📊 Repository Structure

```
daangel27/haptique_rs90/
│
├── .gitignore
├── LICENSE
├── README.md                       # English (default)
├── README_FR.md                    # Français
├── hacs.json
├── icon.png
│
├── CHANGELOG.md                    # English
├── CHANGELOG_FR.md                 # Français
├── WHATS_NEW.md                    # English
├── WHATS_NEW_FR.md                 # Français
├── RELEASE_v1.2.5.md
│
├── GUIDE_DEVICE_ID.md
├── ICON_GUIDE.md
├── CONFORMITE_HAPTIQUE_MQTT.md
│
└── custom_components/
    └── haptique_rs90/
        ├── __init__.py
        ├── binary_sensor.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── icon.png
        ├── manifest.json
        ├── sensor.py
        ├── services.yaml
        ├── strings.json
        ├── switch.py
        └── translations/
            ├── en.json
            └── fr.json
```

---

## 🌐 Documentation Language Strategy

### Primary Language: English
- `README.md` is the main file (English by default)
- HACS and Home Assistant will display `README.md` by default
- English is the international standard

### Secondary Language: French
- `README_FR.md` provides complete French documentation
- Link at the top of `README.md`: `[Français](README_FR.md)`
- Link at the top of `README_FR.md`: `[English](README.md)`

### In Home Assistant UI
- Language automatically switches based on HA system language
- English and French fully supported
- Translation files: `translations/en.json` and `translations/fr.json`

---

## 🎨 Icon Setup

### icon.png
- **Location 1**: Repository root (for HACS and GitHub display)
- **Location 2**: `custom_components/haptique_rs90/` (for Home Assistant integration)

Home Assistant automatically detects and uses the icon in:
- Integration page
- Device cards
- HACS integration list

**No configuration needed!**

---

## 📝 Screenshot Placeholders in README

The README includes placeholders for screenshots:

```markdown
![Haptique RS90](documentation/logo.png)
![Integration Setup](documentation/setup.png)
![Entities](documentation/entities.png)
![Dashboard Example](documentation/dashboard.png)
```

### To Add Screenshots:
1. Create a `documentation/` folder in the repository root
2. Add your screenshots:
   - `logo.png` - Haptique RS90 product image
   - `setup.png` - Configuration flow screenshot
   - `entities.png` - Entity list screenshot
   - `dashboard.png` - Dashboard example screenshot
3. Commit and push

---

## ✅ Verification Steps

### Before Pushing to GitHub:
- [ ] All files are in the correct locations
- [ ] `manifest.json` shows version `1.2.5`
- [ ] `README.md` is in English (default)
- [ ] `README_FR.md` link works
- [ ] `icon.png` is present in both locations
- [ ] `hacs.json` is configured correctly
- [ ] `.gitignore` excludes unnecessary files

### After Pushing:
- [ ] Create GitHub release v1.2.5
- [ ] Attach `haptique_rs90_v1.2.5.tar.gz`
- [ ] Tag the commit as `v1.2.5`
- [ ] Verify HACS can discover the repository
- [ ] Test installation via HACS

---

## 🚀 HACS Discovery

### Requirements Met:
- ✅ `hacs.json` present with correct format
- ✅ `README.md` present (English)
- ✅ `manifest.json` in `custom_components/haptique_rs90/`
- ✅ Integration follows HA structure
- ✅ License file present (MIT)
- ✅ Icon present

### HACS Category: Integration

Users can add via:
1. HACS > Integrations
2. Three dots > Custom repositories
3. URL: `https://github.com/daangel27/haptique_rs90`
4. Category: Integration

---

## 📞 Support Links

Update these in your repository settings:
- Issues: Enable issue tracker
- Discussions: Enable discussions
- Wiki: Optional (documentation is in README)

---

**Repository**: https://github.com/daangel27/haptique_rs90
**Version**: 1.2.5
**Release Date**: December 10, 2024
