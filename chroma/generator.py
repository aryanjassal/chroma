from pathlib import Path
from typing import Callable

from chroma.colors import Color
from chroma.logger import Logger
from chroma.utils.dynamic import discover_modules
from chroma.utils.generator import assert_hslmap_condition, write_lua_colors
from chroma.utils.lua import runtime
from chroma.utils.paths import chroma_builtins_dir, chroma_dir
from chroma.utils.theme import parse_file

logger = Logger.get_logger()

# TODO: Make the generators into a class, just like integrations
GENERATORS_REGISTRY: dict[str, Callable] = {}


def generate(
    name: str,
    image_path: Path | str,
    output_path: Path | str | None = None,
    **kwargs,
) -> dict[str, Color] | None:
    """
    If `output_path` is None, then the colors are returned as a dict of color
    name and the resultant color object. Otherwise, the color is converted to
    a lua theme and written to the output path provided it is valid.
    """

    # Discover generators and add them to the registry
    generators = discover_modules(chroma_dir() / "generators")
    for generator in generators:
        if hasattr(generator, "register") and callable(getattr(generator, "register")):
            entry = getattr(generator, "register")()
            GENERATORS_REGISTRY.update(entry)
            for name in entry:
                logger.debug(f"Registered generator '{name}'")

    generator = GENERATORS_REGISTRY.get(name)
    if generator is None:
        raise ValueError(f"Backend '{name}': no such backend")

    config = parse_file(runtime(), chroma_builtins_dir() / "config.lua")

    hslmap = {
        k: assert_hslmap_condition(v) for k, v in config["generators"]["hslmap"].items()
    }

    image_path = Path(image_path)
    theme = generator(
        image_path=image_path,
        hsl_map=hslmap,
        colors_map=config["generators"]["colors"],
        **kwargs,
    )

    if output_path is None:
        return theme
    else:
        output_path = Path(output_path)
        write_lua_colors(output_path, theme)
