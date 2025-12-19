"""Tests package for test definitions and runners"""
from .test_definitions import (
    TEST_1_DEFINITION,
    TEST_2_DEFINITION,
    TEST_3_DEFINITION,
    TEST_4_DEFINITION,
    TEST_SUITE,
    get_test,
    get_all_tests,
    get_passing_tests,
    get_failing_tests
)
from .test_runner import TestRunner

__all__ = [
    'TEST_1_DEFINITION',
    'TEST_2_DEFINITION',
    'TEST_3_DEFINITION',
    'TEST_4_DEFINITION',
    'TEST_SUITE',
    'get_test',
    'get_all_tests',
    'get_passing_tests',
    'get_failing_tests',
    'TestRunner'
]
