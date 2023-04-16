#!/usr/bin/env bash

# Before you can publish, you need to setup a pypi token
# which lives in ~/.pypirc

# Then use that token in poetry
# poetry config pypi-token.pypi <tokenhere>

poetry publish
