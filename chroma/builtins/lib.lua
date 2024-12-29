local python = require("chroma.builtins.python")

-- Ensure expected global variables exist
use_generated = use_generated or nil
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

-- Takes in a condition set for hue, saturation, and luminance and returns a
-- python-compatible array for the HSL map values. This method is mostly present
-- for code cleanliness, so this can be completely omitted if you know what you
-- are doing.
-- TODO: Check for nils in nested tables
function lib.hslmap_condition(h, s, l)
  -- Replace nil with python.none
  if h == nil then
    h = python.none
  end
  if s == nil then
    s = python.none
  end
  if l == nil then
    l = python.none
  end

  return {h, s, l}
end

-- function lib.hslmap_value(mode, condition)
--   return {mode, condition}
-- end

return lib
