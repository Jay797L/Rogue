#!/bin/bash
mypy .
ruff check . --fix 
ruff format .
autoflake --in-place --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --recursive .