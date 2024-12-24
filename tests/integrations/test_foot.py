from chroma import theme

def test_foot_integration(global_setup_teardown, fixtures):
    tmpdir = global_setup_teardown

    # Load foot integration
    with open(fixtures / "integrations/foot.lua", mode="r") as f:
        integration = f.readlines()
    integration = "".join(integration).format(outpath=tmpdir)

    # Load substitution template
    with open(fixtures / "template.lua", mode="r") as f:
        template = f.readlines()
    template = "".join(template).format(luaintegrations=integration)

    # Run the integration parsing
    theme.load(lua=template)

    # Asserts
    assert (tmpdir / "out.foot").exists(), "Output file does not exist"
