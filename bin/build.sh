#!/usr/bin/env bash

# Ensure you bump up the version number in pyproject.toml AND in __init__.py

# Using --locked ensures the build process uses the precise dependency versions
# specified in poetry.lock, leading to more consistent and reproducible builds.
# This is particularly important for production builds where you want to avoid
# unexpected changes in dependencies that could introduce bugs or vulnerabilities.
# It helps maintain stability and reliability in your application by ensuring
# that the same versions of dependencies are used every time you build the project.
poetry build --locked
