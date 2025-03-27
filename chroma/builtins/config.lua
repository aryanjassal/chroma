local api = require "chroma.builtins.api"
local lib = require "chroma.builtins.lib"
local colors = require "chroma.builtins.colors"
local python = require "chroma.builtins.python"

local config = {}

-- Set the allowable apps that will be themed by chroma.
-- TODO: needs rename for allowed integrations
config.integrations = {
  themable = { "gtk", "kitty" },
}

-- Modify the behavior of chroma.
config.behavior = {
  missing_local_integration = "IGNORE",
  missing_theme_integration = "IGNORE",
}

-- Modify the conditions for the generator and what it considers a color.
-- Changing these values will affect the resultant output of the generator
-- in potentially unpredictable ways. Use with caution.
config.generators = {
  --[[
    The HSL map controls what chroma thinks a particular color is. This is used
    only for inferencing colors from an image, and not all colors are obtained
    this way. For example, the bright counterparts of each normal color is
    generated in `generator_modes` (name TBD). Each condition in a HSL map
    follows the following syntax.

      1. One or more pairs of two values for the hue component.
      2. One pair of two values for the saturation component.
      3. One pair of two values for the luminance component.

    The first number signifies the lower bound and the second number the upper
    bound. A `python.none` means no restriction, and any values will match the
    condition. Don't use `nil` as that has different meanings in this context.
    The resultant colors will remain clamped between these values during color
    generation. Currently, post-processing these colors isn't supported.
    TODO: add color post-processing
  ]]
  hslmap = {
    accent = lib.hslmap_condition(python.none, { 60, 100 }, { 50, 90 }),
    black = lib.hslmap_condition(python.none, python.none, { 5, 20 }),
    white = lib.hslmap_condition(python.none, python.none, { 80, 95 }),
    background = lib.hslmap_condition(python.none, { 0, 20 }, { 5, 10 }),
    foreground = lib.hslmap_condition(python.none, { 0, 20 }, { 90, 95 }),
    red = lib.hslmap_condition({ { 0, 35 }, { 325, 360 } }, { 40, 90 }, { 30, 90 }),
    orange = lib.hslmap_condition({ 35, 75 }, { 30, 90 }, { 40, 80 }),
    brown = lib.hslmap_condition({ 35, 75 }, { 30, 70 }, { 20, 70 }),
    yellow = lib.hslmap_condition({ 65, 105 }, { 40, 90 }, { 30, 90 }),
    green = lib.hslmap_condition({ 100, 160 }, { 40, 90 }, { 30, 90 }),
    blue = lib.hslmap_condition({ 200, 230 }, { 40, 50 }, { 40, 60 }),
    cyan = lib.hslmap_condition({ 170, 200 }, { 40, 90 }, { 40, 90 }),
    magenta = lib.hslmap_condition({ 280, 310 }, { 30, 50 }, { 30, 50 }),
  },

  --[[
    There are multiple modes which modify the behavior of color generation.
    They are present to allow for differences in the calculation of the normal
    colors and their bright counterparts, for example. Look at the type
    signature to see the expected input type for each mode. Each value in the
    mode is a function which takes at least one parameter - an input color, and
    returns a single color as its output. The function may take more parameters
    and can do an arbitrary amount of processing, like chaining transforms.

    To perform complex chaining, rely on the exposed functions under 
    `chroma.builtins.api`. These functions refer back to the python code and is
    likely to be more useful for complex cases.
  ]]

  -- NOTE: Make sure to define `accent`, `black`, and `white` before using any
  -- other generators, as many of then require these colors to be set beforehand.
  -- TODO: order/priority/pass terminology?
  colors = {
    accent = {
      generator = "from_color",
      args = {
        source = "prominent",
        transform = function(color)
          return api.saturate(color, 0.1)
        end,
      },
      pass = 1,
    },
    black = {
      generator = "from_color",
      args = {
        source = "prominent",
        transform = function(color)
          local prominent = color
          color = api.darken(color, 0.4)
          color = api.blend(color, prominent, 0.2)
          color = api.lighten(color, 0.4)
          color = api.blend(color, prominent, 0.1)
          return color
        end,
      },
      pass = 1,
    },
    white = {
      generator = "from_color",
      args = {
        source = "prominent",
        transform = function(color)
          local prominent = color
          color = api.lighten(color, 0.4)
          color = api.blend(color, prominent, 0.2)
          color = api.darken(color, 0.4)
          color = api.blend(color, prominent, 0.1)
          return color
        end,
      },
      pass = 1,
    },
    accent_bg = {
      generator = "from_color",
      args = {
        source = "accent",
        transform = function(color)
          color = api.desaturate(color, 0.2)
          color = api.darken(color, 0.1)
          return color
        end,
      },
    },
    accent_fg = {
      generator = "from_color",
      args = {
        source = "white",
        transform = function(color)
          color = api.lighten(color, 0.15)
          return color
        end,
      },
    },
    bright_black = {
      generator = "from_color",
      args = {
        source = "black",
        transform = function(color)
          return api.lighten(color, 0.1)
        end,
      },
    },
    bright_white = {
      generator = "from_color",
      args = {
        source = "white",
        transform = function(color)
          return api.lighten(color, 0.1)
        end,
      },
    },
    foreground = { generator = "foreground", args = { lightness = 0.08 } },
    foreground_alt = { generator = "foreground", args = { lightness = 0.1 } },
    foreground_unfocus = { generator = "foreground", args = { lightness = 0.12 } },
    background = { generator = "background", args = { darkness = 0.08 } },
    background_alt = { generator = "background", args = { darkness = 0.1 } },
    background_unfocus = { generator = "background", args = { darkness = 0.12 } },
    red = { generator = "norm", args = { base = "#ff0000" } },
    orange = { generator = "norm", args = { base = "#ff8800" } },
    brown = { generator = "norm", args = { base = "#884400" } },
    yellow = { generator = "norm", args = { base = "#ffff00" } },
    green = { generator = "norm", args = { base = "#00ff00" } },
    blue = { generator = "norm", args = { base = "#0000ff" } },
    cyan = { generator = "norm", args = { base = "#00ffff" } },
    magenta = { generator = "norm", args = { base = "#ff00ff" } },
    bright_red = { generator = "bright", args = { base = "#ff0000" } },
    bright_orange = { generator = "bright", args = { base = "#ff8800" } },
    bright_brown = { generator = "bright", args = { base = "#884400" } },
    bright_yellow = { generator = "bright", args = { base = "#ffff00" } },
    bright_green = { generator = "bright", args = { base = "#00ff00" } },
    bright_blue = { generator = "bright", args = { base = "#0000ff" } },
    bright_cyan = { generator = "bright", args = { base = "#00ffff" } },
    bright_magenta = { generator = "bright", args = { base = "#ff00ff" } },
  },
}

return config
