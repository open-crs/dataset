import glob
import os
import re
import typing
import xml.etree.ElementTree as ET

from dataset.configuration import Configuration
from dataset.parsers.base import BaseParser
from dataset.source import Source

DATASET_NAME = "nist_c_test_suite"
COMPILE_FLAGS = ["-w", "-O0", "-std=gnu99", "-m32"]
DATASET_FOLDER = "raw_testsuites/nist_c_test_suite/"
DATASET_SOURCES_FOLDER = DATASET_FOLDER + "sources/"
DATASET_MANIFEST = DATASET_FOLDER + "manifest.xml"
ID_REGEX = r"000\/149\/([0-9]+)"
CWE_REGEX = r"CWE-([0-9]+)"
COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = (
    "gcc -E {source_file} -I {include_dir} -o {output_file}"
    + COMMAND_SUPRESS_OUTPUT
)
GCC_BUILD_COMMAND = (
    "gcc {compile_flags} {source_file} {link_flags} -o {output_file}"
    + COMMAND_SUPRESS_OUTPUT
)


class CTestSuiteParser(BaseParser):
    def __init__(self) -> str:
        super().__init__(DATASET_NAME, COMPILE_FLAGS)

    def _get_all_sources(self) -> typing.List[Source]:
        cwes = self.__get_cwes_from_manifest()

        sources = []
        for filename in glob.iglob(
            DATASET_SOURCES_FOLDER + "**/*.c", recursive=True
        ):
            identifier = int(filename.split("/")[-2])

            source = Source(identifier, filename, cwes[identifier])
            sources.append(source)

        return sources

    def __get_cwes_from_manifest(self) -> dict:
        tree = ET.parse(DATASET_MANIFEST)
        root = tree.getroot()

        cwes = {}
        for file in root.findall("./testcase/file"):
            if "language" in file.attrib:
                groups = re.search(ID_REGEX, file.attrib["path"])
                identifier = int(groups.group(1))
                if identifier not in cwes:
                    cwes[identifier] = []

                for child in file:
                    groups = re.search(CWE_REGEX, child.attrib["name"])
                    cwes[identifier].append(int(groups.group(1)))

        return cwes

    def preprocess(self) -> None:
        sources = self._get_all_sources()
        for source in sources:
            full_identifier = (
                self.test_case_name + "_" + str(source.identifier)
            )

            destination_path = os.path.join(
                Configuration.MAIN_DATASET_SOURCES, full_identifier
            )
            if not os.path.isdir(destination_path):
                os.mkdir(destination_path)

                self.dataset_worker.add_new_source(
                    full_identifier, source.cwes, self.test_case_name
                )

            source_filename = os.path.basename(source.full_filename)
            source_folder = os.path.dirname(source.full_filename)
            destination_file = os.path.join(destination_path, source_filename)
            gcc_command = GCC_PREPROCESS_COMMAND.format(
                source_file=source.full_filename,
                include_dir=source_folder,
                output_file=destination_file,
            )
            os.system(gcc_command)

        self.dataset_worker.dump_to_file()

    def _generate_gcc_command(
        self,
        identifier: str,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flags: typing.List[str] = None,
    ) -> str:
        source_path = os.path.join(
            Configuration.MAIN_DATASET_SOURCES, identifier
        )
        destination_file = os.path.join(
            Configuration.MAIN_DATASET_EXECUTABLES,
            identifier + Configuration.ELF_EXTENSION,
        )
        sources = " ".join(glob.iglob(source_path + "**/*.c"))
        compile_flags = self.compile_flags + (
            additonal_compile_flags if additonal_compile_flags else []
        )
        compile_flags = " ".join(compile_flags)
        link_flags = self.link_flags + (
            additional_link_flags if additional_link_flags else []
        )
        link_flags = " ".join(link_flags)
        gcc_command = GCC_BUILD_COMMAND.format(
            compile_flags=compile_flags,
            source_file=sources,
            link_flags=link_flags,
            output_file=destination_file,
        )

        return gcc_command
