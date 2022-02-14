# -*- coding: utf-8 -*-

from datetime import datetime
from json import JSONDecodeError

import requests
from tzlocal import get_localzone
from .runtime_settings import Settings
from .exceptions import XrayAuthError, XraySubmissionError, JiraError


def to_xray_timestamp(ts):
    local_tz = get_localzone()
    aware_ts = ts.replace(tzinfo=local_tz)
    text = aware_ts.strftime('%Y-%m-%dT%H:%M:%S%z')
    return text[:-2] + ':' + text[-2:]


def authenticate_xray():
    if not Settings.XRAY_TOKEN:
        credentials = {'client_id': Settings.XRAY_CLIENT_ID,
                       'client_secret': Settings.XRAY_CLIENT_SECRET}
        r = requests.post(
            f'{Settings.XRAY_HOST}/api/v1/authenticate',
            json=credentials)
        if r.status_code != 200 and not Settings.XRAY_FAIL_SILENTLY:
            raise XrayAuthError
        Settings.XRAY_TOKEN = r.json()
    return {'Authorization': f'Bearer {Settings.XRAY_TOKEN}'}


def send_test_results(test_results):
    if Settings.XRAY_SERVER:
        headers = {
            'Authorization': 'Bearer {Settings.JIRA_TOKEN}',
            'Content-type': 'application/json'
        }
        r = requests.post(f'{Settings.XRAY_HOST}/rest/raven/1.0/import/execution',
                          headers=headers, json=test_results)
    else:
        headers = authenticate_xray()
        r = requests.post(f'{Settings.XRAY_HOST}/api/v1/import/execution',
                          headers=headers, json=test_results)
    if r.status_code != 200 and not Settings.XRAY_FAIL_SILENTLY:
        raise XraySubmissionError
    try:
        output = r.json()
        return output
    except JSONDecodeError as e:
        return None


def add_remote_link(issue_id, remote_link, title,
                    icon_url='http://allure.qatools.ru/img/favicon.ico'):
    req = {
        'object': {
            'url': remote_link,
            'title': title,
            'icon': {
                'url16x16': icon_url,
                'title': 'Report details'
            }
        }
    }
    r = requests.post(
        f'{Settings.JIRA_HOST}/rest/api/2/issue/{issue_id}/remotelink',
        auth=Settings.JIRA_AUTH, json=req)
    if r.status_code != 200 and not Settings.XRAY_FAIL_SILENTLY:
        raise JiraError
    output = r.json()
    return output


def make_initial_test_result(
        start_time=datetime.now(),
        end_time=datetime.now(),
        summary=f'Execution of plan {Settings.XRAY_PLAN_KEY}'):
    return {
        'info': {
            'summary': summary,
            'startDate': to_xray_timestamp(start_time),
            'finishDate': to_xray_timestamp(end_time),
            'testPlanKey': Settings.XRAY_PLAN_KEY,
            'testEnvironments': []
        },
        'tests': []
    }
