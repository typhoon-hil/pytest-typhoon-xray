# -*- coding: utf-8 -*-

from configparser import ConfigParser
import csv
from itertools import chain
import os
from .exceptions import ConfigurationError


def csvfile(file_name):
    result = []
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) == 1:
                result.append(row[0])
            else:
                result.append(row)
    return result


def get_variable(variable_name, default_value):
    if variable_name in os.environ:
        return os.environ[variable_name]
    else:
        return default_value


def read_variable(file_name, variable_name):
    if not file_name:
        return None
    parser = ConfigParser()
    try:
        with open(file_name) as lines:
            lines = chain(("[top]",), lines)
            parser.read_file(lines)
        return parser['top'][variable_name]
    except IOError:
        raise ConfigurationError(f'File could not be read: {file_name}')
    except KeyError:
        return None


def read_or_get(file_name, variable_name, default_value=None):
    return read_variable(file_name, variable_name) or \
        get_variable(variable_name, default_value)
