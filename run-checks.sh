#!/usr/bin/env bash

# Run mypy and flake8
mypy src
flake8 src
pytest
