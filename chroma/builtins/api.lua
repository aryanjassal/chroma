-- Make sure APIs are defined in the global scope properly.
local assert_api = function(name)
  if _G[name] == nil then
    error("Required state '" .. name .. "' is unset")
  end
end

-- All paths prefixed with a '__' are internal paths. Don't use them.
local _darken = assert_api "__chroma_darken"
local _lighten = assert_api "__chroma_lighten"
local _saturate = assert_api "__chroma_saturate"
local _desaturate = assert_api "__chroma_desaturate"

local api = {}

api.darken = _darken
api.lighten = _lighten
api.saturate = _saturate
api.desaturate = _desaturate

return api
