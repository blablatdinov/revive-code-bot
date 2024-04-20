"""The MIT License (MIT).

Copyright (c) 2013-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from collections import defaultdict
from operator import itemgetter
from os import PathLike
from pathlib import Path

import pytest
from git import Repo

from main.algorithms import files_changes_count, files_sorted_by_last_changes, merge_rating, apply_coefficient


@pytest.fixture()
def repo_path(faker, time_machine):
    """Path to temorary git repo."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    repo = Repo.init(temp_dir_path)
    today = datetime.datetime(2024, 4, 20)
    time_machine.move_to(today)
    for filename in 'first.py', 'second.py', 'third.py', 'config.yaml':
        Path(temp_dir_path / filename).write_text('')
        repo.index.add([filename])
        repo.index.commit(filename)
    for i in range(6):
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'first.py').write_text(faker.text())
        repo.index.add(['first.py'])
        repo.index.commit('Important changes')
    for i in range(5, 7):
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'config.yaml').write_text(faker.text())
        repo.index.add(['config.yaml'])
        repo.index.commit('Config changes')
    time_machine.move_to(today + datetime.timedelta(15))
    (Path(temp_dir_path / 'dir1')).mkdir()
    Path(temp_dir_path / 'dir1/file_in_dir.py').write_text('File in directory')
    repo.index.add(['dir1/file_in_dir.py'])
    repo.index.commit('Create directory')
    time_machine.move_to(today + datetime.timedelta(17))
    Path(temp_dir_path / 'first.py').write_text('Some changes')
    repo.index.add(['first.py'])
    repo.index.commit('Some changes')
    (Path(temp_dir_path / 'second.py')).unlink()
    yield temp_dir_path
    temp_dir.cleanup()


def test_files_change_count(repo_path):
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in files_changes_count(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {
        'dir1/file_in_dir.py': 1,
        'first.py': 19,
        'third.py': 0,
    }


def test_last_changes(repo_path, time_machine):
    time_machine.move_to('2024-06-02')
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {'dir1/file_in_dir.py': 28, 'first.py': 26, 'third.py': 43}


def test_merge_real_ratings(repo_path):
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in merge_rating(
            files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))),
            files_changes_count(repo_path, list(repo_path.glob('**/*.py'))),
        ).items()
    }

    assert got == {'dir1/file_in_dir.py': 3, 'first.py': 19, 'third.py': 17}


def test_merge_rating():
    got = merge_rating(
        {'first.py': 4},
        {'first.py': 6},
    )

    assert got == {'first.py': 10}


def test_apply_coefficient():
    got = apply_coefficient(
        {'first.py': 5},
        0.5
    )

    assert got == {'first.py': 2.5}
