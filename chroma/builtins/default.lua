local python = require "chroma.builtins.python"

---@class GroupTable
-- Setting this field to false will make the application treat this table as a
-- data table. Data tables can not be handled by a handler. All data tables will
-- be sent to each handler.
---@field handle boolean|nil
---@field [string] any

---@class Theme
---@field options ThemeOptions|nil
---@field meta ThemeMeta|nil
---@field colors ThemeColors|nil
---@field gtk GroupGtk|nil
---@field kitty GroupKitty|nil
---@field foot GroupFoot|nil
---@field raw GroupRaw|nil
---@field [string] GroupTable
-- This table should contain all the theming information. There are pre-defined
-- fields on this table to help guide you. All the values mentioned here are
-- optional, but represent valid themable handlers. This table can be extended
-- by adding more fields resembling the standard ones. However, no type hinting
-- exist for any user-defined handlers (yet).
local theme = {}

---@class ThemeOptions
---@field merge_tables boolean|nil
---@field chroma_version string
-- The options table provides many options that govern the application's
-- behaviour. Some options might even end up breaking the application if
-- configured incorrectly, so know what you are doing before changing any
-- option.
theme.options = {
  -- If set, the theme file will be merged with the default theme file. This has
  -- an effect of auto-populating fields with default values if they were unset.
  -- Chroma expects some fields to be defined, and leaving those fields empty
  -- either accidentally or on purpose will break the application. The default
  -- fields will only apply to the fields which were left unset by the theme.
  -- All fields defined by the theme will be left unchanged.
  merge_tables = true,

  -- This option is mandatory and must be set to a valid version string. (see
  -- https://semver.org). This dictates the version of Chroma for which the
  -- theme was designed for. If the minor version differs, then the application
  -- will print out a warning, informing users about this potential
  -- incompatibility. If there is a difference in the major versions, then
  -- an error will be raised, as major version changes usually mean breaking
  -- API changes.
  chroma_version = python.none,
}

---@class ThemeMeta
---@field name string|nil
---@field description string|nil
---@field author string|nil
---@field version string|nil
---@field url string|nil
-- The metadata table provides useful metadata to Chroma and the handlers.
-- Adding metadata to your theme is optional, but recommended. The presence of
-- metadata will not significantly alter the application's behaviour. However,
-- handlers are given access to the metadata. As such, the presence or absence
-- of metadata might impact the generated theme file.
theme.meta = {
  name = python.none,
  description = python.none,
  author = python.none,
  version = python.none,
  url = python.none,
}

---@class ThemeColors
---@type table<string, string>
-- Add types so children themes inheriting from this theme will be able to see
-- the exact defined colors. Otherwise, it would be a shot in the dark for
-- which colors are defined and which aren't. Every theme is encouraged to do
-- this for their colors, but this is not a requirement, merely a quality of
-- life feature. While writing a theme, you can do this:
-- ```lua
-- ---@class MyColors
-- ---@field color1
-- ---@field color2
-- ---@field color3
-- theme.colors = {
--   color1 = '#ffffff',
--   color2 = '#888888',
--   color3 = '#000000',
-- }
-- ```
theme.colors = {}

-- Note that the class definitions have been done in the global scope instead
-- of doing it for each sub-table. This is intentional, ensuring proper static
-- type analysis.

-- All color types are an exception to the "optional defaults" rule. The fields
-- indicated by this class are all recommended fields, but are not required by
-- the theme writer.

---@class GroupGtkColors
---@field accent_color string|nil
---@field accent_fg_color string|nil
---@field accent_bg_color string|nil
---@field window_fg_color string|nil
---@field window_bg_color string|nil
---@field view_fg_color string|nil
---@field view_bg_color string|nil
---@field headerbar_fg_color string|nil
---@field headerbar_bg_color string|nil
---@field card_fg_color string|nil
---@field card_bg_color string|nil
---@field dialog_fg_color string|nil
---@field dialog_bg_color string|nil
---@field popover_fg_color string|nil
---@field popover_bg_color string|nil
---@field sidebar_fg_color string|nil
---@field sidebar_bg_color string|nil
---@field backdrop_fg_color string|nil
---@field backdrop_bg_color string|nil
---@field [string] string

---@class GroupGtkPaletteColors
---@field blue string
---@field green string
---@field yellow string
---@field orange string
---@field red string
---@field purple string
---@field brown string
---@field light string
---@field dark string

---@class GroupGtkPalettes
---@field palette1 GroupGtkPaletteColors
---@field palette2 GroupGtkPaletteColors
---@field palette3 GroupGtkPaletteColors
---@field palette4 GroupGtkPaletteColors
---@field palette5 GroupGtkPaletteColors

---@class GroupGtkOut
---@field gtk3 string
---@field gtk4 string

---@class GroupGtk
---@field colors GroupGtkColors
---@field palettes GroupGtkPalettes
---@field sidebar_patch string|nil
---@field extra_css string|nil
---@field out GroupGtkOut|nil
theme.gtk = {
  -- There are type hints to the recommended colors, you can ignore the
  -- recommendation and go off in your world, too. You can define extra colors
  -- in this table, and they will all be included in the final stylesheet.
  colors = {},

  -- GTK additionally allows themes to set 5 extra colors as theme palettes.
  -- These can be set using the `palettes` table. In this table, you can
  -- update colors on `palette1` to `palette5` to correspond to each of the five
  -- palettes. If left unset, they will not be present in the GTK stylesheet,
  -- and might break some applications which rely on this. It is highly
  -- recommended to at least create one palette, but ideally, create all five.
  -- No default values exist for this attribute.
  palettes = {},

  -- For some reason, even after setting most of the available colors, sidebars
  -- still give me trouble. To ensure that the sidebars are correctly themed, a
  -- patch is generated. This patch is injected into the stylesheet, ensuring
  -- proper theming. If, for some reason, you don't want to use the patch, set
  -- this to an empty string to disable this.
  sidebar_patch = [[
.naviation-sidebar, .sidebar_pane, .top-bar {
  color: @sidebar_fg_color;
  background-color: @sidebar_bg_color;
}
.navigation-sidebar:backdrop, .sidebar_pane:backdrop, .top-bar:backdrop {
  color: @backdrop_fg_color;
  background-color: @backdrop_bg_color;
}]],

  -- The same theme and the same generated file is output to the location for
  -- GTK 3.0 and GTK 4.0 themes.
  out = {
    gtk3 = "~/.config/gtk-3.0/gtk.css",
    gtk4 = "~/.config/gtk-4.0/gtk.css",
  },
}

-- These options are not exhaustive for theming kitty. More options will be
-- added in the future.
---@class GroupKittyColors
---@field foreground string|nil
---@field background string|nil
---@field black string|nil
---@field red string|nil
---@field green string|nil
---@field yellow string|nil
---@field blue string|nil
---@field magenta string|nil
---@field cyan string|nil
---@field white string|nil
---@field bright_black string|nil
---@field bright_red string|nil
---@field bright_green string|nil
---@field bright_yellow string|nil
---@field bright_blue string|nil
---@field bright_magenta string|nil
---@field bright_cyan string|nil
---@field bright_white string|nil

---@class GroupKitty
---@field colors GroupKittyColors
---@field write_meta boolean|nil
---@field out string|nil
theme.kitty = {
  -- The kitty theme supports adding metadata into the actual theme. This option
  -- controls whether that metadata should be inserted or not. This metadata is
  -- obtained via the `metadata` table of the theme.
  write_meta = true,

  out = "~/.config/kitty/theme.conf",
}

-- These options are not exhaustive for theming foot. More options will be
-- added in the future.
---@class GroupFootColors
---@field foreground string|nil
---@field background string|nil
---@field selection_foreground string|nil
---@field selection_background string|nil
---@field black string|nil
---@field red string|nil
---@field green string|nil
---@field yellow string|nil
---@field blue string|nil
---@field magenta string|nil
---@field cyan string|nil
---@field white string|nil
---@field bright_black string|nil
---@field bright_red string|nil
---@field bright_green string|nil
---@field bright_yellow string|nil
---@field bright_blue string|nil
---@field bright_magenta string|nil
---@field bright_cyan string|nil
---@field bright_white string|nil

---@class GroupFoot
---@field colors GroupFootColors
---@field out string|nil
theme.foot = {
  out = "~/.config/foot/theme.ini",
}

-- You can define multiple tables for the raw handler, and each table can have
-- its own attributes. All tables will be processed separately, and each table
-- will be output to the specified output file following the specified
-- formatting. Note that each table inside the raw handler can have anything
-- for names. It doesn't matter. They are just there for convenience and
-- debugging purposes. However, DO NOT repeat names. That's bad. Very bad.
---@class GroupRawTheme
-- Of course, as usual, you can set and override colors as needed. All
-- key-value pairs from the `colors` table will be output in the file
-- following the right formating rules. No error-checking or type safety
-- checks are done here, so you are on your own.
---@field colors table<string, string>
-- This defines how each line will be formatted in the output file. Variables
-- are defined by putting their names inside {}. For example, this format will
-- result in the following output:
-- white #ffffff
-- black #000000
-- Available variables are:
-- {name}: Color name (no spaces allowed)
-- {hex}: Hexadecimal color value (with leading hashtag)
-- {hexval}: Hexadecimal color value (without leading hashtag)
---@field format string
-- Backups the file if it already exists at the target location if set.
-- There usually is little reason to disable automatic backups or warnings
-- if the target file exists, but this way we can force overwrite the
-- target file if desired.
---@field force boolean|nil
-- This format works similar to the color definition format, but instead,
-- this works on the header instead. The header tells Chroma if the file
-- was generated by the user (which we should back up), or by Chroma itself
-- (which it will overwrite without backups). The header format is
-- provided to ensure that the header will be formatted as a comment for
-- the file we are writing to.
-- Available variables are:
-- {header}: The header template, provided by Chroma
-- Set this to `nil` or `python.none` to not generate or check for a header.
-- This is not recommended.
---@field header string|nil
-- You can also expand all environment variables available to the program
-- like in the shell. DO NOT OVERWRITE THE SAME FILE AGAIN! Lua is
-- intrinsically random with table order, so it is undefined behaviour to
-- replace the same file!
---@field out string

---@class GroupRaw
---@field [string] GroupRawTheme
-- Check out the theming section in the README
-- (https://github.com/aryanjassal/chroma?tab=readme-ov-file#theming), and
-- read up on the usage of each field within the raw group.
theme.raw = {}

return theme
