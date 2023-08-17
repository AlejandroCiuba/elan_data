#!/usr/bin/env bash

# Run mypy and flake8 on the test suite
if [[ $1 = "-a" ]] || [[ $1 = "--all" ]] || [[ $1 = "-t" ]] || [[ $1 = "--tests" ]]; then

    echo "===================== TESTS ====================="
    mypy tests --exclude old_tests.py
    flake8 tests --exclude old_tests.py

    if [[ $1 = "-t" ]] || [[ $1 = "--tests" ]]; then
        exit 0
    fi

elif [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then

    echo "-a --all Run checks on the tests directory"
    echo "-h --help This"
    exit 0

fi

echo "===================== SOURCE ====================="

mypy src
flake8 src
pytest -s --cov src --cov-report html:coverage_report/
