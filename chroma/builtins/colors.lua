darken = darken or nil
lighten = lighten or nil
saturate = saturate or nil
desaturate = desaturate or nil
if darken == nil then error("Required state darken is unset") end
if lighten == nil then error("Required state lighten is unset") end
if saturate == nil then error("Required state saturate is unset") end
if desaturate == nil then error("Required state desaturate is unset") end

-- Helper function to help create transform methods
local function create_transform(fn, ...)
  local args = {...}
  return function (input_color)
    return fn(input_color, table.unpack(args))
  end
end

local colors = {}

-- The colors.transform contains methods which expects the program to generate
-- the color. Instead, the transforms only set the transformation the color will
-- experience. The underlying program needs to call the return value with the
-- target color(s) as an argument.
colors.transform = {
  noop = function ()
    return create_transform(function (col) return col end)
  end,

  darken = function (amount)
    -- return create_transform(chroma.colors.methods.darken, amount)
    return create_transform(darken, amount)
  end,

  lighten = function (amount)
    -- return create_transform(chroma.colors.methods.lighten, amount)
    return create_transform(lighten, amount)
  end,

  saturate = function (amount)
    -- return create_transform(chroma.colors.methods.saturate, amount)
    return create_transform(saturate, amount)
  end,

  desaturate = function (amount)
    -- return create_transform(chroma.colors.methods.desaturate, amount)
    return create_transform(desaturate, amount)
  end,
}

return colors
