import typing

from .base import BaseParser, SourceDetails

DATASET_NAME = "dummy_test_suite"
DATASET_FOLDER = "raw_testsuites/dummy_test_suite/"
SOURCE_FILE = DATASET_FOLDER + "source.c"
SET_CWE = 476


class DummyTestSuiteParser(BaseParser):

    def __init__(source_name: str) -> str:
        """Initializes the CTestSuiteParser instance."""
        super().__init__(DATASET_NAME, [])

    def _get_all_sources(self) -> typing.List[SourceDetails]:
        """Gets all the sources from the current test suite.

        Returns:
            typing.List[SourceDetails]: List with all the sources from the
                current dataset
        """
        details = SourceDetails("source", SOURCE_FILE, [SET_CWE])

        return [details]