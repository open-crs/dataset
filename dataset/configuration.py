import os

class Configuration:
    class Assets:
        HOST_WORKING_DIRECTORY = os.getcwd()
        RAW_TESTSUITES = "raw_testsuites/"
        MAIN_DATASET_SOURCES = "sources/"
        ELF_EXTENSION = ".elf"
        MAIN_DATASET_EXECUTABLES = "executables/"

    class DatasetCreation:
        CWES_SEPARATOR = ","
        DATASET_NAME = "vulnerables.csv"

    class ContainerizedCompiler:
        CONTAINER_WORKING_DIRECTORY = "/home/docker"

        _IMAGE_TAGS = {
                "x86": "ubuntu18.04_32bit_compiler",
                "aarch64": "ubuntu22.04_aarch64_cross_compiler",
        }

        @classmethod
        def image_tag(cls):
            return cls._IMAGE_TAGS[Configuration.Toolchain.TARGET_ARCH]
    
    class Toolchain:
        # Cross-compilation target. Defaults to native x86 so existing
        # behaviour is unchanged. Set OPENCRS_TARGET_ARCH=aarch64 to build
        # ARM targets.
        TARGET_ARCH = os.environ.get("OPENCRS_TARGET_ARCH", "x86")

        _COMPILERS = {
            "x86": ("gcc", "g++"),
            "aarch64": ("aarch64-linux-gnu-gcc", "aarch64-linux-gnu-g++"),
        }
        
        _X86_ONLY_FLAGS = ("-m32", "-m64", "-mx32")

        _EXTRA_FLAGS = {
                "x86": [],
                "aarch64": [
                    "-mbranch-protection=none",
                    "-fno-stack-protector",
                    "-no-pie",
                ],
        }
        if TARGET_ARCH not in _COMPILERS:
            raise ValueError(
                "Unsupported OPENCRS_TARGET_ARCH="
                f"{TARGET_ARCH!r}; expected one of {tuple(_COMPILERS)}"
            )

        CC, CXX = _COMPILERS[TARGET_ARCH]

        @classmethod
        def adapt_compile_flags(cls, flags):
            flags = list(flags)
            if cls.TARGET_ARCH == "x86":
                return flags
            
            adapted = [f for f in flags if f not in cls._X86_ONLY_FLAGS]
            for extra in cls._EXTRA_FLAGS.get(cls.TARGET_ARCH, []):
                if extra not in adapted:
                    adapted.append(extra)
            return adapted
