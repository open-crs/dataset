#!/usr/bin/env python3

import typing

import click
import cwe as cwelib
from rich import print  # pylint: disable=redefined-builtin
from rich.table import Table

from dataset import Dataset
from dataset.datasets_parser import AvailableTestSuites, Parser
from dataset.executable import Executable

TESTSUITES_NAMES = [element.name for element in list(AvailableTestSuites)]


@click.group("process")
def process() -> None:
    """Builds and filters datasets of vulnerable programs"""


@process.command("build", help="Builds a test suite.")
@click.option(
    "--testsuite",
    type=click.Choice(TESTSUITES_NAMES, case_sensitive=True),
    required=True,
)
@click.option("--compile-flags", type=str)
@click.option("--link-flags", type=str)
@click.option("--cwe", multiple=True, type=int)
def build(  # pylint: disable=dangerous-default-value
    testsuite: str,
    compile_flags: str = None,
    link_flags: str = None,
    cwe: typing.List[str] = [],
) -> None:
    parser = Parser()
    parser.add_testsuite(AvailableTestSuites[testsuite])

    compile_flags = split_flags(compile_flags)
    link_flags = split_flags(link_flags)
    count = parser.preprocess_and_build(compile_flags, link_flags, cwe)

    print(f":white_check_mark: Successfully built {count} sources.")


def split_flags(flags: str) -> typing.List[str]:
    if flags:
        return flags.split(" ")
    else:
        return None


@process.command("get", help="Gets the executables in the whole dataset.")
def show() -> None:
    print(":white_check_mark: The available executables are:\n")

    sources = Dataset().get_available_executables()
    sources_table = build_sources_table(sources)

    print(sources_table)


def build_sources_table(sources: typing.List[Executable]) -> Table:
    table = Table()

    table.add_column("ID")
    table.add_column("CWEs")
    table.add_column("Parent Database")
    table.add_column("Full Path")

    for source in sources:
        cwes = stringifies_cwes(source.cwes)

        table_row = [
            str(source.identifier),
            cwes,
            source.parent_dataset,
            source.full_path,
        ]
        table.add_row(*table_row)

    return table


def stringifies_cwes(cwes: typing.List[int]) -> str:
    cwes = translate_cwes_to_descriptions(cwes)

    return ", ".join(cwes)


def translate_cwes_to_descriptions(cwes: typing.List[int]) -> typing.List[str]:
    cwe_database = cwelib.Database()

    for current_cwe in cwes:
        if cwe_object := cwe_database.get(current_cwe):
            yield cwe_object.name
        else:
            continue


def main() -> None:
    process(prog_name="process")


if __name__ == "__main__":
    main()
