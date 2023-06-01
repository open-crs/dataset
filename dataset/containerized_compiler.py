import logging
import os

import docker

from dataset.configuration import Configuration


class ContainerizedCompiler:
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
                Configuration.ContainerizedCompiler.CONTAINER_WORKING_DIRECTORY,
                folder,
            )

            volumes[host_folder] = {
                "bind": container_folder,
                "mode": "rw",
            }

        self.__container = self.__docker_client.containers.run(
            Configuration.ContainerizedCompiler.IMAGE_TAG,
            command="tail -f /dev/null",
            detach=True,
            tty=True,
            volumes=volumes,
        )

    def exec_compiler_command(self, command: str) -> int:
        exit_code, output = self.__container.exec_run(
            command,
            workdir=Configuration.ContainerizedCompiler.CONTAINER_WORKING_DIRECTORY,
        )

        logging.log(
            logging.INFO,
            (
                f'The command "{command}" was executed in container, having'
                f" the exit code {exit_code}."
            ),
        )
        if output:
            output = output.decode("utf-8")
            logging.log(logging.INFO, f"The output is:\n\n{output}")

        return exit_code
