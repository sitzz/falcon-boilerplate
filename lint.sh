#!/bin/bash

# Variables

# Detect if in virtual env
[[ "$VIRTUAL_ENV" == "" ]]; INVENV=$?

# If not, exit - user will have to activate it
if [ $INVENV -eq 0 ]; then
  echo "ERROR: not in activated virtual environment"
  exit 1
fi

# Install linting tools
pip -qqq install flake8 pylint mypy bandit

# Install their dependencies etc.
pip -qqq install types-redis

# Run the linting
echo "### RUNNING FLAKE8 ###"
flake8 --max-line-length=120 --ignore=E402,E722 falcon_boilerplate/*.py
if [ $? -gt 0 ]; then
  echo "!!! FLAKE8 RETURNED ERRORS !!!"
else
  echo "- First check ok"
fi
flake8 --max-line-length=120 --ignore=E402,E722 falcon_boilerplate/**/*.py
if [ $? -gt 0 ]; then
  echo "!!! FLAKE8 RETURNED ERRORS !!!"
else
  echo "- Second check ok"
fi
echo

echo "### RUNNING PYLINT ###"
pylint --max-line-length=120 --recursive=yes --errors-only falcon_boilerplate/
if [ $? -gt 0 ]; then
  echo "!!! PYLINT RETURNED ERRORS !!!"
else
  echo "- All ok"
fi
echo

echo "### RUNNING MYPY ###"
mypy falcon_boilerplate/*.py --ignore-missing-imports --no-error-summary --install-types --non-interactive
if [ $? -gt 0 ]; then
  echo "!!! MYPY RETURNED ERRORS !!!"
else
  echo "- First check ok"
fi
mypy falcon_boilerplate/**/*.py --ignore-missing-imports --no-error-summary --install-types --non-interactive
if [ $? -gt 0 ]; then
  echo "!!! MYPY RETURNED ERRORS !!!"
else
  echo "- Second check ok"
fi
echo

echo "### RUNNING BANDIT ###"
bandit -rq falcon_boilerplate/
if [ $? -gt 0 ]; then
  echo "!!! BANDIT RETURNED ERRORS !!!"
else
  echo "- All ok"
fi
