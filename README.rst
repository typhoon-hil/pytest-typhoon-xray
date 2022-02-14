===================
pytest-typhoon-xray
===================

.. image:: https://img.shields.io/pypi/v/pytest-typhoon-xray.svg
    :target: https://pypi.org/project/pytest-typhoon-xray
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-typhoon-xray.svg
    :target: https://pypi.org/project/pytest-typhoon-xray
    :alt: Python versions

.. image:: https://www.travis-ci.org/typhoon-hil/pytest-typhoon-xray.svg?branch=master
    :target: https://travis-ci.org/typhoon-hil/pytest-typhoon-xray
    :alt: See Build Status on Travis CI

Typhoon HIL pytest integration with Jira and Xray
=================================================


Features
--------

* specify test parameters in a python module
* reference them in `pytest.mark.parametrize` decorators
* mark tests as Jira+Xray issues
* send test reports directly to Xray using Xray's REST API
* embed a URL to the test execution report in Xray


Requirements
------------

* pytest 5+
* pytz, tzlocal
* requests 2.23+


Installation
------------

You can install "pytest-typhoon-xray" via `pip`_ from `PyPI`_::

    $ pip install pytest-typhoon-xray


Usage
-----

Credentials for Jira and Xray
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Put credentials needed to access Jira and Xray in environment variables or a
file.

* `XRAY_HOST`: Xray URL, defaults to `https://xray.cloud.getxray.app`
* `XRAY_CLIENT_ID`: Client ID of your Xray API key
* `XRAY_CLIENT_SECRET`: Client secret of your Xray API key
* `JIRA_HOST`: Your Jira host, probably `https://mycompany.atlassian.net`
* `JIRA_USER`: Your Jira account username, probably your email address
* `JIRA_TOKEN`: Your Jira API token, **not your password**

You can define credentials as environment variables::

    export XRAY_CLIENT_ID=...
    export XRAY_CLIENT_SECRET=...


Or you can store credentials in a file, for example, `/private/secrets`::

    XRAY_CLIENT_ID=...
    XRAY_CLIENT_SECRET=...
    ...

Don't put the variable values in quotes.

If you use a file to store credentials, you should use the `secrets` command
line parameter::

    pytest --secrets=/private/secrets

If you use an Xray Server+DC installation, rather than Xray Cloud, you must
specify::

    pytest --server=True

so that the plugin knows which type of Xray deployment is in use.

Test parameters defined in Python modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a test parameter definition file as a Python module, such as this::

    # myparams.py
    import numpy as np

    v_range = [277.0, 278.0]
    f_range = np.arange(58, 63, 0.2)
    vdc_range = [820.0]

    class StayConnected:
        voltage_dip_perc = [22, 45, 85, 95]
        dip_total_time_pu = 0.95


All module attributes will be available at runtime as
`tytest.runtime_settings.Config.attr_name`, for example::

    from tytest.runtime_settings import Config as C

    @python.mark.parametrize('v_range', C.v_range)
    def test_something(v_range):
        pass


Specify which parameter definition file you are using in command line::

    pytest --runconfig=myparams.py


Marking tests for Xray reporting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mark your tests with Jira issue keys, such as this::

    @pytest.mark.xray(test_key='PRJ-123')
    def test_something():
        pass

Associate your test run with a test plan in Xray using the test plan key::

    pytest --xray-plan-key=DEMO-1234


If you want to ignore potential networking errors while submitting test
reports to Xray, turn this flag on::

    pytest --xray-plan-key=DEMO-1234 --xray-fail-silently=True


Embedding a web link in execution report
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you generate an Allure report during a test run, you can embed the link
to the report in Xray's test execution issue by using this command line
parameter::

    pytest web-url=https://jenkins.mycompany.com/my_job/123/allure


Command-line parameter summary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pytest invocation now has some additional command line parameters::

  --runconfig=RUNCONFIG
                        Specify test config script
  --secrets=SECRETS     Full path to secrets file
  --xray-plan-key=XRAY_PLAN_KEY
                        Key of the Xray issue that represents the test plan that is being run
  --xray-fail-silently=XRAY_FAIL_SILENTLY
                        Ignore Xray communication errors
  --web-url=WEB_URL
                        URL pointing to the Allure report
  --server=XRAY_SERVER
                        Flag to indicate that Xray Server+DC is used instead of Xray Cloud

An example of invoking `pytest`::

    pytest --runconfig=myparams.py --secrets=/private/secrets --xray-plan-key=PRJ-321 --xray-fail-silently=True --web-url=https://jenkins.mycompany.com/my_job/123/allure


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-typhoon-xray" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/mbranko/pytest-tytest/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
