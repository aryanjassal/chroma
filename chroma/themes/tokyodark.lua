local theme = require "chroma.builtins.default"

theme.options = {
  chroma_version = "0.5.4",
}

theme.meta = {
  name = "Tokyonight",
  description = "A clean theme that celebrates the lights of downtown Tokyo at night.",
  url = "https://github.com/tokyo-night/tokyo-night-vscode-theme",
  author = "Aryan Jassal",
  version = "0.2.0",
}

---@class TokyodarkColors
---@field black string
---@field red string
---@field green string
---@field yellow string
---@field blue string
---@field magenta string
---@field cyan string
---@field white string
---@field bright_white string
---@field bright_black string
---@field orange string
---@field brown string
---@field foreground string
---@field background string
---@field background_alt1 string
---@field background_alt2 string
---@field background_alt3 string
---@field background_highlight string
theme.colors = {
  -- Classic console colors
  black = "#414868",
  red = "#f7768e",
  green = "#73daca",
  yellow = "#e0af68",
  blue = "#7aa2f7",
  magenta = "#bb9af7",
  cyan = "#7dcfff",
  white = "#c0caf5",

  -- Extended colors
  bright_white = "#ffffff",
  bright_black = "#000000",
  orange = "#ff9e64",
  brown = "#634f30",

  -- Special foreground/background colors
  foreground = "#a9b1d6",
  background = "#1a1b26",
  background_alt1 = "#16161e",
  background_alt2 = "#1f2335",
  background_alt3 = "#24283b",
  background_highlight = "#292e42",
}

---@type table<string, string>
local colors = theme.colors

local gtk_palette_colors = {
  blue = colors.blue,
  green = colors.green,
  yellow = colors.yellow,
  orange = colors.orange,
  red = colors.red,
  purple = colors.magenta,
  brown = colors.brown,
  light = colors.white,
  dark = colors.black,
}

theme.gtk = {
  colors = {
    accent_color = colors.blue,
    accent_fg_color = colors.bright_white,
    accent_bg_color = colors.blue,
    window_fg_color = colors.foreground,
    window_bg_color = colors.background_alt1,
    view_fg_color = colors.foreground,
    view_bg_color = colors.background_alt1,
    headerbar_fg_color = colors.foreground,
    headerbar_bg_color = colors.background,
    card_fg_color = colors.foreground,
    card_bg_color = colors.background,
    dialog_fg_color = colors.foreground,
    dialog_bg_color = colors.background,
    popover_fg_color = colors.bright_white,
    popover_bg_color = colors.background_alt2,
    sidebar_fg_color = colors.foreground,
    sidebar_bg_color = colors.background,
    backdrop_fg_color = colors.foreground,
    backdrop_bg_color = colors.background_alt1,
  },

  palettes = {
    palette1 = gtk_palette_colors,
    palette2 = gtk_palette_colors,
    palette3 = gtk_palette_colors,
    palette4 = gtk_palette_colors,
    palette5 = gtk_palette_colors,
  },
}

theme.kitty = {
  colors = {
    background = colors.background,
    foreground = colors.foreground,
    black = colors.black,
    red = colors.red,
    green = colors.green,
    yellow = colors.yellow,
    blue = colors.blue,
    magenta = colors.magenta,
    cyan = colors.cyan,
    white = colors.white,
    bright_black = colors.black,
    bright_red = colors.red,
    bright_green = colors.green,
    bright_yellow = colors.yellow,
    bright_blue = colors.blue,
    bright_magenta = colors.magenta,
    bright_cyan = colors.cyan,
    bright_white = colors.white,
  },
}

theme.foot = {
  colors = {
    foreground = colors.foreground,
    background = colors.background,
    black = colors.black,
    red = colors.red,
    green = colors.green,
    yellow = colors.yellow,
    blue = colors.blue,
    magenta = colors.magenta,
    cyan = colors.cyan,
    white = colors.white,
    bright_black = colors.black,
    bright_red = colors.red,
    bright_green = colors.green,
    bright_yellow = colors.yellow,
    bright_blue = colors.blue,
    bright_magenta = colors.magenta,
    bright_cyan = colors.cyan,
    bright_white = colors.white,
  },
}

theme.raw = {
  scss = {
    colors = colors,
    format = "${name}: {hex};",
    header = "// {header}",
    out = "~/.cache/chroma/_chroma.scss",
  },
}

return theme
