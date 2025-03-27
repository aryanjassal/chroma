from pathlib import Path
from typing import Optional, cast

from chroma.colors import Color, ColorHSL
from chroma.logger import Logger
from chroma.types import HSLMap, HSLMapField, HSLMapValue
from chroma.utils.tools import closest, flatten

logger = Logger.get_logger()


# TODO: Add "closest match" to result instead of returning immediately
def match_color_from_hslmap(
    color: Color,
    condition_map: HSLMap,
    ignore: list[str] = list(),
) -> Optional[str]:
    """Takes in a color and a condition map, then returns the first color that
    satisfies any condition.

    The color is converted to HSL format, then each value (hue, saturation,
    luminance) is checked against a condition. If the condition is `None`,
    any value will match that condition. Otherwise, if it is a tuple, then
    the value will pass the check only if it falls between the first and
    second conditions. For more information about the structure of the map,
    see below.

    The first key, or the name of the color, is returned from the map which
    satisfies the condition. As such, keep very permissive colors like black
    or white at the end. If any conditions for all keys are not met, then
    `None` is returned. That means that there were no matches in the condition
    map.

    If you want to omit a color from future detections, either add the name to
    the `ignore` list, or remove it's condition from the map. Otherwise, if a
    key with lenient conditions is near the top, all colors will match that
    instead.

    Note that there is no concept of "closest match". This function does not
    check a color to figure out if the color is closer to black or blue. The
    first condition which the color matches is returned.

    The condition map must follow the following structure.

    ```py
    # It is a dict
    condition_map = dict()

    # Each condition is a tuple of upper and lower bound.
    # In this condition, the hue must be between 0-10, the saturation between
    # 50-80, and any luminance value.
    hue = (0, 10)
    saturation = (50, 80)
    luminance = None
    condition = (hue, saturation, luminance)

    # Each entry in the map is indexed by the key it will return if the
    # condition is matched.
    condition_map["key"] = condition

    # To match multiple ranges, each range can be included as a part of a list.
    # This condition will be true if the hue is either between 0 and 10, or
    # between 50 and 60.
    hue = [(0, 10), (50, 60)]
    condition = (hue, None, None)

    # This can be written more concisely as follows, but it is harder to read.
    condition = ([(0, 10), (50, 60)], (50, 80), None)
    ```
    """

    # Get the separated HSL values for the color. Note that by default, the
    # return type of `Color.color` is all its possible values. For `ColorHSL`,
    # it is `int | float`. We know `denormalize()` will return `int`s, so we can
    # manually cast it and appease the linter.
    hsl = color.cast(ColorHSL).denormalize().color
    h, s, l = cast(tuple[int, int, int], hsl)
    for name, condition in condition_map.items():
        if (
            name not in ignore
            and check_value(h, condition[0])
            and check_value(s, condition[1])
            and check_value(l, condition[2])
        ):
            return name


def clamp_color_to_hslrules(
    color: Color,
    condition: HSLMapValue | None,
) -> ColorHSL:
    """Converts a color to satisfy the provided condition.

    The condition for each value of a HSL color is evaluated individually. If
    any value does not satisfy the condition, the value is instead changed by
    the smallest amount to ensure that it satisfies at least one of the
    defined conditions.

    If no changes are required, no changes will be made. If a `None` is provided
    as a condition for a value, then the value will not be changed.

    A denormalized color in HSL space is returned.

    The condition must follow the following structure.

    ```py
    # Each condition is a tuple of upper and lower bound.
    # In this condition, the hue must be between 0-10, the saturation between
    # 50-80, and any luminance value.
    hue = (0, 10)
    saturation = (50, 80)
    luminance = None
    condition = (hue, saturation, luminance)

    # To match multiple ranges, each range can be included as a part of a list.
    # This condition will be true if the hue is either between 0 and 10, or
    # between 50 and 60.
    hue = [(0, 10), (50, 60)]
    condition = (hue, None, None)

    # This can be written more concisely as follows, but it is harder to read.
    condition = ([(0, 10), (50, 60)], (50, 80), None)
    ```
    """

    # If the condition is none, then the color passes by default case
    if condition is None:
        return color.cast(ColorHSL)

    def get_closest_value(element: int, limits: HSLMapField):
        if limits is None:
            logger.warn(f"get_closest_value: cannot get closest for {limits}")
            return element

        valid_values = []
        flatten(limits, valid_values)
        return closest(valid_values, element)

    # Get the separated HSL values for the color. Note that by default, the
    # return type of `Color.color` is all its possible values. For `ColorHSL`,
    # it is `int | float`. We know `denormalize()` will return `int`s, so we can
    # manually cast it and appease the linter.
    hsl = color.cast(ColorHSL).denormalize().color
    h, s, l = cast(tuple[int, int, int], hsl)

    if not check_value(h, condition[0]):
        h = get_closest_value(h, condition[0])

    if not check_value(s, condition[1]):
        s = get_closest_value(s, condition[1])

    if not check_value(l, condition[2]):
        l = get_closest_value(l, condition[2])

    return ColorHSL(h, s, l)


def check_value(value: int, condition: HSLMapField):
    # Get a list of checks to perform on the color
    checks = []
    if type(condition) is tuple:
        checks = [condition]
    elif type(condition) is list:
        checks = condition
    elif condition is None:
        checks = [None]
    else:
        logger.error(f"Invalid type {type(condition)} for HSLMapField")

    results = []
    for check in checks:
        # None means no restriction. Any value goes. Check passes.
        if check is None:
            results.append(True)
            continue

        # If the value we need is in between the lower and upper limit, then
        # it is a valid value. Check passes.
        if check[0] <= value <= check[1]:
            results.append(True)
            continue

        # Otherwise, check fails.
        results.append(False)

    # If even a single check failed, then the value does not meet the
    # conditions.
    return all(results)


def write_lua_colors(path: Path, colors: dict, indent: int = 2):
    contents = []
    contents.append("return {\n")
    for name, color in colors.items():
        contents.append(f"{' ' * indent}{name} = \"{color}\",\n")
    contents.append("}")
    path.write_text("".join(contents))


def assert_hslmap_condition(condition) -> HSLMapValue:
    """
    Validates and converts a raw HSL map condition (list or tuple) to a Python HSLMapValue.

    :param condition: The raw condition to validate and convert.
    :return: A valid HSLMapValue.
    :raises ValueError: If the condition does not match the expected structure.
    """
    if not isinstance(condition, (list, tuple)) or len(condition) != 3:
        raise ValueError(
            f"Value {condition} does not match requirements for HSLMap condition"
        )

    def validate_field(field) -> HSLMapField:
        """Validates and converts a single field."""
        if field is None:
            return None

        if isinstance(field, list):
            # Check for multiple conditions
            if all(
                isinstance(pair, (list, tuple))
                and len(pair) == 2
                and all(isinstance(x, int) for x in pair)
                for pair in field
            ):
                return [tuple(pair) for pair in field]

            # Check for single condition
            if all(isinstance(val, int) for val in field) and len(field) == 2:
                return tuple(field)

            # Otherwise
            raise ValueError(f"Invalid field: {field}")

        raise ValueError(f"Invalid field: {field}")

    # Validate and convert all three fields
    return (
        validate_field(condition[0]),
        validate_field(condition[1]),
        validate_field(condition[2]),
    )
