import abc
import glob
import os
import typing

from modules.dataset_worker import DatasetWorker
from ...configuration import Configuration

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = "gcc -E {} -I {} -o {}" + COMMAND_SUPRESS_OUTPUT
GCC_BUILD_COMMAND = "gcc {} {} {} -o {}" + COMMAND_SUPRESS_OUTPUT


class SourceDetails:
    """Class for storing the details about a sources."""
    id: str
    full_filename: str
    cwes: typing.List[int]

    def __init__(self, id: str, full_filename: str,
                 cwes: typing.List[int]) -> None:
        """Initializes the SourceDetails instance."""
        self.id = id
        self.full_filename = full_filename
        self.cwes = cwes


class BaseParser(abc.ABC):
    """Class for modeling an abstract parser."""
    _test_case_name: str
    _compile_flags: typing.List[str]
    _link_flags: typing.List[str]
    _dataset_worker: DatasetWorker

    def __init__(self,
                 test_case_name: str,
                 compile_flags: typing.List[str] = None,
                 link_flags: typing.List[str] = None) -> None:
        """Initializes the BaseParser instance.

        Args:
            test_case_name (str): Name of the test case
            compile_flags (typing.List[str], optional): Compile flags imposed
                by the test case. Defaults to None.
            link_flags (typing.List[str], optional): Link flags imposed by the
                test case. Defaults to None.
        """
        self._test_case_name = test_case_name
        self._compile_flags = compile_flags if compile_flags else []
        self._link_flags = link_flags if link_flags else []

        # Load the CSV with all the current executables
        self._dataset_worker = DatasetWorker(Configuration.DATASET_NAME)

    @abc.abstractmethod
    def _get_all_sources(self) -> typing.List[SourceDetails]:
        """Gets all the sources from the current test suite.

        Raises:
            NotImplementedError: Method to be implemented in the chilc classes 

        Returns:
            typing.List[SourceDetails]: List with all the sources from the
                current dataset
        """
        raise NotImplementedError()

    def preprocess(self) -> None:
        """Preprocess the sources from the current test suite."""
        sources = self._get_all_sources()
        for source in sources:
            # Create the source full ID (from the name of the dataset and the
            # ID of the source)
            full_source_id = self._test_case_name + "_" + str(source.id)

            destination_path = os.path.join(Configuration.MAIN_DATASET_SOURCES,
                                            full_source_id)
            if not os.path.isdir(destination_path):
                # Create the destination folder
                os.mkdir(destination_path)

                # Add a new entry in the dataset
                self._dataset_worker.add_new_source(full_source_id,
                                                    source.cwes,
                                                    self._test_case_name)

            # Preprocess
            source_filename = os.path.basename(source.full_filename)
            source_folder = os.path.dirname(source.full_filename)
            destination_file = os.path.join(destination_path, source_filename)
            gcc_command = GCC_PREPROCESS_COMMAND.format(
                source.full_filename, source_folder, destination_file)
            os.system(gcc_command)

        # Dump the dataset
        self._dataset_worker.dump()

    def build(self,
              additonal_compile_flags: typing.List[str] = [],
              additional_link_flags: typing.List[str] = [],
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
        sources_ids = self._dataset_worker.get_sources(self._test_case_name,
                                                       cwes, False, True)

        built_count = 0
        for source_id in sources_ids:

            # Build
            source_path = os.path.join(Configuration.MAIN_DATASET_SOURCES,
                                       source_id)
            destination_file = os.path.join(
                Configuration.MAIN_DATASET_EXECUTABLES,
                source_id + Configuration.ELF_EXTENSION)
            sources = " ".join(glob.iglob(source_path + "**/*.c"))
            compile_flags = self._compile_flags + (
                additonal_compile_flags if additonal_compile_flags else [])
            compile_flags = " ".join(compile_flags)
            link_flags = self._link_flags + (additional_link_flags
                                             if additional_link_flags else [])
            link_flags = " ".join(link_flags)
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
        self.preprocess()

        return self.build(additonal_compile_flags, additional_link_flag, cwes)
