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

function shortName(hass, entityId) {
  // "RS90 CANAL" -> "CANAL": the dashboard is already about the RS90.
  return name(hass, entityId).replace(/^RS90\s+/i, "");
}

function remoteButton(hass, entityId, colors, tapAction, icon) {
  return {
    type: "button",
    entity: entityId,
    name: shortName(hass, entityId),
    icon: icon || undefined,
    show_icon: true,
    show_name: true,
    show_state: false,
    icon_height: "28px",
    tap_action: tapAction,
    hold_action: { action: "more-info" },
    card_mod: { style: buttonStyle(colors, 86) },
  };
}

function macroButton(hass, entityId) {
  // Green when the RS90 reports the macro ON, grey otherwise.
  const style = buttonStyle(["{{ '#16a34a' if is_state(config.entity, 'on') else '#3f3f46' }}", "{{ '#052e16' if is_state(config.entity, 'on') else '#18181b' }}"], 86);
  return {
    type: "button",
    entity: entityId,
    name: shortName(hass, entityId),
    icon: "mdi:play-circle",
    show_icon: true,
    show_name: true,
    show_state: true,
    icon_height: "28px",
    tap_action: { action: "toggle" },
    hold_action: { action: "more-info" },
    card_mod: { style },
  };
}

function section(title, icon, cards, columns) {
  return {
    type: "grid",
    cards: [
      { type: "heading", heading: title, heading_style: "title", icon },
      { type: "grid", columns, square: false, grid_options: { columns: "full" }, cards },
    ],
  };
}

function remoteView(hass, remote, t, multi) {
  const sections = [];
  if (remote.macros.length) {
    sections.push(section(t.macros, "mdi:play-circle", remote.macros.map((id) => macroButton(hass, id)), 3));
  }
  if (remote.sequences.length) {
    sections.push(
      section(
        t.sequences,
        "mdi:playlist-play",
        remote.sequences.map((id) => remoteButton(hass, id, COLORS.volume, { action: "toggle" }, "mdi:playlist-play")),
        3,
      ),
    );
  }
  sections.push(
    remote.apps.length
      ? section(
          t.apps,
          "mdi:apps",
          remote.apps.map((id) =>
            remoteButton(hass, id, COLORS.app, { action: "perform-action", perform_action: "button.press", target: { entity_id: id } }),
          ),
          3,
        )
      : { type: "grid", cards: [{ type: "heading", heading: t.apps, heading_style: "title", icon: "mdi:apps" }, { type: "markdown", content: t.noApps }] },
  );
  if (remote.status.length) {
    sections.push({
      type: "grid",
      cards: [
        { type: "heading", heading: t.status, heading_style: "title", icon: "mdi:information-outline" },
        ...remote.status.map((entity) => ({ type: "tile", entity, name: shortName(hass, entity) })),
      ],
    });
  }
  return {
    title: multi ? remote.name : t.remote,
    path: multi ? `rs90-${slug(remote.name)}` : "rs90",
    type: "sections",
    max_columns: 4,
    sections,
  };
}

// ---------------------------------------------------------------------------
// Device views: commands grouped like a physical remote.
// ---------------------------------------------------------------------------

const COLORS = {
  nav: ["#0e7490", "#082f49"],
  power: ["#b91c1c", "#450a0a"],
  volume: ["#1e3a8a", "#0f172a"],
  media: ["#0e7490", "#082f49"],
  number: ["#3f3f46", "#18181b"],
  app: ["#6d28d9", "#2e1065"],
  other: ["#3f3f46", "#18181b"],
};

function buttonStyle(colors, height) {
  return `ha-card {
  height: ${height}px !important;
  border-radius: 14px !important;
  border: none !important;
  border-top: 1px solid rgba(255,255,255,.12) !important;
  background: linear-gradient(145deg, ${colors[0]}, ${colors[1]}) !important;
  color: #fff !important;
  --card-mod-icon-color: #fff;
  box-shadow: 0 4px 0 rgba(0,0,0,.55), 0 8px 14px rgba(0,0,0,.30) !important;
  transition: transform .08s ease, box-shadow .08s ease !important;
}
ha-card:active {
  transform: translateY(3px) !important;
  box-shadow: 0 1px 0 rgba(0,0,0,.55), 0 2px 4px rgba(0,0,0,.30) !important;
}
ha-card span {
  font-size: 11px !important;
  font-weight: 600 !important;
  line-height: 1.15 !important;
  white-space: normal !important;
  text-align: center !important;
  text-shadow: 0 1px 1px rgba(0,0,0,.35) !important;
}`;
}

