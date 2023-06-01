# `dataset` 🗂️

---

- [Description](#description)
  - [Limitations](#limitations)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
  - [As a CLI Tool](#as-a-cli-tool)
    - [Test Suite Build](#test-suite-build)
    - [Executables Listing](#executables-listing)
    - [Help](#help)
  - [As a Python Module](#as-a-python-module)

---

## Description

`dataset` is the CRS module that compiles and manages the vulnerable programs which will be analyzed by the CRS.

The supported test suites are the following:
- NIST's Juliet;
- NIST's C Test Suite;
- A toy dataset.

### Limitations

- ELF format
- x86 architecture

## How It Works

The module does the following steps for each test suite that needs to be built:
1. Getting the available sources into the test suite's folder
2. Preprocessing the sources for including all the required sources and header
3. Writing the preprocessed sources into the `sources` folder from the root of the repository
4. Creating a new entry into the CSV files of the dataset, namely `vulnerables.csv`
5. Filtering the sources based on the wanted CWEs
6. Compiling the preprocessed sources with the compile and link flags from multiple sources (module's ones and user-provided)
7. Writing the executables into the `executables` folder from the root of the repository.

All `gcc` operations are performed inside a 32-bit Ubuntu 18.04 container. 

## Setup

1. Download the repository in `/opencrs/dataset`. If you want to use other path, modify the corresponding configururation parameter.
2. Ensure that the repository's submodules (which are the test suites) are downloaded too. If you want to clone the repository, use the flag `--recurse-submodules` to download them too.
3. Install the required Python 3 packages via `poetry install --no-dev`.
4. Build the Docker image: `docker build --tag ubuntu_32bit_compilator -f docker/Dockerfile.ubuntu_32bit_compilator .`.
5. Ensure the Docker API is accessible by:
   - Running the module as `root`; or
   - Changing the Docker socket permissions (unsecure approach) via `chmod 777 /var/run/docker.sock`.

## Usage

### As a CLI Tool

#### Test Suite Build

```
➜ poetry run dataset build --testsuite TOY_TEST_SUITE
✅ Successfully built 5 executables.
```

#### Executables Listing

```
➜ poetry run dataset get
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

#### Help

```
➜ poetry run dataset
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