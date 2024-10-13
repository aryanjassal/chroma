from pathlib import Path

from chroma import utils
from chroma.logger import Logger

logger = Logger.get_logger()

BACKENDS = {}


def prepare():
    backends = utils.discover_modules(utils.chroma_dir() / "backends")

    for backend in backends:
        if hasattr(backend, "register") and callable(getattr(backend, "register")):
            entry = getattr(backend, "register")()
            BACKENDS.update(entry)
            for name in entry:
                logger.debug(f"Registered generator backend {name}")


def generate(backend: str, image_path: Path | str, output_path: Path | str, **kwargs):
    prepare()
    generator = BACKENDS.get(backend)
    if generator is None:
        logger.fatal(f"Backend {backend}: no such backend")

    image_path = Path(image_path)
    theme = generator(image_path, **kwargs)

    output_path = Path(output_path)
    utils.write_lua_colors(output_path, theme)
