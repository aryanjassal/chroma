import importlib

import chroma
from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()


def parse_file(runtime, filename) -> dict:
    with open(filename, mode="r") as f:
        theme = f.read()
    return runtime.execute(theme)


def parse_meta(meta) -> dict:
    if meta["chroma_version"] is None or not meta["chroma_version"]:
        logger.error(f"Chroma version is unset in theme {meta['name']}!")
        exit(1)

    t_major, t_minor, _ = meta["chroma_version"].split(".")
    major, minor, _ = chroma.__version__.split(".")

    if t_major != major:
        logger.error("Major version mismatch!")
        logger.error(
            f"Theme version {meta['chroma_version']} is incompatible with "
            f"Chroma version {chroma.__version__} in {meta['name']} theme."
        )
        exit(1)

    if t_minor != minor:
        logger.warn("Minor version mismatch!")
        logger.warn(
            f"Theme version {meta['chroma_version']} might be incompatible with"
            f" Chroma version {chroma.__version__} in {meta['name']} theme."
        )

    parsed_meta = {}
    for k, v in meta.items():
        if v != "":
            parsed_meta[k] = v
            logger.debug(f"{k} = {v}")
        else:
            logger.debug(f"{k} is unset. Skipping.")
    return parsed_meta


def load(_, filename):
    # Create a blank dict for the theme, then assign themes in such a way that
    # default becomes the base, and we can override defaults with user theme
    # and override user theme from the override file.
    theme = {}
    default_config = parse_file(utils.runtime(), utils.default_theme())
    user_config = parse_file(utils.runtime(), filename)

    options = user_config["options"]
    if options is not None and options["merge_tables"] is True:
        theme = utils.merge(default_config, user_config)
    else:
        logger.warn("Theme table will not be merged with default table.")
        logger.warn("Some fields may be left unset, which can break Chroma.")

    override_file = utils.override_theme()
    if override_file.is_file():
        override_config = parse_file(utils.runtime(), override_file)
        theme = utils.merge(theme, override_config)

    meta = parse_meta(theme["meta"])

    special_groups = ["meta", "options"]
    for group, config in theme.items():
        if group not in special_groups:
            logger.info(f"Applying theme for {group}")
            try:
                handler = importlib.import_module(f"chroma.handlers.{group}")
                if hasattr(handler, "apply") and callable(handler.apply):
                    handler.apply(config, meta)
                else:
                    logger.error(
                        f"Handler does not properly implement `apply()`. Skipping."
                    )
            except ImportError:
                logger.error(f"No handlers found for {group}. Skipping.")
            except Exception as e:
                logger.error(e)
                logger.error(f"An unhandled exception occured. Bailing!")
                logger.error(f"Traceback:")
                raise e
