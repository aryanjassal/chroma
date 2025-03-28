-- Make sure APIs are defined in the global scope properly.
local assert_api = function(name)
  if _G[name] == nil then
    error("Required state '" .. name .. "' is unset")
  end
  return _G[name]
end

local api = {}

-- All paths prefixed with a '__' are internal paths. Don't use them.

api.darken = function(color, amount)
  local method = assert_api "__darken"
  return method(color, amount)
end

api.lighten = function(color, amount)
  local method = assert_api "__lighten"
  return method(color, amount)
end

api.saturate = function(color, amount)
  local method = assert_api "__saturate"
  return method(color, amount)
end

api.desaturate = function(color, amount)
  local method = assert_api "__desaturate"
  return method(color, amount)
end

api.blend = function(color1, color2, ratio)
  local method = assert_api "__blend"
  return method(color1, color2, ratio)
end

api.set_h = function(color, amount)
  local method = assert_api "__set_hue"
  return method(color, amount)
end

api.set_s = function(color, amount)
  local method = assert_api "__set_saturation"
  return method(color, amount)
end

api.set_l = function(color, amount)
  local method = assert_api "__set_luminance"
  return method(color, amount)
end

return api
