from pathlib import Path
from typing import Callable

from chroma.colors import Color
from chroma.logger import Logger
from chroma.utils.dynamic import discover_modules
from chroma.utils.generator import write_lua_colors
from chroma.utils.paths import chroma_dir

logger = Logger.get_logger()

# TODO: Make the generators into a class, just like integrations
GENERATORS_REGISTRY: dict[str, Callable] = {}


def prepare():
    generators = discover_modules(chroma_dir() / "generators")

    for generator in generators:
        if hasattr(generator, "register") and callable(getattr(generator, "register")):
            entry = getattr(generator, "register")()
            GENERATORS_REGISTRY.update(entry)
            for name in entry:
                logger.debug(f"Registered generator '{name}'")


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
    prepare()
    generator = GENERATORS_REGISTRY.get(name)
    if generator is None:
        raise ValueError(f"Backend '{name}': no such backend")

    image_path = Path(image_path)
    theme = generator(image_path, **kwargs)

    if output_path is None:
        return theme
    else:
        output_path = Path(output_path)
        write_lua_colors(output_path, theme)
