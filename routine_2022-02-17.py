from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
from civilaviation import CivilAviation
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
import sys

if __name__ == "__main__":
    
    cities = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]
    flightDate = date(2022, 2, 17)
    ignore_threshold = 0
    ignore_cities = {('BJS', 'ZHA'), ('BJS', 'LXA'), ('DLC', 'XIY')} | CivilAviation().skipped_routes
    path = None
    
    parameters = (cities, flightDate, 30, 0, ignore_cities, ignore_threshold)
    crawler = CtripCrawler(*parameters)
    
    sys.stdout = Log(f"{flightDate.isoformat()}_{date.today().isoformat()}.log")
    
    parser = ArgumentParser(description = "Input separations - by the number of part and total parts")
    parser.add_argument("--part", type = int, default = 0)
    parser.add_argument("--parts", type = int, default = 0)
    parse_args = parser.parse_args()
    
    for data in crawler.run(part = parse_args.part, parts = parse_args.parts):
        if not path:
            path = crawler.file.parent
        if not Preprocessor(list = data, path = path, file_name = crawler.file.name).run():
            print('WARN: Preprocess skipped...')
