from ctripcrawler import CtripCrawler
from civilaviation import CivilAviation
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
import sys
import pandas

if __name__ == "__main__":

    cities = ["BJS", "TSN", "SHE", "HRB", "CGQ", "SJW", 
              "SHA", "NKG", "HGH", "CZX", "WUX", "HFE", 
              "CAN", "SYX", "HAK", "SZX", "XMN", "CSX", 
              "CTU", "CKG", "KMG", "XIY", "LHW", "INC", 
              "URC", "FOC", "TAO", "DLC", "WUH", "CGO", ]
    flightDate = date(2022, 3, 29)
    ignore_threshold = 3
    airData = CivilAviation()
    ignore_cities = None
    
    parameters = (cities, flightDate, 45, 46, ignore_cities, ignore_threshold)
    
    sys.stdout = Log(f"{flightDate.isoformat()}_{date.today().isoformat()}.log")
    crawler = CtripCrawler(*parameters)
    
    parser = ArgumentParser(description = "Input separations - by the number of part and total parts")
    parser.add_argument("--part", type = int, default = 0)
    parser.add_argument("--parts", type = int, default = 0)
    parse_args = parser.parse_args()
    
    date_coll = pandas.Timestamp.today().toordinal()
    new = []
    header = (
        'date_flight', 'day_week', 'airline', 'type', 'dep', 
        'arr', 'time_dep', 'time_arr', 'price', 'price_rate')
    
    for data in crawler.run(part = parse_args.part, parts = parse_args.parts):
        try:
            data = pandas.DataFrame(data, columns = header).assign(date_coll = date_coll)
            data['date_flight'] = data['date_flight'].map(lambda x: x.toordinal())
            data['day_adv'] = data['date_flight'] - date_coll
            data['hour_dep'] = data['time_dep'].map(lambda x: x.hour if x.hour else 24)
            if airData.is_multiairport(crawler.file.name[:3]) or \
                airData.is_multiairport(crawler.file.name[4:7]):
                data['route'] = data['dep'].map(lambda x: airData.from_name(x)) + \
                    '-' + data['arr'].map(lambda x: airData.from_name(x))
            else:
                data['route'] = data['dep'] + '-' + data['arr']
            new.append(data)
        except:
            print(f'WARN: {crawler.file.name} merging skipped...')
    pandas.concat(new).to_csv('merging_2022-03-29.csv', mode = 'a', index = False)
