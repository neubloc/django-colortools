
from mock import Mock, patch
from django.utils import unittest
from django.utils.unittest.runner import TextTestResult

from colortools.test import (_ColorDecorator, ColorTextTestResult, ColorTextTestRunner,
                             ColorDjangoTestSuiteRunner, ColorProfilerDjangoTestSuiteRunner)

class ColorDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.stream = Mock()
        self.cd = _ColorDecorator(self.stream)

    def test_init_color_decorator(self):
        self.assertEqual(self.cd.stream, self.stream)
        self.assertTrue(callable(self.cd.reset))
        for color in self.cd.style:
            self.assertTrue(callable(self.cd.style[color]))

    def test_color(self):
        self.cd.color('FAIL')
        self.stream.write.assert_called_once_with(self.cd.style['FAIL'](''))

    def test_undefined_color(self):
        self.cd.color('FAKECOLOR')
        self.stream.write.assert_called_once_with(self.cd.reset(''))

    def test_reset_color(self):
        self.cd.colorClear()
        self.stream.write.assert_called_once_with(self.cd.reset(''))
        self.stream.flush.assert_called_once_with()

    def test_access_stream_elements(self):
        self.cd.write("text")
        self.stream.write.assert_called_once_with("text")

    def test_disable_pickling(self):
        with self.assertRaises(AttributeError):
            _ColorDecorator.__getattr__(self.cd, '__getstate__')

        with self.assertRaises(AttributeError):
            _ColorDecorator.__getattr__(self.cd, 'stream')

class ColorTextTestResultTestCase(unittest.TestCase):

    def setUp(self):
        self.result = ColorTextTestResult(Mock(), True, 1)

    def test_success_should_be_in_color(self):
        self.result.addSuccess(Mock())
        self.result.stream.color.assert_called_once_with('SUCCESS')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'addFailure')
    def test_fail_should_be_in_color(self, mock_method):
        self.result.addFailure(Mock(), Mock())
        self.result.stream.color.assert_called_once_with('FAIL')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'addError')
    def test_error_should_be_in_color(self, mock_method):
        self.result.addError(Mock(), Mock())
        self.result.stream.color.assert_called_once_with('ERROR')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'addSkip')
    def test_skip_should_be_in_color(self, mock_method):
        self.result.addSkip(Mock(), Mock())
        self.result.stream.color.assert_called_once_with('SKIP')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'addExpectedFailure')
    def test_expected_failure_should_be_in_color(self, mock_method):
        self.result.addExpectedFailure(Mock(), Mock())
        self.result.stream.color.assert_called_once_with('EXPECTED')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'addUnexpectedSuccess')
    def test_unexpected_success_should_be_in_color(self, mock_method):
        self.result.addUnexpectedSuccess(Mock())
        self.result.stream.color.assert_called_once_with('UNEXPECTED')
        self.result.stream.colorClear.assert_called_once_with()

    @patch.object(TextTestResult, 'getDescription')
    def test_error_list_should_be_in_color(self, mock_method):
        self.result.printErrorList('ERROR', [('test1', 'error1'), ('test2', 'error2')])
        self.result.stream.color.assert_called_with('ERROR')
        self.result.stream.colorClear.assert_called_with()
        self.assertEqual(self.result.stream.color.call_count, 2)
        self.assertEqual(self.result.stream.colorClear.call_count, 2)

        self.assertEqual(mock_method.call_count, 2)

class ColorTextTestRunnerTestCase(unittest.TestCase):

    @patch('colortools.test.registerResult')
    def test_run(self, registerResult):
        test_runner = Mock(spec=ColorTextTestRunner)
        test_runner.failfast = True
        test_runner.buffer = Mock()
        test_runner.stream = Mock()
        suite = Mock()

        result = test_runner._makeResult.return_value
        result.testsRun = 20
        result.expectedFailures = []
        result.unexpectedSuccesses = []
        result.skipped = []

        result.wasSuccessful.return_value = True

        ColorTextTestRunner.run(test_runner, suite)

        result.wasSuccessful.return_value = False
        result.failures = []
        result.errors = []
        ColorTextTestRunner.run(test_runner, suite)
