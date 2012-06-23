#!/bin/sh

python bughub.py -v \
  bugzilla:cf_blocking_basecamp=+:status=NEW:status=ASSIGNED:status=UNCONFIRMED:status=REOPENED \
  github:mozilla-b2g:gaia:state=open
