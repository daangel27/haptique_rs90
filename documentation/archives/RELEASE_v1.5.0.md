# Release v1.5.0 - December 17, 2025

## 🎉 Major Release: Entity Stability & Enhanced Services

This release brings **ultra-stable entities**, **improved service parameters**, and **professional logging** to the Haptique RS90 integration.

---

## 🌟 Highlights

### 1. Rename-Proof Entities ⭐⭐⭐

**The Problem**: 
When you renamed a device or macro in Haptique Config, the entity ID would change in Home Assistant, breaking your automations.

**The Solution**:
- Unique IDs now based on internal Haptique IDs (never change)
- Friendly names update automatically when you rename
- Entity IDs stay stable
- Your automations never break

**Example**:
```yaml
# You rename "Canal" → "Canal+" in Haptique Config

# Before v1.5.0:
❌ Entity ID changed: sensor.commands_canal → sensor.commands_canal_plus
❌ Automations broken
❌ Manual fix required

# After v1.5.0:
✅ Entity ID stable: sensor.commands_canal
✅ Friendly name updated: "Commands - Canal+"
✅ Automations still work
✅ Zero manual intervention
```

### 2. Stable Service Parameters ⭐⭐

**The Problem**:
Service parameters used device/macro names which could change, causing confusion and errors.

**The Solution**:
- New recommended parameters: `macro_id`, `haptique_device_id`
- Old parameters still work but deprecated
- Clear warnings guide you to migrate

**Example**:
```yaml
# Old way (still works):
service: haptique_rs90.trigger_macro
data:
  device_id: abc123
  macro_name: "Watch Movie"  # ← Can change

# New way (recommended):
service: haptique_rs90.trigger_macro
data:
  device_id: abc123
  macro_id: "692eb1561bddd5814022960c"  # ← Never changes
```

### 3. Professional Logging ⭐

**The Change**:
All emojis removed from logs for cleaner, more professional output suitable for monitoring tools.

**Before**: `📥 MQTT received`, `✓ Success`, `🔄 Renamed`  
**After**: `MQTT received`, `SUCCESS:`, `RENAME:`

---

## 🔄 Migration Guide

### Do You Need to Do Anything?

**No!** This release is 100% backwards compatible.

- ✅ Your existing automations work as-is
- ✅ Old service parameters still function
- ✅ No manual changes required

### Should You Migrate?

**Yes, when convenient!** Migration to new parameters gives you:

- 🎯 Rename-proof automations
- 🚀 More reliable operation
- 📝 Future-proof code

### How to Migrate

**Step 1**: Find the ID in entity attributes
- Go to your entity in Home Assistant
- Look for `haptique_macro_id` or `haptique_device_id`

**Step 2**: Update your automations
```yaml
# Replace this:
macro_name: "Watch Movie"

# With this:
macro_id: "692eb1561bddd5814022960c"
```

**Step 3**: Update your Lovelace templates
- Use new template files from `templates/` folder
- See `templates/README.md` for details

---

## 📋 Complete Feature List

### Core Changes

✅ **Unique IDs based on internal IDs**
- Macros: `{remote_id}_macro_{macro_id}`
- Devices: `{remote_id}_commands_{device_id}`

✅ **Automatic rename detection**
- Friendly names update instantly via Entity Registry
- Thread-safe implementation
- No manual refresh needed

✅ **Enhanced service parameters**
- New: `macro_id`, `haptique_device_id` (recommended)
- Deprecated: `macro_name`, `device_name` (still work)
- Clear deprecation warnings in UI

✅ **Professional logging**
- All emojis removed
- Text-only prefixes: SUCCESS, RENAME, NEW, WARNING
- Better compatibility with log monitoring tools

✅ **Updated templates**
- `device_buttons_card.yaml` uses `haptique_device_id`
- `example_canal_plus.yaml` updated
- Complete documentation in `templates/README.md`

### Technical Improvements

- Entity Registry integration for instant UI updates
- Thread-safe async rename detection
- Improved error handling
- Complete EN/FR translations for all services
- Better attribute exposure for easier automation

---

## 📦 What's Included

### Integration Files
- `coordinator.py` - Professional logging
- `sensor.py` - Stable unique IDs + rename detection
- `switch.py` - Stable unique IDs + rename detection
- `services.yaml` - New parameters + deprecation warnings
- `services.fr.yaml` - Complete French translations
- `translations/en.json` - Service descriptions
- `translations/fr.json` - Service descriptions
- `manifest.json` - Version 1.5.0

