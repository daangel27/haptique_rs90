# Device Buttons Card Template

Generate a beautiful remote control dashboard card with all available commands for any device controlled by your Haptique RS90.

![Device Buttons Card Example](../documentation/screenshots/device_buttons_card.png)
*Example: Full remote control card for Canal Plus*

**Updated for v1.5.0** - Now uses stable `haptique_device_id` parameter!

---

## 🎯 What This Template Does

This template automatically generates a **grid card** containing **one button for each command** available on your device. When you press a button:

1. 🖱️ **Button pressed** in Home Assistant dashboard
2. 📡 **Service called**: `haptique_rs90.trigger_device_command`
3. 📤 **MQTT message sent** to your Haptique RS90 remote
4. 📻 **IR command transmitted** from RS90 to your actual device

**Result**: Your TV, receiver, or any IR device responds instantly!

---

## 📋 Prerequisites

Before using this template, you need:

1. ✅ **Haptique RS90 integration v1.5.0+** installed and configured
2. ✅ **Device commands sensor** available (automatically created by the integration)
3. ✅ **card-mod** frontend plugin installed (for the 3D button styling)

### Installing card-mod (Optional but Recommended)

The template uses **card-mod** for beautiful 3D button styling. Without it, buttons will still work but look basic.

Install via HACS:
1. Open HACS → Frontend
2. Search for "card-mod"
3. Install and restart Home Assistant

**Note**: The template works without card-mod, but buttons won't have the 3D effect.

---

## 🔍 Finding Your Required Information

You need **2 pieces of information** to use this template:

### 1. Device Commands Sensor Name

**Where to find it**:
- Go to **Settings** → **Devices & Services**
- Click on **Haptique RS90**
- Click on your RS90 remote
- Look in the **Diagnostic** section
- Find sensors named: `Commands - {Device Name}`

**Example**: `sensor.commands_canal`

**Format**: `sensor.commands_{device_name}` (spaces replaced by underscores, lowercase)

### 2. RS90 Device ID (Home Assistant)

**Where to find it**:
- Same device page as above
- Look at the browser URL: `http://homeassistant.local:8123/config/devices/device/6f99751e78b5a07de72d549143e2975c`
- Copy the long ID at the end: `6f99751e78b5a07de72d549143e2975c`

**Alternative method**: Use the UI selector in Services (see [GUIDE_DEVICE_ID.md](../documentation/GUIDE_DEVICE_ID.md))

---

## 🚀 Quick Start

### Step 1: Copy the Template

Copy the contents of [`device_buttons_card.yaml`](device_buttons_card.yaml)

### Step 2: Replace Placeholders

Find and replace these placeholders:

```yaml
# REPLACE THIS:
sensor.commands_your_device_name

# WITH YOUR SENSOR NAME (example):
sensor.commands_canal
```

```yaml
# REPLACE THIS:
device_id: "YOUR_RS90_DEVICE_ID_HERE"

# WITH YOUR RS90 DEVICE ID (example):
device_id: "6f99751e78b5a07de72d549143e2975c"
```

**Note**: The `haptique_device_id` is **automatically retrieved** from the sensor attributes - no manual input needed!

### Step 3: Add to Dashboard

1. Open your Home Assistant dashboard in **edit mode**
2. Click **Add Card**
3. Choose **Manual** at the bottom
4. Paste your modified template
5. Click **Save**

---

## 📝 Template Structure (v1.5.0)

```yaml
type: grid
title: Your Device
columns: 4
square: false
cards:
  {% for cmd in state_attr('sensor.commands_your_device_name', 'commands') %}
  - type: button
    name: "{{ cmd.replace('_', ' ') }}"
    tap_action:
      action: call-service
      service: haptique_rs90.trigger_device_command
      data:
        device_id: "YOUR_RS90_DEVICE_ID_HERE"
        haptique_device_id: "{{ state_attr('sensor.commands_your_device_name', 'haptique_device_id') }}"
        command_name: "{{ cmd }}"
```

