import os
import typing

from dataset.configuration import Configuration


class Executable:
    identifier: str
    cwes: typing.List[int]
    parent_dataset: str
    is_built: bool

    def __init__(
        self,
        identifier: str,
        cwes: typing.List[int],
        parent_dataset: str,
    ) -> None:
        self.identifier = identifier
        self.parent_dataset = parent_dataset
        self.full_path = self.__get_full_path()

        if isinstance(cwes, int):
            self.cwes = [cwes]
        else:
            self.cwes = cwes

    def __get_full_path(self) -> None:
        filename_with_ext = self.identifier + Configuration.ELF_EXTENSION

        return os.path.join(
            Configuration.MAIN_DATASET_EXECUTABLES, filename_with_ext
        )
