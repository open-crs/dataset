import typing

from dataset.configuration import Configuration
from dataset.executable import Executable
from dataset.vulnerable_executables_index import VulnerableExecutablesIndex


class Dataset:
    def get_available_executables(self) -> typing.List[Executable]:
        worker = VulnerableExecutablesIndex(Configuration.DatasetCreation.DATASET_NAME)

        return worker.get_available_executables()
