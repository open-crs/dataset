from dataset.configuration import Configuration
from dataset.dataset_worker import DatasetWorker
from dataset.executable import Executable


class Dataset:
    def get_available_executables(self) -> str:
        worker = DatasetWorker(Configuration.DATASET_NAME)

        return worker.get_available_executables()
