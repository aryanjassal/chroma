from chroma.colors import ColorRGB
from chroma.colors.base import Color
from chroma.colors.utils import check_types


def test_create_color():
    color = ColorRGB(0, 0, 0)
    assert type(color) == ColorRGB
    assert isinstance(color, Color)

    try:
        color = ColorRGB(999, 0, 0)
    except ValueError:
        assert True
    except:
        assert False

    try:
        color = ColorRGB(0, 0.0, 0)
    except TypeError:
        assert True
    except:
        assert False


def test_check_normalization_denormalization():
    color = ColorRGB(0, 0, 0)

    color = color.normalized()
    assert check_types(color.color, float)
    assert color.r >= 0 and color.r <= 255
    assert color.g >= 0 and color.g <= 255
    assert color.b >= 0 and color.b <= 255

    color = color.denormalized()
    assert check_types(color.color, int)
    assert color.r >= 0 and color.r <= 255
    assert color.g >= 0 and color.g <= 255
    assert color.b >= 0 and color.b <= 255
