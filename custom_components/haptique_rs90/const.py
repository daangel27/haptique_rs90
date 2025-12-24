"""Constants for the Haptique RS90 Remote integration."""

DOMAIN = "haptique_rs90"

# MQTT Topics
TOPIC_BASE = "Haptique"
TOPIC_STATUS = "status"
TOPIC_DEVICE_LIST = "device/list"
TOPIC_MACRO_LIST = "macro/list"
TOPIC_BATTERY_STATUS = "battery/status"  # Publish here to request battery update
TOPIC_BATTERY_LEVEL = "battery_level"    # Subscribe here to receive battery value
TOPIC_KEYS = "keys"
TOPIC_MACRO_TRIGGER = "macro/{macro_name}/trigger"
TOPIC_DEVICE_DETAIL = "device/{device_name}/detail"
TOPIC_DEVICE_TRIGGER = "device/{device_name}/trigger"
TOPIC_TEST_STATUS = "test/status"
TOPIC_LED_LIGHT = "ledlight/on"  # RGB ring light control

# Attributes
ATTR_REMOTE_ID = "remote_id"
ATTR_DEVICE_NAME = "device_name"
ATTR_MACRO_NAME = "macro_name"
ATTR_COMMAND_NAME = "command_name"
ATTR_BUTTON_NUMBER = "button_number"

# Config
CONF_REMOTE_ID = "remote_id"
CONF_NAME = "name"

# States
STATE_ONLINE = "online"
STATE_OFFLINE = "offline"

