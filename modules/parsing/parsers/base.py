import abc
import os
import typing

from modules.dataset_worker import DatasetWorker

MAIN_DATASET_SOURCES = "sources/"
MAIN_DATASET_EXECUTABLES = "executables/"
DATASET_LABELS = "vulnerables.csv"

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = "gcc -E {} -I {} -o {}" + COMMAND_SUPRESS_OUTPUT
GCC_BUILD_COMMAND = "gcc {} {} {} -o {}" + COMMAND_SUPRESS_OUTPUT
ELF_EXTENSION = ".elf"


class SourceDetails:
    id: str
    full_filename: str
    cwes: typing.List[int]

    def __init__(self, id: str, full_filename: str,
                 cwes: typing.List[int]) -> None:
        self.id = id
        self.full_filename = full_filename
        self.cwes = cwes


class BaseParser(abc.ABC):
    _dataset_name: str
    _compile_flags: typing.List[str]
    _link_flags: typing.List[str]
    _dataset_worker: DatasetWorker

    def __init__(self,
                 dataset_name: str,
                 compile_flags: typing.List[str] = None,
                 link_flags: typing.List[str] = None) -> None:
        self._dataset_name = dataset_name
        self._compile_flags = compile_flags if compile_flags else []
        self._link_flags = link_flags if link_flags else []

        # Load the CSV with all the current executables
        self._dataset_worker = DatasetWorker(DATASET_LABELS)

    @abc.abstractmethod
    def _get_all_sources(self) -> typing.List[SourceDetails]:
        raise NotImplementedError()

    def preprocess(self) -> None:
        sources = self._get_all_sources()
        for source in sources:
            # Create the source full ID (from the name of the dataset and the
            # ID of the source)
            full_source_id = self._dataset_name + "_" + str(source.id)

            # Create the destination folder
            destination_path = os.path.join(MAIN_DATASET_SOURCES,
                                            full_source_id)
            if not os.path.isdir(destination_path):
                os.mkdir(destination_path)

            # Preprocess
            source_filename = os.path.basename(source.full_filename)
            source_folder = os.path.dirname(source.full_filename)
            destination_file = os.path.join(destination_path, source_filename)
            gcc_command = GCC_PREPROCESS_COMMAND.format(
                source.full_filename, source_folder, destination_file)
            os.system(gcc_command)

            # Add a new entry in the dataset
            self._dataset_worker.add_new_source(full_source_id, source.cwes,
                                                self._dataset_name)

        # Dump the dataset
        self._dataset_worker.dump()

    def build(self,
              additonal_compile_flags: typing.List[str] = [],
              additional_link_flag: typing.List[str] = [],
              cwes: typing.List[int] = []) -> int:
        sources_ids = self._dataset_worker.get_sources(self._dataset_name,
                                                       cwes)

        built_count = 0
        for source_id in sources_ids:

            # Build
            source_path = os.path.join(MAIN_DATASET_SOURCES, source_id)
            destination_file = os.path.join(MAIN_DATASET_EXECUTABLES,
                                            source_id + ELF_EXTENSION)
            sources = " ".join(glob.iglob(source_path + "**/*.c"))
            compile_flags = " ".join(self._compile_flags +
                                     additonal_compile_flags)
            link_flags = " ".join(self._link_flags + additional_link_flag)
            gcc_command = GCC_BUILD_COMMAND.format(compile_flags, sources,
                                                   link_flags,
                                                   destination_file)
            ret_val = os.system(gcc_command)

            # Mark as built
            if ret_val == 0:
                self._dataset_worker.mark_source_as_built(source_id)

                built_count += 1

        # Dump the dataset
        self._dataset_worker.dump()

        return built_count

    def preprocess_and_build(self,
                             additonal_compile_flags: typing.List[str] = [],
                             additional_link_flag: typing.List[str] = [],
                             cwes: typing.List[int] = []) -> int:
        self.preprocess()
        self.build(additonal_compile_flags, additional_link_flag, cwes)
