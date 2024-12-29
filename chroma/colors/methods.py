from . import Color, ColorHSL, ColorRGB
from .errors import IncompatibleColorError


def darken(color: Color, amount: float) -> Color:
    _type = type(color)
    darkened = color.cast(ColorHSL).darkened(amount)
    return darkened.cast(_type)


def lighten(color: Color, amount: float) -> Color:
    _type = type(color)
    lightened = color.cast(ColorHSL).lightened(amount)
    return lightened.cast(_type)


def saturate(color: Color, amount: float) -> Color:
    _type = type(color)
    saturated = color.cast(ColorHSL).saturated(amount)
    return saturated.cast(_type)


def desaturate(color: Color, amount: float) -> Color:
    _type = type(color)
    desaturated = color.cast(ColorHSL).desaturated(amount)
    return desaturated.cast(_type)


def blend(color1: Color, color2: Color, ratio: float) -> Color:
    _type1 = type(color1)
    _type2 = type(color2)

    if _type1 != _type2:
        raise IncompatibleColorError(
            f"Colors with type {_type1} and {_type2} cannot be blended together"
        )

    blended = color1.cast(ColorRGB).blended(color2, ratio)
    return blended.cast(_type1)  # The two types are guaranteed to be the same
