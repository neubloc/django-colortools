-----
About
-----

Colorful replacement for Django's testrunner

* Makes your test output more colorful
* Profile report for all tests methods
* Runs you fixture heavy TestCases much faster

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

----------
Test Boost
----------

It's pretty common to have many test cases that share the same set of fixtures. It's
also very common to have many test in your TestCase classes. The problem with Djano's
fixture loading routine (version 1.3) is that it loads all fixtures before each test.

If you would think of a fixture as a state of database then this approach is very
inefficient. A better approach would be to: 

1. Load a fixture set
2. Commit
3. Run test in transaction
4. Rollback (this will bring our database to a state from point 2.)
5. Repeat steps 3 and 4 for all test that shares the same fixture set
6. Dump data if necessary or add another fixtures to the set already loaded
7. Run next group of tests.  

-----
Usage
-----

Just run your test using manage-admin.py's ``test`` command.
