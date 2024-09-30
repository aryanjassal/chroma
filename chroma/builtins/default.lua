-- Define a table for storing theme groups. Each group is the application name
-- with a table assigned to it. It can store tables. The color scheme is one
-- such table (see below for an example).
-- Note that you should import the default table when writing your own themes.
-- [[ local theme = require("chroma.builtins.default") ]]
-- This would ensure that any fields you haven't filled in will be set to a
-- default value.
local theme = {}

-- These options control the behaviour of theme generation. Know what you are
-- doing before chaging any option here.
theme.options = {
	-- By default, the theme generator merges the table with the default table.
	-- This ensures doing something like this:
	-- [[ themes.gtk { colors = { red = "#ff0000", } } ]]
	-- Would not result in other values being nil. To disable this behaviour, set
	-- this flag to false.
	merge_tables = true,
}

-- Of course we need a metadata table.
theme.meta = {
	-- This specifies the Chroma version for which the theme was written for. If
	-- the theme is designed for a different version of Chroma, then Chroma will
	-- give you a warning. Most likely, older theme versions will just crash while
	-- applying the theme. Must be defined like: "1.0.0" where there are three
	-- numbers separated by two periods. See https://semver.org/.
	chroma_version = "",

	-- These fields are the metadata of the actual theme. They need to be filled
	-- out manually, but the fields are optional.
	name = "",
	description = "",
	author = "",
	version = "",
	url = "",
}

-- -- You can also extend this by defining custom colors. Any additional colours
-- -- defined in theme groups will be passed to theme handlers.
-- local colors = {
-- 	black = "#000000",
-- 	red = "#ff0000",
-- 	green = "#00ff00",
-- 	yellow = "#ffff00",
-- 	blue = "#0000ff",
-- 	magenta = "#ff00ff",
-- 	cyan = "#00ffff",
-- 	white = "#ffffff",
-- }

-- -- You can also define variables. Note that any defined variables or functions
-- -- will be discarded, and only the values in the returned table will be
-- -- processed.
-- local foreground = colors.white
-- local background = colors.black
-- local gtk_defaultpalette = {
-- 	blue = nil,
-- 	green = nil,
-- 	yellow = nil,
-- 	orange = nil,
-- 	red = nil,
-- 	purple = nil,
-- 	brown = nil,
-- 	light = nil,
-- 	dark = nil,
-- }

-- -- Update GTK settings by changing the options in the GTK group.
-- theme.gtk = {
-- 	colors = {
-- 		accent_color = colors.blue,
-- 		accent_fg_color = foreground,
-- 		accent_bg_color = colors.blue,
-- 		window_fg_color = foreground,
-- 		window_bg_color = background,
-- 		view_fg_color = foreground,
-- 		view_bg_color = background,
-- 		headerbar_fg_color = foreground,
-- 		headerbar_bg_color = background,
-- 		card_fg_color = foreground,
-- 		card_bg_color = background,
-- 		dialog_fg_color = foreground,
-- 		dialog_bg_color = background,
-- 		popover_fg_color = foreground,
-- 		popover_bg_color = background,
-- 		sidebar_fg_color = foreground,
-- 		sidebar_bg_color = background,
-- 		backdrop_fg_color = background,
-- 		backdrop_bg_color = background,
-- 	},
--
-- 	-- GTK additionally allows themes to set 5 extra colors as theme palettes.
-- 	-- That can be set using the `colorscheme` table. In this table, you can
-- 	-- update colors on `scheme1` to `scheme5` to correspond to each of the five
-- 	-- palettes. If left unset, they will not be present in the GTK stylesheet,
-- 	-- and would not render. It is highly recommended to at least create one
-- 	-- colorscheme. No default values exist for this attribute.
-- 	palettes = {
-- 		palette1 = gtk_defaultpalette,
-- 		palette2 = gtk_defaultpalette,
-- 		palette3 = gtk_defaultpalette,
-- 		palette4 = gtk_defaultpalette,
-- 		palette5 = gtk_defaultpalette,
-- 	},
--
-- 	-- This patch is necessary to ensure sidebars are also properly themed. Why
-- 	-- is this not hardcoded? Freedom. Get the classic, broken look by setting
-- 	-- this patch to an empty string.
-- 	sidebar_patch = [[
-- .naviation-sidebar, .sidebar_pane, .top-bar {
--   color: @sidebar_fg_color;
--   background-color: @sidebar_bg_color;
-- }
-- .navigation-sidebar:backdrop, .sidebar_pane:backdrop, .top-bar:backdrop {
--   color: @backdrop_fg_color;
--   background-color: @backdrop_bg_color;
-- }
--   ]],
--
-- 	-- Want to customize your experience EVEN MORE? There's an option for that.
-- 	extra_css = "",
--
-- 	-- You can also customize the file the complied themes will be output to.
-- 	-- You can include home-relative paths (~/) and they will be expanded.
-- 	out = {
-- 		gtk3 = "~/.config/gtk-3.0/gtk.css",
-- 		gtk4 = "~/.config/gtk-4.0/gtk.css",
-- 	},
-- }

