from ctripcrawler import CtripCrawler, ItineraryCollector
from civilaviation import Airport, skipped_routes, Route
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
from pathlib import Path
import sys
import pandas

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
    crawler = ItineraryCollector(CtripCrawler, **kwargs)
    
    parser = ArgumentParser()
    parser.add_argument("--part", type = int, default = 1)
    parser.add_argument("--parts", type = int, default = 1)
    parser.add_argument("--attempt", type = int, default = 3)
    parser.add_argument("-reverse", action = 'store_true')
    parser.add_argument("-overwrite", action = 'store_true')
    parser.add_argument("-nopreskip", action = 'store_true')
    parser.add_argument("--antiempty", type = int, default = 0)
    parser.add_argument("--noretry", type = str, action = 'append', default = [])
    kwargs = vars(parser.parse_args())
    
    date_coll = pandas.Timestamp.today().date()
    name = f"{flight_date}_{date_coll}_{kwargs['part']}_{kwargs['parts']}"
    temp = Path(f"temp_{name}.csv")
    file = Path(f"merging_{name}.csv")
    date_coll = date_coll.toordinal()
    frame = []
    header = (
        'date_flight', 'day_week', 'airline', 'type', 'dep', 
        'arr', 'time_dep', 'time_arr', 'price', 'price_rate')
    
    crawler.run(temp, **kwargs)
    for data in crawler.organize(temp):
        try:
            data = pandas.DataFrame(data, columns = header).assign(date_coll = date_coll)
            data['date_flight'] = data['date_flight'].map(lambda x: x.toordinal())
            data['day_adv'] = data['date_flight'] - date_coll
            data['hour_dep'] = data['time_dep'].map(lambda x: x.hour if x.hour else 24)
            data['route'] = data['dep'].map(Airport) + data['arr'].map(Airport)
            if file.exists():
                data.to_csv(file, mode = 'a', index = False, header = False)
            else:
                data.to_csv(file, index = False)
        except:
            print(f'WARN: {crawler.file.name} merging skipped...')