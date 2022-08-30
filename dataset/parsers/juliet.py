import glob
import os
import re
import shutil
import typing
import xml.etree.ElementTree as ET

from dataset.configuration import Configuration
from dataset.parsers.base import BaseParser
from dataset.source import Source

SOURCE_LIMIT = 10000

DATASET_NAME = "nist_juliet"
DATASET_FOLDER = "raw_testsuites/nist_juliet/"
DATASET_SOURCES_FOLDER = DATASET_FOLDER + "testcases/"
DATASET_HEADER_FOLDER = DATASET_FOLDER + "testcasesupport/"
COMPILE_FLAGS = ["-w", "-O0"]

CWE_REGEX = r"CWE-([0-9]+)"
W32_REGEX = r"w32"
MAIN_DATASET_HEADERS = Configuration.MAIN_DATASET_SOURCES + "nist_lib/"

DATASET_MANIFEST = DATASET_FOLDER + "manifest.xml"

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = (
    "gcc -E {} -O0 -DOMITGOOD -DINCLUDEMAIN -I{}             -o {}"
    + COMMAND_SUPRESS_OUTPUT
)
GPP_PREPROCESS_COMMAND = (
    "g++ -E {} -O0 -DOMITGOOD -DINCLUDEMAIN -I{}              -o {}"
    + COMMAND_SUPRESS_OUTPUT
)
GCC_BUILD_COMMAND = (
    "gcc -x  c  {} {} {} -o {} -lpthread -lm " + COMMAND_SUPRESS_OUTPUT
)
GPP_BUILD_COMMAND = (
    "g++ -x c++ {} {} {} -o {} -lpthread -lm " + COMMAND_SUPRESS_OUTPUT
)

ADITIOAL_GCC_SOURCES = (
    " "
    + MAIN_DATASET_HEADERS
    + "io.c "
    + MAIN_DATASET_HEADERS
    + "std_thread.c "
)
ADITIOAL_GPP_SOURCES = (
    " "
    + MAIN_DATASET_HEADERS
    + "io.cpp "
    + MAIN_DATASET_HEADERS
    + "std_thread.cpp "
)


