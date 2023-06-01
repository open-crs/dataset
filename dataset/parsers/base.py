import abc
import typing

from dataset.configuration import Configuration
from dataset.containerized_compiler import ContainerizedCompiler
from dataset.source import Source
from dataset.vulnerable_executables_index import VulnerableExecutablesIndex

COMMAND_SUPRESS_OUTPUT = " >/dev/null 2>&1"
GCC_PREPROCESS_COMMAND = "gcc -E {} -I {} -o {}"
GCC_BUILD_COMMAND = "gcc {} {} {} -o {}"
DATASET_NAME = Configuration.DatasetCreation.DATASET_NAME


class BaseParser(abc.ABC):
    test_case_name: str
    compile_flags: typing.List[str]
    link_flags: typing.List[str]
    dataset_worker: VulnerableExecutablesIndex

    def __init__(
        self,
        test_case_name: str,
        compile_flags: typing.List[str] = None,
        link_flags: typing.List[str] = None,
    ) -> None:
        self.test_case_name = test_case_name
        self.compile_flags = compile_flags if compile_flags else []
        self.link_flags = link_flags if link_flags else []
        self.dataset_worker = VulnerableExecutablesIndex(DATASET_NAME)
        self.compiler = ContainerizedCompiler()

    @abc.abstractmethod
    def _get_all_sources(self) -> typing.List[Source]:
        raise NotImplementedError()

    @abc.abstractmethod
    def _generate_gcc_command(
        self,
        identifier: str,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flags: typing.List[str] = None,
    ) -> str:
        raise NotImplementedError()

    def _execute_command(self, command: str) -> int:
        return self.compiler.exec_compiler_command(command)

    @abc.abstractmethod
    def preprocess(self) -> None:
        raise NotImplementedError()

    def build(
        self,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flags: typing.List[str] = None,
        rebuild: bool = False,
        cwes: typing.List[int] = None,
    ) -> int:
        sources_ids = self.dataset_worker.get_entries_ids(
            self.test_case_name, cwes, rebuild
        )

        built_count = 0
        for identifier in sources_ids:
            gcc_command = self._generate_gcc_command(
                identifier, additonal_compile_flags, additional_link_flags
            )

            ret_val = self._execute_command(gcc_command)

            if ret_val == 0:
                self.dataset_worker.mark_source_as_built(identifier)

                built_count += 1

        self.dataset_worker.dump_to_file()

        return built_count

    def preprocess_and_build(
        self,
        additonal_compile_flags: typing.List[str] = None,
        additional_link_flag: typing.List[str] = None,
        rebuild: bool = False,
        cwes: typing.List[int] = None,
    ) -> int:
        self.preprocess()

        return self.build(additonal_compile_flags, additional_link_flag, rebuild, cwes)
