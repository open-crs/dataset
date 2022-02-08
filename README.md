# `dataset` 🗂️

## Description 🖼️

**`dataset`** is the CRS module that compiles and manages the vulnerable programs that the CRS will analyze.

The **supported test suites** are the following:
- **NIST's Juliet**; and
- **NIST's C Test Suite**.

## How It Works 🪄

The module does the following steps for each test suite that needs to be built:
1. Getting the available sources into the test suite's folder;
2. Preprocessing the sources for including all the required sources and header;
3. Writing the preprocessed sources into the `sources` folder from the root of the repository;
4. Creating a new entry into the CSV files of the dataset, namely `vulnerables.csv`;
5. Filtering the sources based on the wanted CWEs;
6. Compiling the preprocessed sources with the compile and link flags from multiple sources (module's ones and user-provided); and
7. Writing the executables into the `executables` folder from the root of the repository.

## Limitations 🚧

The only constraint that was imposed for the generated programs is the ELF format, as they are compiled with `gcc`.

## Setup 🔧

Only install the required packages via `pip3 install -r requirements.txt`.

## Usage 🧰

The module can be used both **as a CLI tool**, by using the script `cli.py`.

```
./cli.py build --testsuite C_TEST_SUITE --compile-flags="-m32 -fsanitize=address -g"
[+] Successfully built 50 source(s).
```

```
./cli.py show
[+] The information about the dataset's sources are:

---------------------  ---  -----------------  -----
nist_c_test_suite_145  251  nist_c_test_suite  True
nist_c_test_suite_65   121  nist_c_test_suite  True
[...]
```

In the same time, it can be imported as a **Python 3 module**, taking the `cli.py` as a starting point.