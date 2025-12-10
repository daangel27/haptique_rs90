# Changelog

All notable changes to this project will be documented in this file.

## [1.2.5] - 2024-12-10

### 🎉 Major Changes from v1.2.0

#### ✨ New Features
- **Device Command Sensors**: Added diagnostic sensors showing available commands for each device
  - Sensors created as `sensor.commands_{device_name}`
  - Alphabetically sorted for easy browsing
  - Categorized as diagnostic entities
- **Enhanced MQTT Logging**: Added comprehensive DEBUG logs for all MQTT operations
  - Subscribe/Unsubscribe operations with topics
  - All received messages with payloads
  - All published messages with QoS and retain flags
  - Useful for troubleshooting and monitoring

#### 🔧 Technical Improvements
- **100% Event-Driven**: Removed all periodic polling
  - No more `scan_interval` configuration
  - Updates only via MQTT messages
  - Reduced network traffic and improved responsiveness
- **QoS Optimization**: Aligned with Haptique MQTT best practices
  - QoS 0 for monitoring (status, battery, keys, lists)
  - QoS 1 for control commands (macro/device triggers)
- **Macro Trigger Protocol**: Fixed MQTT retained message handling
  - Changed from `retain=True` to `retain=False` for macro triggers
  - Proper unsubscribe when macros are deleted
  - Automatic cleanup of retained messages on deletion
- **Dynamic Entity Management**: Improved add/remove of entities
  - Proper cleanup when macros/devices are deleted
  - Fixed race conditions in subscription management
  - Entities update in real-time

#### 🗑️ Removed Features
- **Removed Services**:
  - `haptique_rs90.refresh_data` (no longer needed with event-driven updates)
  - `haptique_rs90.get_diagnostics` (use DEBUG logs instead)
- **Removed Entities**:
  - Refresh Data button
  - Scan Interval slider

#### 🎨 UI/UX Improvements
- **Macro Switches**:
  - Blue (ON) / Gray (OFF) coloring via device_class
  - Better visual feedback
- **Connection Sensor**:
  - Dynamic icons: `mdi:connection` (connected) / `mdi:close-network-outline` (disconnected)
- **Running Macro Sensor**:
  - Dynamic icons: `mdi:play-circle` (active) / `mdi:circle-outline` (idle)
- **Number Entity** (removed):
  - Was: Scan interval slider (5-60 min)

#### 🌍 Internationalization
- **Multi-language Support**:
  - English (default)
  - French
- **Service Descriptions**: Improved clarity
  - Better `device_id` explanation (Home Assistant ID vs MQTT ID)
  - Clear instructions: "find it in Settings > Devices & Services"
  - Examples with actual IDs
- **Translated Strings**: Complete translations for:
  - Configuration flow
  - Service names and descriptions
  - Field labels and descriptions

#### 🐛 Bug Fixes
- **MQTT Subscription Management**:
  - Fixed race condition causing macros not to unsubscribe properly
  - Proper tracking of subscription states
  - Synchronized `_subscribed_macros` and `_macro_subscriptions` dictionaries
  - Proper unsubscribe when macros are deleted
- **State Persistence**:
  - Removed `.storage` file-based persistence (was causing random triggers)
  - Now relies solely on MQTT retained messages from RS90 (single source of truth)

#### 📚 Documentation
- **Improved README**:
  - English as default language
  - Clear auto-discovery explanation
  - Prerequisites section added
  - Better screenshots examples
  - Acknowledgment to Cantata Communication Solutions
- **Service Documentation**:
  - Clear distinction between MQTT ID and Home Assistant device_id
  - Step-by-step guide to find device_id
  - Better examples

#### 🔒 Protocol Compliance
- **100% Haptique MQTT Compliant**:
  - Verified against official documentation
  - Correct QoS levels for all operations
  - Proper retained message handling
  - Subscribe-once pattern implemented

### Technical Details

#### MQTT Topics
- **Monitoring** (QoS 0, Retained):
  - `status`, `battery_level`, `keys`, `device/list`, `macro/list`, `device/{name}/commands`
- **Control** (QoS 1, Not Retained):
  - `macro/{name}/trigger`, `device/{name}/trigger`

#### File Structure Changes
```diff
- button.py (removed - refresh button)
- number.py (removed - scan interval slider)
+ Enhanced coordinator.py (event-driven, no polling)
+ Improved services.yaml (EN/FR translations)
+ New translations/en.json
+ New translations/fr.json
```

---

## [1.2.0] - 2024-12-XX

### Initial Features
- MQTT integration with Haptique RS90
- Basic sensors (battery, last key, running macro, device list)
- Binary sensor for connection status
- Macro switches with ON/OFF states
- Services for triggering macros and device commands
- Configurable scan interval (60s-3600s)
- Manual refresh button
- Diagnostic service

---

## Migration Guide: 1.2.0 → 1.2.5

### Breaking Changes
- ⚠️ **Removed entities**: `button.{name}_refresh_data` and `number.{name}_scan_interval`
- ⚠️ **Removed services**: `haptique_rs90.refresh_data` and `haptique_rs90.get_diagnostics`

### What You Need to Do
1. **Remove automations/scripts** that use removed services
2. **Update dashboards** to remove refresh button and scan interval entities
3. **Enable DEBUG logs** if you were using `get_diagnostics` service:
   ```yaml
   logger:
     logs:
       custom_components.haptique_rs90: debug
   ```

### What Stays the Same
- ✅ All macro switches work identically
- ✅ All sensors continue to function
- ✅ Services `trigger_macro` and `trigger_device_command` unchanged
- ✅ No configuration changes needed

### Benefits of Upgrading
- 🚀 Faster response times (event-driven vs polling)
- 📉 Reduced network traffic
- 🐛 No more random macro triggers
- 🎨 Better visual feedback (colors, icons)
- 🌍 Multi-language support
- 📋 Device command sensors for easy command discovery