### Documentation
- `CHANGELOG.md` / `CHANGELOG_FR.md` - Complete changelog
- `WHATS_NEW.md` / `WHATS_NEW_FR.md` - User guide
- `README.md` / `README_FR.md` - Updated badges
- `INDEX.md` - Updated documentation index

### Templates
- `templates/device_buttons_card.yaml` - Updated template
- `templates/example_canal_plus.yaml` - Working example
- `templates/README.md` - Complete guide with migration
- `templates/README_FR.md` - French version

---

## 🔧 Technical Details

### Unique ID Format

**Before v1.5.0**:
```python
# Based on sanitized name (could change)
unique_id = f"{remote_id}_commands_{sanitized_name}"
```

**v1.5.0**:
```python
# Based on internal ID (never changes)
unique_id = f"{remote_id}_commands_{device_id}"
```

### Rename Detection

```python
# Detects rename in coordinator updates
if sensor._device_name != new_name:
    # Update internal name
    sensor._device_name = new_name
    
    # Update Entity Registry for instant UI refresh
    entity_reg = er.async_get(hass)
    entity_reg.async_update_entity(
        sensor.entity_id,
        name=f"Commands - {new_name}"
    )
    
    # Force state update
    sensor.async_write_ha_state()
    sensor.async_schedule_update_ha_state(force_refresh=True)
```

---

## ⚠️ Breaking Changes

**None!** This release is fully backwards compatible.

- Old service parameters work (with deprecation warnings)
- Existing automations continue to function
- No database migration required
- Entity IDs may change once on upgrade (stable afterward)

---

## 📊 Version Comparison

| Feature | v1.2.8 | v1.5.0 | Improvement |
|---------|--------|--------|-------------|
| **Unique IDs** | Name-based | ID-based | Ultra-stable |
| **Rename Handling** | Manual | Automatic | Zero intervention |
| **Service Parameters** | Names only | IDs + names | Rename-proof |
| **Logging** | Emojis | Text-only | Professional |
| **Entity Stability** | Good | Excellent | No breaks |
| **Breaking Changes** | N/A | None | Safe upgrade |

---

## 🎯 Use Cases

### Use Case 1: Renaming Devices

**Scenario**: You want to rename "Free - 10996" to just "Free" in Haptique Config.

**Before v1.5.0**:
1. Rename in Haptique Config
2. Entity ID changes in HA
3. Automations break
4. Manual fix required

**With v1.5.0**:
1. Rename in Haptique Config
2. Friendly name updates in HA (instant)
3. Entity ID stays same
4. Automations keep working
5. Done! ✅

### Use Case 2: Managing Similar Names

**Scenario**: You have "TV" and "TV - Bedroom" macros.

**Before v1.5.0**:
```yaml
# Confusing when names are similar
macro_name: "TV"  # Which one?
```

**With v1.5.0**:
```yaml
# Crystal clear with IDs
macro_id: "692eb1561bddd5814022960c"  # Definitely this one
```

### Use Case 3: Future-Proof Automations

**Scenario**: You're building automations you won't touch for months.

**Before v1.5.0**:
- Risk: Names might change
- Result: Automations might break

**With v1.5.0**:
- Use IDs: Never change
- Result: Automations always work

---

## 📚 Documentation

### For Users
- **[WHATS_NEW.md](WHATS_NEW.md)** - User-friendly what's new guide
- **[CHANGELOG.md](CHANGELOG.md)** - Technical changelog
- **[README.md](README.md)** - Complete documentation

### For Developers
- **[SUMMARY_v1.5.0.md](SUMMARY_v1.5.0.md)** - Package summary
- **[templates/README.md](templates/README.md)** - Template guide
- **[INDEX.md](INDEX.md)** - Documentation index

---

## 🙏 Acknowledgments

Special thanks to:
- **Cantata Communication Solutions** - RS90 hardware
- **Haptique** - MQTT protocol and software
- **Home Assistant Community** - Testing and feedback
- **All users** who reported issues and requested features

---

## 📞 Support

- **Issues**: https://github.com/daangel27/haptique_rs90/issues
- **Discussions**: https://github.com/daangel27/haptique_rs90/discussions
- **Documentation**: https://github.com/daangel27/haptique_rs90

---

## 🎉 Thank You!

Thank you for using the Haptique RS90 integration! This release represents weeks of work to make your home automation more stable and reliable.

**Enjoy v1.5.0!** 🚀

---

**Version**: 1.5.0  
**Release Date**: December 17, 2025  
**Type**: Major Feature Release  
**Compatibility**: Home Assistant 2024.1.0+  
**License**: MIT
