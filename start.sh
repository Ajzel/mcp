#!/bin/sh
python weather.py &
uvicorn client:app --host 0.0.0.0 --port ${PORT:-8000}