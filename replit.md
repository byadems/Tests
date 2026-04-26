# Enough — SMS Control Panel

## Overview
Web-based control panel for the Enough SMS tool. Replaced the original terminal-based CLI (`enough.py`) with a Flask web dashboard.

## Architecture
- **app.py** — Flask web server (port 5000). Handles routes, SSE log streaming, start/stop control.
- **sms.py** — SMS service class (`SendSms`) with 22 service methods.
- **templates/index.html** — Dark-themed English dashboard UI.
- **enough.py** — Original CLI tool (kept for reference).

## Running
The workflow `Start application` runs `python3 app.py` and serves the dashboard at port 5000.

## Features
- Normal mode: send to one or multiple phone numbers, configurable count and interval
- Turbo mode: multi-threaded maximum-speed sending to a single number
- Real-time live log via Server-Sent Events
- Sent/Failed statistics with polling
- 22 active SMS services displayed

## Dependencies
- flask
- requests
- colorama
