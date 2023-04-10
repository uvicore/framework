#!/usr/bin/env bash

# Ensure running from base package path
base="$( cd "$(dirname "$0")" ; cd .. ; pwd -P )"; cd $base

# -x Print a trace of simple commands
# -e Exit immediately if anything return on-zero status
set -x; set -e

# Add ./testapp to pythonpath
export PYTHONPATH=./testapp

# Run tests
./bin/test.sh "$@" --cov=uvicore --cov=tests/apps/app1 --cov-report=term-missing
#./bin/test.sh "$@" --cov=uvicore/database --cov-report=term-missing
