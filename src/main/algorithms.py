"""The MIT License (MIT).

Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
from typing import TypedDict
import tempfile
from collections import defaultdict, OrderedDict
from operator import itemgetter
from os import PathLike
from pathlib import Path

import pytest
from git import Repo


def files_changes_count(repo_path: Path, files_for_check: list[Path]):
    repo = Repo(repo_path)
    file_change_count: dict[str | PathLike[str], int] = defaultdict(int)
    for commit in repo.iter_commits():
        for item in commit.stats.files.items():
            filename, stats = item
            if (repo_path / filename) in files_for_check:
                file_change_count[repo_path / filename] += stats['lines']
    return {
        file: hoc
        for file, hoc in file_change_count.items()
    }


def files_sorted_by_last_changes(repo_path: Path, files_for_check: list[Path]):
    repo = Repo(repo_path)
    file_last_commit: dict[PathLike[str], datetime.datetime] = {}
    now = datetime.datetime.now(tz=datetime.UTC)
    for file in files_for_check:
        file_last_commit[file] = (now - next(repo.iter_commits(paths=file)).committed_datetime).days
    return {
        file: days
        for file, days in file_last_commit.items()
    }


def apply_coefficient(file_point_map: dict[PathLike[str], int], coefficient: float):
    return {
        file: points * coefficient
        for file, points in file_point_map.items()
    }


def file_editors_count(repo_path, files_for_check: list[Path]):
    repo = Repo(repo_path)
    file_editors_map = defaultdict(set)
    for commit in repo.iter_commits():
        files = commit.stats.files
        author = commit.author.email
        for file in files:
            if repo_path / file in files_for_check:
                file_editors_map[repo_path / file].add(author)
    return {
        file: len(authors)
        for file, authors in file_editors_map.items()
    }


def lines_count(files_for_check: list[Path]):
    return {
        file: file.read_text().count('\n')
        for file in files_for_check
    }


def merge_rating(
    *file_point_maps: tuple[dict[PathLike[str], int]],
):
    res = defaultdict(int)
    for file_points_map in file_point_maps:
        for file, points in file_points_map.items():
            res[file] += points
    return dict(res)
