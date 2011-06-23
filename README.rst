-----
About
-----

Colorful replacement for Django's testrunner

* Makes your test output more colorful
* Profile report for all tests methods
* Runs you fixture heavy TestCases much faster
* Reports db queries count for each test 

------------
Installation
------------

The code has been tested only on Django 1.3. It does some nasty monkey patching on 
TestCase and TransactionTestCase classes so be careful. 

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
 
Additionally you can define a list of apps to test to exclude tests from django
and other installed libraries::

	TEST_APPS = (
		'userprofile',
		...
	)

If you want to include info about query counts in the final report of 
ColorProfilerDjangoTestSuiteRunner then add following line to your settings::

	TEST_COUNT_QUERIES = True
	
The routine that counts queries works similarly to the assertNumQueries function
from the TransactionTestCase class. Because of that there is that the numbers you
will see in the results are not 100% accurate. This will be the case if you will
use assertNumQueries in your test with will also call some requests (By default
start_request signal clears queries statistics). 

If you think that profiler report is to long you can limit amount of functions
included by defining following setting:

    TEST_PROFILER_REPORT_LIMIT = 20
   
You can use integer or float value. Values less or equal zero will discard the
limit.

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

If you were using Profiler class then you can print profiler report using manage.py
command::

    python manage.py teststats
 
 This will print almost the same report that you can see after running the test
 command. The only difference is that you won't see queries count info event if
 the TEST_QUERIES_COUNT is set to True.
 
 Use switch --help to see other options available for this commands. Examples:
 
    python manage.py teststats --order=time
 
 Changes default ordering
 
    python manage.py teststats "" 10
 
 Prints report for all functions (not only named test_*) and limit the results to 
 10 functions.
 
    python manage.py teststats "test_create_object" --report=callees
    python manage.py teststats "test_create_object" --report=callers

First command prints all callees for functions that match "test_create_object"
The second prints all callers for the same set of functions.

If you want you can also use this command to interact with other results file from 
pstats library - just use --file switch to change the file used by the command.