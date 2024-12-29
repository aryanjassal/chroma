# Chroma

Use a single command to theme your entire system.

Why does this exist, you ask? I wasn't happy with how other theming applications worked. Granted, "other" means only three applications: [Gradience](https://github.com/GradienceTeam/Gradience), [Pywal](https://github.com/dylanaraps/pywal), and [Chameleon](https://github.com/GideonWolfe/Chameleon). I know two of those applications are archived, and the third one relies on one of the archived application. But still. I don't like that.

And, what started off as a simple script to take in a lua file theme file and write it to some set applications' configuration became this. It's like you were trying to build a sand castle on the beach, but you somehow end up building Rome within a day. Crazy stuff, huh?

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

That's it! This will load the theme and run it through the integrations. If the target file already exists, the integration will attempt to back up the file automatically. If the backup fails, then you would have to manually back the file up. Chroma checks if a particular header exists in the file. If it does, that means that the file was generated by Chroma, and it can freely edit/modify the file.

In case the header changes in the future, all the old themes would need to be removed. Most likely a command will exist at that time, which will iterate over the theme and remove all output files generated by Chroma.

Note that you don't need to provide a fixed path to the theme. If the theme exist in the expected directories (being `~/.config/chroma/themes` or is an inbuilt Chroma theme), then merely passing the theme name is sufficient. Chroma will automatically try to match the name with an actual theme path. You can optionally also include the extension if you want. However, do note that the path you provide isn't a partial path to match, but is the strict name of the file. So, passing in `'mytheme/nesteddir/theme.lua'` will not work. This can be used as follows.


```console
[aryanj@laptop:~]$ chroma load tokyodark
```

To generate colors from an image (it will usually be your wallpaper) and apply that as your new color palette, you can use this command to do so. Remember, however, that the colors this command generates aren't always the best, and if you solely rely on this, you might end up with weird theme or artifacts.

```console
[aryanj@laptop:~]$ chroma generate path/to/image.img [--output path/to/generated/theme.lua] [--override path/to/override.lua]
```

This command will automatically generate a lua theme file with your wallpaper and save it to the desired path (the cache directory by default). The command will not generate any metadata or anything fancy. These are just plain colors and themes. Also, make sure that you have `imagemagick` installed on your system before you run the generation command. It is already present for Nix users in both the development shell and after building if installed as a program.

Do note that there are way more options available. Take a look at the help menu to see all the avilable options.

To keep using the default theme palette and remove the auto-generated palette, run this command. You will need to regenerate the palette if you have already run this command.

> [!IMPORTANT]
> The colors generated are heavily opinionated and might not work perfectly for all images. Please understand this, and raise any issues with the image palette generation along with an image on which we see that behavior. Of course, we fix one image, we break another.

```console
[aryanj@laptop:~]$ chroma remove
```

## Theming

