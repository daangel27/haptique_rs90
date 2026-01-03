# Migration Guide - v1.5.0

## ⚠️ BREAKING CHANGES

Version 1.5.0 introduces breaking changes to service parameters. **All automations and scripts using Haptique RS90 services must be updated.**

---

## 🎯 What Changed

### Service Parameters Renamed

| Old Parameter (v1.2.8) | New Parameter (v1.5.0) | Service |
|------------------------|------------------------|---------|
| `device_id` | `rs90_id` | All services |
| `macro_name` | `rs90_macro_id` | `trigger_macro` |
| `device_name` | `rs90_device_id` | `trigger_device_command` |

### Attributes Renamed

| Old Attribute | New Attribute | Entity |
|--------------|---------------|---------|
| `haptique_device_id` | `rs90_device_id` | `sensor.*_commands_*` |
| `macro_id` | `rs90_macro_id` | `switch.macro_*` |

### New Entity

**Created**: `sensor.macro_{name}_info` for each macro
- **Attributes**: `rs90_macro_id`, `macro_name`, `current_state`
- **Purpose**: Easy access to macro IDs for services

---

## 📋 Step-by-Step Migration

### Step 1: Find Your IDs

Before updating automations, collect the IDs you'll need.

#### For Macros

**Option 1** - New info sensor:
1. Go to **Settings** → **Devices & Services** → **Haptique RS90**
2. Click your RS90 remote
3. Find **Diagnostic** sensors
4. Click `sensor.macro_{name}_info`
   - Example: `sensor.macro_watch_movie_info`
5. Copy the `rs90_macro_id` from attributes

**Option 2** - Existing switch:
1. Find `switch.macro_{name}`
   - Example: `switch.macro_watch_movie`
2. Look in attributes
3. Copy `rs90_macro_id`

#### For Devices

1. Find `sensor.{remote_name}_commands_{device_name}`
   - Example: `sensor.salon_commands_canal`
   - Format: `rs90_` + your RS90 remote name + `_commands_` + device name
2. Click to view details
3. Look in attributes
4. Copy `rs90_device_id`

#### For RS90 Remote

**Method 1** - Browser URL:
1. Go to your RS90 device page
2. Look at URL: `.../device/ABC123`
3. Copy the ID at the end

**Method 2** - Service UI selector:
1. Use the device selector in services
2. The ID will be used automatically

### Step 2: Update Automations

#### trigger_macro Service

**BEFORE (v1.2.8)**:
```yaml
service: haptique_rs90.trigger_macro
data:
  device_id: "6f99751e78b5a07de72d549143e2975c"
  macro_name: "Watch Movie"
  action: "on"
```

**AFTER (v1.5.0)**:
```yaml
service: haptique_rs90.trigger_macro
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
  rs90_macro_id: "692eb1561bddd5814022960c"
  action: "on"
```

**Changes**:
- ✅ `device_id` → `rs90_id`
- ✅ `macro_name` → `rs90_macro_id`
- ✅ `action` - unchanged

#### trigger_device_command Service

**BEFORE (v1.2.8)**:
```yaml
service: haptique_rs90.trigger_device_command
data:
  device_id: "6f99751e78b5a07de72d549143e2975c"
  device_name: "Canal"
  command_name: "POWER"
```

**AFTER (v1.5.0)**:
```yaml
service: haptique_rs90.trigger_device_command
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
  rs90_device_id: "692ead781bddd58140228e33"
  command_name: "POWER"
```

**Changes**:
- ✅ `device_id` → `rs90_id`
- ✅ `device_name` → `rs90_device_id`
- ✅ `command_name` - unchanged

#### refresh_lists Service

**BEFORE (v1.2.8)**:
```yaml
service: haptique_rs90.refresh_lists
data:
  device_id: "6f99751e78b5a07de72d549143e2975c"
```

**AFTER (v1.5.0)**:
```yaml
service: haptique_rs90.refresh_lists
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
```

**Changes**:
- ✅ `device_id` → `rs90_id`

### Step 3: Update Lovelace Templates

#### Device Buttons Card

**BEFORE (v1.2.8)**:
```yaml
tap_action:
  action: call-service
  service: haptique_rs90.trigger_device_command
  data:
    device_id: "6f99751e78b5a07de72d549143e2975c"
    device_name: "Canal"
    command_name: "{{ cmd }}"
```

