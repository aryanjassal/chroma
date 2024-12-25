import random

from chroma import theme


def map_suffix(integration: str) -> list[str]:
    suffix_map = {
        "gtk": ["gtk3", "gtk4"]
    }
    # Default case: return integration itself
    return suffix_map.get(integration, [integration])


def test_all_integrations(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown
    integration_dir = fixtures / "integrations"

    # Load all integrations
    integrations = []
    integration_map = {}
    files = [file for file in integration_dir.iterdir() if file.is_file()]
    for file in files:
        with open(file, mode="r") as f:
            integration = "".join(f.readlines()).format(outpath=tmpdir)
        integrations.append(integration)

        for name in map_suffix(file.stem):
            integration_map[integration] = tmpdir / f"out.{name}"

    # Randomly select a selection to test
    n = random.randint(1, len(integrations) - 1)
    selection = random.choices(integrations, k=n)
    expected_out_paths = [v for k, v in integration_map.items() if k in selection]
    selection = "\n".join(selection)

    # Load substitution template
    with open(fixtures / "template.lua", mode="r") as f:
        template = f.readlines()
    template = "".join(template).format(luaintegrations=selection)

    # Run the integration parsing
    theme.load(lua=template)

    # Asserts
    for path in expected_out_paths:
        assert path.exists(), f"Output file for {path} does not exist"
