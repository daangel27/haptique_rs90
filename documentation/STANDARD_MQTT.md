# Standard MQTT macros, sequences and state queries

Since 1.8.0 the integration uses the Standard MQTT firmware contract documented in
`ccs777/HaptiqueRS90`, `docs/standard-mqtt.md` (contributed by @ccs777 in PR #38
and #39). It requires firmware which publishes real macros separately from command
sequences and implements `currentstatus` and `discovery/refresh`. Verified on
RS90 firmware **4.1.2** and **4.2**. Existing unmarked macro inventories remain supported.

## Controls and compatibility

Real macros and command sequences each have an ON/OFF switch. Discovery
accepts both `id` and the older `Id` spelling. IDs remain stable when names
change. A sequence formerly exposed as a macro reuses its registered switch
identity after moving to sequence discovery, preserving automation references.
Migration ownership is persisted in entity-registry capabilities, so a later
ID conflict or restart cannot redirect an existing automation to another target.
Removed targets become unavailable; their registry entries remain so they
can return without losing user customizations. Malformed inventories do not
erase the last valid snapshot; a valid empty array clears the inventory.

Name-based feedback is accepted only for unambiguous aliases. ID feedback
takes precedence for modern targets. Unmarked legacy inventory continues to
accept unique name feedback after an ID query because older firmware reports
subsequent execution by name. Historical sequence aliases which collide with
a real macro ID are ignored, including their execution results. If modern macro and sequence inventories advertise the
same ID, both controls become unavailable and calls fail with an inventory
conflict rather than dispatching to a guessed target.

Every execution request uses QoS 1 and **retain=false**. Publication does not
change the switch state. Retained firmware status establishes `ON`, `OFF`
or `UNKNOWN`; no status is also unknown. These are persisted execution
states, **not measurements of physical TV/receiver power**.

Switch attributes expose `target_kind`, `target_id`, `last_result` and the
legacy `rs90_macro_id`/`macro_name` fields. Execution results such as
`rejected` with `execution_busy`, `failed`, `executed` or `skipped` are
informational. A rejected request preserves the last confirmed state.
This protocol has no request IDs, so results cannot be reliably correlated
with concurrent callers.

## Actions

`rs90_id` is the **Home Assistant device ID** selected in the action editor.
It is different from the MQTT remote ID in the topic tree.

Existing `haptique_rs90.trigger_macro` fields are unchanged. Its stable
`rs90_macro_id` resolves a real macro first and a migrated sequence second.
`haptique_rs90.trigger_sequence` explicitly selects a sequence:

```yaml
action: haptique_rs90.trigger_sequence
data:
  rs90_id: YOUR_HOME_ASSISTANT_DEVICE_ID
  rs90_sequence_id: YOUR_SEQUENCE_ID
  action: "off"
```

`haptique_rs90.query_status` requests persisted state without executing:

```yaml
action: haptique_rs90.query_status
data:
  rs90_id: YOUR_HOME_ASSISTANT_DEVICE_ID
  target_kind: macro  # macro or sequence
  target_id: YOUR_TARGET_ID
```

It sends a non-retained request to `macro/{id}/currentstatus` or
`sequence/{id}/currentstatus`. The response updates the switch asynchronously;
the action does not return a synchronous equipment power measurement.

Setup, remote reconnection and `refresh_lists` request target state.
`refresh_lists` also sends `discovery/refresh`, requests battery state and
keeps device-detail requests for older firmware. A firmware version which
ignores the discovery request cannot provide a fresh list this way.

Info Summary retains its name-to-ID attributes and adds `macros_by_id`,
`devices_by_id`, `sequences_by_id`, `sequences` and `sequences_count`.
Use the ID-indexed maps when display names are duplicated.

## Validation

Tests use Home Assistant's MQTT utilities with simulated broker messages.
Run `python -m pip install -r requirements_test.txt` with Python 3.14,
then `python -m pytest`.

Live acceptance was done on 2026-11-07 with an RS90 on firmware 4.2 and
Home Assistant 2026.10: discovery, macro ON/OFF, `skipped` results, app launch
from Home Assistant and from the RS90 screen, sleep and reconnection.

Known firmware limitations (reported to Haptique): a macro run from the RS90
screen publishes no status or result; switching macros can leave the previous
one ON; `active_app` reports the app label (not the package) when an app is
opened on the screen, and nothing when leaving an app.

## Installed app controls

Firmware
publishes `app/list` as `[{id:packageId,name:label}]` and the integration adds
one launch button per package. Package IDs determine identity and routing;
duplicate or changed labels do not affect the controls. Removed apps become
unavailable and their registered buttons survive reinstallation.

New app buttons are disabled by default, including system apps. Enable only
the apps you want under Settings > Devices & services > Entities. Existing
entity enable/disable choices and the RGB Ring Light button are unchanged.

```yaml
action: haptique_rs90.launch_app
data:
  rs90_id: YOUR_HOME_ASSISTANT_DEVICE_ID
  app_package_id: com.spotify.music
```

The action publishes non-retained `open` to `app/{packageId}/open` at QoS 1.
The button's `last_result` records `launched` or an error such as
`launch_failed`, `activity_unavailable` or `app_not_found`. `launched` confirms
Android accepted the intent; it does not confirm playback or loading completion.
An error never changes the Last Reported App sensor.

Last Reported App shows the label of the app received on retained `active_app`,
with the package in `app_package_id`. Apps opened on the RS90 screen are reported
by label and resolved to their package through `app/list`. This is the last firmware observation, not
continuous tracking of every later manual app transition. Info Summary adds
`apps_by_id` and `apps_count`. `refresh_lists` refreshes app discovery through
`discovery/refresh`; the firmware also supports `app/list/get`.


## Execution results

Every non-retained `macro/{id}/result` or `sequence/{id}/result` updates the
**Last Macro Result** sensor, e.g. `CANAL · OFF · skipped (already_in_requested_state)`,
and fires the `haptique_rs90_macro_result` event with `device_id`, `remote_id`,
`target_kind`, `target_id`, `target_name`, `action`, `status`, `error` and
`timestamp`. `action` is known only for runs requested from Home Assistant.
Each event gets its own logbook entry attached to the macro/sequence switch,
so repeated identical results stay visible. Retained results replayed on
(re)subscribe are ignored. The sensor restores its last value after a restart.
