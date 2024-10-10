import argparse
import shutil
import traceback as tb
from pathlib import Path

from chroma.logger import Logger, LogLevel

logger = Logger(LogLevel.DEBUG)
Logger.set_logger(logger)

import chroma
from chroma import generator, theme, utils


def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"Chroma {chroma.__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Parse commands for keyword load
    load_parser = subparsers.add_parser("load", help="Loads a theme from a lua file")
    load_parser.add_argument("theme_name", help="Location of the lua theme file")
    load_parser.add_argument("-u", "--override", type=str, help="Override settings")

    # Parse commands for keyword generate
    gen_parser = subparsers.add_parser("generate", aliases=["gen"], help="Generates a theme from an image")
    gen_parser.add_argument("image_path", help="Path to the image to extract colors from")
    gen_parser.add_argument("-u", "--override", type=str, help="Override settings")
    gen_parser.add_argument("-o", "--output", type=str, help="Output path of generated color scheme")
    gen_parser.add_argument("--experimental", action="store_true", help="Enable experimental command usage")

    known_args, unknown = parser.parse_known_args()
    args = parser.parse_args(unknown, namespace=known_args)

    # Map particular commands to other commands. Useful to map aliases to
    # original parser name.
    command_map = { "gen": "generate" }

    if args.command in command_map:
        args.command = command_map[args.command]

    if args.command is None:
        parser.print_help()
        exit(1)

    return args


def exception_hook(exc_type, exc_val, exc_tb):
    logger.error("An unhandled exception occured. Bailing!")
    logger.error(f"Raised: {exc_type.__name__}")
    logger.error(f"Reason: {exc_val}")
    logger.error("Traceback (most recent call last):")
    logger.error("".join(tb.format_tb(exc_tb)).rstrip())
    logger.error("Report this at https://github.com/aryanjassal/chroma/issues")


def main():
    # Set up custom error handler
    utils.set_exception_hook(exception_hook)

    # Get command-line arguments
    args = setup_args()

    if args.command == "load":
        # Cache the theme we are going to apply. This will be useful for overriding
        # options across all themes. Make sure that the name is consistent, like
        # "current.lua", to ensure overrides can always refer to a single file
        # which will reflect the current theme.
        shutil.copy(Path(args.theme_name), utils.themes_dir() / "current.lua")

        # If we are not loading any user overrides, then load the theme directly.
        # Otherwise, the user override must load the theme file anyways, so we
        # can just load the overrides, which will automatically compile the current
        # theme for us.
        if args.override:
            theme.load(args.overide)
        else:
            theme.load(args.theme_name)
        exit(0)

    if args.command == "generate":
        if not args.experimental:
            logger.warn("This is an experimental setting. Enable the experimental flag to continue:")
            logger.warn("  `chroma generate --experimental ...`")
            exit(1)

        if args.output:
            out_path = args.output
        else:
            out_path = utils.cache_dir() / "palettes/generated.lua"
        colors = generator.generate(args.image_path)
        generator.write_lua_colors(colors, out_path)
        generator.write_lua_theme(utils.themes_dir() / "generated.lua", ["gtk", "kitty", "foot"])

if __name__ == "__main__":
    main()
