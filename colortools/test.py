#
# Copyright 2011 by Neubloc, LLC. All rights reserved.
# Author: Szymon Rajchman
#

import time

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.test.simple import DjangoTestSuiteRunner
from django.utils.unittest.runner import TextTestResult, TextTestRunner, registerResult
from django.utils import termcolors
from django.utils import unittest


_COLORS = {
    'FAIL': {'fg': 'red', 'opts': ('bold', 'noreset')},
    'SUCCESS': {'fg': 'green', 'opts': ('bold', 'noreset')},
    'EXPECTED': {'fg': 'cyan', 'opts': ('bold', 'noreset')},
    'UNEXPECTED': {'fg': 'magenta', 'opts': ('bold', 'noreset')},
    'SKIP': {'fg': 'yellow', 'opts': ('bold', 'noreset')},
    'ERROR': {'fg': 'yellow', 'opts': ('bold', 'noreset')},
}

class _ColorDecorator(object):
    """Used to decorate output with ANSI colors"""

    def __init__(self, stream):
        self.stream = stream
        self.style = {}

        for code, params in _COLORS.items():
            self.style[code] = termcolors.make_style(**params)

        self.reset = termcolors.make_style(opts=('reset'))

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr) # pragma: no cover
        return getattr(self.stream, attr)

    def color(self, code):
        style = self.style.get(code, self.reset)
        self.stream.write(style(''))

    def colorClear(self):
        self.stream.write(self.reset(''))
        self.stream.flush()


class ColorTextTestResult(TextTestResult):
    """A test result class that can print formatted text results to a stream the supports ANSI color output.

    Used by TextTestRunner.
    """

    def __init__(self, *args, **kwargs):
        super(ColorTextTestResult, self).__init__(*args, **kwargs)

    def addSuccess(self, test):
        self.stream.color('SUCCESS')
        super(ColorTextTestResult, self).addSuccess(test)
        self.stream.colorClear()

    def addError(self, test, err):
        self.stream.color('ERROR')
        super(ColorTextTestResult, self).addError(test, err)
        self.stream.colorClear()

    def addFailure(self, test, err):
        self.stream.color('FAIL')
        super(ColorTextTestResult, self).addFailure(test, err)
        self.stream.colorClear()

    def addSkip(self, test, reason):
        self.stream.color('SKIP')
        super(ColorTextTestResult, self).addSkip(test, reason)
        self.stream.colorClear()

    def addExpectedFailure(self, test, err):
        self.stream.color('EXPECTED')
        super(ColorTextTestResult, self).addExpectedFailure(test, err)
        self.stream.colorClear()

    def addUnexpectedSuccess(self, test):
        self.stream.color('UNEXPECTED')
        super(ColorTextTestResult, self).addUnexpectedSuccess(test)
        self.stream.colorClear()

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.color(flavour)
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.colorClear()
            self.stream.writeln("%s" % err)

class ColorTextTestRunner(TextTestRunner):
    """
    Color implementation of unittest's TextTestRunner
    """
    resultclass = ColorTextTestResult

    def __init__(self, *args, **kwargs):
        super(ColorTextTestRunner, self).__init__(*args, **kwargs)
        self.stream = _ColorDecorator(self.stream)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        result.failfast = self.failfast
        result.buffer = self.buffer
        registerResult(result)

        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
            else:
                result.printErrors()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
            expectedFails, unexpectedSuccesses, skipped = results
        except AttributeError:
            pass
        infos = []
        if not result.wasSuccessful():
            self.stream.color('FAIL')
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.color('SUCCESS')
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        self.stream.colorClear()
        return result

def fixture_list(fixtures, global_fixtures=[]):
    if fixtures == global_fixtures:
        return []
    else:
        start = 0
        for x in range(len(global_fixtures)):
            if (len(fixtures) == start or len(global_fixtures) == start
                or fixtures[x] != global_fixtures[x]):
                break
            start += 1
        return fixtures[start:]


