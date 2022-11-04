# -*- coding: utf-8 -*-
import os


def xtest_xray_markers(testdir):
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


def xtest_xray_server(testdir):
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
        "--xray-plan-key=XMPL-125 --xray-fail-silently=True --server=True")
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


def test_xray_communication(testdir):
    secrets_file = os.path.join(os.path.dirname(os.path.dirname(
        os.path.realpath(__file__))), 'secrets')
    if not os.path.exists(secrets_file):
        return
    with open(secrets_file, 'r') as infile:
        secrets = infile.read()
    test_secrets_file = testdir.makefile('.ini', secrets)
    test_example = """
    import pytest

    pytest_plugins = "pytester"

    @pytest.mark.xray(test_key="DEMO-4")
    def test_always_pass():
        assert True
    """
    testdir.makepyfile(test_example)
    result = testdir.runpytest(
        "--xray-plan-key", "DEMO-8",
        "--secrets", str(test_secrets_file))
    assert len(result.errlines) == 0
