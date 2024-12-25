from chroma import generator
from chroma.utils.theme import parse_file, runtime
from tests.utils import generate_name

def test_magick_aliases(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown
    generator.generate(
        name="imagemagick",
        image_path=fixtures / "images/image_small.jpg",
        output_path=tmpdir / generate_name(),
    )
    generator.generate(
        name="magick",
        image_path=fixtures / "images/image_small.jpg",
        output_path=tmpdir / generate_name(),
    )


def test_magick_output_file(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown
    filename = tmpdir / generate_name()

    retval = generator.generate(
        name="imagemagick",
        image_path=fixtures / "images/image_small.jpg",
        output_path=filename,
    )
    assert retval is None, f"Unexpected return value, expected None, got {retval}"

    # Check if the file has the correct number of lines
    lines = []
    with open(filename, mode="r") as f:
        lines = f.readlines()
    # Length - 2 for the `return {` and `}` lines
    assert len(lines) == 31, f"Number of output colors must be 29, got {len(lines) - 2}"

    # Check if the file is a valid lua file and returns a valid number of colors
    colors = parse_file(runtime(), filename)
    assert len(colors) == 29, f"Number of output colors must be 29, got {len(colors)}"


def test_magick_output_dict(fixtures):
    retval = generator.generate(
        name="imagemagick",
        image_path=fixtures / "images/image_small.jpg",
    )
    assert type(retval) is dict, f"Unexpected return value, expected dict, got {retval}"
    assert len(retval) == 29, f"Number of output colors must be 29, got {len(retval)}"
