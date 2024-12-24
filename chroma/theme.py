import re

import chroma
from chroma.exceptions import InvalidFieldException, VersionMismatchException
from chroma.integration import Integration
from chroma.logger import Logger
from chroma.utils.dynamic import discover_modules
from chroma.utils.paths import chroma_dir, chroma_themes_dir, config_dir, override_theme
from chroma.utils.theme import parse_file, runtime
from chroma.utils.tools import merge, to_dict

logger = Logger.get_logger()

# Default metadata fields. Other fields are unsupported and shouldn't be relied
# upon by integrations.
VALID_META_KEYS = ["name", "description", "url", "author", "version"]

# Special groups are groups which do not contain theme data. As such, no
# integrations exists for these groups.
SPECIAL_GROUPS = ["meta", "options", "colors"]

# A registry for all the integrations and their corresponding constructor classes.
INTEGRATION_REGISTRY: dict[str, Integration] = {}


def assert_version(version, meta) -> None:
    def meta_get(opt):
        v = meta.get(opt)
        if v is None:
            return "Unknown"
        return v

    if version is None:
        InvalidFieldException(f"Chroma version is unset in '{meta_get('name')}'.")

    if not re.match("^[0-9]+\\.[0-9]+\\.[0-9]+$", version):
        InvalidFieldException(
            f"Chroma version is incorrectly set in '{meta_get('name')}': " f"{version}"
        )

    # Patches signify no changes in the actual API. As such, we don't care if
    # we have a patch version mismatch.
    theme_major, theme_minor, _ = version.split(".")
    chroma_major, chroma_minor, _ = chroma.__version__.split(".")

    if theme_major != chroma_major:
        raise VersionMismatchException(
            "Major version mismatch!\n"
            f"Theme version {version} is incompatible with Chroma version"
            f" {chroma.__version__} in '{meta_get('name')}'."
        )

    if theme_minor != chroma_minor:
        logger.warn(
            "Minor version mismatch!\n"
            f"Theme version {version} might be incompatible with Chroma version"
            f" {chroma.__version__} in '{meta_get('name')}'."
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
    user_config = parse_file(runtime(), filename)
    default_config = parse_file(runtime(), chroma_themes_dir() / "default.lua")

    options = merge(user_config["options"], default_config["options"])
    if options["merge_tables"]:
        theme = merge(default_config, user_config)
    else:
        logger.warn(
            "Theme table will not be merged with default table. Some fields "
            "may be left unset, which can break the theme."
        )

    override_file = override_theme()
    if override_file.is_file():
        override_config = parse_file(runtime(), override_file)
        theme = merge(theme, override_config)

    assert_version(options["chroma_version"], theme["meta"])
    meta = parse_meta(theme["meta"])
    theme = to_dict(theme)

    # Filter all tables marked as `handle` to be data tables. Sanitize the input
    # to remove the `handle` field too. This can be done as the following
    # one-liner, but we won't be able to sanitize the data, so the longer loop
    # was used.
    # data = {k: v for k, v in theme.items() if v.get("handle") is not None}
    data = {}
    for name, group in theme.items():
        if not group.get("handle", True):
            logger.debug(f"Table {name} marked as a data table")
            data[name] = group
            del data[name]["handle"]

    for name in data:
        del theme[name]

    # Override application's integraions by user's integrations if defined.
    # TODO: Warn users if they are overriding a local integration, in case the
    # action was unintentional.
    integrations = [
        *discover_modules(chroma_dir() / "integrations"),
        *discover_modules(config_dir() / "integrations"),
    ]

    for integration in integrations:
        if hasattr(integration, "register") and callable(
            getattr(integration, "register")
        ):
            # Get the key-value pairs for the registry
            entry = getattr(integration, "register")()

            # Validate each pair before adding them to the registry.
            # The issubclass() can only throw one error: TypeError when the
            # first argument isn't a class. In that case, our integration would
            # be malformed, so we can safely detect and ignore that exception.
            # TEST: testing is required for this
            for key, sub_int in entry:
                try:
                    subclass = isinstance(sub_int, Integration)
                    if subclass:
                        INTEGRATION_REGISTRY[key] = sub_int
                    else:
                        raise TypeError
                except TypeError:
                    logger.error(f"Integration {key} is malformed. Skipping.")

            # Finally update the registry with the correct pairs
            INTEGRATION_REGISTRY.update(entry)
            for name in entry:
                logger.debug(f"Registered integration {name}")

    for group, config in theme.items():
        if group in SPECIAL_GROUPS:
            continue

        logger.info(f"Applying theme for {group}")
        integration = INTEGRATION_REGISTRY.get(group)

        # If the integration doesn't exist, then skip it.
        if integration is None:
            logger.error(f"No integrations found for {group}. Skipping.")
            continue

        # Otherwise, check if the required signatures match. If they do,
        # then run the respective integration.
        if callable(integration):
            integration_class: Integration = integration(config, meta, data)
            integration_class.apply()
            continue

        # If the signatures don't match, then warn the user and skip the
        # integration.
        logger.error(f"Integration for {group} is malformed. Skipping.")
