from ctripcrawler import CtripCrawler
from civilaviation import skipped_routes, Airport
from datetime import date
from __init__ import Log
from argparse import ArgumentParser
from pathlib import Path
import sys
import pandas

if __name__ == "__main__":
    
    targets = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]
    flight_date = date(2022, 2, 17)
    ignore_threshold = 0
    ignore_cities = {('BJS', 'ZHA'), ('BJS', 'LXA'), ('DLC', 'XIY')} | skipped_routes
    
    parameters = (targets, flight_date, 30, 0, ignore_cities, ignore_threshold)
    crawler = CtripCrawler(*parameters)
    
    sys.stdout = Log(f"{flight_date.isoformat()}_{date.today().isoformat()}.log")
    
    parser = ArgumentParser(description = "Input separations - by the number of part and total parts")
    parser.add_argument("--part", type = int, default = 0)
    parser.add_argument("--parts", type = int, default = 0)
    parse_args = parser.parse_args()
    
    date_coll = pandas.Timestamp.today().date()
    name = f'{flight_date.isoformat()}_{date_coll.isoformat()}_{parse_args.part}_{parse_args.parts}'
    file = Path('merging_' + name + '.csv')
    date_coll = date_coll.toordinal()
    frame = []
    header = (
        'date_flight', 'day_week', 'airline', 'type', 'dep', 
        'arr', 'time_dep', 'time_arr', 'price', 'price_rate')
    
    for data in crawler.run(part = parse_args.part, parts = parse_args.parts):
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
    