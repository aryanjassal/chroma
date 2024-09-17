import importlib
from pathlib import Path

from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
default_theme = Path(__name__).parent.joinpath('themes/default.lua').resolve()

if __name__ == "__main__":
    with open(default_theme, "r") as f:
        script = f.read()

    theme = lua.execute(script)

    for name, config in theme.items():
        print(f" INFO  Applying theme for {name}")
        try:
            handler = importlib.import_module(f"handlers.{name}")
            handler.apply(config)
        except ImportError:
            print(f" WARN  No handlers found for {name}. Skipping.")
        except AttributeError:
            print(
                f" WARN  The handler for {name} does not implement 'apply()'."
                "Skipping."
            )
        except:
            print(f" EROR  An unhandled exception occured while applying themes")
            exit(1)
