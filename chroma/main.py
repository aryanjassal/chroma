import argparse
import shutil
import traceback as tb
from pathlib import Path

from chroma.logger import Logger, LogLevel

logger = Logger(LogLevel.DEBUG)
Logger.set_logger(logger)

from chroma import theme, utils


def setup_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    # Parse commands for keyword load
    load_parser = subparsers.add_parser("load", help="Loads a theme from a lua file")
    load_parser.add_argument("theme_name", help="Location of the lua theme file")
    load_parser.add_argument("-u", "--override", type=str, help="Override settings")
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(1)
    return args


def exception_hook(exc_type, value, traceback):
    _ = value
    logger.error("An unhandled exception occured. Bailing!")
    logger.error(f"Raised: {exc_type.__name__}")
    logger.error("Traceback (most recent call last)")
    logger.error("".join(tb.format_tb(traceback)).rstrip())
    logger.error("Report this at https://github.com/aryanjassal/chroma/issues")


def main():
    # Set up custom error handler
    utils.set_exception_hook(exception_hook)

    # Get command-line arguments
    args = setup_args()

    # Create a runtime to parse the theme scripts in
    runtime = utils.runtime()

    theme_name = Path(args.theme_name).name

    # Cache the theme we are going to apply. This will be useful for overriding
    # options across all themes. Make sure that the name is consistent, like
    # "current.lua", to ensure overrides can always refer to a single file
    # which will reflect the current theme.
    shutil.copy(Path(args.theme_name), utils.themes_dir())
    shutil.move(utils.themes_dir() / theme_name, utils.themes_dir() / "current.lua")

    if not Path(f"{str(utils.cache_dir())}/example.lua").is_file():
        shutil.copy(
            utils.chroma_themes_dir() / "default.lua",
            utils.cache_dir() / "example.lua",
        )

    # If we are not loading any user overrides, then load the theme directly.
    # Otherwise, the user override must load the theme file anyways, so we
    # can just load the overrides, which will automatically compile the current
    # theme for us.
    if args.override:
        theme.load(runtime, args.overide)
    else:
        theme.load(runtime, args.theme_name)


if __name__ == "__main__":
    main()
