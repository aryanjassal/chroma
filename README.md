# Chroma

Use a single command to theme your entire system.

Why does this exist, you ask? I wasn't happy with how other theming applications worked. Granted, "other" means only three applications: [Gradience](https://github.com/GradienceTeam/Gradience), [Pywal](https://github.com/dylanaraps/pywal), and [Chameleon](https://github.com/GideonWolfe/Chameleon). I know two of those applications are archived, and the third one relies on one of the archived application. But still. I don't like that.

And, what started off as a simple script to take in a lua file theme file and write it to some set applications' configuration became this. It's like you were trying to build a sand castle on the beach, but you somehow end up building Rome within a day. Crazy things.

## Installation

To launch Chroma in development mode, simply enter a `nix develop` shell. It will automatically install it locally in edit mode, allowing you to test out or edit the program while retaining access to the command itself.

```console
[aryanj@laptop:~]$ git clone https://github.com/aryanjassal/chroma.git
Cloning into 'chroma'...
remote: Enumerating objects: 58, done.
remote: Counting objects: 100% (58/58), done.
remote: Compressing objects: 100% (35/35), done.
remote: Total 58 (delta 22), reused 49 (delta 16), pack-reused 0 (from 0)
Receiving objects: 100% (58/58), 31.91 KiB | 1.68 MiB/s, done.
Resolving deltas: 100% (22/22), done.

[aryanj@laptop:~]$ cd chroma

[aryanj@laptop:~/chroma]$ nix develop
```

Currently, Chroma is well-supported in Nix. To install for Nix, update home manager's flake file to have Chroma as an input, and add the following as a package (assuming you have `inputs` and `system` passed through from the flake to the actual module). Currently, a home manager module **does not exist**, but it is planned.

```nix
home.packages = [
    ...
    inputs.chroma.packages.${system}.default
    ...
]
```

For other, _normal_ distros with mutable filesystem, simply install this into your system-wide `pip` installation after cloning the repository. Almost all distros now disallow directly interacting with the system-wide python environment because you can break things. But I haven't released an actual package to PyPi or other package registries yet, so this is the only way for regular distros to gain access to this command.

```console
[aryanj@laptop:~]$ git clone https://github.com/aryanjassal/chroma.git
Cloning into 'chroma'...
remote: Enumerating objects: 58, done.
remote: Counting objects: 100% (58/58), done.
remote: Compressing objects: 100% (35/35), done.
remote: Total 58 (delta 22), reused 49 (delta 16), pack-reused 0 (from 0)
Receiving objects: 100% (58/58), 31.91 KiB | 1.68 MiB/s, done.
Resolving deltas: 100% (22/22), done.

[aryanj@laptop:~]$ cd chroma

[aryanj@laptop:~/chroma]$ pip install .
```

I personally don't use normal distros, so I can't really test this out myself. If someone has an issue, post it up. Even better if someone has a solution!

## Usage

Chroma is a command line tool. This means that you must interact with the _terminal_ (oo, scary!).

To load a theme, simply run the following command. It will load a theme at the given location, and print out a bunch of logs. By default, currently, it prints out everything including debug logs. Verbosity flags will be added in the future.

```console
[aryanj@laptop:~]$ chroma load path/to/theme.lua [--override path/to/override.lua]
```

That's it! This will load the theme and run it through the handlers. If the target file already exists, the handler will attempt to back up the file automatically. If the backup fails, then you would have to manually back the file up. Chroma checks if a particular header exists in the file. If it does, that means that the file was generated by Chroma, and it can freely edit/modify the file.

In case the header changes in the future, all the old themes would need to be removed. Most likely a command will exist at that time, which will iterate over the theme and remove all output files generated by Chroma.

To generate colors from an image (it will usually be your wallpaper) and apply that as your new color palette, you can use this command to do so. Remember, however, that the colors this command generates aren't always the best, and if you solely rely on this, you might end up with weird theme or artifacts. This option is currently under heavy development, so you need to specify the `--experimental` flag to use this feature anyways.

