import glob
import os
import typing

from dataset.configuration import Configuration
from dataset.parsers.base import BaseParser
from dataset.source import Source

DATASET_NAME = "toy_test_suite"
COMPILE_FLAGS = ["-no-pie", "-O0", "-std=gnu99", "-m32"]
DATASET_FOLDER = "raw_testsuites/toy_test_suite/"
COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = (
    "gcc -E {source_file} -I {include_dir} -o {output_file}"
    + COMMAND_SUPRESS_OUTPUT
)
GCC_BUILD_COMMAND = (
    "gcc {compile_flags} {source_file} {link_flags} -o {output_file}"
    + COMMAND_SUPRESS_OUTPUT
)


class ToyTestSuiteParser(BaseParser):
    def __init__(self) -> str:
        super().__init__(DATASET_NAME, COMPILE_FLAGS)

    def _get_all_sources(self) -> typing.Generator[Source, None, None]:
        identifier = 0
        for directory in os.listdir(DATASET_FOLDER):
            full_path_dir = os.path.join(DATASET_FOLDER, directory)
            source_filename = os.path.join(full_path_dir, "source.c")
            cwe = self.__get_cwe_from_source_folder(full_path_dir)

            source = Source(str(identifier), source_filename, [cwe])
            yield source

            identifier += 1

    def __get_cwe_from_source_folder(self, source_folder: str) -> int:
        cwe_filename = os.path.join(source_folder, "cwe.txt")

        with open(cwe_filename, "r", encoding="utf-8") as cwe_file:
            content = cwe_file.read().split()
            content = content[0]

            if content:
                return int(content)
            else:
                return -1

    def preprocess(self) -> None:
        sources = self._get_all_sources()
        for source in sources:
            full_identifier = self.__get_source_full_id(source.identifier)
            destination_folder = (
                self.__get_destination_location_for_preprocessed_source(source)
            )
            if not os.path.isdir(destination_folder):
                os.mkdir(destination_folder)

                self.dataset_worker.add_new_source(
                    full_identifier, source.cwes, self.test_case_name
                )

            source_filename = os.path.basename(source.full_filename)
            source_folder = os.path.dirname(source.full_filename)
            destination_file = os.path.join(
                destination_folder, source_filename
            )
            gcc_command = GCC_PREPROCESS_COMMAND.format(
                source_file=source.full_filename,
                include_dir=source_folder,
                output_file=destination_file,
            )
            os.system(gcc_command)

        self.dataset_worker.dump_to_file()

    def __get_destination_location_for_preprocessed_source(
        self, source: Source
    ) -> None:
        full_identifier = self.__get_source_full_id(source.identifier)

        return os.path.join(
            Configuration.Assets.MAIN_DATASET_SOURCES, full_identifier
        )

    def __get_source_full_id(self, identifier: int) -> None:
        return self.test_case_name + "_" + str(identifier)

    def _generate_gcc_command(
        self,
        identifier: str,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flags: typing.List[str] = None,
    ) -> str:
        source_path = os.path.join(
            Configuration.Assets.MAIN_DATASET_SOURCES, identifier
        )
        destination_file = os.path.join(
            Configuration.Assets.MAIN_DATASET_EXECUTABLES,
            identifier + Configuration.Assets.ELF_EXTENSION,
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
