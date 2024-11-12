def test_plugin_manager():
    from transport_data.util.pluggy import pm

    assert 9 == len(pm.list_name_plugin())