const SPACER_STYLE =
  "ha-card { background: none !important; box-shadow: none !important; border: none !important; pointer-events: none; }";

// Icon and whether to show the name, per command.
const ICONS = {
  POWER: ["mdi:power", true], POWER_ON: ["mdi:power-on", true], POWER_OFF: ["mdi:power-off", true],
  POWER_OFF_ALL_ZONES: ["mdi:power-off", true],
  UP: ["mdi:chevron-up", false], DOWN: ["mdi:chevron-down", false],
  LEFT: ["mdi:chevron-left", false], RIGHT: ["mdi:chevron-right", false],
  OK: ["mdi:circle-small", true], SELECT: ["mdi:circle-small", true], ENTER: ["mdi:circle-small", true],
  BACK: ["mdi:keyboard-return", true], RETURN: ["mdi:keyboard-return", true],
  EXIT: ["mdi:exit-to-app", true], HOME: ["mdi:home", true], MENU: ["mdi:menu", true],
  MENU_HOME: ["mdi:home", true], INFO: ["mdi:information-outline", true], INFOS: ["mdi:information-outline", true],
  GUIDE: ["mdi:television-guide", true], DISPLAY: ["mdi:information-outline", true],
  VOLUME_UP: ["mdi:volume-plus", false], VOLUME_DOWN: ["mdi:volume-minus", false],
  MUTE_UNMUTE: ["mdi:volume-mute", false], MUTE: ["mdi:volume-mute", false], UNMUTE: ["mdi:volume-high", false],
  CHANNEL_UP: ["mdi:chevron-double-up", false], CHANNEL_DOWN: ["mdi:chevron-double-down", false],
  PLAY_PAUSE: ["mdi:play-pause", false], PLAY: ["mdi:play", false], PAUSE: ["mdi:pause", false],
  STOP: ["mdi:stop", false], MEDIA_REWIND: ["mdi:rewind", false], MEDIA_FAST_FORWARD: ["mdi:fast-forward", false],
  REWIND: ["mdi:rewind", false], FAST_FORWARD: ["mdi:fast-forward", false],
  PREVIOUS: ["mdi:skip-previous", false], NEXT: ["mdi:skip-next", false], RECORD: ["mdi:record", false],
  PLAYBACK: ["mdi:play-pause", true], FAVORITE: ["mdi:star", true],
  INPUT: ["mdi:import", true], SOURCE: ["mdi:import", true],
};

const GROUPS = [
  { key: "power", icon: "mdi:power", test: (c) => /^POWER/.test(c) },
  { key: "nav", icon: "mdi:gamepad", test: (c) => ["UP", "DOWN", "LEFT", "RIGHT", "OK", "SELECT", "ENTER", "BACK", "RETURN", "EXIT", "HOME", "MENU", "MENU_HOME", "INFO", "INFOS", "GUIDE", "DISPLAY"].includes(c) },
  { key: "volume", icon: "mdi:volume-high", test: (c) => /^(VOLUME_|MUTE|UNMUTE)/.test(c) || /^CHANNEL_(UP|DOWN)$/.test(c) },
  { key: "media", icon: "mdi:play-pause", test: (c) => ["PLAY_PAUSE", "PLAY", "PAUSE", "STOP", "MEDIA_REWIND", "MEDIA_FAST_FORWARD", "REWIND", "FAST_FORWARD", "PREVIOUS", "NEXT", "RECORD", "PLAYBACK"].includes(c) },
  { key: "number", icon: "mdi:dialpad", test: (c) => /^[0-9]$/.test(c) || c === "-/--" },
  { key: "input", icon: "mdi:import", test: (c) => /^(INPUT|SOURCE|HDMI)/.test(c) },
  { key: "other", icon: "mdi:dots-grid", test: () => true },
];

const GROUP_TEXT = {
  en: { power: "Power", nav: "Navigation", volume: "Volume & channels", media: "Playback", number: "Numbers", input: "Inputs", other: "More" },
  fr: { power: "Alimentation", nav: "Navigation", volume: "Volume & chaînes", media: "Lecture", number: "Pavé numérique", input: "Entrées", other: "Autres" },
};

function commandButton(remote, device, cmd, colors) {
  const [icon, showName] = ICONS[cmd] || [null, true];
  return {
    type: "button",
    name: label(cmd).replace(/^MEDIA /, ""),
    icon: icon || undefined,
    show_icon: Boolean(icon),
    show_name: showName || !icon,
    icon_height: "22px",
    tap_action: {
      action: "perform-action",
      perform_action: `${DOMAIN}.trigger_device_command`,
      data: { rs90_id: remote.device_id, rs90_device_id: device.rs90_device_id, command_name: cmd },
    },
    hold_action: { action: "none" },
    card_mod: { style: buttonStyle(colors, 58) },
  };
}

