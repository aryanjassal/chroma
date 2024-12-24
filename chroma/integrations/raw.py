"""
Creates a dynamically generated color palette.
"""

from pathlib import Path

import chroma
from chroma.utils.theme import validate_header
from chroma.colors import ColorHex
from chroma.integration import Integration
from chroma.logger import Logger

logger = Logger.get_logger()


def generate_header(template) -> str:
    variables = {"header": chroma.CHROMA_GENERATED_HEADER}
    return template.format(**variables)


def generate_colors(template, variables) -> str:
    return template.format(**variables)


class RawIntegration(Integration):
    def apply(self):
        applied_count = 0
        for name, attr in self.group.items():
            header_template = attr.get("header")
            header = None
            if header_template is not None:
                header = generate_header(header_template)

            if not validate_header(
                Path(attr["out"]), header, attr.get("force", False)
            ):
                logger.error(f"Cannot write configuration for {name}. Skipping group.")
                continue

            generated_file = []
            if header is not None:
                generated_file.append(header)

            for col_name, col_value in attr["colors"].items():
                col = ColorHex(col_value)
                variables = {
                    "name": col_name,
                    "hex": col.color,
                    "hexval": col.value,
                }
                color = generate_colors(attr["format"], variables)
                generated_file.append(color)

            # Manually insert newlines to make it play well with file.writelines()
            generated_file = [line + "\n" for line in generated_file]

            try:
                with open(Path(attr["out"]).expanduser(), "w") as f:
                    f.writelines(generated_file)
                logger.info(f"Successfully generated theme for {name}!")
                applied_count += 1
            except FileNotFoundError as e:
                logger.error(e)
                logger.error("Failed to open file. Does the parent directory exist?")
                continue

        if applied_count > 0 or len(self.group) == 0:
            logger.info("Successfully generated raw themes!")
        else:
            logger.error("Failed to apply one or more raw themes")


def register():
    return {"raw": RawIntegration}
