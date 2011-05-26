-----
About
-----

Colorful replacement for Django's testrunner

* Makes your test output more colorful
* Profile report for all tests methods

------------
Installation
------------

To install the latest stable version::

	pip install git+git://github.com/neubloc/django-colortools#egg=django-colortools



At the current state you don't need to include ``colortools`` in your 
``INSTALLED_APPS`` but you could still do it if you want to run tests from
``colortools``::

	INSTALLED_APPS = (
	    'colortools',
	    ...
	)

Specify test runner class::

	TEST_RUNNER = "colortools.test.ColorDjangoTestSuiteRunner"

or::

	TEST_RUNNER = "colortools.test.ColorProfilerDjangoTestSuiteRunner"

The first test runner class will only add colors to your report. The second will also 
generate pstats report for all test methods.
 
Additionally you can define a list of apps to test::

	TEST_APPS = (
		'userprofile',
		...
	)

-----
Usage
-----

Just run your test using manage-admin.py's ``test`` command.
