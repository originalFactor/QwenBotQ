#!/bin/bash

pyenv install 3.11.9
pyenv local 3.11.9
python3 -m virtualenv .venv
. .venv/bin/activate
python3 -m pip install pipx --user
python3 -m pipx ensurepath
pipx install nb-cli
python3 -m pip install dashscope
