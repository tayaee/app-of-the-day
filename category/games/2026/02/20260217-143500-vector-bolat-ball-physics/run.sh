#!/bin/bash
if [ -f .venv/bin/python ]; then
    .venv/bin/python main.py
else
    uv sync
    .venv/bin/python main.py
fi
