# -*- coding: utf-8 -*-


class PluginError(Exception):
    """Base exception class"""
    pass


class ConfigurationError(PluginError):
    """Errors in runtime configuration"""
    pass


class CommunicationError(PluginError):
    """Base exception class"""
    pass


class XrayError(CommunicationError):
    """Represents an error in communication with Xray"""
    pass


class XrayAuthError(XrayError):
    """Xray authentication error"""
    pass


class XraySubmissionError(XrayError):
    """Xray test execution submission error"""
    pass


class JiraError(CommunicationError):
    """Represents an error in communication with JIRA"""
    pass
