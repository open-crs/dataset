#!/usr/bin/env python3

import re
import os
import shutil
import xml.etree.ElementTree as ET

import click

from modules.dataset_worker import DatasetWorker
from modules.dataset_nist_parser import make_nist

RAW_DATASETS = "raw_datasets/"
C_TEST_SUITE_DATASET_NAME = "nist_c_test_suite"
C_TEST_SUITE_DATASET = RAW_DATASETS + C_TEST_SUITE_DATASET_NAME + "/"
C_TEST_SUITE_DATASET_SOURCES = C_TEST_SUITE_DATASET + "sources/"
C_TEST_SUITE_DATASET_EXECUTABLES = C_TEST_SUITE_DATASET + "executables/"
C_TEST_SUITE_DATASET_MANIFEST = C_TEST_SUITE_DATASET + "manifest.xml"
C_TEST_SUITE_ID_REGEX = r"000\/149\/([0-9]+)"
MAIN_DATASET_SOURCES = "sources/"
MAIN_DATASET_EXECUTABLES = "executables/"
DATASET_LABELS = "vulnerables.csv"
ELF_EXTENSION = ".elf"
CWE_REGEX = r"CWE-([0-9]+)"


@click.group("process")
@click.pass_context
def process(ctx):
    """A script for building and filtering datasets of vulnerable programs"""
    pass


@process.command("build-nist-c-test-suite",
                 help="Build only the NIST C test suite dataset")
@click.pass_context
def make_nist_c_test_suite(ctx):
    # Parse the manifest to get the CWEs
    tree = ET.parse(C_TEST_SUITE_DATASET_MANIFEST)
    root = tree.getroot()
    cwes = {}
    for file in root.findall('./testcase/file'):
        if ("language" in file.attrib):
            # Get the ID of the source file
            groups = re.search(C_TEST_SUITE_ID_REGEX, file.attrib["path"])
            id = int(groups.group(1))
            if id not in cwes:
                cwes[id] = []

            current_cwes = []
            for child in file:
                groups = re.search(CWE_REGEX, child.attrib["name"])
                cwes[id].append(int(groups.group(1)))

    # Load the CSV with all the current executables
    dataset_worker = DatasetWorker(DATASET_LABELS)

    # Create all the executables
    #TODO(@iosifache): Ensure that the programs are compiled via a wait
    #                  mechanism.
    os.system("cd {} && make all".format(C_TEST_SUITE_DATASET))

    # Process each executable
    files = os.listdir(C_TEST_SUITE_DATASET_EXECUTABLES)
    for executable in files:
        if executable.endswith(ELF_EXTENSION):
            # Copy the executable
            executable_path = C_TEST_SUITE_DATASET_EXECUTABLES + executable
            shutil.copytree(executable_path, MAIN_DATASET_EXECUTABLES)

            # Copy the source code
            base_program_id = executable[:len(ELF_EXTENSION) - 1]
            program_id = C_TEST_SUITE_DATASET_NAME + "_" + base_program_id
            src_folder = C_TEST_SUITE_DATASET_SOURCES + base_program_id
            dest_folder = MAIN_DATASET_SOURCES + program_id
            shutil.copytree(src_folder, dest_folder)

            # Add the executable into the CSV
            dataset_worker.add(program_id, cwes[int(base_program_id)],
                               C_TEST_SUITE_DATASET_NAME)

    # Clear the initial dataset
    os.system("cd {} && make clean".format(C_TEST_SUITE_DATASET))

    # Dump the dataset
    dataset_worker.dump()


@process.command("build-nist-juliet",
                 help="Build only the NIST Juliet dataset")
@click.pass_context
def make_nist_juliet(ctx):
    dataset_worker = DatasetWorker(DATASET_LABELS)
    make_nist(dataset_worker)
    dataset_worker.dump()


@process.command("build-all", help="Build the whole dataset")
@click.pass_context
def make_dataset(ctx):
    ctx.invoke(make_nist_c_test_suite)
    ctx.invoke(make_nist_juliet)


@process.command("filter", help="Filter the dataset by specific CWEs")
@click.argument("cwes", nargs=-1)
@click.pass_context
def make_dataset(ctx, cwes):
    print(cwes)


def main():
    process(prog_name="process")


if __name__ == '__main__':
    main()
