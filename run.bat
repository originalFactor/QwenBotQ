@echo off
poetry lock
poetry install
poetry run nb run
pause