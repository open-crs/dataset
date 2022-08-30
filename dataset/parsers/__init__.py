from enum import Enum

from dataset.parsers.base import BaseParser
from dataset.parsers.c_test_suite import CTestSuiteParser
from dataset.parsers.juliet import CNistJulietParser
from dataset.parsers.toy_test_suite import ToyTestSuiteParser


class AvailableTestSuites(Enum):
    TOY_TEST_SUITE = ToyTestSuiteParser
    C_TEST_SUITE = CTestSuiteParser
    JULIET = CNistJulietParser
