# -*- coding: utf-8 -*-


def test_xray_markers(testdir):
    test_example = """
    import pytest

    pytest_plugins = "pytester"

    @pytest.mark.xray(test_key="XMPL-123")
    def test_1():
        pass

    @pytest.mark.xray(test_key="XMPL-124")
    def test_2():
        pass
    """
    testdir.makepyfile(test_example)
    result = testdir.runpytest(
        "--xray-plan-key=XMPL-125 --xray-fail-silently=True")
    assert len(result.errlines) == 0


def test_parameters(testdir):
    test_config = """
    param1 = range(10)
    param2 = ['a', 'b', 'c']
    """
    test_example = """
    import pytest
    from tytest.runtime_settings import Config as C

    pytest_plugins = "pytester"

    @pytest.mark.parametrize('param1', C.param1)
    @pytest.mark.parametrize('param2', C.param2)
    def test_1(param1, param2):
        pass
    """
    testdir.makepyfile(__init__="")
    testdir.makepyfile(runconfig=test_config)
    testdir.makepyfile(test_example)
    result = testdir.runpytest("--runconfig", "runconfig.py")
    assert len(result.errlines) == 0
