# What's New in v1.2.5

## 🎉 Major Update: From Polling to 100% Event-Driven

The biggest change in v1.2.5 is the complete removal of periodic polling. Your integration now responds **instantly** to every change via MQTT!

---

## ✨ Key Highlights

### 🚀 Performance & Responsiveness
- **Instant updates**: No more waiting for the next poll cycle
- **Reduced network traffic**: Updates only when something changes
- **Lower CPU usage**: No periodic background tasks

### 📋 New: Device Command Sensors
- See all available commands for each device at a glance
- Located in the Diagnostic category
- Alphabetically sorted for easy browsing
- Example: `sensor.commands_samsung_tv` shows all TV commands

### 🎨 Visual Improvements
- **Macro Switches**: Now show blue when ON, gray when OFF
- **Connection Sensor**: Dynamic icons (connected/disconnected)
- **Running Macro**: Dynamic icons (playing/idle)

### 🌍 Multi-Language Support
- **English** (default)
- **Français**
- Complete translations for all services and UI elements

### 🔧 Better Service Documentation
- Clear distinction between MQTT ID and Home Assistant device_id
- Step-by-step instructions integrated in the UI
- Real-world examples with actual IDs

---

## 🗑️ What's Removed (and Why)

### Removed Entities
- ❌ **Refresh Data button** → Not needed with event-driven updates
- ❌ **Scan Interval slider** → No more polling!

### Removed Services
- ❌ **`haptique_rs90.refresh_data`** → Updates happen automatically
- ❌ **`haptique_rs90.get_diagnostics`** → Use DEBUG logs instead

**Don't worry!** The essential services (`trigger_macro` and `trigger_device_command`) remain unchanged.

---

## 🐛 Critical Bug Fixes

### Fixed: Random Macro Triggers
**Problem**: Macros would sometimes trigger randomly without user action.
**Cause**: Dual state management (file + MQTT) created conflicts.
**Solution**: Now uses MQTT retained messages as the single source of truth.

### Fixed: Subscription Leaks
**Problem**: Deleted macros would remain subscribed to MQTT.
**Cause**: Race condition in async subscription management.
**Solution**: Synchronized subscription tracking and proper cleanup on deletion.

---

## 📚 Documentation Improvements

### Auto-Discovery Explained
Clear documentation about prerequisites:
1. ✅ MQTT broker configured in Home Assistant
2. ✅ RS90 configured to connect to MQTT (Haptique Config app)
3. ✅ RS90 online and publishing

Once these are met, the integration automatically discovers your remote!

### Screenshot Examples
The README now includes placeholders for screenshots:
- Setup process
- Entity list
- Dashboard examples

### Acknowledgments
Special thanks to [Cantata Communication Solutions](https://github.com/Cantata-Communication-Solutions) for creating the Haptique RS90.

---

## 🔒 Protocol Compliance

### 100% Haptique MQTT Compliant
Every aspect has been verified against the [official Haptique MQTT documentation](https://support.haptique.io/en/articles/mqtt):

- ✅ **QoS Levels**: QoS 0 for monitoring, QoS 1 for control
- ✅ **Retained Messages**: Only on monitoring topics, not on triggers
- ✅ **Subscribe-Once**: No unnecessary re-subscriptions
- ✅ **Proper Cleanup**: Unsubscribe and delete on entity removal

---

## 📊 Technical Details

### MQTT Topic Structure

**Monitoring Topics** (QoS 0, Retained):
```
Haptique/{RemoteID}/status
Haptique/{RemoteID}/battery_level
Haptique/{RemoteID}/keys
Haptique/{RemoteID}/device/list
Haptique/{RemoteID}/macro/list
Haptique/{RemoteID}/device/{device}/commands
```

**Control Topics** (QoS 1, Not Retained):
```
Haptique/{RemoteID}/macro/{name}/trigger
Haptique/{RemoteID}/device/{device}/trigger
```

### Debug Logging
Enable comprehensive MQTT logging:
```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

You'll see:
- 📡 All SUBSCRIBE/UNSUBSCRIBE operations
- 📥 All received MQTT messages with payloads
- 📤 All published messages with QoS and retain flags

---

## 🔄 Migration from v1.2.0

### What You Need to Do

1. **Update the integration** via HACS or manually
2. **Restart Home Assistant**
3. **Remove from dashboards**:
   - Refresh Data button
   - Scan Interval slider
4. **Update automations** that used removed services
5. **Enable DEBUG logs** if you used `get_diagnostics`

### What Stays the Same

✅ All macro switches work identically
✅ All sensors function unchanged
✅ Configuration requires no changes
✅ Your automations using `trigger_macro` and `trigger_device_command` work as before

---

## 💡 Tips for Best Experience

### 1. Use Device Command Sensors
Instead of guessing command names, check the `sensor.commands_{device}` entity to see all available commands.

### 2. Enable DEBUG Logs
For troubleshooting or monitoring:
```yaml
logger:
  logs:
    custom_components.haptique_rs90: debug
```

### 3. Multi-Language
Switch Home Assistant language to see the integration in French or English.

### 4. Use the Icon
The integration now has a nice Haptique logo in the UI!

---

## 🎯 What's Next?

Future improvements being considered:
- More language support (Spanish, German, Dutch)
- Advanced automation examples
- Blueprint library
- Enhanced diagnostics panel

Have ideas? Open an issue or discussion on [GitHub](https://github.com/daangel27/haptique_rs90)!

---

**Version**: 1.2.5
**Release Date**: December 10, 2024
**Breaking Changes**: Yes (removed entities and services)
**Migration Required**: Minimal (update dashboards and automations)