> [!IMPORTANT]
> To theme GTK apps, please install the `adw-gtk3` theme from [here](https://github.com/lassekongo83/adw-gtk3). Without this installed, the GTK theme will fail to apply.

> [!IMPORTANT]
> GTK is known for not being friendly to theming. As such, no formal API for theming is exposed. This means that, while many apps will be themed, many will still remain unthemed or in a broken state. Some cases will be impossible to resolve, but some might be oversights/mistakes. If you see one such issue, then please report it.
>
> Other integrations also might have similar issues, as you might use features which I never use, so I never implemented theming for it. If such cases arise, feel free to raise an issue about it.

```lua
--[[
  Define a table for storing theme groups. Each group is the application name
  with a table assigned to it. It can store tables. The color scheme is one
  such table (see below for an example).

  Note that you should import the default table when writing your own themes.
  This would ensure that any fields you haven't filled in will be set to a
  default value. This is not necessary as the options are merged with the
  default table anyways (see `theme.options` below), but you might get hard to
  debug bugs without this, so its good practice to include it.

  Here, we also include `python`. It is an empty table whose sole purpose is to
  silence LSP errors when using `python.none` to signify a `None` value to the
  Python backend. Otherwise, a bunch of warnings will be generated and I hate
  that. If you don't need to use `python.none`, just don't include it.
]]
local theme = require "chroma.bultins.default"
local python = require "chroma.builtins.python"

--[[
  This contains many utility functions for theming, especially one for setting
  colors if an autogenerated palette exists.
]]
local lib = require "chroma.builtins.lib"

--[[
  These options control the behavior of theme generation. Know what you are
  doing before chaging any option here, as you most likely don't want to be
  changing anything here.
]]
theme.options = {
  --[[
    This specifies the Chroma version for which the theme was written for. If
    the theme is designed for a different version of Chroma, then Chroma will
    give you a warning. Most likely, older theme versions will just crash while
    applying the theme. Must be defined like: "1.0.0" where there are three
    numbers separated by two periods. See https://semver.org/.
  ]]
  chroma_version = "1.0.0",

  --[[
    By default, the theme generator merges the table with the default table.
    This ensures doing something like this would not result in other values,
    like the default out file, being nil. To disable this behavior, set this
    flag to false.

    themes.gtk { colors = { red = "#ff0000", } }
  ]]
  merge_tables = true,
}

theme.meta = {
  --[[
    These fields are the metadata of the actual theme. They need to be filled
    out manually, but the fields are optional. All parameters within the meta
    table are purely cosmetic and shouldn't seriously impact the behavior of
    Chroma.
  ]]
  name = "Example",
  description = "This is an example config",
  author = "Chroma",
  version = "1.0.0",
  url = "https://github.com/aryanjassal/chroma",
}

--[[
  This field requires a specific pattern of colors to be matched. Some
  integrations accept multiple themes, while some need a strict set of keys.
  Set the keys manually for each integration when you can. If an autogenerated
  palette does not exist, then use the given colors. Otherwise, the theme colors
  are used.
]]
theme.colors = lib.generated_or({
  black = "#000000",
  red = "#ff0000",
  green = "#00ff00",
  yellow = "#ffff00",
  blue = "#0000ff",
  magenta = "#ff00ff",
  cyan = "#00ffff",
  white = "#ffffff",
  -- more as required
})

local colors = theme.colors

--[[
  You can also define variables. Note that any defined variables or functions
  will be discarded, and only the values in the returned table will be
  processed by Chroma.
]]
local foreground = colors.white
local background = colors.black

--[[
  See, this is where the definition of `python.none` can come in handy.
  Basically, replace all references to `nil` for lua to `python.none` for
  Python compatibility, otherwise lua get weird with tables.
]]
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

--[[
  Update all GTL settings here by changing the relevant options in the GTK
  integration. Please note that GTK is difficult to theme and the frequency of
  identified bugs will be greater in general.
]]
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

  --[[
    GTK additionally allows themes to set 5 extra colors as theme palettes.
    That can be set using the `palettes` table. In this table, you can
    update colors on `palette1` to `palette5` to correspond to each of the five
    palettes. If left unset, they will not be present in the GTK stylesheet,
    and would not render. It is highly recommended to at least create one
    palette, but ideally, create all five. No default values exist for this
    attribute.
  ]]
  palettes = {
    palette1 = gtk_defaultpalette,
    palette2 = gtk_defaultpalette,
    palette3 = gtk_defaultpalette,
    palette4 = gtk_defaultpalette,
    palette5 = gtk_defaultpalette,
  },

  --[[
    We have a patch to ensure libadwaita sidebars are also properly themed. Why
    is this not hardcoded? Freedom. Get the classic, broken look by setting
    this patch to an empty string like this.

    sidebar_patch = ""
  ]]

  --[[
    Want to customize your experience EVEN MORE? There's an option for that.
    Inject custom CSS into the css files to change behavior in interesting
    ways.
  ]]
  extra_css = "",

  --[[
    You can also customize the file the complied themes will be output to. You
    can include home-relative paths (~/) and they will be expanded. As of now,
    the stylesheet is generated the same for both GTK3 and GTK4. This might
    change in the future.
  ]]
  out = {
    gtk3 = "~/.config/gtk-3.0/gtk.css",
    gtk4 = "~/.config/gtk-4.0/gtk.css",
  },
}

--[[
  Update kitty options here. This application is only concerned with color
  themes, and will not update other UI-related config like fonts, cursors,
  opacity, etc. so don't try to include them. If you want that feature, make
  your voice heard and make an issue.
]]
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

  --[[
    You can also customize the file the complied themes will be output to. You
    can include home-relative paths (~/) and they will be expanded. Here, the
    output file is actually not `kitty.conf`. You would need to import the
    theme in kitty using the `include` directive. Google it if you don't know
    how that works.
  ]]
  out = "~/.config/kitty/theme.conf",
}

--[[
  Output the colors to a file in a way which can be used by other programs. You
  have full control over the formatting of the file to ensure it is maximally
  usable with your needs.
]]
theme.raw = {
  --[[
    You can define multiple tables for the raw integrations, and each table can have
    its own attributes. All tables will be processed separately, and each table
    will be output to the specified output file following the specified
    formatting. Note that each table inside the raw integration can have anything
    for names. It doesn't matter. They are just there for convenience and
    debugging purposes. However, DO NOT repeat names. That's bad. Very bad.
    Due to lua's inherent randomness with tables and its values, the final data
    written to the target file if two integrations are pointing to the same file
    will be random.

    -- WARNING --
    Forcing a superpositional collapse on two distict tables under the same
    label will result in the destruction of the universe due to the induced
    inconsistency in the fabric of space-time. Please avoid doing so at all
    costs.
  ]]

  spaced = {
    --[[
      Of course, as usual, you can set and override colors as needed. All
      key-value pairs from the `colors` table will be output in the files
      following the right formatting rules. No error-checking or type safety
      checks are done here, so you are on your own.
    ]]
    colors = colors,

    --[[
      This defines how each line will be formatted in the output file. Variables
      are defined by putting their names inside {}. For example, this format will
      result in the following output.

      white #ffffff
      black #000000

      Available variables are:
      {name}: Color name (no spaces allowed)
      {hex}: Hexadecimal color value (with leading hashtag)
      {hexval}: Hexadecimal color value (without leading hashtag)
    ]]
    format = "{name} {hex}",

    --[[
      Backups the file if it already exists at the target location if set.
      There usually is little reason to disable automatic backups or warnings
      if the target file exists, but this way we can force overwrite the
      target file if desired.
    ]]
    force = false,

    --[[
      This format works similar to the color definition format, but instead,
      this works on the header instead. The header tells Chroma if the file
      was generated by the user (which we should back up), or by Chroma itself
      (which it will overwrite without backups). The header format is
      provided to ensure that the header will be formatted as a comment for
      the file we are writing to.

      Available variables are:
      {header}: The header template, provided by Chroma

      Set this to `nil` or `python.none` to not generate or check for a header.
      This is not recommended.
    ]]
    header = "# {header}"

    --[[
      You can also expand all environment variables available to the program
      just like in the shell. Make sure to not run the program with `sudo`, as
      that might mess up the variables. For example, `~` might point to `/root`.
    ]]
    out = "~/cache/chroma/colors.col",
  },

  --[[
    Following the previous instructions, another integration is provided for your
    reading pleasure. This integration creates a custom partial scss color sheet.
    This file will have the following output.

    // This is a demo header text. The real one will look different than this.
    $white: #ffffff;
    $black: #000000;
  ]]
  scss = {
    colors = colors,
    out = "~/cache/chroma/_colors.scss",
    header = "// {header}"
    format = "${name}: {hex};",
  },
}

--[[
  Each theme must return the theme table at the end. This is what tells Chroma
  about the actual settings you changed. Without returning the theme data,
  Chroma won't be able to apply a theme.
]]
return theme
```

## Overrides

We can create themes, sure. But, what if I have my configuration files saved somewhere else? Or you want particular colors in GTK's palette 5? This is where the overrides come into play. All you need to do is create `~/.config/chroma/overrides.lua` and populate it with the overrides you want. Note that you need to reference the current theme to override its options. This override file (if it exists) will apply overrides to every loaded theme.

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

## Custom Integrations

You can make custom integrations by making your own python file. Each integration must be inside `chroma/integrations` or `~/.config/chroma/integrations`. Each integration is a Python file which must create a class inheriting `chroma.integration.Integration` and must contain a `register()` method. The method `apply()` must be implemented in the custom class. You can access relevant theme information by using the class attributes. These are all the valid class attributes and their contents:

- The `self.group` attribute contains the group options, like `colors`, `out`, etc. and will be probably used the most. These fields are the actual fields that the theme defines to be themed like `theme.integrationname = {}`.
- The `self.meta` attribute contains any relevant set metadata like the theme name, author, etc. which could be useful in embedding the metadata directly into the generated theme file.
- The `self.data` attribute contains data tables. Data tables are custom tables which have a `handle = false` field. Data tables cannot be handled by any integration. Rather, they are made available to all the integrations.

The `register()` method must return a dictionary of groups that will be handled along with the constructor of the class. If a registered integration matches the group name, then the corresponding integration class is constructed, setting the required parameters. Then, the `apply()` method is called after construction. Integratons which do not implement a registration method will be ignored.

Make sure that the signatures of the integrations strictly follow this. Otherwise, the integration would be marked as malformed and will be skipped. Take a look at the following minimum example for an integration. Of course, you should make it more featureful and informative.

> [!WARNING]
> Custom integrations are just any regular python scripts. They can do malicious things. Make sure you trust the source of the integration, and that the contents of the integration seem valid.

```py
# ~/.config/chroma/integrations/my_integration.py

from chroma.logger import Logger
from chroma.integration import Integration

logger = Logger.get_logger()

class MyIntegration(Integration):
  def apply():
    logger.debug("Greetings from this custom integration!")
    logger.info("We have the following tables available:")
    logger.info(f"{self.group} contains all set key-value pairs in the theme file")
    logger.info(f"{self.meta} contains metadata about the theme")
    logger.info(f"{self.data} contains all custom data tables from the theme")

def register():
  return {
    "groupname": MyIntegration,
    "anothergroup": MyIntegration,
  }
```

### Extra steps for Nixers

This might give a warning that Chroma doesn't exist as a library. Worry not, as when Chroma executes the integrations, it will be able to detect and provide the `chroma` module. This just happens due to Nix's strict isolation policies. To fix this issue, include Chroma in the devshell's `buildInputs`. This will allow python to detect the library and get rid of those pesky and annoying warnings.

## Generation

You can use the palette generator to generate a palette from an image. You can do this dynamically whenever a wallpaper is changed by using this script to do the changing.

```bash
#!/usr/bin/env bash

# Assume changing wallpapers using `swww` and `$1` (first argument) is path to
# the image to set as the wallpaper.

swww img $1

chroma generate $1 && \
chroma load /path/to/theme.lua
```

This script will first set an image as a wallpaper, then generate and load a theme using Chroma.

Chroma generates a theme palette and saves the generated palette to either a specified path, or `~/.config/chroma/palettes/generated.lua` by default.

Unlike Pywal, which can set the wallpaper based on a theme, Chroma can generate a theme based on the wallpaper. While some palettes might end up looking less than perfect, others might look fitting. It's kind of a hit-or-miss. If you really want a perfect color palette, make it yourself.

However, changing some variables could result in interesting behavior. As such, options to further customise currently hardcoded values will be provided in the future, but for now, it is all static.

All a generated color palette does is that it overrides the base color palette provided by the theme. The theme's settings are still applicable. For example, if the theme assigns `theme.colors.blue` to `theme.gtk.colors.accent`, then the generated blue color will be used as the accent instead of the actual generated accent color.

## Custom backends

Unfortunately, while this is going against the design philosophy of Chroma, adding custom backends isn't supported yet. While it is no longer experimental, it still needs general feedback and more code updates before it is ready for public usage.

## `chroma.colors`

> [!NOTE]
> For theme writers: The `chroma.colors` API will be very unstable during development, as I'm not happy with where it is right now. Be warned.
>
> For users: Make sure to check for updates for your theme if a chroma update breaks your theme.

Unfortunately, just like custom generator backends, adding custom colors isn't supported yet either. The current implementation isn't suitable for that. See [this comment](https://github.com/aryanjassal/chroma/pull/1#issuecomment-2481729224). If you still want to do it anyways, you will need to add it inside the project files manually. Moreover, there will be no official support for custom color spaces until the API stabilizes.

Chroma supplies a custom library to deal with colors in different color spaces.

```py
from chroma.colors import Color, ColorHex, ColorRGB

def generate_rgb_from_hex(rgb_color):
  """Converts a RGB color to a Hex color"""

  if isinstance(rgb_color, Color):
    return rgb_color.cast(ColorHex)
```

Each color extends the `chroma.colors.base.Color` class. There are some methods which are expected to be present across all colors, like darkening or lightening colors, changing their saturation, etc.

The main benefit of using `Color` over a string representation is that casting to other color types, like RGB or HSL, is trivial. Moreover, the colors can be easily manipulated. Look at the `magick` generator. It extensively uses the colorspace casting and color modification, especially in color generation.

### Usage

```py
from chroma.colors import *

# Make a new color object of the desired type
color_hex = ColorHex('#ffffff')

# Note the input values will change depending on the color type
color_rgb = ColorRGB(255, 255, 255)

# RGB operates on a denormalized scale of 0-255. HSL operates on 0-360 for hue
# and 0-100 for saturation and luminance.
color_hsl = ColorHSL(360, 100, 100)

# The raw values can be obtained via the color property
print(color_hex.color)  # Outputs "#ffffff"
print(color_rgb.color)  # Outputs "(255, 255, 255)"
print(color_hsl.color)  # Outputs "(360, 100, 100)"

# The string representation works a bit differently
print(color_hex)  # Outputs "#ffffff"
print(color_rgb)  # Outputs "rgb(255, 255, 255)"
print(color_hsl)  # Outputs "hsl(360, 100, 100)"
# NOTE: This is what the string representation should look like. However, this
# only works for ColorHex. You will get a warning if you try and convert a
# ColorRGB or ColorHSL to a string.

# To convert between color spaces, use the `cast` method with the target type
new_color = color_hex.cast(ColorRGB)
print(new_color)  # Outputs "rgb(255, 255, 255)"

# As a standard, all colors support the following operations
new_color.darkened(amount=0.1)  # Darken a color with the given amount
new_color.lightened(amount=0.1)  # Lighten a color with the given amount
new_color.saturated(amount=0.1)  # Saturate a color with the given amount
new_color.desaturated(amount=0.1)  # Desaturate a color with the given amount
new_color.blended(color=color_hsl, ratio=0.1)  # Blend two colors by the given ratio

# These methods aren't supported by all color types.
new_color.normalize()    # Normalization and denormalization is currently
new_color.denormalize()  # only supported by ColorHSL and ColorRGB.

# For ColorHex, there's an additional method available to get the hex value
# without the leading '#'
print(color_hex.value)  # Outputs "ffffff"

# You can also access individual components of a color
print(color_hex.h)  # Outputs 360
print(color_rgb.r)  # Outputs 255
```

## Roadmap

For an exhaustive changelog, refer to the [Changelog](https://github.com/aryanjassal/chroma/blob/main/CHANGELOG.md)

- Update `imagemagick` backend
  - Use "generated.lua" theme as base instead, unless specified otherwise
    - Something like '-t --theme "theme_name"' could be used for theme overriding
- Provide preset themes for quicker start with system theming (in progress)
  - Make user defined themes directory
  - Change lua imports for all themes
    - Merge namespace for themes (`chroma.themes` will include both user themes and builtin themes)
    - If not possible, then move user config to `chroma.user` namespace
- Update integrations to rely on `Color` more heavily
- Make icon (inspired by Prism Launcher)
- Allow custom variable substitution for paths (or just use regular path substitution for that)
- Add upstream metadata field
  - Update the integrations to implement a versioning system like the themes, so older/newer integrations won't be supported or will throw a warning/error.
  - Allow themes to be updated by a command, replacing local with remote content
- Add a `config.lua` file which the users can configure the default integrations in
  - Add enabled modules config option
  - Add config for backends
- Add `chroma.lib` for utility functions within lua
  - Add `Color` class and conversion utilities for lua
  - By default, all colors should be `Color` objects
- Make lua integrations more powerful
  - Add pre and post inserts for the files
  - Add support for template files
- QT SUPPORT [HIGH PRIORITY] (probably via kvantum)
- Separate backup to validity check in utils
- Make free-standing `darken`, etc. methods for colors
- Unify exit codes (like 64 for incorrect usage, 1 for other errors, etc.)
- Split lua types into another file
- Make lua state into all caps matching lua expectation

## Credits

Credit to [pywal](https://github.com/dylanaraps/pywal) for inspiration on implementing dynamic palette generation.

## Notes

I have been trying to inject the default theme table into lua's system path, so theme developers can get type hints. Applications like `vim` (kind of) do it, so it should be possible. I just can't figure out how to do it. If anyone does, you're welcome to contribute. Rather, _please_ contribute.

I want to add a GUI to go with Chroma, but I don't have time to make the whole thing by myself in a reasonable time frame. If anyone wants to contribute, then feel free to step up and take over the development.

I need opinions on the type system of my code. It is a _hot mess_. I'm coming from a TypeScript/C++ background where we have stricter typing. In ways, Python is liberating. In other ways, it is a nightmare. This is one such way of being a nightmare. Litearlly no type safety. This alone is making me want to switch languages to something like TypeScript, but I want to keep this beginner-friendly, so I will try my best to keep the code free of unneeded jargon. Still, however, I still need inputs on handling typing in my code base, especially under `chroma.colors` as that is the hottest of messes so far.
