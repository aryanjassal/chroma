-- This module is mostly to return an empty table to silence LSP warnings
-- regarding missing import for `python`. In `lupa` (the lua framework
-- being used by this application), `python.none` actually tells it to
-- return a value of python's None instead of lua's nil, which has a
-- different meaning of a field not existing.

return {
  none = {},
}
