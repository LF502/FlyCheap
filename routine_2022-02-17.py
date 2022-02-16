from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
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
    ignore_cities = {('BJS', 'ZHA'), ('BJS', 'LXA'), ('DLC', 'XIY')} | super(CtripCrawler).skipped_routes
    path = None
    
    parameters = (cities, flightDate, 30, 0, ignore_cities, ignore_threshold)
    crawler = CtripCrawler(*parameters)
    
    sys.stdout = Log(f"{flightDate.isoformat()}_{date.today().isoformat()}.log")
    
    
    for data in crawler.run():
        if not path:
            path = crawler.file.parent
        Preprocessor(list = data, path = path, file_name = crawler.file.name).run()
    
    orig_folder = path / Path(".orig")
    if not orig_folder.exists():
        orig_folder.mkdir()
    preproc_folder = path / Path(".preproc")
    if not preproc_folder.exists():
        preproc_folder.mkdir()
    orig = ZipFile(path / Path("orig.zip"), "a")
    preproc = ZipFile(path / Path("preproc.zip"), "a")
    for file in path.iterdir():
        if file.match('*_preproc.xlsx') or file.match('*_预处理.xlsx'):
            preproc.write(file, file.name)
            file.replace(preproc_folder / Path(file.name))
        elif file.match('*.xlsx'):
            orig.write(file, file.name)
            file.replace(orig_folder / Path(file.name))
    orig.close
    preproc.close