class ColorDjangoTestSuiteRunner(DjangoTestSuiteRunner):
    """
    Support for coloring error output
    """
    def wrap_tests(self, suite):
        """
        monkeypatches TestCase tests. Sorts them by fixtures and then
        optimizes fixture loading.
        """

        self.currernt_fixtures = []
        self.flushes = 0
        self.fixtures = 0
        self.fixtures_prevented = 0
        self.fixtures_sets = []

        def fast_fixture_setup(instance):
            fixtures = getattr(instance, 'fixtures', [])

            loaddata = fixtures
            flush_db = True
            if len(self.currernt_fixtures) <= len(fixtures):
                if fixtures[:len(self.currernt_fixtures)] == self.currernt_fixtures:
                    # current fixtures are still OK
                    loaddata = fixtures[len(self.currernt_fixtures):]
                    self.fixtures_prevented += len(self.currernt_fixtures)
                    flush_db = False

            if flush_db:
                self.flushes += 1
                self.currernt_fixtures = []
                for db in connections:
                    call_command('flush', verbosity=0, interactive=False, database=db)

            if len(loaddata):
                self.fixtures += len(loaddata)
                self.fixtures_sets.append(self.currernt_fixtures + loaddata)
                for db in connections:
                    call_command('loaddata', *loaddata, **{
                                                        'verbosity': 0,
                                                        'commit': True,
                                                        'database': db
                                                        })
            instance.fixtures = []
            self.currernt_fixtures = fixtures

            instance._old_fixture_setup()

        setattr(TestCase, '_old_fixture_setup', getattr(TestCase, '_fixture_setup'))
        setattr(TestCase, '_fixture_setup', fast_fixture_setup)
        new_suite = unittest.TestSuite()

        other_tests = []
        test_cases = []
        for test in suite:
            if isinstance(test, TestCase):
                # optimize only TestCases - transaction based tests
                test._runner = self
                test_cases.append(test)
            else:
                other_tests.append(test)

        def comparator(tc1, tc2):
            tc1_fixtures = getattr(tc1, 'fixtures', [])
            tc2_fixtures = getattr(tc2, 'fixtures', [])
            if tc1_fixtures == tc2_fixtures:
                return 0
            else:
                return tc1_fixtures > tc2_fixtures and 1 or - 1

        test_cases.sort(comparator)

        new_suite.addTests(test_cases + other_tests)

        return new_suite

    def print_fixture_statistics(self):
        print("")
        print("Fixture statistics:")
        print("    Number of fixtures loaded for TestCases: %s" % self.fixtures)
        print("    Number of fixtures prevented from "\
                "loading for TestCases: %s" % self.fixtures_prevented)
        print("    Number of database flushes: %s" % self.flushes)
        print("    Fixture sets:")
        for set in self.fixtures_sets:
            print("        %s" % set)
        print("")

    def run_suite(self, suite, **kwargs):
        result = ColorTextTestRunner(verbosity=self.verbosity,
                                       failfast=self.failfast).run(suite)
        return result

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        """
        if no test labels has been defined for this test run then try to test
        only application defined in TEST_APPS list. The TEST_APPS list should
        consist only of your project apps excluding third party and django apps.
        """

        TEST_APPS = getattr(settings, 'TEST_APPS', None)
        if not test_labels and TEST_APPS:
            test_labels = TEST_APPS

        return self.wrap_tests(super(ColorDjangoTestSuiteRunner, self).build_suite(test_labels, **kwargs))

    def setup_databases(self, **kwargs):
        """
        calls super setup_databases and then loads global fixtures for all databases
        from TEST_GLOBAL_FIXTURES setting
        """

        return super(ColorDjangoTestSuiteRunner, self).setup_databases(**kwargs)


    @staticmethod
    def fixture_list(*fixtures):
        TEST_GLOBAL_FIXTURES = getattr(settings, 'TEST_GLOBAL_FIXTURES', [])
        return fixture_list(list(fixtures), TEST_GLOBAL_FIXTURES)



class ColorProfilerDjangoTestSuiteRunner(ColorDjangoTestSuiteRunner):
    """
    Support for coloring error output
    """
    def run_suite(self, suite, **kwargs):
        import cProfile
        import unipath
        import StringIO

        use_profiler = True
        try:
            import pstats
        except:
            use_profiler = False

        result = []
        def _profile_run():
            result.append(super(ColorProfilerDjangoTestSuiteRunner,
                                self).run_suite(suite, **kwargs))

        if use_profiler:
            root = unipath.Path(settings.APPLICATION_ROOT)
            profile_file = root.child('.profiler')

            class ColorStats(pstats.Stats):
                def __init__(self, *args, **kwargs):
                    pstats.Stats.__init__(self, *args, **kwargs)

                    class dummy(object): pass
                    style = dummy()
                    style.LONGRUN = termcolors.make_style(opts=('bold',), fg='red')
                    style.NAME = termcolors.make_style(opts=('bold',), fg='cyan')
                    style.FILE = termcolors.make_style(opts=('bold',), fg='yellow')
                    style.APP = termcolors.make_style(opts=('bold',), fg='white')
                    self.style = style

                def print_title(self):
                    print >> self.stream, 'calls  cumtime  percall',
                    print >> self.stream, 'filename:lineno(function)'

                def print_line(self, func):  # hack : should print percentages
                    cc, nc, tt, ct, callers = self.stats[func] #@UnusedVariable
                    c = str(nc)
                    if nc != cc:
                        c = c + '/' + str(cc)
                    print >> self.stream, c.rjust(5),
                    print >> self.stream, pstats.f8(ct),
                    if cc == 0:
                        print >> self.stream, ' '*8,
                    else:
                        percall = float(ct) / cc
                        result = pstats.f8(percall)
                        if percall > 0.1:
                            result = self.style.LONGRUN(result)
                        print >> self.stream, result,
                    print >> self.stream, self.func_std_string(func)

                def func_std_string(self, func_name): # match what old profile produced
                    if func_name[:2] == ('~', 0):
                        # special case for built-in functions
                        name = func_name[2]
                        if name.startswith('<') and name.endswith('>'):
                            return '{%s}' % name[1:-1]
                        else:
                            return name
                    else:
                        file, line, name = func_name
                        file = unipath.Path(file)
                        return ("%s (%s:%d [%s])" %
                            (self.style.NAME(name),
                             self.style.FILE(file.name), line,
                             self.style.APP(file.parent.parent.name)))

            cProfile.runctx('profile_run()', {'profile_run':_profile_run}, {}, str(profile_file))

            results = StringIO.StringIO()
            stats = ColorStats(str(profile_file), stream=results)
            stats.sort_stats('cumulative')
            stats.print_stats('\(test\_*')

            print results.getvalue()
        else:
            _profile_run()

        self.print_fixture_statistics()

        return result[0]
