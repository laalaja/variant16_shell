@echo off
python "%~dp0..\src\main.py" ^
  --vfs "%~dp0..\fixtures\vfs_demo.json" ^
  --script "%~dp0startup_all.txt"
