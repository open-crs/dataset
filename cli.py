#!/usr/bin/env python3

import typing

import click
import tabulate

from modules.configuration import Configuration
from modules.dataset_worker import DatasetWorker
from modules.parsing.leader import AvailableTestSuites, Leader

TESTSUITES_NAMES = [element.name for element in list(AvailableTestSuites)]


@click.group("process")
@click.pass_context
def process(ctx: click.Context):
    """A script for building and filtering datasets of vulnerable programs"""
    pass


@process.command("build", help="Build a test suite")
@click.option("--testsuite",
              type=click.Choice(TESTSUITES_NAMES, case_sensitive=True),
              required=True)
@click.option("--compile-flags", type=str)
@click.option("--link-flags", type=str)
@click.option("--cwe", multiple=True, type=int)
@click.pass_context
def build(ctx: click.Context,
          testsuite: str,
          compile_flags: str = None,
          link_flags: str = None,
          cwe: typing.List[str] = []):
    """Build specific sources from a test suite, with some given flags.

    Args:
        ctx (click.Context): Click's context
        testsuite (str): Test suite to build
        compile_flags (str, optional): Compile flags. Defaults to None.
        link_flags (str, optional): Link flags. Defaults to None.
        cwe (typing.List[str], optional): CWEs that the built sources needs to
            be vulnerable. Defaults to [].
    """
    # Transform the strings resulted from options into arrays
    if compile_flags:
        compile_flags = compile_flags.split(" ")
    if link_flags:
        link_flags = link_flags.split(" ")

    # Create the leader and run with the given test suite
    leader = Leader()
    leader.add_testsuite(AvailableTestSuites[testsuite])
    count = leader.preprocess_and_build(compile_flags, link_flags, cwe)

    # Log
    print(f"[+] Successfully built {count} source(s).")


@process.command("show", help="Show the sources in the dataset")
@click.pass_context
def show(ctx: click.Context):
    print(f"[+] The information about the dataset's sources are:\n")

    worker = DatasetWorker(Configuration.DATASET_NAME)
    sources = worker.get_sources()

    print(tabulate.tabulate(sources))


def main() -> None:
    """Main function"""
    process(prog_name="process")


if __name__ == "__main__":
    main()
