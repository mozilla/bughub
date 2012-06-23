"""
Tests for bughub.

"""
import bughub


def test_parse_source_github():
    s = bughub.parse_source("github:user:repo:foo=bar:foo=baz")

    assert s.user == "user"
    assert s.repo == "repo"
    assert s.filters == {"foo": ["bar", "baz"]}


def test_parse_source_bugzilla():
    s = bughub.parse_source("bugzilla:foo=bar:foo=baz")

    assert s.filters == {"foo": ["bar", "baz"]}
