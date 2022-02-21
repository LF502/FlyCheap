@echo off

start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
TIMEOUT /T 30

start python routine_2022-02-17.py --part 4 --parts 6
start python routine_2022-02-17.py --part 5 --parts 6
start python routine_2022-02-17.py --part 6 --parts 6

exit