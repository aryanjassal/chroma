import importlib.util
from pathlib import Path

from chroma.logger import Logger

logger = Logger.get_logger()


def load_module(path: str | Path):
    """Dynamically load a handler from a file path."""

    module_name = Path(path).stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)
            return module
        else:
            logger.fatal(f"Could not load module {module_name}")
    else:
        logger.fatal(f"Could not load module {module_name}")


def discover_modules(path: str | Path):
    """Discover and load all handlers from a directory."""

    config_dir = Path(path).expanduser()
    modules = []

    if Path(config_dir).is_dir():
        for filename in Path(config_dir).iterdir():
            if filename.suffix == ".py":
                module_path = Path(config_dir) / filename
                module = load_module(module_path)
                modules.append(module)
    return modules
