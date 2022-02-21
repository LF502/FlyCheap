from ctripcrawler import CtripCrawler
from preprocessor import Preprocessor
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
import sys

if __name__ == "__main__":

    cities = ["BJS", "TSN", "SHE", "HRB", "CGQ", "SJW", 
              "SHA", "NKG", "HGH", "CZX", "WUX", "HFE", 
              "CAN", "SYX", "HAK", "SZX", "XMN", "CSX", 
              "CTU", "CKG", "KMG", "XIY", "LHW", "INC", 
              "URC", "FOC", "TAO", "DLC", "WUH", "CGO", ]
    flightDate = date(2022, 3, 29)
    ignore_threshold = 3
    ignore_cities = None
    path = None
    
    parameters = (cities, flightDate, 45, 46, ignore_cities, ignore_threshold)
    
    sys.stdout = Log(f"{flightDate.isoformat()}_{date.today().isoformat()}.log")
    crawler = CtripCrawler(*parameters)
    
    parser = ArgumentParser(description = "Input separations - by the number of part and total parts")
    parser.add_argument("--part", type = int, default = 0)
    parser.add_argument("--parts", type = int, default = 0)
    parse_args = parser.parse_args()
    
    for data in crawler.run(part = parse_args.part, parts = parse_args.parts):
        if not path:
            path = crawler.file.parent
        if not Preprocessor(list = data, path = path, file_name = crawler.file.name).run():
            print(f'WARN: {crawler.file.name} preprocess skipped...')
