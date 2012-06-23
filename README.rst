BugHub
======

Get bugs from GitHub and Bugzilla and dump them to a CSV file.

Usage::

    python bughub.py SOURCE [SOURCE] [...]

Each ``SOURCE`` is a string such as::

    github:user:repo:field=value

or::

    bugzilla:field=value

In either of the above cases, any number of ``field=value`` clauses can be
included in the source definition; they will be urlencoded and passed directly
to the relevant API as querystring parameters.

CSV output will go to stdout.

Use the ``-v`` or ``--verbose`` option to get debug logging to stderr.

See the included ``basecamp.sh`` for sample usage.

Requires Python 2.7 (or Python 2.6 with the ``argparse`` package installed).

Developing
----------

To install the requirements for running the tests::

    pip install -r requirements.txt

To run the tests and measure coverage::

    ./runtests.sh

To view test coverage data::

    firefox htmlcov/index.html