function spacer() {
  return { type: "button", show_icon: false, show_name: false, tap_action: { action: "none" }, hold_action: { action: "none" }, card_mod: { style: SPACER_STYLE } };
}

/** Lay out commands like a remote: D-pad, keypad, transport row… */
function arrange(group, cmds) {
  const has = (c) => cmds.includes(c);
  const pick = (...names) => names.find((n) => has(n));
  if (group === "nav") {
    const tl = pick("EXIT", "MENU", "HOME", "MENU_HOME");
    const tr = pick("INFO", "INFOS", "GUIDE", "DISPLAY");
    const bl = pick("RETURN", "BACK");
    const br = pick(...["HOME", "MENU_HOME", "MENU", "GUIDE"].filter((n) => n !== tl && n !== tr));
    const center = pick("OK", "SELECT", "ENTER");
    const grid = [tl, pick("UP"), tr, pick("LEFT"), center, pick("RIGHT"), bl, pick("DOWN"), br];
    const used = new Set(grid.filter(Boolean));
    return { columns: 3, cells: [...grid, ...cmds.filter((c) => !used.has(c))] };
  }
  if (group === "number") {
    const digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", null, "0", null];
    const cells = digits.map((d) => (d && has(d) ? d : null));
    while (cells.length && cells[cells.length - 1] === null) cells.pop();
    const extra = cmds.filter((c) => !digits.includes(c));
    if (extra.length && cells.length >= 10 && cells[9] === null) cells[9] = extra.shift();
    return { columns: 3, cells: [...cells, ...extra] };
  }
  if (group === "volume") {
    // Volume on the left, mute in the middle, channels on the right.
    const mute = pick("MUTE_UNMUTE", "MUTE");
    const unmute = mute === "MUTE" ? pick("UNMUTE") : null;
    const channels = has("CHANNEL_UP") || has("CHANNEL_DOWN");
    const rows = channels
      ? [pick("VOLUME_UP"), mute, pick("CHANNEL_UP"), pick("VOLUME_DOWN"), unmute, pick("CHANNEL_DOWN")]
      : [pick("VOLUME_UP"), mute, pick("VOLUME_DOWN"), unmute];
    const used = new Set(rows.filter(Boolean));
    const extra = cmds.filter((c) => !used.has(c));
    const cells = rows.map((c) => c || null);
    while (cells.length && cells[cells.length - 1] === null) cells.pop();
    return { columns: channels ? 3 : 2, cells: [...cells, ...extra] };
  }
  if (group === "media") {
    const order = ["PREVIOUS", "MEDIA_REWIND", "REWIND", "PLAY_PAUSE", "PLAY", "PAUSE", "STOP", "MEDIA_FAST_FORWARD", "FAST_FORWARD", "NEXT", "RECORD"];
    const known = order.filter(has);
    return { columns: 4, cells: [...known, ...cmds.filter((c) => !known.includes(c))] };
  }
  return { columns: group === "power" ? 3 : 4, cells: cmds };
}

function deviceView(hass, remote, device, config) {
  const wanted = config.devices && config.devices[device.name];
  let commands = device.commands;
  if (Array.isArray(wanted)) commands = commands.filter((cmd) => wanted.includes(cmd));
  const lang = ((hass.locale && hass.locale.language) || "en").split("-")[0];
  const names = GROUP_TEXT[lang] || GROUP_TEXT.en;

  const remaining = [...commands];
  const sections = [];
  for (const group of GROUPS) {
    const cmds = remaining.filter((c) => group.test(c));
    if (!cmds.length) continue;
    cmds.forEach((c) => remaining.splice(remaining.indexOf(c), 1));
    const { columns, cells } = arrange(group.key, cmds);
    const colors = COLORS[group.key] || COLORS.other;
    sections.push({
      type: "grid",
      cards: [
        { type: "heading", heading: names[group.key], heading_style: "title", icon: group.icon },
        {
          type: "grid",
          columns,
          square: false,
          grid_options: { columns: "full" },
          cards: cells.map((cmd) => (cmd ? commandButton(remote, device, cmd, colors) : spacer())),
        },
      ],
    });
  }
  return {
    title: device.name,
    path: slug(device.name),
    type: "sections",
    max_columns: 3,
    sections,
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
      views.push(deviceView(hass, remote, device, config));
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
