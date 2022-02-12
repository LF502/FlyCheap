from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
from zipfile import ZipFile
from datetime import date
from pathlib import Path

if __name__ == "__main__":
    cities = ["BJS", "TSN", "SHE", "HRB", "CGQ", "SJW", 
              "SHA", "NKG", "HGH", "CZX", "WUX", "HFE", 
              "CAN", "SYX", "HAK", "SZX", "XMN", "CSX", 
              "CTU", "CKG", "KMG", "XIY", "LHW", "INC", 
              "URC", "FOC", "TAO", "DLC", "WUH", "CGO", ]
    flightDate = date(2022, 3, 29)
    ignore_threshold = 3
    ignore_cities = None
    crawler = CtripCrawler(cities, flightDate, 3, 45, ignore_cities, ignore_threshold)
    path = None
    
    for data in crawler.run():
        if not path:
            path = crawler.file.parent
        Preprocessor(list = data, path = path, file_name = crawler.file.name).run()
    
    orig = ZipFile(path / Path("orig.zip"), "a")
    preproc = ZipFile(path / Path("preproc.zip"), "a")
    for file in path.iterdir():
        if file.match('*_preproc.xlsx') or file.match('*_预处理.xlsx'):
            preproc.write(file, file.name)
        elif file.match('*.xlsx'):
            orig.write(file, file.name)