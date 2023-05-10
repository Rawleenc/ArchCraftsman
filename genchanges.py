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

"""
A Python script to generate a changelog from git commits.
"""
import re
import sys
from datetime import datetime

from git import Commit
from git.repo import Repo


def print_commit(commit: Commit):
    """
    Print a commit in markdown format.
    """
    message: str = re.sub(
        r"^[a-z]+(:|\(\w+\):)|:[a-z]+:", "", str(commit.message)
    ).strip()
    short_message: str = str(message).split("\n", maxsplit=1)[0]
    details: str = message.replace(short_message, "").strip().replace("\n", "\n  ")
    print(f"* {short_message}")
    if details:
        print("  <details>")
        print(f"  {details}")
        print("  </details>")


def main(version: str):
    """
    Generate a changelog from git commits.
    """
    repo = Repo(".")
    commits: list[Commit] = []

    for commit in repo.iter_commits():
        if "chore: :wrench: Prepare next version" in str(commit.message):
            break
        if re.match(r"^[a-z]+(:|\(\w+\):) ", str(commit.message)):
            commits.append(commit)

    features = [it for it in commits if re.match(r"^feat(:|\(\w+\):)", str(it.message))]
    fixes = [it for it in commits if re.match(r"^fix(:|\(\w+\):)", str(it.message))]
    others = [
        it
        for it in commits
        if not re.match(r"^feat(:|\(\w+\):)", str(it.message))
        and not re.match(r"^fix(:|\(\w+\):)", str(it.message))
    ]

    print(f"## Release {version} ({datetime.now().strftime('%Y-%m-%d')})")

    if features:
        print("#### New features")
        for commit in features:
            print_commit(commit)

    if fixes:
        print("#### Fixed issues")
        for commit in fixes:
            print_commit(commit)

    if others:
        print("#### Other changes")
        for commit in others:
            print_commit(commit)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python genchangelog.py <version>")
        sys.exit(1)
    main(sys.argv[1])
