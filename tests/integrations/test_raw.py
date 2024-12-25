from chroma import theme

def test_raw_integration(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown

    # Load raw integration
    with open(fixtures / "integrations/raw.lua", mode="r") as f:
        integration = f.readlines()
    integration = "".join(integration).format(outpath=tmpdir)

    # Load substitution template
    with open(fixtures / "template.lua", mode="r") as f:
        template = f.readlines()
    template = "".join(template).format(luaintegrations=integration)

    # Run the integration parsing
    theme.load(lua=template)

    # Asserts
    assert (tmpdir / "out.raw").exists(), "Output file does not exist"
