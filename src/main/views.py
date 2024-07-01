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
from pathlib import Path
import json
from django.http import JsonResponse, HttpResponse, HttpRequest
from github import Auth, Github
from django.views.decorators.csrf import csrf_exempt

from main.models import GhInstallation, GhRepo


def healthcheck(request):
    """Endpoint for checking app."""
    return JsonResponse({
        'app': 'ok',
    })


@csrf_exempt
def webhook(request: HttpRequest):  # FIXME add secret
    if request.headers['X-GitHub-Event'] == 'installation_repositories':
        request_json = json.loads(request.body)
        installation_id = request_json['installation']['id']
        gh_instn, _ = GhInstallation.objects.get_or_create(installation_id=installation_id)
        new_repos = []
        auth = Auth.AppAuth(874924, Path('revive-code-bot.2024-04-11.private-key.pem').read_text())
        gh = Github(auth=auth.get_installation_auth(installation_id))
        for repo in request_json['repositories_added']:
            new_repos.append(GhRepo(
                full_name=repo['full_name'],
                gh_installation=gh_instn,
                has_webhook=False),
            )
            GhRepo.objects.bulk_create(new_repos)
            gh_repo = gh.get_repo(repo['full_name'])
            gh_repo.create_hook(
                'web', {'url': 'http://revive-code-bot.ilaletdinov.ru/hook/github', 'content_type': 'json'},
                ['issues', 'issue_comment', 'push'],
            )
        gh.close()
    elif request.headers['X-GitHub-Event'] == 'ping':
        request_json = json.loads(request.body)
        pg_repo = GhRepo.objects.get(full_name=request_json['repository']['full_name'])
        pg_repo.has_webhook = True
        pg_repo.save()
    return HttpResponse()
