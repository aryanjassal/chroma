# Changelog

## v0.5.3 (in progress)

This update introduces significant changes to the luascape, changing the requirement of themes and the general layout of the lua code altogether.

### Key changes

- User-defined handlers are no longer experimental. Create handlers in `~/.config/chroma/handlers`. Check the [README](https://github.com/aryanjassal/chroma?tab=readme-ov-file#custom-handlers) for instructions on writing a custom handler.
- Each theme must return a table with all the available colors. The colors must be a part of the theme itself.

### Additions

- Added types to lua default theme for an easier time writing themes.
- Added a bunch of documentation in lualands.

### Changes

- Moved `python` from an export of the default theme to it's own module under `chroma.builtins.python`.
- Tuples can no longer be returned from themes. Instead, return only the theme with an added colors group. This does not and can not have a handler associated with it.