```console
[aryanj@laptop:~]$ chroma generate --experimental path/to/image.img [--output path/to/generated/theme.lua] [--override path/to/override.lua]
```

This command will automatically generate a lua theme file with your wallpaper and save it to the desired path (the cache directory by default). The command will not generate any metadata or anything fancy. These are just plain colors and themes. Also, make sure that you have `imagemagick` installed on your system before you run the generation command. It is already present for Nix users in both the development shell and after building if installed as a program.

## Theming

> [!IMPORTANT]
> To theme GTK apps, please install the `adw-gtk3` theme from [here](https://github.com/lassekongo83/adw-gtk3). Without this installed, the GTK theme will fail to apply.

> [!IMPORTANT]
> GTK is known for not being friendly to theming. As such, no formal API for theming is exposed. This means that, while many apps will be themed, many will still remain unthemed or in a broken state. Some cases will be impossible to resolve, but some might be oversights/mistakes. If you see one such issue, then please report it.
>
> Other handlers also might have similar issues, as you might use features which I never use, so I never implemented theming for it. If such cases arise, feel free to raise an issue about it.

```lua
-- Define a table for storing theme groups. Each group is the application name
-- with a table assigned to it. It can store tables. The color scheme is one
-- such table (see below for an example).
-- Note that you should import the default table when writing your own themes.
-- This would ensure that any fields you haven't filled in will be set to a
-- default value. This is not necessary as the options are merged with the
-- default table anyways (see `theme.options` below), but you might get
-- hard to debug bugs without this, so its good practice to include it.
-- Here, we also include `python`. It is an empty table whose sole purpose is
-- to silence LSP errors when using `python.none` to signify a `None` value
-- to the Python backend. Otherwise, a bunch of warnings will be generated
-- and I hate that. If you don't need to use `python.none`, just don't include
-- it.
local theme = require "chroma.bultins.default"
local python = require "chroma.builtins.python"

-- This contains many utility functions for theming, especially one for setting
-- colors if an autogenerated palette exists.
local lib = require "chroma.builtins.lib"

-- These options control the behaviour of theme generation. Know what you are
-- doing before chaging any option here, as you most likely don't want to be
-- changing anything here.
theme.options = {
  -- This specifies the Chroma version for which the theme was written for. If
  -- the theme is designed for a different version of Chroma, then Chroma will
  -- give you a warning. Most likely, older theme versions will just crash while
  -- applying the theme. Must be defined like: "1.0.0" where there are three
  -- numbers separated by two periods. See https://semver.org/.
  chroma_version = "1.0.0",

  -- By default, the theme generator merges the table with the default table.
  -- This ensures doing something like this:
  -- [[ themes.gtk { colors = { red = "#ff0000", } } ]]
  -- Would not result in other values, like the default out file, being nil.
  -- To disable this behaviour, set this flag to false.
  merge_tables = true,
}

-- Of course we need metadata.
theme.meta = {
  -- These fields are the metadata of the actual theme. They need to be filled
  -- out manually, but the fields are optional. Note that we have two version
  -- fields, `chroma_version` and `version`. The `chroma_version` field is the
  -- important one as that impacts the behaviour of Chroma based on the expected
  -- version and actual version. The `version` in metadata is the version of the
  -- actual theme.
  -- All parameters within the meta table are purely cosmetic and shouldn't
  -- seriously impact the behaviour of Chroma.
  name = "Example",
  description = "This is an example config",
  author = "Chroma",
  version = "0.0.1",
  url = "https://github.com/aryanjassal/chroma",
}

-- You can also extend this by defining custom colors. Any additional colours
-- defined in theme groups will be passed to theme handlers. Some handlers
-- accept multiple themes, while some need a strict set of keys. Set the keys
-- manually for each handler when you can. If an autogenerated palette does
-- not exist, then use the given colors. Otherwise, the theme colors are
-- used instead.
theme.colors = lib.generated_or({
  black = "#000000",
  red = "#ff0000",
  green = "#00ff00",
  yellow = "#ffff00",
  blue = "#0000ff",
  magenta = "#ff00ff",
  cyan = "#00ffff",
  white = "#ffffff",
})

local colors = theme.colors

-- You can also define variables. Note that any defined variables or functions
-- will be discarded, and only the values in the returned table will be
-- processed by Chroma.
local foreground = colors.white
local background = colors.black

-- See, this is where the definition of `python.none` can come in handy.
-- Basically, replace all references to `nil` for lua to `python.none` for
-- Python compatibility.
local gtk_defaultpalette = {
  blue = python.none,
  green = python.none,
  yellow = python.none,
  orange = python.none,
  red = python.none,
  purple = python.none,
  brown = python.none,
  light = python.none,
  dark = python.none,
}

-- Update GTK settings by changing the options in the GTK group.
theme.gtk = {
  colors = {
    accent_color = colors.blue,
    accent_fg_color = foreground,
    accent_bg_color = colors.blue,
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
    backdrop_fg_color = background,
    backdrop_bg_color = background,
  },

  -- GTK additionally allows themes to set 5 extra colors as theme palettes.
  -- That can be set using the `palettes` table. In this table, you can
  -- update colors on `palette1` to `palette5` to correspond to each of the five
  -- palettes. If left unset, they will not be present in the GTK stylesheet,
  -- and would not render. It is highly recommended to at least create one
  -- palette, but ideally, create all five. No default values exist for this
  -- attribute.
  palettes = {
    palette1 = gtk_defaultpalette,
    palette2 = gtk_defaultpalette,
    palette3 = gtk_defaultpalette,
    palette4 = gtk_defaultpalette,
    palette5 = gtk_defaultpalette,
  },

  -- We have a patch to ensure libadwaita sidebars are also properly themed. Why
  -- is this not hardcoded? Freedom. Get the classic, broken look by setting
  -- this patch to an empty string like this.
  -- sidebar_patch = ""

  -- Want to customize your experience EVEN MORE? There's an option for that.
  -- Inject custom CSS into the css files to change behaviour in interesting
  -- ways.
  extra_css = "",

  -- You can also customize the file the complied themes will be output to. You
  -- can include home-relative paths (~/) and they will be expanded. As of now,
  -- the content output to gtk3 and gtk4 are not separated. The same css file
  -- will be written for both gtk versions. This might change in the future.
  out = {
    gtk3 = "~/.config/gtk-3.0/gtk.css",
    gtk4 = "~/.config/gtk-4.0/gtk.css",
  },
}

-- Update kitty options here. This application is only concerned with color
-- themes, and will not update other UI-related config like fonts, cursors,
-- opacity, etc. so don't try to include them.
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
    bright_black = colors.black,
    bright_red = colors.red,
    bright_green = colors.green,
    bright_yellow = colors.yellow,
    bright_blue = colors.blue,
    bright_magenta = colors.magenta,
    bright_cyan = colors.cyan,
    bright_white = colors.white,
  },

  -- You can also customize the file the complied themes will be output to. You
  -- can include home-relative paths (~/) and they will be expanded. Here, the
  -- output file is actually not `kitty.conf`. You would need to import the
  -- theme in kitty using the `include` directive.
  out = "~/.config/kitty/theme.conf",
}

-- Output the colors to a file in a way which can be used by other programs. You
-- have full control over the formatting of the file to ensure it is maximally
-- usable with your needs.
theme.raw = {
  -- You can define multiple tables for the raw handler, and each table can have
  -- its own attributes. All tables will be processed separately, and each table
  -- will be output to the specified output file following the specified
  -- formatting. Note that each table inside the raw handler can have anything
  -- for names. It doesn't matter. They are just there for convenience and
  -- debugging purposes. However, DO NOT repeat names. That's bad. Very bad.
  spaced = {
    -- Of course, as usual, you can set and override colors as needed. All
    -- key-value pairs from the `colors` table will be output in the file
    -- following the right formating rules. No error-checking or type safety
    -- checks are done here, so you are on your own.
    colors = colors,

    -- This defines how each line will be formatted in the output file. Variables
    -- are defined by putting their names inside {}. For example, this format will
    -- result in the following output:
    -- white #ffffff
    -- black #000000
    -- Available variables are:
    -- {name}: Color name (no spaces allowed)
    -- {hex}: Hexadecimal color value (with leading hashtag)
    -- {hexval}: Hexadecimal color value (without leading hashtag)
    format = "{name} {hex}",

    -- Backups the file if it already exists at the target location if set.
    -- There usually is little reason to disable automatic backups or warnings
    -- if the target file exists, but this way we can force overwrite the
    -- target file if desired.
    force = false,

    -- This format works similar to the color definition format, but instead,
    -- this works on the header instead. The header tells Chroma if the file
    -- was generated by the user (which we should back up), or by Chroma itself
    -- (which it will overwrite without backups). The header format is
    -- provided to ensure that the header will be formatted as a comment for
    -- the file we are writing to.
    -- Available variables are:
    -- {header}: The header template, provided by Chroma
    -- Set this to `nil` or `python.none` to not generate or check for a header.
    -- This is not recommended.
    header = "# {header}"

    -- You can also expand all environment variables available to the program
    -- like in the shell. DO NOT OVERWRITE THE SAME FILE AGAIN! Lua is
    -- intrinsically random with table order, so it is undefined behaviour to
    -- replace the same file!
    out = "~/cache/chroma/colors.col",
  },

  -- Similarly, another handler for sass colors is also provided to get the hang of
  -- the formatting.
  scss = {
    colors = colors,
    out = "~/cache/chroma/_colors.scss",
    header = "// {header}"

    -- This format will result in the following output:
    -- $white: #ffffff;
    -- $black: #000000;
    format = "${name}: {hex};",
  },
}

-- You need to return the theme table at the end. Without this, Chroma can't see
-- any theme data.
return theme
```

## Overrides

We can create themes, sure. But, what if I have my configuration files saved somewhere else? Or you want particular colors in GTK's palette 5? This is where the overrides come into play. All you need to do is create `~/.config/chroma/overrides.lua` and populate it with the overrides you want. Note that you need to reference the current theme to override its options. This override file, if existing, will apply overrides to every loaded theme.

```lua
-- ~/.config/chroma/overrides.lua

-- Note the different require clause to import current theme. Python can also
-- be imported here from builtins.
local theme = require("chroma.themes.current")
local python = require("chroma.builtins.python")

-- The override table is merged with the themes table. This ensures only the
-- overridden values are updated, and other values are untouched.
theme.kitty = {
  out = "~/.config/kitty/themes/" .. theme.meta.name .. '.conf'
}

-- Of course, we still need to return the theme so Chroma can read the theme data.
return theme
```

## Custom Handlers

You can make custom integrations by making your own handler. Each handler must be inside `chroma/handlers` or `~/.config/chroma/handlers`. Each handler is a Python file which must create a class inheriting `chroma.handler.Handler` and must contain a `register()` method. The method `apply()` must be implemented in the custom class. You can access relevant theme information by using the class attributes. These are all the valid class attributes and their contents:

- The `self.group` attribute contains the group options, like `colors`, `out`, etc. and will be probably used the most. These fields are the actual fields that the theme defines to be themed like `theme.handlername = {}`.
- The `self.meta` attribute contains any relevant set metadata like the theme name, author, etc. which could be useful in embedding the metadata directly into the generated theme file.
- The `self.data` attribute contains data tables. Data tables are custom tables which have a `handle = false` field. Data tables cannot be handled by any handler. Rather, they are made available to all the handlers.

The `register()` method must return a dictionary of groups that will be handled along with the constructor of the class. If a registered handler matches the group name, then the corresponding handler class is constructed, setting the required parameters. Then, the `apply()` method is called after construction.

Make sure that the signatures of the handlers strictly follow this. Otherwise, the handler would be marked as malformed and will be skipped. Take a look at the following minimum example for a handler. Of course, you should make it more featureful and informative.

> [!NOTE]
> This works, but is still kind of experimental. Expect bugs or changes to the behaviour. Further testing is required. Feel free to provide feedback.

> [!WARNING]
> Custom handlers are just any regular python scripts. They can do malicious things. Make sure you trust the source of the handler, and that the contents of the handler seem valid.

```py
# ~/.config/chroma/handlers/my_handler.py

from chroma.logger import Logger
from chroma.handler import Handler

logger = Logger.get_logger()

class MyHandler(Handler):
    def apply():
        logger.debug("Greetings from this custom handler!")
        logger.info("We have the following tables available:")
        logger.info(f"{self.group} contains all set key-value pairs in the theme file")
        logger.info(f"{self.meta} contains metadata about the theme")
        logger.info(f"{self.data} contains all custom data tables from the theme")

def register():
    return {
        "groupname": MyHandler,
        "anothergroup": MyHandler,
    }
```

This might give a warning that Chroma doesn't exist as a library. Worry not, as when Chroma executes the handler, it will be able to detect and provide the `chroma` module. This just happens due to Nix's strict isolation policies. To fix this issue, include Chroma in the devshell's `buildInputs`. This will allow python to detect the library and get rid of those pesky and annoying warnings.

## Generation

TODO

## Custom backends

TODO

## Roadmap

> [!NOTE]
> For an exhaustive changelog, refer to the [Changelog](https://github.com/aryanjassal/chroma/blob/main/CHANGELOG.md)

- Add default themes, as colors are now static
- Provide preset themes for quicker start with system theming (in progress)
  - Make user defined themes directory
  - Registry for theme names to parsed theme
    - Change imports
      - Merge namespace for themes (`chroma.themes` will include both user themes and builtin themes)
      - If not possible, then move user config to `chroma.user` namespace
- Clean up and update `Colors` to be more streamlined (in progress)
  - Add utility to guess color type using regexes (needed? more testing required)
  - In place vs returned type transformations for color
  - Properly implement denormalization for HSL
  - Custom getter/setter for RGB/HSL fields
  - Fix linter errors
  - Set saturation/luminosity
- Update handlers to rely on `Color` more heavily
- Make icon (inspired by Prism Launcher)
- Allow custom variable substitution for paths (or just use regular path substitution for that)
- Add upstream metadata field
  - Allow themes to be updated by a command, replacing local with remote content
- Add a `config.lua` file which the users can configure the default integrations in
  - Add enabled modules config option
- Rename 'handlers' to 'integrations'
- Add `chroma.lib` for utility functions within lua
  - Add `Color` class and conversion utilities for lua
  - By default, all colors should be `Color` objects
- Make lua handlers more powerful
  - Add pre and post inserts for the files
  - Add support for template files
- Add tests
- Separate backup to validity check in utils

## Credits

Credit to [pywal](https://github.com/dylanaraps/pywal) for inspiration on implementing dynamic palette generation.

## Notes

I have been trying to inject the default theme table into lua's system path, so theme developers can get type hints. Applications like `vim` (kind of) do it, so it should be possible. I just can't figure out how to do it. If anyone does, you're welcome to contribute. Rather, _please_ contribute.

I want to add a GUI to go with Chroma, but I don't have time to make the whole thing by myself in a reasonable time frame. If anyone wants to contribute, then feel free to step up and take over the development.
