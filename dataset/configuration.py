class Configuration:
    class Assets:
        HOST_WORKING_DIRECTORY = "/opencrs/dataset"
        RAW_TESTSUITES = "raw_testsuites/"
        MAIN_DATASET_SOURCES = "sources/"
        ELF_EXTENSION = ".elf"
        MAIN_DATASET_EXECUTABLES = "executables/"

    class DatasetCreation:
        CWES_SEPARATOR = ","
        DATASET_NAME = "vulnerables.csv"

    class ContainerizedCompiler:
        IMAGE_TAG = "ubuntu_32bit_compilator"
        CONTAINER_WORKING_DIRECTORY = "/home/docker"
