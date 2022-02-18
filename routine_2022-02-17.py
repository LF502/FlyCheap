from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
from civilaviation import CivilAviation
from zipfile import ZipFile
from datetime import date
from pathlib import Path
from __init__ import Log
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
    
    
    for data in crawler.run(part = 0, parts = 0):
        if not path:
            path = crawler.file.parent
        if not Preprocessor(list = data, path = path, file_name = crawler.file.name).run():
            print('WARN: Preprocess skipped...')
