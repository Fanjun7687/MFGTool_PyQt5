@echo off
rem ============================================================
rem  MFGTool_PyQt5 launcher
rem
rem  NOTE: The official PyQt5 Windows wheels bundle Qt 5.15.2,
rem  which CRASHES (0xC0000409) when the venv path contains
rem  non-ASCII characters. This project path has Chinese chars,
rem  so the venv must live at an ASCII-only path, selected via
rem  UV_PROJECT_ENVIRONMENT (used by both "uv sync" and "uv run"):
rem      C:\Users\Jason.Fan\.venvs\MFGTool_PyQt5
rem
rem  Usage: double-click this file, or: run.bat [extra args]
rem ============================================================
set "UV_PROJECT_ENVIRONMENT=C:\Users\Jason.Fan\.venvs\MFGTool_PyQt5"
cd /d "%~dp0"
uv run python main_MFGWind.py %*
