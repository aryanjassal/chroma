from chroma import theme

def test_gtk_integration(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown

    # Load gtk integration
    with open(fixtures / "integrations/gtk.lua", mode="r") as f:
        integration = f.readlines()
    integration = "".join(integration).format(outpath=tmpdir)

    # Load substitution template
    with open(fixtures / "template.lua", mode="r") as f:
        template = f.readlines()
    template = "".join(template).format(luaintegrations=integration)

    # Run the integration parsing
    theme.load(lua=template)

    # Asserts
    assert (tmpdir / "out.gtk3").exists(), "Output file does not exist"
    assert (tmpdir / "out.gtk4").exists(), "Output file does not exist"
