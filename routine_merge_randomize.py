from zipfile import ZipFile
from pathlib import Path
from datetime import date
from civilaviation import Route, Airport
from ctripcrawler import ItineraryCollector
from pandas import DataFrame

if __name__ == "__main__":
    date_coll = date.today()
    paths, files = [], {}
    header = (
        'date_flight', 'day_week', 'airline', 'type', 'dep', 
        'arr', 'time_dep', 'time_arr', 'price', 'price_rate')
    for path in Path().iterdir():
        if path.is_file():
            if path.suffix == '.csv' and date_coll.isoformat() in path.stem and 'temp' in path.stem:
                key = path.stem.split('_', 4)[1]
                if files.get(key):
                    files[key].append(path)
                else:
                    files[key] = [path]
    
    for key, file in files.items():
        collector = ItineraryCollector(
            targets = [Route.random()], flight_date = date.fromisoformat(key), days = 180)
        merged = Path('merged_' + key + '.csv')
        for data in collector.organize(*file):
            try:
                data = DataFrame(data, columns = header).assign(date_coll = date_coll.toordinal())
                data['date_flight'] = data['date_flight'].map(lambda x: x.toordinal())
                data['day_adv'] = data['date_flight'] - date_coll.toordinal()
                data['hour_dep'] = data['time_dep'].map(lambda x: x.hour if x.hour else 24)
                data['route'] = data['dep'].map(Airport) + data['arr'].map(Airport)
            except:
                print(f'WARN: {collector.file.name} merging skipped...')
                continue
            kwargs = {'mode': 'a', 'header': False} if merged.exists() else {}
            data.to_csv(merged, index = False, **kwargs)
    
    for path in Path().iterdir():
        if path.is_dir():
            path = path / Path(date_coll.isoformat())
            if path.exists():
                paths.append(path)
    
    for path in paths:
        orig_folder = path / Path(".orig")
        if not orig_folder.exists():
            orig_folder.mkdir()
        orig = ZipFile(path / Path("orig.zip"), "a")
        for file in path.iterdir():
            if file.suffix == '.xlsx' and '_preproc' not in file.stem:
                orig.write(file, file.name)
                file.replace(orig_folder / Path(file.name))
        orig.close