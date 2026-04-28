def test_plugin_manager() -> None:
    from transport_data.util.pluggy import pm

    assert 10 == len(pm.list_name_plugin())
