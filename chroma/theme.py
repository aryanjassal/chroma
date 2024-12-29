import re

import chroma
from chroma.exceptions import InvalidFieldException, VersionMismatchException
from chroma.integration import Integration, IntegrationT
from chroma.logger import Logger
from chroma.utils.dynamic import discover_modules
from chroma.utils.paths import (
    chroma_builtins_dir,
    chroma_dir,
    config_dir,
    override_theme,
)
from chroma.utils.theme import (
    DEFAULT_STATE,
    parse_file,
    parse_lua,
    runtime,
    sanitize_python,
)
from chroma.utils.tools import merge, to_dict
from chroma.colors import ColorHex

logger = Logger.get_logger()

# Default metadata fields. Other fields are unsupported and shouldn't be relied
# upon by integrations.
VALID_META_KEYS = ["name", "description", "url", "author", "version"]

# Special groups are groups which do not contain theme data. As such, no
# integrations exists for these groups.
SPECIAL_GROUPS = ["meta", "options", "colors"]

# A registry for all the integrations and their corresponding constructor classes.
INTEGRATION_REGISTRY: dict[str, IntegrationT] = {}


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


def load(filename=None, lua=None, state: dict = dict()):
    # Create a blank dict for the theme, then assign themes in such a way that
    # default becomes the base, and we can override defaults with user theme
    # and override user theme from the override file.
    theme = {}

    # Set the default state
    runtime_state = DEFAULT_STATE
    runtime_state.update(sanitize_python(state))

    config = parse_file(runtime(runtime_state), chroma_builtins_dir() / "config.lua")
    print(config)
    c = config["generators"]["generator_modes"]["background"](ColorHex('#ffffff'))
    print(c)
    exit()

    if lua is None:
        user_theme = parse_file(runtime(runtime_state), filename)
    else:
        user_theme = parse_lua(runtime(runtime_state), lua)

    default_theme = parse_file(
        runtime(runtime_state), chroma_builtins_dir() / "default.lua"
    )

    options = merge(user_theme["options"], default_theme["options"])
    if options["merge_tables"]:
        theme = merge(default_theme, user_theme)
    else:
        logger.warn(
            "Theme table will not be merged with default table. Some fields "
            "may be left unset, which can break the theme."
        )

    override_file = override_theme()
    if override_file.is_file():
        override_config = parse_file(runtime(runtime_state), override_file)
        theme = merge(theme, override_config)

    assert_version(options["chroma_version"], theme["meta"])
    meta = parse_meta(theme["meta"])
    theme = to_dict(theme)

    # Filter all tables not marked as `integration` to be data tables. Sanitize
    # the input to remove the `integration` field too.
    data = {}
    for name, group in theme.items():
        if not group.get("integration", True):
            logger.debug(f"Table {name} marked as a data table")
            data[name] = group
            del data[name]["integration"]

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
            for key, sub_int in entry.items():
                try:
                    subclass = issubclass(sub_int, Integration)
                    if subclass:
                        INTEGRATION_REGISTRY[key] = sub_int
                        logger.debug(f"Registered integration {key}")
                    else:
                        logger.debug(
                            f"Integration {key} is not subclass of Integration"
                        )
                        raise TypeError
                except TypeError:
                    logger.error(f"Integration {key} is malformed. Skipping.")

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
