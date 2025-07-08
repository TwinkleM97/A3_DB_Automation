#!/bin/bash
# Launch headless display and run Selenium test cleanly
Xvfb :99 -screen 0 1920x1080x24 2>/dev/null &  # Suppress xkbcomp warnings
export DISPLAY=:99
python tests/test_login.py
# Check if the test ran successfully