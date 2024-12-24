from pathlib import Path
from typing import Callable

from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

# TODO: Make the generators into a class, just like handlers
GENERATORS_REGISTRY: dict[str, Callable] = {}


def prepare():
    generators = utils.discover_modules(utils.chroma_dir() / "generators")

    for generator in generators:
        if hasattr(generator, "register") and callable(getattr(generator, "register")):
            entry = getattr(generator, "register")()
            GENERATORS_REGISTRY.update(entry)
            for name in entry:
                logger.debug(f"Registered generator '{name}'")


def generate(name: str, image_path: Path | str, output_path: Path | str, **kwargs):
    prepare()
    generator = GENERATORS_REGISTRY.get(name)
    if generator is None:
        raise ValueError(f"Backend '{name}': no such backend")

    image_path = Path(image_path)
    theme = generator(image_path, **kwargs)

    output_path = Path(output_path)
    utils.write_lua_colors(output_path, theme)
