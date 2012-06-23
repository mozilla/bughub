"""
Pull issues from GitHub and Bugzilla and dump as CSV.

CSV columns:

source
id
url
assigned
status
title
product
module
patch ("y" if there is an attachment / pull request, else "n")


"""
import argparse
from collections import defaultdict
import csv
from itertools import chain
import json
import logging
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urljoin
import sys


log = logging.getLogger("bughub")


class IssueSource(object):
    def get_all(self):
        """Yield all issues as standardized dictionaries."""
        raise NotImplemented



class Github(IssueSource):
    API_BASE = "https://api.github.com/"


    def __init__(self, user, repo, **filters):
        """
        Instantiate a Github issues source.

        Filter values that are lists will be sent to the API as multiple values
        for the same-named query string parameter.

        """
        self.user = user
        self.repo = repo
        self.filters = filters
        self.filters.setdefault("per_page", 100)


    def get_all(self):
        """Yield all github issues in standard dictionary format."""
        for issue in self.get_issues():
            yield {
                "source": "github",
                "id": issue["number"],
                "url": issue["html_url"],
                "assigned": issue["assignee"]["login"] if issue["assignee"] else "",
                "status": issue["state"],
                "title": issue["title"],
                "product": self.repo,
                "module": self.repo,
                "patch": "y" if issue["pull_request"]["html_url"] else "n"
                }



    def get_issues(self):
        """Yield github issues in GitHub API JSON format."""
        url = "{0}?{1}".format(
            urljoin(
                self.API_BASE,
                "/".join(["repos", self.user, self.repo, "issues"])
                ),
            urlencode(self.filters, doseq=True),
            )

        while url:
            log.info("Fetching {0}".format(url))
            response = urlopen(url)
            for issue in json.loads(response.read()):
                yield issue

            # Link: <https://.../issues?page=2&state=open>; rel="next",
            #       <https://.../issues?page=13&state=open>; rel="last"
            url = dict(
                reversed([s.strip() for s in l.strip().split(";")])
                for l in response.headers["Link"].split(",")
                ).get('rel="next"', "").strip("<>")



class Bugzilla(IssueSource):
    API_BASE = "https://api-dev.bugzilla.mozilla.org/latest/bug"
    BUG_URL_FORMAT = "https://bugzilla.mozilla.org/show_bug.cgi?id={0}"


    def __init__(self, **filters):
        """
        Instantiate a Bugzilla issues source.

        Filter values that are lists will be sent to the API as multiple values
        for the same-named query string parameter.

        """
        self.filters = filters
        self.filters["include_fields"] = (
            "id,assigned_to,status,summary,product,component,attachments")


    def get_all(self):
        """Yield issues in standard dictionary format."""
        for issue in self.get_issues():
            yield {
                "source": "bugzilla",
                "id": issue["id"],
                "url": self.BUG_URL_FORMAT.format(issue["id"]),
                "assigned": issue["assigned_to"]["name"],
                "status": issue["status"],
                "title": issue["summary"],
                "product": issue["product"],
                "module": issue["component"],
                "patch": "y" if "attachments" in issue else "n"
                }


    def get_issues(self):
        """Yield Bugzilla issues in Bugzilla REST API JSON format."""
        url = "{0}?{1}".format(
            self.API_BASE,
            urlencode(self.filters, doseq=True)
            )

        log.info("Fetching {0}".format(url))

        for issue in json.loads(urlopen(url).read())["bugs"]:
            yield issue


SOURCE_TYPES = {
    "github": Github,
    "bugzilla": Bugzilla,
    }



def parse_source(definition):
    """Parse source definition, return appropriate ``IssueSource`` instance."""
    bits = definition.split(":")
    source_class = SOURCE_TYPES[bits.pop(0)]
    args = []
    kwargs = defaultdict(list)

    for bit in bits:
        if "=" in bit:
            key, val = bit.split("=")
            kwargs[key].append(val)
        else:
            args.append(bit)

    return source_class(*args, **kwargs)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pull bugs from github/bugzilla and dump to CSV.")

    parser.add_argument(
        "sources", metavar="SOURCE", type=str, nargs="+",
        help=(
            "A source definition: "
            "'github:user:repo:field=val' or 'bugzilla:field=val' "
            "(any number of field=val)"
            ),
        )

    parser.add_argument('--verbose', '-v', action='count')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING - (10 * (args.verbose or 0)),
        format="%(name)s - %(levelname)s - %(message)s",
        )

    sources = [parse_source(sd) for sd in args.sources]

    fieldnames = [
        "source",
        "id",
        "url",
        "assigned",
        "status",
        "title",
        "product",
        "module",
        "patch",
        ]


    writer = csv.DictWriter(sys.stdout, fieldnames)
    writer.writerow(dict(zip(fieldnames, fieldnames)))

    for issue in chain(*[source.get_all() for source in sources]):
        writer.writerow(issue)
