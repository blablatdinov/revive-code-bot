# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

# TODO: rename file

"""Creating github client."""

from pathlib import Path

from django.conf import settings
from github import Auth, Github
from github.GithubException import GithubException, UnknownObjectException
from github.Repository import Repository

from main.exceptions import RepoUnavailableError


def github_repo(installation_id: int, full_name: str) -> Repository:
    """Fetch github repo.

    TODO: make object
    """
    auth_methods = (
        Auth.AppAuth(
            874924,
            Path(settings.BASE_DIR / 'revive-code-bot.private-key.pem').read_text(encoding='utf-8'),
        ).get_installation_auth(installation_id),
        Auth.Token(settings.GH_TOKEN),
    )
    for auth_method in auth_methods:
        try:
            return Github(auth=auth_method).get_repo(full_name)
        except (GithubException, UnknownObjectException):
            continue
    raise RepoUnavailableError
