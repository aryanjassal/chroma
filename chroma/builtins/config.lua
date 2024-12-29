local lib = require("chroma.builtins.lib")

local config = {}

config.integrations = {
  themable = { "gtk", "kitty" }
}

config.behavior = {
  missing_local_integration = "IGNORE",
  missing_theme_integration = "IGNORE"
}

config.generators = {
  hslmap = {
    accent = lib.hslmap_condition(nil, {60, 100}, {50, 90}),
    black = lib.hslmap_condition(nil, nil, {5, 20}),
    white = lib.hslmap_condition(nil, nil, {80, 95}),
    background = lib.hslmap_condition(nil, {0, 20}, {5, 10}),
    foreground = lib.hslmap_condition(nil, {0, 20}, {90, 95}),
    red = lib.hslmap_condition({{0, 35}, {325, 360}}, {40, 90}, {30, 90}),
    orange = lib.hslmap_condition({35, 75}, {30, 90}, {40, 80}),
    brown = lib.hslmap_condition({35, 75}, {30, 70}, {20, 70}),
    yellow = lib.hslmap_condition({65, 105}, {40, 90}, {30, 90}),
    green = lib.hslmap_condition({100, 160}, {40, 90}, {30, 90}),
    blue = lib.hslmap_condition({200, 230}, {40, 50}, {40, 60}),
    cyan = lib.hslmap_condition({170, 200}, {40, 90}, {40, 90}),
    magenta = lib.hslmap_condition({280, 310}, {30, 50}, {30, 50}),
  },

  generator_modes = {
    accent = "saturate 0.1",
    norm = "",
    bright = "lighten 0.1",
    background = "darken 0.15",
    foreground = "lighten 0.15",
  }
}

return config
