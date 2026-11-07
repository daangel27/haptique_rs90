/*
 * Haptique RS90 dashboard strategy.
 *
 * Builds a dashboard from the entities of the Haptique RS90 integration every
 * time it is opened, so it always matches what the remote publishes:
 *   - one "RS90" view: macros, sequences, apps and status
 *   - one view per RS90 device: a button per command
 *
 * Usage: create a dashboard and pick "Haptique RS90" (Home Assistant 2026.5+),
 * or use this raw configuration:
 *   strategy:
 *     type: custom:haptique-rs90
 * Optional configuration:
 *   strategy:
 *     type: custom:haptique-rs90
 *     devices:            # limit the device views and their commands
 *       KODI: [UP, DOWN, LEFT, RIGHT, OK, PLAY_PAUSE]
 *       TV: all
 *     hide_devices: [XBOX]
 *     columns: 4          # buttons per row in device views
 */

const DOMAIN = "haptique_rs90";

const TEXT = {
  en: {
    remote: "RS90",
    macros: "Macros",
    sequences: "Sequences",
    apps: "Apps",
    status: "Status",
    noApps: "No app enabled. Enable app buttons in Settings → Entities.",
    noDevice: "No Haptique RS90 found. Add the integration first.",
  },
  fr: {
    remote: "RS90",
    macros: "Macros",
    sequences: "Séquences",
    apps: "Applications",
    status: "État",
    noApps: "Aucune application activée. Activez les boutons d'applications dans Paramètres → Entités.",
    noDevice: "Aucune Haptique RS90 trouvée. Ajoutez d'abord l'intégration.",
  },
};

function text(hass) {
  const lang = (hass.locale && hass.locale.language) || hass.language || "en";
  return TEXT[lang.split("-")[0]] || TEXT.en;
}

function slug(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "device";
}

function label(command) {
  return String(command).replace(/_/g, " ");
}

/** Layout of every RS90, from the integration (stable while the remote sleeps). */
async function collect(hass) {
  const result = await hass.callWS({ type: `${DOMAIN}/dashboard` });
  const remotes = result.remotes || [];
  for (const remote of remotes) {
    for (const key of ["macros", "sequences", "apps", "status"]) {
      remote[key] = remote[key].filter((id) => hass.states[id]);
      remote[key].sort((a, b) => name(hass, a).localeCompare(name(hass, b)));
    }
  }
  return remotes;
}

function name(hass, entityId) {
  const state = hass.states[entityId];
  return (state && state.attributes.friendly_name) || entityId;
}

function tiles(entities, extra = {}) {
  return entities.map((entity) => ({ type: "tile", entity, ...extra }));
}

function section(title, cards) {
  return {
    type: "grid",
    cards: [{ type: "heading", heading: title }, ...cards],
  };
}

function remoteView(hass, remote, t, multi) {
  const sections = [];
  if (remote.macros.length) {
    sections.push(section(t.macros, tiles(remote.macros, { features: [{ type: "toggle" }], features_position: "inline" })));
  }
  if (remote.sequences.length) {
    sections.push(section(t.sequences, tiles(remote.sequences, { tap_action: { action: "toggle" } })));
  }
  sections.push(
    section(
      t.apps,
      remote.apps.length
        ? remote.apps.map((entity) => ({
            type: "tile",
            entity,
            tap_action: { action: "perform-action", perform_action: "button.press", target: { entity_id: entity } },
          }))
        : [{ type: "markdown", content: t.noApps }],
    ),
  );
  if (remote.status.length) sections.push(section(t.status, tiles(remote.status)));
  return {
    title: multi ? remote.name : t.remote,
    path: multi ? `rs90-${slug(remote.name)}` : "rs90",
    icon: "mdi:remote",
    type: "sections",
    max_columns: 4,
    sections,
  };
}

function deviceView(remote, device, config) {
  const wanted = config.devices && config.devices[device.name];
  let commands = device.commands;
  if (Array.isArray(wanted)) commands = commands.filter((cmd) => wanted.includes(cmd));
  const columns = Number(config.columns) || 4;
  const buttons = commands.map((cmd) => ({
    type: "button",
    name: label(cmd),
    show_icon: false,
    show_name: true,
    grid_options: { columns: Math.max(1, Math.floor(12 / columns)), rows: 1 },
    tap_action: {
      action: "perform-action",
      perform_action: `${DOMAIN}.trigger_device_command`,
      data: {
        rs90_id: remote.device_id,
        rs90_device_id: device.rs90_device_id,
        command_name: cmd,
      },
    },
  }));
  return {
    title: device.name,
    path: slug(device.name),
    type: "sections",
    max_columns: 1,
    sections: [{ type: "grid", column_span: 1, cards: [{ type: "heading", heading: device.name }, ...buttons] }],
  };
}

async function build(config, hass) {
  config = config || {};
  const t = text(hass);
  const remotes = await collect(hass);
  if (!remotes.length) {
    return { views: [{ title: "RS90", cards: [{ type: "markdown", content: t.noDevice }] }] };
  }
  const multi = remotes.length > 1;
  const hidden = new Set(config.hide_devices || []);
  const views = [];
  for (const remote of remotes) {
    views.push(remoteView(hass, remote, t, multi));
    for (const device of remote.devices) {
      if (hidden.has(device.name)) continue;
      if (config.devices && !(device.name in config.devices)) continue;
      if (!device.commands.length) continue;
      views.push(deviceView(remote, device, config));
    }
  }
  return { title: "Haptique RS90", views };
}

class HaptiqueRS90DashboardStrategy extends HTMLElement {
  // Home Assistant 2026.x
  static async generate(config, hass) {
    return build(config, hass);
  }

  // Older Home Assistant releases
  static async generateDashboard(info) {
    return build(info.config && info.config.strategy, info.hass);
  }
}

if (!customElements.get("ll-strategy-dashboard-haptique-rs90")) {
  customElements.define("ll-strategy-dashboard-haptique-rs90", HaptiqueRS90DashboardStrategy);
  window.customStrategies = window.customStrategies || [];
  window.customStrategies.push({
    type: "haptique-rs90",
    strategyType: "dashboard",
    name: "Haptique RS90",
    description: "Macros, sequences, apps and a remote for each device of your RS90, always up to date.",
    documentationURL: "https://github.com/daangel27/haptique_rs90",
  });
}
