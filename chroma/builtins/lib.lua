if use_generated == nil then
  error("Required state 'use_generated' is unset")
end

---@class Lib
local lib = {}

---@param theme_colors ThemeColors
---@return ThemeColors
-- Takes in the theme's default color palette, and returns that. However, if
-- an autogenerated palette exists, then the generated palette is returned
-- instead.
function lib.generated_or(theme_colors)
  local success, generated_colors = pcall(require, "chroma.palettes.generated")
  if success
    and use_generated
    and type(generated_colors) == "table"
    and next(generated_colors) ~= nil
  then
    return generated_colors
  else
    return theme_colors
  end
end

return lib
