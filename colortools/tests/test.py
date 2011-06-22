
from mock import Mock, patch
from django.test import TestCase
from django.utils.unittest.runner import TextTestResult

from colortools.test import (ColorTextTestResult)

class ColorTextTestResultTestCase(TestCase):


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
