@echo off

start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
TIMEOUT /T 30

start python routine_2022-03-29.py --part 1 --parts 3
start python routine_2022-03-29.py --part 2 --parts 3
start python routine_2022-03-29.py --part 3 --parts 3

exit