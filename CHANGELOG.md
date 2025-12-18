# Changelog

All notable changes to this project will be documented in this file.


## [1.5.0] - 2025-12-18

### ⚠️ BREAKING CHANGES

This release includes **breaking changes** to service parameters. All automations and scripts using Haptique RS90 services **must be updated**.

#### 🔄 Service Parameters Renamed

| Old Parameter (v1.2.8) | New Parameter (v1.5.0) | Service |
|------------------------|------------------------|---------|
| `device_id` | `rs90_id` | All services |
| `macro_name` | `rs90_macro_id` | `trigger_macro` |
| `device_name` | `rs90_device_id` | `trigger_device_command` |

**Migration Required**: See [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

#### 🎯 What Changed

**1. Service Parameters - Breaking Changes**

All service parameters have been renamed for clarity and consistency:

```yaml
# OLD (v1.2.8) - NO LONGER WORKS
service: haptique_rs90.trigger_macro
data:
  device_id: "6f99751e78b5a07de72d549143e2975c"
  macro_name: "Watch Movie"
  action: "on"

# NEW (v1.5.0) - REQUIRED
service: haptique_rs90.trigger_macro
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
  rs90_macro_id: "692eb1561bddd5814022960c"
  action: "on"
```

**Reason**: 
- `device_id` was ambiguous (RS90 remote? Controlled device?)
- `rs90_id` clearly indicates it's the RS90 remote's Home Assistant device ID
- All IDs now use stable internal identifiers instead of names

**2. New Sensor: Macro Info**

Created `sensor.macro_{name}_info` for each macro:
- **State**: `available` (sensor serves to expose attributes)
- **Attributes**:
  - `rs90_macro_id`: Stable ID for service calls
  - `macro_name`: Current macro name
  - `current_state`: on/off state

**Purpose**: Easy access to macro IDs for services and automations

**3. Entity Attributes Renamed**

| Entity Type | Old Attribute | New Attribute |
|------------|--------------|---------------|
| `sensor.*_commands_*` | `haptique_device_id` | `rs90_device_id` |
| `switch.macro_*` | `macro_id` | `rs90_macro_id` |

**4. Ultra-Stable Entity IDs**

Entity unique IDs now based on internal Haptique IDs:
- **Macros**: `{remote_id}_macro_{macro_id}`
- **Devices**: `{remote_id}_commands_{device_id}`

**Benefit**: Entity IDs never change, even when renaming in Haptique Config

**5. Automatic Friendly Name Updates**

When you rename a device or macro in Haptique Config:
- ✅ Entity ID stays stable (automations don't break)
- ✅ Friendly name updates automatically in Home Assistant
- ✅ No manual intervention needed

**Example**:
```yaml
# Before rename
Entity ID: sensor.salon_commands_canal
Friendly Name: Commands - Canal

# After rename "Canal" → "Canal+" in Haptique Config
Entity ID: sensor.salon_commands_canal        # ← Unchanged
Friendly Name: Commands - Canal+        # ← Updated automatically
```

**6. Professional Logging**

All emoji removed from logs for cleaner, more professional output:
- `📥 MQTT` → `MQTT`
- `✓` → `SUCCESS:`
- `🔄` → `RENAME:`

#### 📋 Migration Steps

1. **Find your IDs**:
   - `rs90_macro_id`: Check `sensor.macro_{name}_info` or `switch.macro_{name}` attributes
   - `rs90_device_id`: Check `sensor.commands_{name}` attributes
   - `rs90_id`: Check RS90 device page URL

2. **Update automations**:
   - Replace `device_id` with `rs90_id`
   - Replace `macro_name` with `rs90_macro_id`
   - Replace `device_name` with `rs90_device_id`

3. **Update Lovelace templates**:
   - Use dynamic lookups: `{{ state_attr('sensor.salon_commands_canal', 'rs90_device_id') }}`

4. **Test everything**

**See detailed guide**: [MIGRATION_GUIDE_v1.5.0.md](MIGRATION_GUIDE_v1.5.0.md)

#### 📦 Files Modified

**Core Integration**:
- `services.yaml` / `services.fr.yaml` - Parameters renamed
- `__init__.py` - Service handlers updated
- `sensor.py` - New macro info sensor + attribute renamed
- `switch.py` - Attribute renamed
- `translations/en.json` / `fr.json` - Service descriptions

**Templates**:
- `templates/device_buttons_card.yaml` - Updated for new parameters
- `templates/example_canal_plus.yaml` - Updated for new parameters
- `templates/README.md` - Migration guide
- `templates/README_FR.md` - Guide de migration

**Documentation**:
- `MIGRATION_GUIDE_v1.5.0.md` - Complete migration guide (NEW)
- `CHANGELOG.md` - This file
- `README.md` - Updated examples

#### ⚡ Performance & Stability

- Thread-safe rename detection
- Entity Registry integration for instant UI updates
- Improved error handling
- Better attribute exposure

#### 🌍 Translations

- Complete EN/FR translations for all services
- Service descriptions updated in both languages

---

---

### 🔄 Migration Guide: 1.2.8 → 1.5.0

#### What Changed

**Services**:
- ✅ New parameters: `macro_id`, `haptique_device_id` (recommended)
- ⚠️ Deprecated: `macro_name`, `device_name` (still work, but discouraged)

**Entity Stability**:
- ✅ Unique IDs now based on internal IDs (ultra-stable)
- ✅ Friendly names update automatically on rename
- ⚠️ Entity IDs may change on first upgrade (one-time only)

#### Migration Steps

**Option A: Keep Using Names (No Changes Required)**
```yaml
# Your existing automations continue to work
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_name: "Watch Movie"  # ← Still works with deprecation warning
```

**Option B: Migrate to IDs (Recommended)**

1. **Find the ID** in entity attributes:
   - Go to Settings > Devices & Services > Haptique RS90
   - Click on a macro switch or device sensor
   - Look for `haptique_macro_id` or `haptique_device_id` in attributes

2. **Update your automations**:
```yaml
# Old way
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_name: "Watch Movie"

# New way (recommended)
service: haptique_rs90.trigger_macro
data:
  device_id: 1234567890abcdef
  macro_id: "692eb1561bddd5814022960c"  # ← Copy from attributes
```

3. **Test** your automations

#### Benefits of Migrating

- 🎯 **Rename-proof**: IDs never change, even if you rename in Haptique Config
- 🚀 **More reliable**: No confusion between devices/macros with similar names
- 📝 **Future-proof**: Prepared for eventual removal of name-based parameters

---

## [1.2.8] - 2025-12-12

### ✨ Major Improvements

This release brings automatic device command discovery and battery monitoring improvements.

#### 🎯 New Features
- **Automatic Device Commands Discovery**: New devices added in Haptique Config now automatically appear with their commands
- **Automatic Battery Refresh**: Battery level now updates automatically every hour

#### 🔧 Improvements
- **Enhanced refresh_lists Service**: Improved to actively re-scan and subscribe to new devices/macros
- **Better MQTT Compliance**: Fixed final QoS issue with macro trigger subscriptions

#### 🐛 Bug Fixes
- **Fixed Integration Reload Error**: Resolved "Cannot unsubscribe topic twice" error

---

## Version Comparison Table

| Feature | 1.2.8 | 1.5.0 |
|---------|-------|-------|
| **Entity Unique IDs** | Name-based | ID-based (stable) |
| **Friendly Name Updates** | Manual | Automatic |
| **Service Parameters** | `macro_name`, `device_name` | `macro_id`, `haptique_device_id` (recommended) |
| **Logging Style** | Emojis | Professional text-only |
| **Rename Detection** | No | Yes (instant UI update) |
| **Entity Stability** | Good | Excellent |
| **Migration Required** | No | Optional (recommended) |

---

## Support

- **Issues**: https://github.com/daangel27/haptique_rs90/issues
- **Discussions**: https://github.com/daangel27/haptique_rs90/discussions
- **Documentation**: https://github.com/daangel27/haptique_rs90
