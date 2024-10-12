# Changelog

## v0.6.0

This update introduces significant changes to the luascape, changing the requirement of themes and the general layout of the lua code altogether.

Similarly significant changes were also introduced to the pythonscape, mostly updating the API the handlers must now use.

### Key changes

- User-defined handlers are no longer experimental. Create handlers in `~/.config/chroma/handlers`. Check the [README](https://github.com/aryanjassal/chroma?tab=readme-ov-file#custom-handlers) for instructions on writing a custom handler.
- Each theme must return a table with all the available colors. The colors must be a part of the theme itself.

### Additions

- Added types to lua default theme for an easier time writing themes.
- Added a bunch of documentation in lualands.
- Instead of naming the handler to the intended capture group, now a registry can hold that information. Add this line to export a registry field: `def registry(): return { 'type': HandlerClass }`. Note that the handler class constructor is returned. Chroma will construct the handler with the required parameters and call the `apply()` function.

### Changes

- Moved `python` from an export of the default theme to it's own module under `chroma.builtins.python`.
- Tuples can no longer be returned from themes. Instead, return only the theme with an added colors group. This does not and can not have a handler associated with it.
- `Color.to(fmt)` has been removed in favor of `Color.as_format(fmt)` and `Color.as_rgb()`, `Color.as_hsl()`, `Color.as_hex()`, `Color.as_hexval()`.
- `Color.blend` and similar methods which alter colors now return a `Color` object, allowing to chain operations like `Color.as_rgb().normalize().darken(0.5).as_hex()`.
- Instead of writing a handler with a single `apply()` definition with the required parameters, now it is required to extend the `Handler` class and override the default `apply()` handler.
- Documented the `perform_backup` option for raw handlers and renamed it to `force`.

### Removals
- `Color.convert(fmt)` has been removed as regular commands return full colors by default.
