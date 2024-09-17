-- Define a table for storing theme groups. Each group is the application name
-- with a table assigned to it. It can store tables. The color scheme is one
-- such table (see below for an example).
local theme = {}

-- You can also extend this by defining custom colors. Any additional colours
-- defined in theme groups will be passed to theme handlers.
local colors = {
	black = "#000000",
	red = "#ff0000",
	green = "#00ff00",
	yellow = "#ffff00",
	blue = "#0000ff",
	magenta = "#ff00ff",
	cyan = "#00ffff",
	white = "#ffffff",
}

-- You can also define variables!
local foreground = colors.white
local background = colors.black
local gtk_defaultscheme = {
	blue = nil,
	green = nil,
	yellow = nil,
	orange = nil,
	red = nil,
	purple = nil,
	brown = nil,
	light = nil,
	dark = nil,
}
local gtk_defaultset = {
	colors = theme.gtk.colors,
	colorschemes = theme.gtk.colorschemes,
	extra_css = theme.gtk.extra_css,
	sidebar_patch = theme.gtk.sidebar_patch,
}

-- Update GTK settings by changing the options in the GTK group.
theme.gtk = {
	colors = {
		accent_color = colors.blue,
		accent_fg_color = foreground,
		accent_bg_color = background,
		window_fg_color = foreground,
		window_bg_color = background,
		view_fg_color = foreground,
		view_bg_color = background,
		headerbar_fg_color = foreground,
		headerbar_bg_color = background,
		card_fg_color = foreground,
		card_bg_color = background,
		dialog_fg_color = foreground,
		dialog_bg_color = background,
		popover_fg_color = foreground,
		popover_bg_color = background,
		sidebar_fg_color = foreground,
		sidebar_bg_color = background,
	},

	-- GTK additionally allows themes to set 5 extra colors as theme palettes.
	-- That can be set using the `colorscheme` table. In this table, you can
	-- update colors on `scheme1` to `scheme5` to correspond to each of the five
	-- palettes. If left unset, they will not be present in the GTK stylesheet,
	-- and would not render. It is highly recommended to at least create one
	-- colorscheme. No default values exist for this attribute.
	colorschemes = {
		scheme1 = gtk_defaultscheme,
		scheme2 = gtk_defaultscheme,
		scheme3 = gtk_defaultscheme,
		scheme4 = gtk_defaultscheme,
		scheme5 = gtk_defaultscheme,
	},

	-- This patch is necessary to ensure sidebars are also properly themed. Why
	-- is this not hardcoded? Freedom. Get the classic, broken look by setting
	-- this patch to an empty string.
	sidebar_patch = [[
  .naviation-sidebar, .top-bar {
    color: @sidebar_fg_color;
    background-color: @sidebar_bg_color;
  }
  ]],

	-- Want to customize your experience EVEN MORE? There's an option for that.
	extra_css = nil,

	-- Both GTK3 and GTK4 attributes rely on the colors set in the GTK group.
	-- Here is where custom theming can be applied to GTK 3 and 4 separately.
	gtk3 = gtk_defaultset,
	gtk4 = gtk_defaultset,

	-- You can also customize the file the complied themes will be output to.
	-- You can include home-relative paths (~/) and they will be expanded.
	out = nil,
}

-- Update Kitty options here. This application is only concerned with color
-- themes, and will not update other UI-related config like fonts, cursors,
-- opacity, etc.
theme.kitty = {
	colors = {
		background = background,
		foreground = foreground,
		black = colors.black,
		red = colors.red,
		green = colors.green,
		yellow = colors.yellow,
		blue = colors.blue,
		magenta = colors.magenta,
		cyan = colors.cyan,
		white = colors.white,
		bright_black = theme.kitty.black,
		bright_red = theme.kitty.red,
		bright_green = theme.kitty.green,
		bright_yellow = theme.kitty.yellow,
		bright_blue = theme.kitty.blue,
		bright_magenta = theme.kitty.magenta,
		bright_cyan = theme.kitty.cyan,
		bright_white = theme.kitty.white,
	},

	-- You can also customize the file the complied themes will be output to.
	-- You can include home-relative paths (~/) and they will be expanded.
	out = nil,
}

-- Output the colors to a file in a way which can be used by other programs. You
-- have full control over the formatting of the file to ensure it is maximally
-- usable with your needs. Although, to establish a standard, a default format
-- is provided.
theme.raw = {
	-- Of course, as usual, you can set and override colors as needed.
	colors = colors,

	-- This defines how each line will be formatted in the output file. Variables
	-- are defined by putting their names inside {}. For example, this format will
	-- result in the following output:
	-- white #ffffff
	-- black #000000
	-- Available variables are:
	-- {name}: Color name (no spaces allowed)
	-- {hexcode}: Hexadecimal color value (with leading hashtag)
	-- {hexvalue}: Hexadecimal color value (without leading hashtag)
	format = "{name} {hexcode}",

	-- You can also customize the file the complied themes will be output to. You
  -- can include home-relative paths (~/) and they will be expanded.
	out = "~/.cache/chroma/colors.col",
}

return theme
