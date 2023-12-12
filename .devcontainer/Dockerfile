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

FROM python

RUN apt-get update \
    && apt-get install -y \
    zsh \
    curl \
    git \
    sudo \
    vim \
    wget \
    && apt-get clean \
    && rm -rf "/var/lib/apt/lists/*"

RUN useradd --create-home --groups sudo --shell /bin/zsh coder \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/coder \
    && chmod 0440 /etc/sudoers.d/coder

USER coder

RUN wget -O /home/coder/.zshrc https://git.grml.org/f/grml-etc-core/etc/zsh/zshrc \
    && wget -O /home/coder/.zshrc.local  https://git.grml.org/f/grml-etc-core/etc/skel/.zshrc
