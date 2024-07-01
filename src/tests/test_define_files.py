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
import tempfile
from itertools import cycle
from pathlib import Path

import pytest
from git import Repo

from main.algorithms import (
    apply_coefficient,
    file_editors_count,
    files_changes_count,
    files_sorted_by_last_changes,
    lines_count,
    merge_rating,
)


@pytest.fixture()
def repo_path(faker, time_machine):
    """Path to temorary git repo."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    repo = Repo.init(temp_dir_path)
    today = datetime.datetime(2024, 4, 20, tzinfo=datetime.UTC)
    time_machine.move_to(today)
    repo.config_writer().set_value('user', 'name', 'First Contributer').release()
    repo.config_writer().set_value('user', 'email', 'first-contributer@github.com').release()
    for filename in 'first.py', 'second.py', 'third.py', 'config.yaml':
        Path(temp_dir_path / filename).write_text('', encoding='utf-8')
        repo.index.add([filename])
        repo.index.commit(filename)
    for i, (name, email) in zip(
        range(6),
        cycle([
            ('First Contributer', 'first-contributer@github.com'),
            ('Second Contributer', 'second-contributer@github.com')],
        ),
    ):
        repo.config_writer().set_value('user', 'name', name).release()
        repo.config_writer().set_value('user', 'email', email).release()
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'first.py').write_text(faker.text(), encoding='utf-8')
        repo.index.add(['first.py'])
        repo.index.commit('Important changes')
    for i in range(5, 7):
        repo.config_writer().set_value('user', 'name', 'Thrird Contributer').release()
        repo.config_writer().set_value('user', 'email', 'thrird-contributer@github.com').release()
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'config.yaml').write_text(faker.text(), encoding='utf-8')
        repo.index.add(['config.yaml'])
        repo.index.commit('Config changes')
    time_machine.move_to(today + datetime.timedelta(15))
    repo.config_writer().set_value('user', 'name', 'First Contributer').release()
    repo.config_writer().set_value('user', 'email', 'first-contributer@github.com').release()
    (Path(temp_dir_path / 'dir1')).mkdir()
    Path(temp_dir_path / 'dir1/file_in_dir.py').write_text('File in directory', encoding='utf-8')
    repo.index.add(['dir1/file_in_dir.py'])
    repo.index.commit('Create directory')
    time_machine.move_to(today + datetime.timedelta(17))
    Path(temp_dir_path / 'first.py').write_text(faker.text(1000), encoding='utf-8')
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
        'first.py': 28,
        'third.py': 0,
    }


def test_last_changes(repo_path, time_machine):
    time_machine.move_to('2024-06-02')
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {'dir1/file_in_dir.py': 28, 'first.py': 26, 'third.py': 43}


def test_file_editors_count(repo_path):
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in file_editors_count(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {'dir1/file_in_dir.py': 1, 'first.py': 2, 'third.py': 1}


def test_merge_real_ratings(repo_path):
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in merge_rating(
            files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))),
            files_changes_count(repo_path, list(repo_path.glob('**/*.py'))),
        ).items()
    }

    assert got == {'dir1/file_in_dir.py': 3, 'first.py': 28, 'third.py': 17}


def test_lines_count(repo_path):
    got = {
        str(file).replace(str(repo_path), '')[1:]: rating
        for file, rating in lines_count(list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {'dir1/file_in_dir.py': 0, 'first.py': 9, 'third.py': 0}


def test_merge_rating():
    got = merge_rating(
        {'first.py': 4},
        {'first.py': 6},
        {'first.py': 7, 'second.py': 2},
    )

    assert got == {'first.py': 17, 'second.py': 2}


def test_apply_coefficient():
    got = apply_coefficient(
        {'first.py': 5},
        0.5,
    )

    assert got == {'first.py': 2.5}


def test():
    repo_path = Path('/Users/almazilaletdinov/code/quranbot/bot')
    # repo_path = Path('/Users/almazilaletdinov/code/source-codes/wemake-python-styleguide')
    # repo_path = Path('/Users/almazilaletdinov/code/moment/mindskills-frontend')
    # repo_path = Path('/Users/almazilaletdinov/code/source-codes/django')
    # for file in repo_path.glob('**/*.py'):
    #     if '.venv' in str(file) or 'venv' in str(file) or '__init__.py' in str(file):
    #         continue
    #     if file.read_text().count('\n') < 5:
    #         print(file)
    #         file.unlink()
    files_for_search = [
        # Path('/Users/almazilaletdinov/code/moment/portal_back/static/static_dev/AdminLTE/bower_components/moment/min/tests.js'),
    ]
    for entry in Repo(repo_path).commit().tree.traverse():
        if Path(repo_path / entry.path).is_file() and str(entry.path).endswith('.py'):
            try:
                Path(repo_path / entry.path).read_text()
                files_for_search.append(Path(repo_path / entry.path))
            except:
                pass
    got = merge_rating(
        apply_coefficient(
            files_sorted_by_last_changes(repo_path, files_for_search),
            1,
        ),
        # apply_coefficient(
        #     files_changes_count(repo_path, files_for_search),
        #     -1,
        # ),
    )
    # got = merge_rating(
    #     apply_coefficient(
    #         file_editors_count(repo_path, files_for_search),
    #         -20,
    #     ),
    #     apply_coefficient(
    #         lines_count(files_for_search),
    #         0.5,
    #     ),
    #     apply_coefficient(
    #         files_sorted_by_last_changes(repo_path, files_for_search),
    #         1,
    #     ),
    #     apply_coefficient(
    #         files_changes_count(repo_path, files_for_search),
    #         -1,
    #     ),
    # )

    from operator import itemgetter
    a = sorted(
        [
            (file, points)
            for file, points in got.items()
        ],
        key=itemgetter(1),
        reverse=True,
    )
    for idx, (file, points) in enumerate(a):
        print(idx, str(file), points)
