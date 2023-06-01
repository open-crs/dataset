import typing

import pandas

from dataset.configuration import Configuration
from dataset.executable import Executable


class VulnerableExecutablesIndex:
    _filename: str = None
    _dataset: str = None

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._dataset = pandas.read_csv(self._filename)

    def __del__(self) -> None:
        """Destroys a VulnerableExecutablesIndex instance."""
        self.dump_to_file()

    def add_new_source(
        self, name: str, cwes: typing.List[int], parent_dataset: str
    ) -> None:
        cwes = self.__stringifies_cwes(cwes)

        self._dataset.loc[len(self._dataset.index)] = [
            name,
            cwes,
            parent_dataset,
            False,
        ]

    def __stringifies_cwes(self, cwes: typing.List[str]) -> str:
        return Configuration.DatasetCreation.CWES_SEPARATOR.join(
            [str(cwe) for cwe in cwes]
        )

    def mark_source_as_built(self, name: str) -> None:
        self._dataset.loc[self._dataset.name == name, "is_built"] = True

    def dump_to_file(self) -> None:
        self._dataset.to_csv(self._filename, index=False)

    def get_entries_ids(
        self,
        dataset: str = None,
        cwes: typing.List[int] = None,
        is_built: bool = None,
    ) -> list:
        for _, row in self._dataset.iterrows():
            if self.__is_source_skipped_by_filters(
                row, dataset, cwes, is_built
            ):
                continue

            yield row["name"]

    def get_available_executables(
        self, dataset: str = None, cwes: typing.List[int] = None
    ) -> typing.List[Executable]:
        for _, row in self._dataset.iterrows():
            if self.__is_source_skipped_by_filters(row, dataset, cwes, True):
                continue

            details = row.tolist()[:-1]

            yield Executable(*details)

    def __is_source_skipped_by_filters(
        self,
        source: list,
        dataset: str = None,
        cwes: typing.List[int] = None,
        is_built: bool = None,
    ) -> bool:
        return (
            self.__is_source_skipped_by_dataset_filter(source, dataset)
            or self.__is_source_skipped_by_status_filter(source, is_built)
            or self.__is_source_skipped_by_cwes_filter(source, cwes)
        )

    def __is_source_skipped_by_dataset_filter(
        self, source: list, dataset: str
    ) -> bool:
        return dataset and source.parent_dataset != dataset

    def __is_source_skipped_by_status_filter(
        self, source: list, is_built: bool
    ) -> bool:
        return is_built is not None and source.is_built != is_built

    def __is_source_skipped_by_cwes_filter(
        self, source: list, cwes: typing.List[int]
    ) -> bool:
        if not cwes:
            return False

        current_cwes = str(source.cwes).split(
            Configuration.DatasetCreation.CWES_SEPARATOR
        )
        current_cwes = [int(element) for element in current_cwes]

        if len(set(current_cwes).intersection(set(cwes))) == 0:
            return True

        return False
