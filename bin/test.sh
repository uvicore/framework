#!/usr/bin/env bash

# Ensure running from base package path
base="$( cd "$(dirname "$0")" ; cd .. ; pwd -P )"; cd $base

# -x Print a trace of simple commands
# -e Exit immediately if anything return on-zero status
set -x; set -e

#cd $base && pytest --cov=uvicore --cov=tests --cov-report=term-missing --cov-report=xml tests
pytest --cov=uvicore --cov=tests --cov-report=term-missing tests ${@}
