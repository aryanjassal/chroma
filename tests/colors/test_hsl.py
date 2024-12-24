from chroma.colors import ColorHSL
from chroma.colors.base import Color
from chroma.colors.utils import check_types


def test_create_color():
    color = ColorHSL(0, 0, 0)
    assert type(color) is ColorHSL
    assert isinstance(color, Color)

    try:
        color = ColorHSL(999, 0, 0)
    except ValueError:
        assert True
    except:
        assert False

    try:
        color = ColorHSL(0, 0.0, 0)
    except TypeError:
        assert True
    except:
        assert False


def test_check_normalization_denormalization():
    color = ColorHSL(0, 0, 0)

    color = color.normalized()
    assert check_types(color.color, float)
    assert all([(x >= 0.0 and x <= 1.0) for x in color.color])

    color = color.denormalized()
    assert check_types(color.color, int)
    assert color.h >= 0 and color.h <= 360
    assert color.s >= 0 and color.s <= 100
    assert color.l >= 0 and color.l <= 100


def test_check_darken_lighten():
    color = ColorHSL(0.5, 0.5, 0.5)
    assert color.darkened(0.25).l == 0.25
    assert color.darkened(1.0).l == 0.0
    assert color.lightened(0.25).l == 0.75
    assert color.lightened(1.0).l == 1.0


def test_check_saturate_desaturate():
    color = ColorHSL(0.5, 0.5, 0.5)
    assert color.saturated(0.25).s == 0.75
    assert color.saturated(1.0).s == 1.0
    assert color.desaturated(0.25).s == 0.25
    assert color.desaturated(1.0).s == 0.0
