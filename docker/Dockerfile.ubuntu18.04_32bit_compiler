FROM i386/ubuntu:18.04

ENV USER="docker" \
    HOME="/home/docker"

RUN apt-get update \
                   && apt-get upgrade -y \
                       && apt-get install -y \
        build-essential \
        cmake \
        libstdc++-8-dev

CMD ["/bin/bash"]
