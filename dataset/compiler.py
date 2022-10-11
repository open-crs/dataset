import os

import docker

from dataset.configuration import Configuration


class Compiler:
    docker_client: docker.client

    def __init__(self) -> None:
        self.__docker_client = docker.from_env()

        self.__create_container()

    def __del__(self) -> None:
        self.__container.remove(force=True)

    def __create_container(self) -> None:
        volumes = {}
        for folder in [
            Configuration.Assets.MAIN_DATASET_SOURCES,
            Configuration.Assets.MAIN_DATASET_EXECUTABLES,
            Configuration.Assets.RAW_TESTSUITES,
        ]:
            host_folder = os.path.join(
                Configuration.Assets.HOST_WORKING_DIRECTORY,
                folder,
            )
            container_folder = os.path.join(
                Configuration.Compiler.CONTAINER_WORKING_DIRECTORY,
                folder,
            )

            volumes[host_folder] = {
                "bind": container_folder,
                "mode": "rw",
            }

        self.__container = self.__docker_client.containers.run(
            Configuration.Compiler.IMAGE_TAG,
            command="tail -f /dev/null",
            detach=True,
            tty=True,
            volumes=volumes,
        )

    def exec_compiler_command(self, command: str) -> int:
        result = self.__container.exec_run(
            command, workdir=Configuration.Compiler.CONTAINER_WORKING_DIRECTORY
        )

        return result.exit_code