class DatasetException(Exception):
    """Dataset exception class for our app

    Attributes:
        expression : input expression in which the error occurred
        message : explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class CNistJulietParser(BaseParser):
    _current_id: int
    _source_limit: int

    def __init__(self) -> str:
        super().__init__(DATASET_NAME, COMPILE_FLAGS)

    def preprocess(self) -> None:
        """Preprocess the sources from the current test suite."""

        if not os.path.isdir(MAIN_DATASET_HEADERS):
            os.mkdir(MAIN_DATASET_HEADERS)
        for file in glob.iglob(DATASET_HEADER_FOLDER + "*.h"):
            source_filename = os.path.basename(file)
            shutil.copy(file, MAIN_DATASET_HEADERS + source_filename)

        for file in glob.iglob(DATASET_HEADER_FOLDER + "*.c"):
            source_filename = os.path.basename(file)
            gcc_command = GCC_PREPROCESS_COMMAND.format(
                file,
                MAIN_DATASET_HEADERS,
                MAIN_DATASET_HEADERS + source_filename,
            )
            os.system(gcc_command)
            gcc_command = GPP_PREPROCESS_COMMAND.format(
                file,
                MAIN_DATASET_HEADERS,
                MAIN_DATASET_HEADERS + source_filename + "pp",
            )
            os.system(gcc_command)

        sources = self._get_all_sources()
        for source in sources:
            # Create the source full ID (from the name of the dataset and the
            # ID of the source)
            full_identifier = DATASET_NAME + "_" + str(source.identifier)

            # Create the destination folder
            destination_path = os.path.join(
                Configuration.MAIN_DATASET_SOURCES, full_identifier
            )
            if not os.path.isdir(destination_path):
                os.mkdir(destination_path)

            for source_complete_filename in source.additional_files:
                # Preprocess

                source_filename = os.path.basename(source_complete_filename)
                source_folder = os.path.dirname(source_filename)
                destination_file = os.path.join(
                    destination_path, source_filename
                )

                # If .h just copy else use g++ or gcc

                file_extension = os.path.splitext(source_complete_filename)[1]
                gcc_command = ""
                if file_extension == ".h":
                    shutil.copy(
                        source_complete_filename,
                        MAIN_DATASET_HEADERS + source_filename,
                    )
                else:
                    if file_extension == ".c":
                        gcc_command = GCC_PREPROCESS_COMMAND.format(
                            source_complete_filename,
                            MAIN_DATASET_HEADERS,
                            destination_file,
                        )
                    else:
                        gcc_command = GPP_PREPROCESS_COMMAND.format(
                            source_complete_filename,
                            MAIN_DATASET_HEADERS,
                            destination_file,
                        )
                # print(gcc_command)
                os.system(gcc_command)

            self.dataset_worker.add_new_source(
                full_identifier, source.cwes, DATASET_NAME
            )

        # Dump the dataset
        self.dataset_worker.dump_to_file()

    def _get_all_sources(self) -> typing.List[Source]:
        # Parse the manifest to get the CWEs

        global SOURCE_LIMIT
        self._source_limit = SOURCE_LIMIT

        self._current_id = 1
        tree = ET.parse(DATASET_MANIFEST)
        root = tree.getroot()
        cwes = {}
        sources = []
        for testcase in root.findall("./testcase"):
            try:
                filePaths = []
                identifier = self._current_id

                if identifier not in cwes:
                    cwes[identifier] = []

                for file in testcase.findall("./file"):
                    if re.search(W32_REGEX, file.attrib["path"]):
                        # Means it is a W32 exe, skip
                        # print("Skipped " + file.attrib["path"])
                        raise Exception("W32 source file")
                    filePath = glob.iglob(
                        DATASET_SOURCES_FOLDER + "**/" + file.attrib["path"],
                        recursive=True,
                    )
                    filePaths.append(next(filePath))

                    for child in file:
                        groups = re.search(CWE_REGEX, child.attrib["name"])
                        cwes[identifier].append(int(groups.group(1)))

                self._current_id += 1
                source = Source(identifier, "", cwes[identifier], filePaths)
                sources.append(source)
                if identifier == self._source_limit:
                    return sources
            except Exception as e:
                pass
        return sources

    def _generate_gcc_command(
        self,
        identifier,
        additonal_compile_flags: typing.List[str] = [],
        additional_link_flags: typing.List[str] = [],
    ) -> str:
        """Get the gcc_command string needed to preprocess the cuurrent source

        Args:
            identifier (_type_): identifier of the current test case
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

        # Build

        source_path = os.path.join(
            Configuration.MAIN_DATASET_SOURCES, identifier
        )
        destination_file = os.path.join(
            Configuration.MAIN_DATASET_EXECUTABLES,
            identifier + Configuration.ELF_EXTENSION,
        )
        sources = " ".join(glob.iglob(source_path + "/**"))

        binary_type = os.path.splitext(sources.split(" ")[-1])[1]

        compile_flags = self.compile_flags + (
            additonal_compile_flags if additonal_compile_flags else []
        )
        compile_flags = " ".join(compile_flags)
        link_flags = self.link_flags + (
            additional_link_flags if additional_link_flags else []
        )
        link_flags = " ".join(link_flags)
        gcc_command = ""

        if binary_type == ".c":
            gcc_command = GCC_BUILD_COMMAND.format(
                compile_flags,
                sources + ADITIOAL_GCC_SOURCES,
                link_flags,
                destination_file,
            )
        else:
            gcc_command = GPP_BUILD_COMMAND.format(
                compile_flags,
                sources + ADITIOAL_GPP_SOURCES,
                link_flags,
                destination_file,
            )

        return gcc_command
