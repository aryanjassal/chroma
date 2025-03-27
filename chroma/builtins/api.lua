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

return api