**What's New in v1.5.0**:
- ✅ Uses `haptique_device_id` (stable ID) instead of `device_name`
- ✅ Automatically retrieves the device ID from sensor attributes
- ✅ Rename-proof: Works even if you rename the device in Haptique Config

---

## 🎨 Customization

### Change Grid Layout

```yaml
columns: 3  # Change number of columns (default: 4)
square: true  # Make buttons square (default: false)
```

### Change Button Colors

Find these lines in the template and modify the hex colors:

```yaml
--mdc-theme-primary: #1e3a8a;    # Button color (default: dark blue)
--mdc-theme-secondary: #0f172a;  # Button gradient (default: darker blue)
```

**Color Examples**:
- Red: `#dc2626` / `#7f1d1d`
- Green: `#16a34a` / `#14532d`
- Orange: `#ea580c` / `#7c2d12`
- Purple: `#9333ea` / `#581c87`

### Change Button Size

```yaml
height: 50px !important;      # Button height (default: 50px)
min-height: 50px !important;  # Minimum height
font-size: 11px !important;   # Text size (default: 11px)
```

---

## 📱 Example: Canal Plus

See [`example_canal_plus.yaml`](example_canal_plus.yaml) for a complete working example.

**Features**:
- 4-column grid layout
- 3D button styling with shadows
- Automatic command retrieval
- Uses stable `haptique_device_id`

---

## ❓ Troubleshooting

### Buttons Don't Work

**Check**:
1. Is the service name correct? `haptique_rs90.trigger_device_command`
2. Is your RS90 remote online? (Check binary sensor: `binary_sensor.{name}_connection`)
3. Are you using the correct device_id? (Check URL or use UI selector)

### "Command not found" Error

**Check**:
1. Is the command name correct? (Check sensor attributes for exact command IDs)
2. Does the device have this command? (Commands list in sensor attributes)

### Buttons Look Basic

**Solution**: Install **card-mod** from HACS (see Prerequisites section above)

### Device Renamed - Buttons Stopped Working

**Solution**: With v1.5.0, this should NOT happen! The template uses `haptique_device_id` which is stable.

If you're using an old template (pre-v1.5.0 with `device_name`), update to the new version.

---

## 🔄 Migrating from Old Template (pre-v1.5.0)

**Old template used**:
```yaml
device_name: "Your Device Name"  # ← Breaks on rename
```

**New template uses**:
```yaml
haptique_device_id: "{{ state_attr('sensor.commands_your_device', 'haptique_device_id') }}"  # ← Stable!
```

**Migration steps**:
1. Replace your old template with the new one
2. Update sensor name
3. Update device_id
4. Done! The `haptique_device_id` is automatic

---

## 💡 Tips

### Organize by Room

Create separate dashboard views for each room:
- **Living Room**: TV, Soundbar, Cable Box
- **Bedroom**: TV, Fan
- **Office**: Projector, Sound System

### Use Card Titles

Add a title to identify each remote:

```yaml
title: Canal Plus Remote  # ← Custom title
type: grid
```

### Combine with Other Cards

Add macro switches above device buttons:

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - switch.macro_watch_movie
      - switch.macro_tv
  - type: grid  # ← Your device buttons template
    ...
```

---

## 📚 See Also

- [GUIDE_DEVICE_ID.md](../documentation/GUIDE_DEVICE_ID.md) - How to find Home Assistant device IDs
- [GUIDE_DEVICE_ID_FR.md](../documentation/GUIDE_DEVICE_ID_FR.md) - French version
- [README.md](../README.md) - Main integration documentation
- [CHANGELOG.md](../CHANGELOG.md) - v1.5.0 changes

---

## 🙏 Credits

Template created for the **Haptique RS90** Home Assistant integration.

- **Hardware**: Cantata Communication Solutions
- **Software**: Haptique
- **Integration**: [@daangel27](https://github.com/daangel27)

---

**Questions?** Open an issue on [GitHub](https://github.com/daangel27/haptique_rs90/issues)!
