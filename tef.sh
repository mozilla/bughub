#!/bin/sh

python bughub.py -v bugzilla:cf_blocking_b2g=tef+ github:mozilla-b2g:gaia:state=open:labels=blocking-basecamp+ github:mozilla-b2g:gaia:state=closed:labels=blocking-basecamp+
