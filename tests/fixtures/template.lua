local theme = require "chroma.builtins.default"

-- TODO: make this code version-independent
theme.options = {{
  chroma_version = "0.7.0",
}}

-- Inject lua integrations here from Python tests
{luaintegrations}

return theme
