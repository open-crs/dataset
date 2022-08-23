import abc
import os
import typing

from dataset.dataset_worker import DatasetWorker
from ...configuration import Configuration

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = "gcc -E {} -I {} -o {}" + COMMAND_SUPRESS_OUTPUT
GCC_BUILD_COMMAND = "gcc {} {} {} -o {}" + COMMAND_SUPRESS_OUTPUT


class SourceDetails:
    """Class for storing the details about a sources."""
    id: str
    full_filename: str
    cwes: typing.List[int]
    full_filenames: typing.List[str]

    def __init__(self,
                 id: str,
                 full_filename: str,
                 cwes: typing.List[int],
                 full_filenames: typing.List[str] = None) -> None:
        """Initializes the SourceDetails instance."""
        self.id = id
        self.full_filename = full_filename
        self.cwes = cwes
        self.full_filenames = full_filenames


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

    @abc.abstractmethod
    def _generate_gcc_command(
            self,
            source_id,
            additonal_compile_flags: typing.List[str] = [],
            additional_link_flags: typing.List[str] = []) -> str:
        """Get the gcc_command string needed to preprocess the cuurrent source

        Args:
            source_id (_type_): id of the current test case
            additonal_compile_flags (typing.List[str], optional): User-provided
                compile flags. Defaults to [].
            additional_link_flag (typing.List[str], optional): User-provided
                link flags. Defaults to [].

        Raises:
            NotImplementedError: Method to be implemented in the child classes

        Returns:
            string: Returns the command string to be executed to preprocess
                the current source
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def preprocess(self) -> None:
        """Preprocess the sources from the current test suite.
        
        Raises:
            NotImplementedError: Method to be implemented in the chilc classes
        
        Returns: None, has no return value
        """

        raise NotImplementedError()

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

            gcc_command = self._generate_gcc_command(source_id,
                                                     additonal_compile_flags,
                                                     additional_link_flags)

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
