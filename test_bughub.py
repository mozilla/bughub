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

    output = output.replace("\r\n", "\n")
    expected = """source,id,url,assigned,status,title,product,module,patch,feature
github,123,https://github.com/user/repo/issues/123,nobody,open,Fix the things,repo,repo,n,n
github,124,https://github.com/user/repo/issues/124,nobody,open,Fix the things,repo,repo,n,y
github,125,https://github.com/user/repo/issues/125,nobody,open,Fix the things,repo,repo,n,n
github,123,https://github.com/user/repo/issues/123,nobody,open,Fix the things,repo,repo,n,n
github,124,https://github.com/user/repo/issues/124,nobody,open,Fix the things,repo,repo,n,y
github,125,https://github.com/user/repo/issues/125,nobody,open,Fix the things,repo,repo,n,n
bugzilla,123,https://bugzilla.mozilla.org/show_bug.cgi?id=123,foo,open,Fix the things,Core,Component,n,n
bugzilla,124,https://bugzilla.mozilla.org/show_bug.cgi?id=124,foo,open,Fix the things,Core,Component,n,y
bugzilla,125,https://bugzilla.mozilla.org/show_bug.cgi?id=125,foo,open,Fix the things,Core,Component,n,n
"""
    # Uncomment these lines for debugging
    #print "output: %s" % output
    #print "expected: %s" % expected
    assert output == expected

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
    defaults ={
        "number": 123,
        "assignee": None,
        "state": "open",
        "title": "Fix the things",
        "pull_request": {"html_url": None},
        "labels": []
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
        "keywords": ""
        }
    defaults.update(kwargs)

    return defaults


def fake_urlopen(url):
    githubissues = [fake_github_issue(),
                    fake_github_issue(number=124,labels=[{"name":"foo","color":"red"},{"name":"feature","color": "black"}]),
                    fake_github_issue(number=125,labels=[{"name":"foo","color":"blue"}])]

    bugzillaissues = [fake_bugzilla_issue(),
                      fake_bugzilla_issue(id=124, keywords=["foo","feature"]),
                      fake_bugzilla_issue(id=125, keywords=["foo"])]

    if "github" in url:
        body = json.dumps(githubissues)
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
        return FakeResponse(json.dumps({"bugs": bugzillaissues}), {})
    else:
        raise NotImplementedError
