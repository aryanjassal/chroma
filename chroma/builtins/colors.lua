local api = require "chroma.builtins.api"

-- Helper function to help create transform methods
local function create_transform(fn, ...)
  local args = { ... }
  return function(input_color)
    return fn(input_color, table.unpack(args))
  end
end

local colors = {}

-- The colors.transform contains methods which expects the program to generate
-- the color. Instead, the transforms only set the transformation the color will
-- experience. The underlying program needs to call the return value with the
-- target color(s) as an argument.
colors.transform = {
  noop = function()
    return create_transform(function(color)
      return color
    end)
  end,

  darken = function(amount)
    return create_transform(api.darken, amount)
  end,

  lighten = function(amount)
    return create_transform(api.lighten, amount)
  end,

  saturate = function(amount)
    return create_transform(api.saturate, amount)
  end,

  desaturate = function(amount)
    return create_transform(api.desaturate, amount)
  end,
}

return colors