-- Actual defaults for the GTK handler
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

-- -- Update Kitty options here. This application is only concerned with color
-- -- themes, and will not update other UI-related config like fonts, cursors,
-- -- opacity, etc.
-- theme.kitty = {
-- 	colors = {
-- 		background = background,
-- 		foreground = foreground,
-- 		black = colors.black,
-- 		red = colors.red,
-- 		green = colors.green,
-- 		yellow = colors.yellow,
-- 		blue = colors.blue,
-- 		magenta = colors.magenta,
-- 		cyan = colors.cyan,
-- 		white = colors.white,
-- 		bright_black = colors.black,
-- 		bright_red = colors.red,
-- 		bright_green = colors.green,
-- 		bright_yellow = colors.yellow,
-- 		bright_blue = colors.blue,
-- 		bright_magenta = colors.magenta,
-- 		bright_cyan = colors.cyan,
-- 		bright_white = colors.white,
-- 	},
--
-- 	-- You can also customize the file the complied themes will be output to.
-- 	-- You can include home-relative paths (~/) and they will be expanded.
-- 	out = "~/.config/kitty/theme.conf",
-- }

-- Actual defaults for the Kitty handler
theme.kitty = {
	out = "~/.config/kitty/theme.conf",
}

-- -- Output the colors to a file in a way which can be used by other programs. You
-- -- have full control over the formatting of the file to ensure it is maximally
-- -- usable with your needs. Although, to establish a standard, a default format
-- -- is provided.
-- theme.raw = {
-- 	-- You can define multiple tables for the raw handler, and each table can have
-- 	-- its own attributes. All tables will be processed separately, and each table
-- 	-- will be output to the specified output file following the specified
-- 	-- formatting. The name here doesn't really matter that much; it's just a way
-- 	-- of grouping each raw output.
-- 	scss = {
-- 		-- Of course, as usual, you can set and override colors as needed. All
-- 		-- key-value pairs from the `colors` table will be output in the file
-- 		-- following the right formating rules. No error-checking or type safety
-- 		-- checks are done here, so you are on your own.
-- 		colors = colors,
--
-- 		-- This defines how each line will be formatted in the output file. Variables
-- 		-- are defined by putting their names inside {}. For example, this format will
-- 		-- result in the following output:
-- 		-- $white: #ffffff;
-- 		-- $black: #000000;
-- 		-- Available variables are:
-- 		-- {name}: Color name (no spaces allowed)
-- 		-- {hexcode}: Hexadecimal color value (with leading hashtag)
-- 		-- {hexvalue}: Hexadecimal color value (without leading hashtag)
-- 		format = "${name}: {hexcode};",
--
-- 		-- You also need to define the format of comments in this format. The
-- 		-- comment will be used to input a header into the file, which marks the
-- 		-- file as a Chroma-generated file. This header will allow Chroma to
-- 		-- overwrite the file without backing it up.
-- 		-- Set this to nil to not add any comments. Note that you also need to
-- 		-- disable automatic backup to overwrite any file at that location.
-- 		-- Available variables are:
-- 		-- {header}: An automatically generated header by Chroma.
-- 		header = "// {header}",
--
-- 		-- Disable this option to prevent backing up the target file if it already
-- 		-- exists. Be careful, as once deleted, files are impossible to recover.
-- 		perform_backup = true,
--
-- 		-- You can also expand all environment variables available to the program
-- 		-- like in the shell. Extra variables have also been added, including:
-- 		-- $CACHEDIR: The cache directory for Chroma, usually `~/.cache/chroma`
-- 		out = "~/.cache/chroma/_chroma.scss",
-- 	},
-- }

return theme
