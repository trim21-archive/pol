#!/usr/bin/env bash
set -e

pip-compile --no-index ./requirements/dev.in

pip-compile --no-index ./requirements/prod.in

cat ./requirements/prod.in | grep linux >> ./requirements/prod.txt

pip-sync requirements/*.txt docs/requirements.txt
