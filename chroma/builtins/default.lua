local theme = {}

-- Silence the LSP. The value for `python.none` gets converted to `None` when
-- processing the lua file, and `nil` skips the parameters instead.
local python = {}

theme.options = {
  merge_tables = true,
}

theme.meta = {
  chroma_version = python.none,
  name = python.none,
  description = python.none,
  author = python.none,
  version = python.none,
  url = python.none,
}

theme.gtk = {
  sidebar_patch = [[
.naviation-sidebar, .sidebar_pane, .top-bar {
  color: @sidebar_fg_color;
  background-color: @sidebar_bg_color;
}
.navigation-sidebar:backdrop, .sidebar_pane:backdrop, .top-bar:backdrop {
  color: @backdrop_fg_color;
  background-color: @backdrop_bg_color;
}]],

  out = {
    gtk3 = "~/.config/gtk-3.0/gtk.css",
    gtk4 = "~/.config/gtk-4.0/gtk.css",
  },
}

theme.kitty = {
  out = "~/.config/kitty/theme.conf",
}

theme.foot = {
  out = "~/.config/foot/theme.ini",
}

return theme, python
