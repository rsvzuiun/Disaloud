@echo off
setlocal
set CurrentDirectory="%~dp0"

if exist .venv\Scripts\activate call .venv\Scripts\activate
python -m disaloud
