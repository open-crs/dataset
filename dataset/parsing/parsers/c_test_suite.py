import glob
import re
import typing
import xml.etree.ElementTree as ET
import os

from .base import BaseParser, SourceDetails
from ...configuration import Configuration

DATASET_NAME = "nist_c_test_suite"
COMPILE_FLAGS = ["-w", "-O0", "-std=gnu99"]
DATASET_FOLDER = "raw_testsuites/nist_c_test_suite/"
DATASET_SOURCES_FOLDER = DATASET_FOLDER + "sources/"
DATASET_MANIFEST = DATASET_FOLDER + "manifest.xml"
ID_REGEX = r"000\/149\/([0-9]+)"
CWE_REGEX = r"CWE-([0-9]+)"

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = "gcc -E {} -I {} -o {}" + COMMAND_SUPRESS_OUTPUT
GCC_BUILD_COMMAND = "gcc {} {} {} -o {}" + COMMAND_SUPRESS_OUTPUT


class CTestSuiteParser(BaseParser):

    def __init__(source_name: str) -> str:
        """Initializes the CTestSuiteParser instance."""
        super().__init__(DATASET_NAME, COMPILE_FLAGS)

    def _get_all_sources(self) -> typing.List[SourceDetails]:
        """Gets all the sources from the current test suite.

        Returns:
            typing.List[SourceDetails]: List with all the sources from the
                current dataset
        """
        # Parse the manifest to get the CWEs
        tree = ET.parse(DATASET_MANIFEST)
        root = tree.getroot()
        cwes = {}
        for file in root.findall("./testcase/file"):
            if ("language" in file.attrib):
                # Get the ID of the source file
                groups = re.search(ID_REGEX, file.attrib["path"])
                id = int(groups.group(1))
                if id not in cwes:
                    cwes[id] = []

                current_cwes = []
                for child in file:
                    groups = re.search(CWE_REGEX, child.attrib["name"])
                    cwes[id].append(int(groups.group(1)))

        # Traverse the source folder
        sources = []
        for filename in glob.iglob(DATASET_SOURCES_FOLDER + "**/*.c",
                                   recursive=True):
            source_id = int(filename.split("/")[-2])

            source = SourceDetails(source_id, filename, cwes[source_id])
            sources.append(source)

        return sources

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

    def _generate_gcc_command(
            self,
            source_id,
            additonal_compile_flags: typing.List[str] = [],
            additional_link_flags: typing.List[str] = []) -> str:

        # Build
        source_path = os.path.join(Configuration.MAIN_DATASET_SOURCES,
                                   source_id)
        destination_file = os.path.join(
            Configuration.MAIN_DATASET_EXECUTABLES,
            source_id + Configuration.ELF_EXTENSION)
        sources = " ".join(glob.iglob(source_path + "**/*.c"))
        compile_flags = self._compile_flags + (additonal_compile_flags if
                                               additonal_compile_flags else [])
        compile_flags = " ".join(compile_flags)
        link_flags = self._link_flags + (additional_link_flags
                                         if additional_link_flags else [])
        link_flags = " ".join(link_flags)
        gcc_command = GCC_BUILD_COMMAND.format(compile_flags, sources,
                                               link_flags, destination_file)

        return gcc_command
