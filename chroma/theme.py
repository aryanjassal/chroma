import re

import chroma
from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

# Default metadata fields. Other fields are unsupported and shouldn't be relied
# upon by handlers.
VALID_META_KEYS = ["name", "description", "url", "author", "version"]

# Special groups are groups which do not contain theme data. As such, no handler
# exists for these groups.
SPECIAL_GROUPS = ["meta", "options", "colors"]


def match_version(version, meta) -> None:
    def meta_get(opt):
        v = meta.get(opt)
        if v is None:
            return "Unknown"
        return v

    if version is None:
        logger.fatal(f"Chroma version is unset in {meta_get('name')} theme")

    if not re.match("^[0-9]+\\.[0-9]+\\.[0-9]+$", version):
        logger.fatal(
            f"Chroma version is incorrectly set in {meta_get('name')} theme: "
            f"{version}"
        )

    # Patches signify no changes in the actual API. As such, we don't care if
    # we have a patch version mismatch.
    theme_major, theme_minor, _ = version.split(".")
    chroma_major, chroma_minor, _ = chroma.__version__.split(".")

    if theme_major != chroma_major:
        logger.error("Major version mismatch")
        logger.fatal(
            f"Theme version {version} is incompatible with Chroma version"
            f" {chroma.__version__} in {meta_get('name')} theme."
        )

    if theme_minor != chroma_minor:
        logger.warn("Minor version mismatch")
        logger.warn(
            f"Theme version {version} might be incompatible with Chroma version"
            f" {chroma.__version__} in {meta_get('name')} theme."
        )


def parse_meta(meta) -> dict:
    parsed_meta = {}
    for k, v in meta.items():
        if k not in VALID_META_KEYS:
            logger.warn(f"{k} is not a valid metadata field.")
        if v is None:
            logger.debug(f"{k} is unset")
        else:
            parsed_meta[k] = v
            logger.debug(f"{k} = {v}")
    return parsed_meta


def load(filename):
    # Create a blank dict for the theme, then assign themes in such a way that
    # default becomes the base, and we can override defaults with user theme
    # and override user theme from the override file.
    theme = {}
    user_config = utils.parse_file(utils.runtime(), filename)
    default_config = utils.parse_file(
        utils.runtime(), utils.chroma_themes_dir() / "default.lua"
    )

    options = utils.merge(user_config["options"], default_config["options"])
    if options["merge_tables"]:
        theme = utils.merge(default_config, user_config)
    else:
        logger.warn(
            "Theme table will not be merged with default table. Some fields "
            "may be left unset, which can break the theme."
        )

    override_file = utils.override_theme()
    if override_file.is_file():
        override_config = utils.parse_file(utils.runtime(), override_file)
        theme = utils.merge(theme, override_config)

    match_version(options["chroma_version"], theme["meta"])
    meta = parse_meta(theme["meta"])
    theme = utils.to_dict(theme)

    # Override application's handlers by user's handlers if defined.
    handlers = {
        **utils.discover_handlers(utils.chroma_dir() / "handlers"),
        **utils.discover_handlers(utils.config_dir() / "handlers"),
    }

    for group, config in theme.items():
        if group in SPECIAL_GROUPS:
            continue

        logger.info(f"Applying theme for {group}")
        handler = handlers.get(group)

        # If the handler doesn't exist, then skip handling it.
        if handler is None:
            logger.error(f"No handlers found for {group}. Skipping.")
            continue

        # Otherwise, check if the required signatures match. If they do,
        # then run the respective handler.
        if hasattr(handler, "apply") and callable(getattr(handler, "apply")):
            getattr(handler, "apply")(config, meta)
            continue

        # If the signatures don't match, then warn the user and skip the handler.
        logger.error(f"Handler does not properly implement `apply()`. Skipping.")
