#!/usr/bin/env bash

GITHUB="https://github.com"

failed_checkout() {
  echo "Failed to git clone $1"
  exit -1
}

checkout() {
  [ -d "$2" ] || git clone --depth 1 "$1" "$2" || failed_checkout "$1"
}

pyenv version
pyenv --version

export PYENV_ROOT="/opt/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

cd $PYENV_ROOT
git fetch --depth=1 origin
git checkout origin/master

if ! pyenv update;then
    checkout "${GITHUB}/pyenv/pyenv-update.git"     "${PYENV_ROOT}/plugins/pyenv-update"
    pyenv update
fi

pyenv versions

if ! pyenv latest install 3.7 -s;then
    checkout "${GITHUB}/momo-lab/xxenv-latest.git"  "${PYENV_ROOT}/plugins/xxenv-latest"
    pyenv latest install 3.7 -s
fi

pyenv versions

pyenv latest global 3.7
