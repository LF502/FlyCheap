from ctripcrawler import CtripCrawler, ItineraryCollector
from civilaviation import skipped_routes
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
from pathlib import Path
import sys
import time

class Log():
    def __init__(self, logfile: str):
        self.terminal = sys.stdout
        self.log = open(logfile, "a", encoding = 'UTF-8',)
 
    def write(self, message):
        self.terminal.write(message)
        if message.startswith("\n") or message.endswith("\n"):
            self.log.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
        self.log.write(message)
    def flush(self):
        pass

if __name__ == "__main__":

    flight_date = date(2022, 3, 29)
    kwargs = {
        'targets': [
            "BJS", "TSN", "SHE", "HRB", "CGO", "SJW", 
            "SHA", "NKG", "HGH", "CZX", "WUX", "HFE", 
            "CAN", "SYX", "HAK", "SZX", "XMN", "CSX", 
            "CTU", "CKG", "KMG", "XIY", "LHW", "INC", 
            "URC", "FOC", "TAO", "DLC", "WUH", "CGQ", ], 
        'flight_date': flight_date, 
        'ignore_threshold': 0, 
        'ignore_routes': skipped_routes, 
        'days': 45, 'day_limit': 45}
    
    sys.stdout = Log(f"{flight_date}_{date.today()}.log")
    crawler = ItineraryCollector(**kwargs)
    
    parser = ArgumentParser()
    parser.add_argument("--part", type = int, default = 1)
    parser.add_argument("--parts", type = int, default = 1)
    parser.add_argument("--attempt", type = int, default = 3)
    parser.add_argument("--noretry", type = str, action = 'append', default = [])
    kwargs = vars(parser.parse_args())
    
    date_coll = date.today()
    temp = Path(f"temp_{flight_date}_{date_coll}.csv")
    crawler.run(temp, **kwargs)
    