**AFTER (v1.5.0)**:
```yaml
tap_action:
  action: call-service
  service: haptique_rs90.trigger_device_command
  data:
    rs90_id: "6f99751e78b5a07de72d549143e2975c"
    rs90_device_id: "{{ state_attr('sensor.salon_commands_canal', 'rs90_device_id') }}"
    command_name: "{{ cmd }}"
```

**Changes**:
- ✅ `device_id` → `rs90_id`
- ✅ `device_name` → Dynamic lookup via `rs90_device_id`

### Step 4: Update Scripts

If you have scripts calling these services, apply the same changes as automations.

**Example**:
```yaml
# scripts.yaml
watch_movie:
  sequence:
    - service: haptique_rs90.trigger_macro
      data:
        rs90_id: "6f99751e78b5a07de72d549143e2975c"
        rs90_macro_id: "692eb1561bddd5814022960c"  # ← Updated
        action: "on"
```

---

## 🔍 Complete Example - Before & After

### Complete Automation Example

**BEFORE (v1.2.8)**:
```yaml
automation:
  - alias: "Evening Routine"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      # Turn on TV
      - service: haptique_rs90.trigger_macro
        data:
          device_id: "6f99751e78b5a07de72d549143e2975c"
          macro_name: "TV On"
      # Change to Canal
      - service: haptique_rs90.trigger_device_command
        data:
          device_id: "6f99751e78b5a07de72d549143e2975c"
          device_name: "Canal"
          command_name: "POWER"
```

**AFTER (v1.5.0)**:
```yaml
automation:
  - alias: "Evening Routine"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      # Turn on TV
      - service: haptique_rs90.trigger_macro
        data:
          rs90_id: "6f99751e78b5a07de72d549143e2975c"
          rs90_macro_id: "692eb1561bddd5814022960c"
      # Change to Canal
      - service: haptique_rs90.trigger_device_command
        data:
          rs90_id: "6f99751e78b5a07de72d549143e2975c"
          rs90_device_id: "692ead781bddd58140228e33"
          command_name: "POWER"
```

---

## ✅ Verification Checklist

After migration, verify:

- [ ] All automations updated and saved
- [ ] All scripts updated and saved
- [ ] All Lovelace templates updated
- [ ] Test each automation manually
- [ ] Check Home Assistant logs for errors
- [ ] Verify services work in **Developer Tools** → **Services**

---

## ❓ Troubleshooting

### Error: "rs90_macro_id is required"

**Problem**: Old automation still uses `macro_name`

**Solution**: Replace with `rs90_macro_id` (see Step 2 above)

### Error: "Could not find macro with rs90_macro_id"

**Problem**: Wrong ID or macro was deleted

**Solution**:
1. Check if macro still exists in Haptique Config
2. Verify ID in `sensor.macro_{name}_info` attributes
3. Update automation with correct ID

### Error: "Device not found"

**Problem**: Wrong `rs90_id` (RS90 remote ID)

**Solution**:
1. Go to device page
2. Check URL for correct device ID
3. Update automation

### Automation doesn't trigger

**Problem**: YAML syntax error after manual edit

**Solution**:
1. Check YAML indentation
2. Use **Developer Tools** → **Check Configuration**
3. Review Home Assistant logs

---

## 💡 Tips

### Keep Old Code as Comment

While migrating, keep old parameters as comments:

```yaml
service: haptique_rs90.trigger_macro
data:
  rs90_id: "6f99751e78b5a07de72d549143e2975c"
  rs90_macro_id: "692eb1561bddd5814022960c"
  # OLD: macro_name: "Watch Movie"
  action: "on"
```

### Use Search & Replace

If you have many automations:
1. Backup your configuration
2. Use editor search & replace:
   - `device_id:` → `rs90_id:`
3. Then manually update macro/device parameters

### Test in Developer Tools First

Before updating automations:
1. Go to **Developer Tools** → **Services**
2. Test new service calls
3. Verify they work
4. Then update automations

---

## 📞 Need Help?

- **Issues**: https://github.com/daangel27/haptique_rs90/issues
- **Discussions**: https://github.com/daangel27/haptique_rs90/discussions

---

**Migration Time**: 10-30 minutes (depending on number of automations)  
**Difficulty**: Easy (straightforward search & replace)  
**Breaking**: Yes (old parameters no longer work)
