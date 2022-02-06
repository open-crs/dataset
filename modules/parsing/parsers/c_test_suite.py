import glob
import re
import typing
import xml.etree.ElementTree as ET

from .base import BaseParser, SourceDetails

DATASET_NAME = "nist_c_test_suite"
COMPILE_FLAGS = ["-w", "-O0", "-std=gnu99"]
DATASET_FOLDER = "raw_testsuites/nist_c_test_suite/"
DATASET_SOURCES_FOLDER = DATASET_FOLDER + "sources/"
DATASET_MANIFEST = DATASET_FOLDER + "manifest.xml"
ID_REGEX = r"000\/149\/([0-9]+)"
CWE_REGEX = r"CWE-([0-9]+)"


class CTestSuiteParser(BaseParser):

    def __init__(source_name: str) -> str:
        super().__init__(DATASET_NAME, COMPILE_FLAGS)

    def _get_all_sources(self) -> typing.List[SourceDetails]:
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