@echo off
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    uv sync
    .venv\Scripts\python.exe main.py
)
