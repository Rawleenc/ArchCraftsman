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
import argparse
import datetime
import re

import git
import git.repo

TITLES = {
    "feat": "#### New features",
    "fix": "#### Fixed issues",
    "revert": "#### Revertions",
    "perf": "#### Performance improvements",
    "refactor": "#### Refactors",
    "test": "#### Tests",
    "docs": "#### Documentation changes",
    "style": "#### Code style changes",
    "chore": "#### Chores",
    "build": "#### Build system or dependencies changes",
    "ci": "#### CI related changes",
}
TITLE_DEFAULT = "#### Other changes"
TYPE_OTHER = "other"


class ConventionalCommit:
    """
    A class representing a conventional commit.
    """

    def __init__(self, commit: git.Commit) -> None:
        header = str(commit.message).split("\n", maxsplit=1)[0]
        type_scope = header.split(":", maxsplit=1)[0].strip()

        match = re.search(r"^[a-z]+", type_scope)
        self.ctype = match.group(0) if match else TYPE_OTHER

        match = re.search(r"\(([^()]+)\)", type_scope)
        self.scope = (
            next(group for group in match.groups()) if match and match.groups() else ""
        )

        self.short_message = header.split(":", maxsplit=1)[1].strip()
        self.body = str(commit.message).replace(header, "").strip()


def print_commit(commit: ConventionalCommit):
    """
    Print a commit in markdown format.
    """
    if commit.scope:
        print(f"* {commit.scope}: {commit.short_message}")
    else:
        print(f"* {commit.short_message}")
    if commit.body:
        print("  <details>")
        print(f"  {commit.body}")
        print("  </details>")


TYPE = "type"
TITLE = "title"
COMMITS = "commits"


def new_part(ctype: str) -> dict:
    """
    Build a part of the changelog.
    """
    return {
        TYPE: ctype,
        TITLE: TITLES.get(ctype, TITLE_DEFAULT),
        COMMITS: [],
    }


def parse_commits(args) -> list[dict]:
    """
    Parse commits and build parts by type.
    """
    repo = git.repo.Repo(".")
    parts: list[dict] = []
    for commit in repo.iter_commits():
        if "chore: :wrench: Prepare next version" in str(commit.message):
            break
        if re.search(r"^[a-z]+(:|\(\w+\):) ", str(commit.message)):
            ccommit = ConventionalCommit(commit)
            ctype = ccommit.ctype if ccommit.ctype in args.types else TYPE_OTHER
            part = next(
                (part for part in parts if part[TYPE] == ctype),
                new_part(ctype) if ctype != TYPE_OTHER or args.others else None,
            )
            if part:
                part[COMMITS].append(ccommit)
                if part not in parts:
                    parts.append(part)

    # Sort parts by type based on the TITLES dictionary order
    parts.sort(
        key=lambda part: len(TITLES) + 1
        if part[TYPE] not in TITLES
        else list(TITLES).index(part[TYPE])
    )
    return parts


def main():
    """
    Generate a changelog from git commits.
    """
    parser = argparse.ArgumentParser(
        description=(
            "The conventional commits changelogs generator "
            "(cf. https://www.conventionalcommits.org/en/v1.0.0)"
        )
    )
    parser.add_argument(
        "version",
        help="specify the version to generate the changelog for",
    )
    parser.add_argument(
        "-t",
        "--types",
        nargs="+",
        default=TITLES.keys(),
        help=(
            "specify types to include in the changelog, separated by spaces "
            "(default: all types of conventional commits)"
        ),
    )
    parser.add_argument(
        "-o",
        "--others",
        action="store_true",
        help="specifty whether to include commits of other types in a dedicated section",
    )
    args = parser.parse_args()

    parts = parse_commits(args)

    # Print the changelog
    print(f"## {args.version} ({datetime.datetime.now().strftime('%Y-%m-%d')})")
    for part in parts:
        title = part[TITLE]
        commits = part[COMMITS]
        commits.reverse()
        if title and commits:
            print(f"{title}")
            for commit in commits:
                print_commit(commit)


if __name__ == "__main__":
    main()
