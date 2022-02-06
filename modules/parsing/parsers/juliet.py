import os
import subprocess
import shutil
from .dataset_worker import DatasetWorker

DATABASE_NAME = 'nist_juliet_'
NIST_JULIET_DATASET_NAME = "nist_juliet"
DATABASE_PATH = "/raw_testsuites/" + NIST_JULIET_DATASET_NAME

#os.chdir('/mnt/d/Master/Disertatie/Datasets/dataset')


class DatasetException(Exception):
    """Dataset exception class for our app
    
    Attributes:
        expression : input expression in which the error occurred
        message : explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def _generate_makefile(source_id: int) -> int:
    try:
        working_dir = os.getcwd()
        source_root_dir = working_dir + "/sources/" + DATABASE_NAME + str(
            source_id)
        source_location = source_root_dir + "/src"
        source_location_files_list = os.listdir(source_location)

        if len(source_location_files_list) == 1:
            # Only one source at this point at least is used per binary
            source_file_path = source_location_files_list[0]
            source_type = os.path.splitext(source_file_path)[1]

            compiler = None

            # Some sources are .cpp other are .c
            if source_type == '.c':
                compiler = 'gcc'
            else:
                compiler = 'g++'

            makefile_string = "FLAGS = -c -Wall -DINCLUDEMAIN -I../nist_lib/\n\nall: binary\n\nbinary:\n\t%s $(FLAGS) -o binary.elf src/source%s" % (
                compiler, source_type)
            makefile_path = source_root_dir + "/Makefile"

            # Write the makefile so that it will work from that directory when calling `make`

            # Check fi existst
            if os.path.isfile(makefile_path) == False:
                with open(makefile_path, "w") as makefile:
                    makefile.write(makefile_string)
        else:
            raise DatasetException(
                "_generate_makefile", "No source file was find for " +
                DATABASE_NAME + str(source_id))

    except Exception as exception:
        raise DatasetException("_generate_makefile", str(exception))

    return 0


def _generate_readme(source_id: int, cwe: str, binary_description: str) -> int:

    if not cwe or not binary_description:
        raise DatasetException("_generate_readme",
                               "Empty cwe or binary_description strings!")

    try:
        working_dir = os.getcwd()
        source_root_dir = working_dir + "/sources/" + DATABASE_NAME + str(
            source_id)

        readme_path = source_root_dir + "/README.md"
        readme_string = "# %s\n\nVulnerability Name: **%s**\n\nDataset: **MNIST**\n\nBinary can be build via the **Makefile**" % (
            cwe, binary_description)

        if os.path.isfile(readme_path) == False:
            with open(readme_path, "w") as makefile:
                makefile.write(readme_string)

    except Exception as exception:
        raise DatasetException("_generate_readme", str(exception))
    return 0


def _compile_binary(source_id: int) -> int:

    try:
        working_dir = os.getcwd()
        source_root_dir = working_dir + "/sources/" + DATABASE_NAME + str(
            source_id)
        source_location = source_root_dir + "/src"
        source_location_files_list = os.listdir(source_location)

        include_folder_path = working_dir + "/sources/" + "nist_lib/"
        binary_out_path = working_dir + "/executables/" + DATABASE_NAME + str(
            source_id) + ".elf"

        if len(source_location_files_list) == 1:
            # Only one source at this point at least is used per binary
            source_file_path = source_location_files_list[0]
            source_type = os.path.splitext(source_file_path)[1]
            compiler = None

            # Some sources are .cpp other are .c
            if source_type == '.c':
                compiler = 'gcc'
            else:
                compiler = 'g++'

            compile_string = "%s -c -Wall -DINCLUDEMAIN -I%s -o %s %s" % (
                compiler, include_folder_path, binary_out_path,
                source_location + "/" + source_file_path)

            # Run gcc or g++ with given arguments inside a TreadPoolExecutor

            #if os.path.isfile(binary_out_path) == False:

            process = subprocess.Popen(compile_string.split(" "),
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out, err = process.communicate()

            # If no exception or out was generated then we are ok!
            if not out and not err:
                return 0

        else:
            raise DatasetException(
                "_compile_binary", "No source file was find for " +
                DATABASE_NAME + str(source_id))

    except Exception as exception:
        raise DatasetException("_compile_binary", str(exception))

    return 1


def _log_compile(future):
    try:
        thread_result = future.result()
        if thread_result == 0:
            print("Executable " + str(future.source_id) +
                  " has finished succesfully!")
        else:
            print("Executable " + str(future.source_id) +
                  " has finished with error " + str(thread_result) + " !")
    except Exception as exception:
        print("Exception occured during compiling of " +
              str(future.source_id) + " : " + str(exception))


def _create_directory_not_exist(directory_path: str) -> None:
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


def _process_file(source_id: int, source_path: str,
                  dataset_worker: DatasetWorker) -> int:

    working_dir = os.getcwd()

    # Create directories
    source_directory = working_dir + "/sources/" + DATABASE_NAME + str(
        source_id)
    _create_directory_not_exist(source_directory)
    _create_directory_not_exist(source_directory + "/src/")
    _create_directory_not_exist(source_directory + "/lib/")

    # Copy source file

    extension = os.path.splitext(source_path)[1]

    # Error if we have a .h file
    # Must write more code here
    # Found a solution @ 6:13 AM

    base_file_name = os.path.basename(source_path)

    if extension == ".h":
        shutil.copy(working_dir + source_path,
                    working_dir + "/sources/nist_lib/" + base_file_name)
        return 0
    else:
        shutil.copy(
            working_dir + source_path, working_dir + "/sources/" +
            DATABASE_NAME + str(source_id) + "/src/source" + extension)
        # We are here so it's a valid source file
        # Get propetry from filename
        # /raw_testsuites/nist/testcases/CWE90_LDAP_Injection/CWE90_LDAP_Injection__w32_wchar_t_listen_socket_84_goodG2B.cpp # Example
        base_file_name = os.path.splitext(base_file_name)[
            0]  # Keep only filename without extension
        # First test if source file exists

        if os.path.exists(working_dir + "/sources/" + DATABASE_NAME +
                          str(source_id) + "/src/source" + extension) == True:
            _generate_makefile(source_id)
            cwe_filename_splitted = base_file_name.split("_")
            cwe_name = cwe_filename_splitted[0]
            cwe_filename_splitted.pop()
            _generate_readme(source_id, cwe_name,
                             " ".join(cwe_filename_splitted))
            compile_result = _compile_binary(source_id)

            if compile_result == 0:
                dataset_worker.add(DATABASE_NAME + str(source_id), [cwe_name],
                                   NIST_JULIET_DATASET_NAME)
                print("Executable " + DATABASE_NAME + str(source_id) +
                      " has finished succesfully!")
                return 1
            else:
                print("Executable " + DATABASE_NAME + str(source_id) +
                      " has finished with error " + str(compile_result) + " !")
                os.remove(working_dir + "/sources/" + DATABASE_NAME +
                          str(source_id) + "/src/source" + extension)
                return 0

    return 0


def make_nist_juliet(dataset_worker: DatasetWorker) -> int:
    '''Function used to build and move the NIST dataset accordingly to our plan. 
Returns 0 if it succeeded else throws an DatasetException'''

    # Find all files with .c and their path

    #_generate_makefile(1)
    #_generate_readme(1, "CWE23", "Relative Path Traversal char environment ofstream")

    # Must find a way to get an ID, starting from 1 if folder is empty or from the max number if it is not empty

    # Must compile the executable first if does not compile, mark it as error

    working_dir = os.getcwd()
    cew_root_dir = working_dir + DATABASE_PATH + "/testcases/"
    cwe_source_dirss = os.listdir(cew_root_dir)

    # Find the source_id start, either it's one or max
    #existing_sources = os.listdir(working_dir + "/sources")

    # source_id = None
    # existing_sources.append("1")
    # source_id = max(int(i) for i in existing_sources if i.isnumeric())

    source_id = 1

    # Create the nist_lib directory containing all .h files

    _create_directory_not_exist(working_dir + "/sources/nist_lib/")

    # Copy header files

    header_files = os.listdir(working_dir + DATABASE_PATH + "/testcasesupport")
    for header_file in header_files:
        shutil.copy(
            working_dir + DATABASE_PATH + "/testcasesupport/" + header_file,
            working_dir + "/sources/nist_lib/" + header_file)

    # Fetch all files
    for cwe_directory in cwe_source_dirss:
        cwe_directory_files = os.listdir(cew_root_dir + cwe_directory + "/")
        for source_file in cwe_directory_files:

            # Check if it's a folder
            if os.path.isdir(cew_root_dir + cwe_directory + "/" +
                             source_file) == True:
                source_files = os.listdir(cew_root_dir + cwe_directory + "/" +
                                          source_file)
                for file in source_files:
                    #process file
                    source_id += _process_file(
                        source_id, DATABASE_PATH + "/testcases/" +
                        cwe_directory + "/" + source_file + "/" + file,
                        dataset_worker)

            else:
                # process file
                source_id += _process_file(
                    source_id, DATABASE_PATH + "/testcases/" + cwe_directory +
                    "/" + source_file, dataset_worker)

    return 0
