import pandas
import pathlib
import openpyxl
import datetime
import zipfile
__sdict = {}
__title = {}
def run(paths: list[str] | tuple[str] = None, day_limit: int = 0) -> None:
    if not paths:
        paths = []
        for item in pathlib.Path().iterdir():
            if item.is_dir():
                paths.append(item)
    for path in paths:
        try:
            colldate = datetime.datetime.fromisoformat(path.name).date().toordinal()
            try:
                zipfile.ZipFile(pathlib.Path(path / pathlib.Path("orig.zip")), "r").extractall(path)
                unlink = True
            except:
                unlink = False
            finally:
                print(f"\n{path.name}:")
        except:
            continue
        for file in path.iterdir():
            if not file.match("*.xlsx") or "preproc" in file.name:
                continue
            name = file.name.split('~')
            print('\r' + file.name, end = ' processing...')
            data = pandas.read_excel(file.joinpath()).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - colldate
                if day_limit and days > day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
                if __title.get(name):
                    if days not in __title[name]:
                        __title[name].append(days)
                else:
                    __title[name] = [days, ]
                fdate = item[0].date().isoformat()
                if __sdict.get(name):
                    if __sdict[name].get(fdate):
                        if __sdict[name][fdate].get(days):
                            __sdict[name][fdate][days].append(item[3])
                        else:
                            __sdict[name][fdate][days] = [item[3], ]
                    else:
                        __sdict[name][fdate] = {days: [item[3], ]}
                else:
                    __sdict[name] = {fdate: {days: [item[3], ]}}
            if unlink:
                file.unlink()
def merge() -> None:
    print('\nMerging...')
    wb = openpyxl.Workbook()
    for name in __sdict.keys():
        print('\r' + name, end = ' data appending...')
        ws = wb.create_sheet(name)
        ws.column_dimensions['A'].width = 11
        __title[name].sort()
        ws.append(["航班日期", ] + __title[name])
        for fdate in __sdict[name].keys():
            row = [fdate, ]
            for day in __title[name]:
                if __sdict[name][fdate].get(day):
                    total = 0
                    for rate in __sdict[name][fdate][day]:
                        total += rate
                    row.append(total / len(__sdict[name][fdate][day]))
                else:
                    row.append(None)
            ws.append(row)
    wb.remove(wb.active)
    wb.save(f"route-day-rate.xlsx")
    wb.close
    print('Done!')

if __name__ == "__main__":
    folders = ("2022-01-24", "2022-01-25", "2022-01-26", "2022-01-27", "2022-01-28", "2022-01-29", 
               "2022-01-30", "2022-01-31", "2022-02-01", "2022-02-02", "2022-02-08", "2022-02-09", )
    run(day_limit = 45)
    merge()