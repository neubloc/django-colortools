
from mock import Mock, patch
from django.test import TestCase
from django.utils.unittest.runner import TextTestResult
from django.conf import settings

from colortools.test import (ColorTextTestResult, ColorDjangoTestSuiteRunner,
                             fixture_list)

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

class ColorDjangoTestSuiteRunnerTestCase(TestCase):

    def test_fixture_list(self):
        settings.TEST_GLOBAL_FIXTURES = ['one']
        self.assertEqual(ColorDjangoTestSuiteRunner.fixture_list('one'), [])
        settings.TEST_GLOBAL_FIXTURES = []

    def test_fixture_list_no_settings(self):
        self.assertEqual(ColorDjangoTestSuiteRunner.fixture_list('one'), ['one'])

class FixtureListFunctionTestCase(TestCase):

    def test_empty_should_return_empty(self):
        self.assertEqual([], fixture_list([]))

    def test_if_no_setting_defined_return_as_it_is(self):
        self.assertEqual(['one'], fixture_list(['one']))

    def test_return_empty_list_if_parameters_are_the_same(self):
        self.assertEqual([], fixture_list(['one'], ['one']))

    def test_return_first_list_if_second_is_different(self):
        self.assertEqual(['one'], fixture_list(['one'], ['two']))

    def test_return_first_list_excluding_first_element_from_the_second(self):
        self.assertEqual(['two'], fixture_list(['one', 'two'], ['one']))

    def test_return_empty_by_excluding_all_elements(self):
        self.assertEqual([], fixture_list(['one', 'two'], ['one', 'two']))

    def test_return_first_list_excluding_first_element_from_the_second_2(self):
        self.assertEqual(['three'], fixture_list(['one', 'two', 'three'], ['one', 'two']))
