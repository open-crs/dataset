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
- [Building for AArch64 (ARM)](#building-for-aarch64-arm)
  - [Build the AArch64 Compiler Image](#build-the-aarch64-compiler-image)
  - [Build an AArch64 Test Suite](#build-an-aarch64-test-suite)
  - [Run the AArch64 Binaries](#run-the-aarch64-binaries)
  - [Switch Back to x86](#switch-back-to-x86)
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
- AArch64 (ARM) arhitecture

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
The target architecture is selected by the `OPENCRS_TARGET_ARCH` environment variable (default `x86`): 
- `x86` builds with `gcc`/`g++` in a 32-bit Ubuntu 18.04 container
- `aarch64` cross-compiles with `aarch64-linux-gnu-gcc`/`aarch64-linux-gnu-g++` in an Ubuntu 22.04 container. See [Building for AArch64 (ARM)](#building-for-aarch64-arm).

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

You can use the `dataset` module either standalone, as a CLI tool, or integrated into Python applications, as a Python module.

### As a CLI Tool

As a CLI tool, you can either use the `cli.py` module:

```console
python dataset/cli.py
```

or the Poetry interface:

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

## Building for AArch64 (ARM)
 
By default, the `dataset` module builds `x86` targets. It can also build 64-bit ARM (**AArch64**) targets.
 
The AArch64 targets are **cross-compiled on your existing x86 host** — the cross-compiler itself runs natively and emits ARM code, so no ARM machine is needed to build. For this first corpus, the targets are compiled **without modern ARM mitigations** (`-mbranch-protection=none`, `-fno-stack-protector`, `-no-pie`) so they are cleanly exploitable, which is the purpose of a known-vulnerable dataset.
 
Everything is driven by a single environment variable, `OPENCRS_TARGET_ARCH`:
 
- unset or `x86` (default) — the original behaviour, unchanged;
- `aarch64` — build ARM targets.
> **Note.** The `dataset` module only *builds* targets; it never runs them. Building AArch64 targets needs only the steps below. *Running* them on an x86 host additionally needs QEMU — see [Run the AArch64 Binaries](#run-the-aarch64-binaries).
 
### Build the AArch64 Compiler Image
 
The ARM toolchain lives in its own container image, separate from the x86 one. Build it once:
 
```console
docker build --platform linux/amd64 \
  --tag ubuntu22.04_aarch64_cross_compiler \
  -f docker/Dockerfile.ubuntu22.04_aarch64_cross_compiler .
```
 
The `--platform linux/amd64` flag is deliberate: it keeps the image native to your x86 host, so the cross-compiler runs at full speed instead of under emulation.
 
You can confirm the image carries the cross-compiler:
 
```console
docker run --rm ubuntu22.04_aarch64_cross_compiler aarch64-linux-gnu-gcc --version
```

### Build an AArch64 Test Suite
 
Set `OPENCRS_TARGET_ARCH=aarch64` and build as usual:
 
```console
$ OPENCRS_TARGET_ARCH=aarch64 poetry run dataset build --testsuite TOY_TEST_SUITE
✅ Successfully built 5 executables.
```
 
The produced ELFs land in `executables/`, exactly as for `x86`. Confirm they are genuine AArch64 binaries:
 
```console
$ file executables/toy_test_suite_0.elf
executables/toy_test_suite_0.elf: ELF 64-bit LSB executable, ARM aarch64, ...
 
$ readelf -h executables/toy_test_suite_0.elf | grep -E "Machine|Type"
  Type:                              EXEC (Executable file)
  Machine:                           AArch64
```
 
`Machine: AArch64` confirms the architecture, and `Type: EXEC` (rather than `DYN`) confirms the `-no-pie` cleanly-exploitable profile was applied.
 
### Run the AArch64 Binaries
 
To execute ARM binaries on an x86 host, register QEMU user-mode emulation through the kernel's `binfmt_misc`. With Docker already installed, the simplest way is:
 
```console
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```
 
This is a one-time, host-level step (it is kernel-wide, so it also applies inside containers). Confirm the handler is registered:
 
```console
cat /proc/sys/fs/binfmt_misc/qemu-aarch64
```
 
You should see an `enabled` entry whose flags include `F`.
 
The targets are dynamically linked against ARM libraries, so QEMU needs an ARM sysroot to find the loader. Install the runtime libraries and point QEMU at them:
 
```console
sudo apt-get install -y libc6-arm64-cross
export QEMU_LD_PREFIX=/usr/aarch64-linux-gnu
```
 
Now the binaries run transparently:
 
```console
$ ./executables/toy_test_suite_0.elf; echo "exit: $?"
```
 
> **Note.** These are deliberately vulnerable programs, so a crash (non-zero exit) can be the *correct* behaviour — a NULL-dereference or buffer-overflow target is meant to crash. You are confirming the binary **loads and starts executing** under emulation, not that it exits cleanly.
 
### Switch Back to x86
 
The `x86` path is untouched. To build `x86` targets again, just unset the variable (or set it to `x86`):
 
```console
unset OPENCRS_TARGET_ARCH
poetry run dataset build --testsuite TOY_TEST_SUITE
```
