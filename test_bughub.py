"""
Tests for bughub.

"""
import json
import sys
from StringIO import StringIO

import bughub


def test_main(monkeypatch):
    monkeypatch.setattr(bughub, "urlopen", fake_urlopen)
    argv = [
        "prog",
        "github:user:repo:state=open",
        "bugzilla:state=NEW",
        ]
    monkeypatch.setattr(sys, "argv", argv)

    stdout = StringIO()

    bughub.main(stdout)

    stdout.seek(0)
    output = stdout.read()

    assert output.replace("\r\n", "\n") == """source,id,url,assigned,status,title,product,module,patch
github,123,https://github.com/user/repo/issues/123,nobody,open,Fix the things,repo,repo,n
github,123,https://github.com/user/repo/issues/123,nobody,open,Fix the things,repo,repo,n
bugzilla,123,https://bugzilla.mozilla.org/show_bug.cgi?id=123,foo,open,Fix the things,Core,Component,n
"""


def test_parse_source_github():
    s = bughub.parse_source("github:user:repo:foo=bar:foo=baz")

    assert s.user == "user"
    assert s.repo == "repo"
    assert s.filters == {"foo": ["bar", "baz"]}


def test_parse_source_bugzilla():
    s = bughub.parse_source("bugzilla:foo=bar:foo=baz")

    assert s.filters == {"foo": ["bar", "baz"]}



class FakeResponse(object):
    def __init__(self, body, headers):
        self.body = body
        self.headers = headers


    def read(self):
        return self.body



def fake_github_issue(**kwargs):
    defaults = {
        "number": 123,
        "assignee": None,
        "state": "open",
        "title": "Fix the things",
        "pull_request": {"html_url": None},
        }
    defaults.update(kwargs)

    defaults.setdefault(
        "html_url",
        "https://github.com/user/repo/issues/{0}".format(defaults["number"]),
        )

    return defaults



def fake_bugzilla_issue(**kwargs):
    defaults = {
        "id": 123,
        "assigned_to": {"name": "foo"},
        "status": "NEW",
        "summary": "Fix the things",
        "product": "Core",
        "component": "Component",
        }
    defaults.update(kwargs)

    return defaults


def fake_urlopen(url):
    if "github" in url:
        body = json.dumps([fake_github_issue()])
        if "page=2" in url:
            headers = {
                "Link": 'Link: <https://github.com/user/repo/issues?page=1>; rel="first"'
                }
        else:
            headers = {
                "Link": 'Link: <https://github.com/user/repo/issues?page=2&state=open>; rel="next", <https://github.com/user/repo/issues?page=2&state=open>; rel="last"'
                }
        return FakeResponse(body, headers)
    elif "bugzilla" in url:
        return FakeResponse(json.dumps({"bugs": [fake_bugzilla_issue()]}), {})
    else:
        raise NotImplementedError
