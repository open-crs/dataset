# `dataset` 🗂️

---

- [Description](#description)
  - [Limitations](#limitations)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
  - [As a CLI Tool](#as-a-cli-tool)
    - [Build Test Suite](#build-test-suite)
    - [List Executables](#list-executables)
    - [Get Help](#get-help)
  - [As a Python Module](#as-a-python-module)

---

## Description

`dataset` is the CRS module that compiles and manages the vulnerable programs which will be analyzed by the CRS.

The supported test suites are:

- NIST's Juliet
- NIST's C Test Suite
- A toy dataset

### Limitations

- ELF format
- x86 architecture

## How It Works

The module does the following steps for each test suite that needs to be built:

1. Gets the available sources into the test suite's directory.

1. Preprocesses the sources for including all the required source code files and header files.

1. Writes the preprocessed sources into the `sources/` directory in the root of the repository.

1. Creates a new entry into the `vulnerables.csv` of the dataset.

1. Filters the source code files based on the wanted CWEs.

1. Compiles the preprocesses source files with the compile and link flags from multiple source code files (module files and user-provided files).

1. Writes the executables into the `executables/` directory in the root of the repository.

All build operations use GCC and are performed inside a 32-bit Ubuntu 18.04 container.

## Setup

1. Make sure you have set up the repositories and Python environment according to the [top-level instructions](https://github.com/open-crs#requirements).
   That is:

   - Docker is installed and is properly running.
     Check using:

     ```console
     docker version
     docker ps -a
     docker run --rm hello-world
     ```

     These commands should run without errors.

   - The current repository and the [`commons` repository](https://github.com/open-crs/commons) are cloned (with submodules) in the same directory.

   - You are running all commands inside a Python virtual environment.
     There should be `(.venv)` prefix to your prompt.

   - You have installed Poetry in the virtual environment.
     If you run:

     ```console
     which poetry
     ```

     you should get a path ending with `.venv/bin/poetry`.

1. Disable the Python Keyring:

   ```console
   export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
   ```

   This is an problem that may occur in certain situations, preventing Poetry from getting packages.

1. Install the required packages with Poetry (based on `pyprojects.toml`):

   ```console
   poetry install --only main
   ```

1. Build the Docker image used to build the dataset assets:

   ```console
   docker build --platform linux/386 --tag ubuntu18.04_32bit_compiler -f docker/Dockerfile.ubuntu18.04_32bit_compiler .
   ```

## Usage

You can use the `dataset` module either standalone, as a CLI tool, or integrated into Python applications.

### As a CLI Tool

As a CLI tool, you can either use the `cli.py` module:

```console
python dataset/cli.py
```

or use the Poetry interface:

```console
poetry run dataset
```

#### Build Test Suite

```console
$ poetry run dataset build --testsuite TOY_TEST_SUITE
✅ Successfully built 5 executables.
```

#### List Executables

```console
$ poetry run dataset get
✅ The available executables are:

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID               ┃ CWEs                        ┃ Parent Database ┃ Full Path                        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ toy_test_suite_0 │ Stack-based Buffer Overflow │ toy_test_suite  │ executables/toy_test_suite_0.elf │
│ toy_test_suite_1 │                             │ toy_test_suite  │ executables/toy_test_suite_1.elf │
│ toy_test_suite_2 │ NULL Pointer Dereference    │ toy_test_suite  │ executables/toy_test_suite_2.elf │
│ toy_test_suite_3 │ NULL Pointer Dereference    │ toy_test_suite  │ executables/toy_test_suite_3.elf │
│ toy_test_suite_4 │                             │ toy_test_suite  │ executables/toy_test_suite_4.elf │
└──────────────────┴─────────────────────────────┴─────────────────┴──────────────────────────────────┘
```

#### Get Help

```console
$ poetry run dataset
Usage: dataset [OPTIONS] COMMAND [ARGS]...

  Builds and filters datasets of vulnerable programs

Options:
  --help  Show this message and exit.

Commands:
  build  Builds a test suite.
  show   Gets the executables in the whole dataset.
```

### As a Python Module

```python
from dataset import Dataset

available_executables = Dataset().get_available_executables()
```
