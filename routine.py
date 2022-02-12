from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
from zipfile import ZipFile
from datetime import date
from pathlib import Path

if __name__ == "__main__":
    
    cities = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]
    flightDate = date(2022, 2, 17)
    ignore_threshold = 3
    ignore_cities = {('BJS', 'LXA'), ('DLC', 'XIY')}
    crawler = CtripCrawler(cities, flightDate, 30, 0, ignore_cities, ignore_threshold)
    path = None
    
    for data in crawler.run():
        if not path:
            path = crawler.file.parent
        Preprocessor(list = data, path = path, file_name = crawler.file.name).run()
    
    orig = ZipFile(path / Path(f"orig.zip"), "a")
    preproc = ZipFile(path / Path(f"preproc.zip"), "a")
    for file in path.iterdir():
        if file.match('*_preproc.xlsx') or file.match('*_预处理.xlsx'):
            preproc.write(file, file.name)
        elif file.match('*.xlsx'):
            orig.write(file, file.name)