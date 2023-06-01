import typing

from dataset.parsers import AvailableTestSuites, BaseParser


class ParsersManager:
    _parsers: typing.List[BaseParser]

    def __init__(self) -> None:
        self._parsers = []

    def add_testsuite(self, testsuite: AvailableTestSuites) -> None:
        parser = testsuite.value()
        self._parsers.append(parser)

    def preprocess_all(self) -> None:
        for parser in self._parsers:
            parser.preprocess()

    def build_all(
        self,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flag: typing.List[str] = None,
        cwes: typing.List[int] = None,
    ) -> int:
        sources_count = 0
        for parser in self._parsers:
            sources_count += parser.build(
                additonal_compile_flags, additional_link_flag, cwes
            )

        return sources_count

    def preprocess_and_build(
        self,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flag: typing.List[str] = None,
        rebuild: bool = False,
        cwes: typing.List[int] = None,
    ) -> int:
        sources_count = 0
        for parser in self._parsers:
            sources_count += parser.preprocess_and_build(
                additonal_compile_flags, additional_link_flag, rebuild, cwes
            )

        return sources_count
