"""
Creates a dynamically generated color palette.
"""

from pathlib import Path

import chroma
from chroma import utils
from chroma.colors import Color
from chroma.handler import Handler
from chroma.logger import Logger

logger = Logger.get_logger()


def generate_header(template) -> str:
    variables = {"header": chroma.CHROMA_GENERATED_HEADER}
    return template.format(**variables)


def generate_colors(template, variables) -> str:
    return template.format(**variables)


class RawHandler(Handler):
    def apply(self):
        for name, attr in self.group.items():
            header_template = attr.get("header")
            header = None
            if header_template is not None:
                header = generate_header(header_template)

            if not utils.validate_header(
                Path(attr["out"]), header, attr.get("force", False)
            ):
                logger.error(f"Cannot write configuration for {name}. Skipping group.")
                continue

            generated_file = []
            if header is not None:
                generated_file.append(header)

            for col_name, col_value in attr["colors"].items():
                col = Color(col_value, "hex")
                variables = {
                    "name": col_name,
                    "hex": col.as_format("hex"),
                    "hexval": col.as_format("hexval"),
                }
                color = generate_colors(attr["format"], variables)
                generated_file.append(color)

            # Manually insert newlines to make it play well with file.writelines()
            generated_file = [line + "\n" for line in generated_file]

            try:
                with open(Path(attr["out"]).expanduser(), "w") as f:
                    f.writelines(generated_file)
                logger.info(f"Successfully generated theme for {name}!")
            except FileNotFoundError as e:
                logger.error(e)
                logger.error("Failed to open file. Does the parent directory exist?")
                continue

        logger.info("Successfully generated raw themes!")


def register():
    return {"raw": RawHandler}
