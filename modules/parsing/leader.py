import typing
from enum import Enum

from .parsers import BaseParser, CTestSuiteParser


class AvailableTestSuites(Enum):
    C_TEST_SUITE = CTestSuiteParser


class Leader:
    _parsers: typing.List[BaseParser]

    def __init__(self):
        self._parsers = []

    def add_testsuite(self, testsuite: AvailableTestSuites):
        parser = testsuite.value()
        self._parsers.append(parser)

    def preprocess(self) -> None:
        for parser in self._parsers:
            parser.preprocess()

    def build(self,
              additonal_compile_flags: typing.List[str] = [],
              additional_link_flag: typing.List[str] = [],
              cwes: typing.List[int] = []) -> int:
        for parser in self._parsers:
            parser.build(additonal_compile_flags, additional_link_flag, cwes)

    def preprocess_and_build(self,
                             additonal_compile_flags: typing.List[str] = [],
                             additional_link_flag: typing.List[str] = [],
                             cwes: typing.List[int] = []) -> int:
        for parser in self._parsers:
            parser.preprocess()
            parser.build(additonal_compile_flags, additional_link_flag, cwes)