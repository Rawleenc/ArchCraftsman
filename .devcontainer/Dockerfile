FROM ubuntu:rolling

RUN apt-get update \
    && apt-get install -y \
    curl \
    git \
    golang \
    python3 \
    python3-venv \
    python3-pip \
    sudo \
    vim \
    wget \
    && apt-get clean \
    && rm -rf "/var/lib/apt/lists/*"

ARG USER=coder
RUN useradd --groups sudo --shell /bin/bash ${USER} \
    && echo "${USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/${USER} \
    && chmod 0440 /etc/sudoers.d/${USER}
USER ${USER}
WORKDIR /home/${USER}

RUN cp /etc/skel/.bashrc . \
    && cp /etc/skel/.profile . \
    && cp /etc/skel/.bash_logout .
