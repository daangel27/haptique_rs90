# Finding your RS90 ID (`rs90_id`)

Every action of the integration (`trigger_macro`, `trigger_sequence`, `trigger_device_command`, `launch_app`, `query_status`…) needs **`rs90_id`**: the **Home Assistant device ID** of your remote, e.g. `6f99751e78b5a07de72d549143e2975c`.

It is **not**:
- ❌ the MQTT ID of the RS90 (e.g. `3d5d95aa3a7f7b20`, used in topics like `Haptique/3d5d95aa3a7f7b20/status`)
- ❌ the name of the RS90 (e.g. "RS90 Living Room")

> 💡 Just want to press buttons? The **Haptique RS90 dashboard** needs no ID at all (see the README). This guide is for automations and scripts.

---

## 1. The Info Summary sensor (quickest)

On the RS90 device page → **Sensors** → **Info Summary** → **Attributes**:
- **Rs90 ID**: the `rs90_id` to use in actions
- **Rs90 remote ID**: the MQTT ID
- **Macros / Sequences / Devices / Apps by ID**: the IDs to use for `rs90_macro_id`, `rs90_sequence_id`, `rs90_device_id` and `app_package_id`

See [Finding the IDs](../README.md#-finding-the-ids-the-info-summary-sensor) in the README.

## 2. Let Home Assistant fill it in

In an automation, a script or **Developer Tools → Actions**, pick an action such as **Haptique RS90: Trigger macro**, then select your remote in the **RS90 Remote** field. In YAML mode, Home Assistant shows the `rs90_id` it filled in.

## 3. From a template (no copy-paste)

```yaml
rs90_id: "{{ device_id('sensor.rs90_battery') }}"
```

Replace `sensor.rs90_battery` with any entity of your RS90. The ID then follows the remote even if the integration is removed and added again.

## 4. From the device page URL

**Settings → Devices & services → Haptique RS90 → your RS90**. The end of the URL is the ID:
```
http://homeassistant.local:8123/config/devices/device/6f99751e78b5a07de72d549143e2975c
```

---

## Examples

Turn a macro on:
```yaml
action: haptique_rs90.trigger_macro
data:
  rs90_id: "{{ device_id('sensor.rs90_battery') }}"
  rs90_macro_id: "692eb1561bddd5814022960c"   # Info Summary → Macros by ID
  action: "on"
```

Send a device command:
```yaml
action: haptique_rs90.trigger_device_command
data:
  rs90_id: 6f99751e78b5a07de72d549143e2975c
  rs90_device_id: "6adf6831cd975fa9bbfbb363"   # Info Summary → Devices by ID
  command_name: "VOLUME_UP"                    # Commands sensor of the device
```

> ⚠️ `rs90_id` goes in `data:`. Using `target: device_id:` instead does not work with these actions.

---

## FAQ

**Does `rs90_id` change?**
No, as long as you don't delete the RS90 from Home Assistant. If you do, the template of method 3 keeps your automations working.

**I have several RS90s, which is which?**
Give each one a clear name when adding it ("RS90 Living Room", "RS90 Bedroom"): the **RS90 Remote** selector shows these names.
