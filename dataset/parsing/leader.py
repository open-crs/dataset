import typing
from enum import Enum

from .parsers import BaseParser, CTestSuiteParser, DummyTestSuiteParser


class AvailableTestSuites(Enum):
    """Enumeration for storing the implemented parsers for test suites"""
    DUMMY_TEST_SUITE = DummyTestSuiteParser
    C_TEST_SUITE = CTestSuiteParser


class Leader:
    """Class for managing the parsers"""
    _parsers: typing.List[BaseParser]

    def __init__(self) -> None:
        """Initializes the Leader instance."""
        self._parsers = []

    def add_testsuite(self, testsuite: AvailableTestSuites) -> None:
        """Adds a parser to be managed by the leader."""
        parser = testsuite.value()
        self._parsers.append(parser)

    def preprocess(self) -> None:
        """Apply the preprocessing phase of each parser."""
        for parser in self._parsers:
            parser.preprocess()

    def build(self,
              additonal_compile_flags: typing.List[str] = [],
              additional_link_flag: typing.List[str] = [],
              cwes: typing.List[int] = []) -> int:
        """Build specific sources from a test suite, with some given flags.

        Args:
            additonal_compile_flags (typing.List[str], optional): User-provided
                compile flags. Defaults to [].
            additional_link_flag (typing.List[str], optional): User-provided
                link flags. Defaults to [].
            cwes (typing.List[int], optional): CWEs that the built sources needs
                to be vulnerable. Defaults to [].

        Returns:
            int: Number of built sources
        """
        total_sources = 0
        for parser in self._parsers:
            total_sources += parser.build(additonal_compile_flags,
                                          additional_link_flag, cwes)

        return total_sources

    def preprocess_and_build(self,
                             additonal_compile_flags: typing.List[str] = [],
                             additional_link_flag: typing.List[str] = [],
                             cwes: typing.List[int] = []) -> int:
        """Preprocess and build specific sources from a test suite.

        Args:
            additonal_compile_flags (typing.List[str], optional): User-provided
                compile flags. Defaults to [].
            additional_link_flag (typing.List[str], optional): User-provided
                link flags. Defaults to [].
            cwes (typing.List[int], optional): CWEs that the built sources needs
                to be vulnerable. Defaults to [].

        Returns:
            int: Number of built sources
        """
        total_sources = 0
        for parser in self._parsers:
            total_sources += parser.preprocess_and_build(
                additonal_compile_flags, additional_link_flag, cwes)

        return total_sources
