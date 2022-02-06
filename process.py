#!/usr/bin/env python3

import click

from modules.dataset_worker import DatasetWorker
from modules.parsing.leader import Leader, AvailableTestSuites


@click.group("process")
@click.pass_context
def process(ctx):
    """A script for building and filtering datasets of vulnerable programs"""
    pass


@process.command("build", help="Build a testsuite")
@click.option(
    "--testsuite",
    type=click.Choice(
        [str(name).split(".")[-1] for name in list(AvailableTestSuites)],
        case_sensitive=False),
    required=True)
@click.option("--compile-flags", type=str)
@click.option("--link-flags", type=str)
@click.option("--cwe", multiple=True, type=int)
@click.pass_context
def build(ctx, testsuite, compile_flags, link_flags, cwe):
    # Preprocess the options
    compile_flags = compile_flags.split(" ")
    link_flags = link_flags.split(" ")

    # Create the leader and run
    leader = Leader()
    leader.add_testsuite(AvailableTestSuites[testsuite])
    leader.preprocess_and_build(compile_flags, link_flags, cwe)


def main():
    process(prog_name="process")


if __name__ == "__main__":
    main()
