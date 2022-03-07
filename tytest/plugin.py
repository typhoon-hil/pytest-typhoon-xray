# -*- coding: utf-8 -*-

from datetime import datetime
import importlib
import os
import pytest
import sys
from .utils import read_or_get
from .xray_api import make_initial_test_result, send_test_results, \
    add_remote_link
from .runtime_settings import Config, Settings, Stats, TestExecutionResult


def pytest_addoption(parser):
    group = parser.getgroup('tytest')
    group.addoption(
        '--runconfig',
        dest='runconfig',
        help='Test parameters script')
    group.addoption(
        '--secrets',
        dest='secrets',
        help='Full path to secrets file')
    group.addoption(
        '--xray-plan-key',
        dest='xray_plan_key',
        help='Xray test plan key')
    group.addoption(
        '--xray-fail-silently',
        dest='xray_fail_silently',
        default='False',
        help='Ignore Xray communication errors')
    group.addoption(
        '--web-url',
        dest='web_url',
        help='Web link to be added to the test execution report')
    group.addoption(
        '--server',
        dest='server',
        default='False',
        help='Indicate the use of Xray Server+DC instead of Xray Cloud')


@pytest.fixture
def runconfig(request):
    return request.config.option.runconfig


@pytest.fixture
def secrets(request):
    return request.config.option.secrets


@pytest.fixture
def xray_plan_key(request):
    return request.config.option.xray_plan_key


@pytest.fixture
def xray_fail_silently(request):
    return request.config.option.xray_fail_silently


@pytest.fixture
def web_url(request):
    return request.config.option.web_url


@pytest.fixture
def server(request):
    return request.config.option.server


def pytest_configure(config):
    # import runtime configuration module
    file_name = config.getoption('runconfig')
    if file_name and os.path.isfile(file_name):
        Settings.RUN_CONFIG = file_name
        dirname, basename = os.path.split(os.path.abspath(file_name))
        sys.path.append(dirname)
        if basename.endswith('.py'):
            module_name = os.path.splitext(basename)[0]
        else:
            module_name = file_name
        importlib.invalidate_caches()
        module = importlib.import_module(module_name)
        if module:
            for key, value in module.__dict__.items():
                if not key.startswith('_'):
                    setattr(Config, key, value)

    # register mark for Xray
    config.addinivalue_line(
        'markers',
        'xray(test_key): Issue key of the test in Xray')

    Settings.XRAY_PLAN_KEY = config.getoption('xray_plan_key')
    Settings.XRAY_FAIL_SILENTLY = \
        config.getoption('xray_fail_silently') == 'True'
    Settings.WEB_URL = config.getoption('web_url')
    Settings.XRAY_SERVER = config.getoption('server') == 'True'

    # initialize secret params
    secrets = config.getoption('secrets')
    Settings.XRAY_HOST = read_or_get(
        secrets, 'XRAY_HOST', 'https://xray.cloud.getxray.app')
    Settings.XRAY_CLIENT_ID = read_or_get(secrets, 'XRAY_CLIENT_ID', '')
    Settings.XRAY_CLIENT_SECRET = read_or_get(
        secrets, 'XRAY_CLIENT_SECRET', '')
    Settings.JIRA_HOST = read_or_get(secrets, 'JIRA_HOST', '')
    Settings.JIRA_USER = read_or_get(secrets, 'JIRA_USER', '')
    Settings.JIRA_TOKEN = read_or_get(secrets, 'JIRA_TOKEN', '')
    Settings.JIRA_AUTH = (Settings.JIRA_USER, Settings.JIRA_TOKEN)

    Stats.START_TIME = datetime.now()


def pytest_collection_modifyitems(config, items):
    for item in items:
        _store_item(item)


def pytest_terminal_summary(terminalreporter):
    PASSED = 'PASS' if Settings.XRAY_SERVER else 'PASSED'
    FAILED = 'FAIL' if Settings.XRAY_SERVER else 'FAILED'
    SKIPPED = 'SKIP' if Settings.XRAY_SERVER else 'SKIPPED'
    Stats.END_TIME = datetime.now()
    result = make_initial_test_result(
        start_time=Stats.START_TIME, end_time=Stats.END_TIME)
    _fill_keys(terminalreporter.stats, 'passed')
    _fill_keys(terminalreporter.stats, 'failed')
    _fill_keys(terminalreporter.stats, 'skipped')

    for key, values in TestExecutionResult.xray_keys.items():
        test = {'testKey': key, 'status': PASSED, 'comment': ''}
        stat_counter = {'passed': 0, 'failed': 0, 'skipped': 0}
        for item in values:
            if test['status'] == PASSED and item.outcome == 'failed':
                test['status'] = FAILED
            stat_counter[item.outcome] += 1
            test['comment'] += f'{item.outcome.upper()}: {item.nodeid}\n'
            if item.outcome == 'failed':
                test['comment'] += str(item.longrepr) + '\n'
        total = len(values)
        test['comment'] = _stat(PASSED, stat_counter['passed'], total) + \
            "   " + _stat(FAILED, stat_counter['failed'], total) + \
            "   " + _stat(SKIPPED, stat_counter['skipped'], total) + "\n" + \
            test['comment']
        result['tests'].append(test)
    new_issue = send_test_results(result)
    print(new_issue)
    if Settings.WEB_URL and new_issue is not None:
        issue_id = new_issue['testExecIssue']['id'] \
            if Settings.XRAY_SERVER else new_issue['id']
        add_remote_link(issue_id, Settings.WEB_URL, 'Web report')


def pytest_sessionfinish(session):
    pass


def _fill_keys(stats, outcome):
    if outcome in stats:
        for stat in stats[outcome]:
            try:
                xray_key = TestExecutionResult.functions[stat.nodeid]
            except KeyError:
                continue
            try:
                TestExecutionResult.xray_keys[xray_key].append(stat)
            except KeyError:
                TestExecutionResult.xray_keys[xray_key] = [stat]


def _get_xray_marker(item):
    return item.get_closest_marker('xray')


def _store_item(item):
    marker = _get_xray_marker(item)
    if not marker:
        return
    test_key = marker.kwargs['test_key']
    TestExecutionResult.functions[item.nodeid] = test_key


def _stat(type, counter, total):
    return f"{type}: {counter} ({round(counter/total*100, 2)}%)"
