import importlib

import chroma
from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

VALID_META_KEYS = [
    "name",
    "description",
    "url",
    "author",
    "version"
]

def parse_file(runtime, filename) -> dict:
    with open(filename, mode="r") as f:
        theme = f.read()
    result = runtime.execute(theme)

    # If multiple tables are being exported, the theme table will be first one.
    # Otherwise, the only output would be the theme table.
    if type(result) == tuple:
        return result[0]
    return result


def match_version(version, meta) -> None:
    if version is None or not version:
        logger.error(f"Chroma version is unset in theme {meta['name']}!")
        exit(1)

    t_major, t_minor, _ = version.split(".")
    major, minor, _ = chroma.__version__.split(".")

    if t_major != major:
        logger.error("Major version mismatch!")
        logger.error(
            f"Theme version {version} is incompatible with Chroma version"
            f" {chroma.__version__} in {meta['name']} theme."
        )
        exit(1)

    if t_minor != minor:
        logger.warn("Minor version mismatch!")
        logger.warn(
            f"Theme version {version} might be incompatible with Chroma version"
            f" {chroma.__version__} in {meta['name']} theme."
        )

def parse_meta(meta) -> dict:
    parsed_meta = {}
    for k, v in meta.items():
        if k not in VALID_META_KEYS:
            logger.warn(f"{k} is not a valid metadata field.")

        if v != "" or v is not None:
            parsed_meta[k] = v
            logger.debug(f"{k} = {v}")
        else:
            logger.debug(f"{k} is unset. Skipping.")
    return parsed_meta

def get_option(opt, user_opts, default_opts):
    if user_opts is None:
        return

    user_opt = user_opts.get(opt)
    if user_opt is None:
        if default_opts is None:
            return

        default_opt = default_opts.get(opt)
        if default_opt is None:
            logger.error(f"Option {opt} does not exist")
            return
        return default_opt
    return user_opt


def load(_, filename):
    # Create a blank dict for the theme, then assign themes in such a way that
    # default becomes the base, and we can override defaults with user theme
    # and override user theme from the override file.
    theme = {}
    default_config = parse_file(utils.runtime(), utils.default_theme())
    user_config = parse_file(utils.runtime(), filename)

    user_opts = dict(user_config["options"])
    default_opts = dict(default_config["options"])
    # if options is not None and options["merge_tables"] is True:
    if get_option("merge_tables", user_opts, default_opts):
        theme = utils.merge(default_config, user_config)
    else:
        logger.warn("Theme table will not be merged with default table.")
        logger.warn("Some fields may be left unset, which can break the theme.")

    override_file = utils.override_theme()
    if override_file.is_file():
        override_config = parse_file(utils.runtime(), override_file)
        theme = utils.merge(theme, override_config)

    match_version(get_option("chroma_version", user_opts, None), theme["meta"])
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
            # except Exception as e:
            #     logger.error(e)
            #     logger.error(f"An unhandled exception occured. Bailing!")
            #     logger.error(f"Traceback:")
            #     raise e
