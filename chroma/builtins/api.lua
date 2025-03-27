-- Make sure APIs are defined in the global scope properly.
local assert_api = function(name)
  if _G[name] == nil then
    error("Required state '" .. name .. "' is unset")
  end
  return _G[name]
end

local api = {}

-- All paths prefixed with a '__' are internal paths. Don't use them.
api.darken = assert_api "__darken"
api.lighten = assert_api "__lighten"
api.saturate = assert_api "__saturate"
api.desaturate = assert_api "__desaturate"
api.blend = assert_api "__blend"

return api
