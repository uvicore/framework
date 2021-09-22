#!/usr/bin/env bash

# Ensure running from base package path
base="$( cd "$(dirname "$0")" ; cd .. ; pwd -P )"; cd $base

# -x Print a trace of simple commands
# -e Exit immediately if anything return on-zero status
set -x; set -e

# Add ./testapp to pythonpath
export PYTHONPATH=./tests/apps

pytest \
    --color=yes \
    --log-level=WARNING \
    -W ignore::DeprecationWarning \
    --ignore=tests/test_api \
    --ignore=tests/test_database \
    ${@}
