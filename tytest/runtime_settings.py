# -*- coding: utf-8 -*-

class Config:
    pass


class Settings:
    XRAY_HOST = ''
    XRAY_CLIENT_ID = ''
    XRAY_CLIENT_SECRET = ''
    XRAY_PLAN_KEY = ''
    XRAY_FAIL_SILENTLY = False
    XRAY_TOKEN = ''
    JIRA_HOST = ''
    JIRA_USER = ''
    JIRA_PASSWORD = ''
    JIRA_AUTH = []
    RUN_CONFIG = ''
    WEB_URL = ''
    XRAY_SERVER = False


class Stats:
    START_TIME = None
    END_TIME = None


class TestExecutionResult:
    xray_keys = {}
    functions = {}
