#!/usr/bin/env bash

CHANGED_FILES=$(git diff HEAD --name-only --diff-filter=ACMRTUXB|grep \.py\$)
echo ${CHANGED_FILES}
yapf -i ${CHANGED_FILES}
isort ${CHANGED_FILES}
pyupgrade ${CHANGED_FILES}
flake8 ${CHANGED_FILES}
