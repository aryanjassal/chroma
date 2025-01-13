local api = {}

api.assert_api = function(name)
  if _G[name] == nil then
    error("Required state '" .. name .. "' is unset")
  end
end

return api
