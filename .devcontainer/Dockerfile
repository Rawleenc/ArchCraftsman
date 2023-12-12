# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

RUN useradd --groups sudo --shell /bin/bash coder \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/coder \
    && chmod 0440 /etc/sudoers.d/coder \
    && cp /etc/skel/.bashrc /home/coder \
    && cp /etc/skel/.profile /home/coder \
    && cp /etc/skel/.bash_logout /home/coder

USER coder