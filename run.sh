#!/bin/bash

# This script is for running project in systemd service.

# Load environment
. /home/PsbYu/.profile
. /home/PsbYu/.pyenv/versions/mybot/bin/activate

# Set proxies
export https_proxy=http://127.0.0.1:7897 
export http_proxy=http://127.0.0.1:7897
export all_proxy=socks5://127.0.0.1:7897

# Mark as daemon mode
export RUNNING_AS_SERVICE=yes

# Run
python3 ./bot.py

