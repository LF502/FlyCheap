import pandas
import openpyxl
from datetime import datetime, date
from zipfile import ZipFile
from pathlib import Path
from civilaviation import CivilAviation

class Rebuilder(CivilAviation):
    '''
    Rebuilder
    -----
    Rebuild all data by filtering factors that influence ticket rate.
    
    Here are 6 significant factors in class property:
    - `airline`: Airlines' rates, competition and flight time;
    - `city`: City class, location and airport throughput;
    - `buyday`: Day of purchase before flights;
    - `flyday`: Date and weekday of flights;
    - `time`: Dep time of flights;
    - `type`: Aircraft Type.
    
    Data
    -----
    `append`: Append a excel file in `Path`.
    
    `zip`: Load excel files from a zip file in the given path.
    
    Parameters
    -----
    root: `Path`, path of collection. 
    
    This should be the same for a class unless their data 
    are continuous or related.
    
    day_limit: `int`, limit of processing days.
            default: `0`, no limits
    
    '''
    def __init__(self, root: Path = Path(), day_limit: int = 0) -> None:
        
        self.__airData = CivilAviation()
        
        self.day_limit = day_limit
        self.__root = root
        self.__title = {
            "airline": {"airlines": [], "dates": [], 
                        "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                  16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
            "city": ("航线", "总价", "平均折扣", "航班总量",
                     "出发地", "机场系数", "地理位置", "城市级别", "旅游", 
                     "到达地", "机场系数", "地理位置", "城市级别", "旅游", ), 
            "buyday": [], 
            "flyday": [], 
            "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                     13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
            "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                     "日均数量", "大型折扣", "日均数量", "平均折扣", 
                     "小型", "中型", "大型")}
        
        self.master = {"airline": {}, "city": {}, "buyday": {}, 
                       "flyday": {}, "time": {}, "type": {},}
        
        self.files: list[Path] = []
        self.__unlink: list[Path] = []
        
        self.__warn = 0
        
    def append_file(self, file: Path) -> Path:
        '''Append data to rebuilder for further processes.
        
        Return `None` for loading failure or none-excel file.'''
        try:
            datetime.fromisoformat(file.parent.name)
        except:
            print("WARN: File not in a standard path name of collecting date!")
            return None
        if file.match("*.xlsx"):
            self.files.append(file)
            return file
        else:
            return None
    
    def append_folder(self, path: Path) -> int:
        '''Load files from a folder, 
        whose name should be data's collecting date.
        
        Return the number of excels loaded.'''
        files = 0
        try:
            datetime.fromisoformat(path.name)
        except:
            print("WARN: File not in a standard path name of collecting date!")
            return files
        for file in path.iterdir():
            if file.match("*.xlsx") and "_" not in file.name:
                self.files.append(file)
                files += 1
        return files
    
    def append_zip(self, path: Path, file: Path | str = "orig.zip") -> int:
        '''
        Append data from a zip file to process.
        
        - path: `Path`, where to extract the zip file.
        
        - file: `Path` | `str`, the zip file path or name.
        
                default: `orig.zip` as a collection's extract.
        
        return the number of excels loaded.
        '''
        try:
            if path.is_dir:
                datetime.fromisoformat(path.name)
            else:
                raise ValueError("Parameter `path` should be a folder!")
        except:
            raise ValueError("Not a standard path name of collecting date!")
        files = 0
        try:
            if isinstance(file, str):
                zip = ZipFile(Path(path / Path(file)), "r")
            elif isinstance(file, Path):
                zip = ZipFile(file, "r")
            else:
                print(f"Warn: {file} is not a Path or str!")
                return file
            zip.extractall(path)
            zip.close
        except:
            print(f"Warn: {file} not found in", path.name)
            self.__warn += 1
        for file in path.iterdir():
            files += 1
            if file.match("*.xlsx"):
                self.files.append(file)
                self.__unlink.append(file)
        return files
    
    def reset(self, unlink_file: bool = True, clear_data: bool = True) -> None:
        '''- Clear all files in the data process queue
        - Unlink excels zip file extracted if unlink_file == `True`
        - Clear all rebuilt data if clear_data == `True`'''
        if unlink_file and len(self.__unlink):
            for file in self.__unlink:
                file.unlink()
        self.files.clear()
        self.__unlink.clear()
        if clear_data:
            self.__title = {
                "airline": {"airlines": [], "dates": [], 
                            "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                    16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
                "city": ("航线", "总价", "平均折扣", "航班总量", 
                         "出发地", "机场系数", "地理位置", "城市级别", "旅游", 
                         "到达地", "机场系数", "地理位置", "城市级别", "旅游", ), 
                "buyday": [], 
                "flyday": [], 
                "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                        13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
                "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                        "日均数量", "大型折扣", "日均数量", "平均折扣", 
                        "小型", "中型", "大型")}
            
            self.master = {"airline": {}, "city": {}, "buyday": {}, 
                           "flyday": {}, "time": {}, "type": {},}
    
    @property
    def airline(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["airline"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rairline data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 2, 4, 5, 6, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = f"{self.__airData.from_name(item[2])}-{self.__airData.from_name(item[3])}"
                date = item[0].date()
                if item[1] not in self.__title["airline"]["airlines"]:
                    self.__title["airline"]["airlines"].append(item[1])
                if date not in self.__title["airline"]["dates"]:
                    self.__title["airline"]["dates"].append(date)
                if datadict.get(name):
                    datadict[name]["counts"] += 1
                    datadict[name]["rates"] += item[5]
                    if datadict[name].get(item[1]):
                        datadict[name][item[1]]["rate"] += item[5]
                        datadict[name][item[1]]["count"] += 1
                        if datadict[name][item[1]].get(item[4].hour):
                            datadict[name][item[1]][item[4].hour]["rate"] += item[5]
                            datadict[name][item[1]][item[4].hour]["count"] += 1
                        else:
                            datadict[name][item[1]][item[4].hour] = {"rate": item[5], "count": 1}
                    else:
                        datadict[name][item[1]] = {"rate": item[5], "count": 1, 
                                               item[4].hour: {"rate": item[5], "count": 1},}
                else:
                    datadict[name] = {item[1]: {"rate": item[5], "count": 1, 
                                            item[4].hour: {"rate": item[5], "count": 1},},
                                  "counts": 1, "rates": item[5],}
        print()
        self.master["airline"] = datadict
        return "airline", self.__excel_format(self.__airline(datadict, self.__title["airline"]), 
                                              B_width = 12)
    
    @staticmethod
    def __airline(datadict: dict, title: dict) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        sheets = ["航线航司 - 每日航班密度", "航线时刻 - 时刻航班密度", 
                  "航线时刻 - 航司竞争", "航线航司 - 机票折扣总览", ]
        for airline in title["airlines"]:
            sheets.append(airline)
        for sheet in sheets:
            wb.create_sheet(sheet)
        del sheets
        
        ws = wb["航线航司 - 每日航班密度"]
        ws.append(["航线", "运营航司数量"] + title["airlines"])
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(1/4) >>", int(idct / total * 100), end = "%")
            row = [name, len(datadict[name]) - 2]
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["count"] / len(title["dates"]))
                else:
                    row.append(None)
            ws.append(row)
        
        wsd = wb["航线时刻 - 时刻航班密度"]
        wsd.append(["航线", "运营航司数量"] + title["hours"])
        wsc = wb["航线时刻 - 航司竞争"]
        wsc.append(["航线", "运营航司数量"] + title["hours"])
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(2/4) >>", int(idct / total * 100), end = "%")
            rowc = [name, len(datadict[name]) - 2]
            rowd = [name, len(datadict[name]) - 2]
            for hour in title["hours"]:
                count = 0
                density = 0
                for airline in title["airlines"]:
                    if datadict[name].get(airline):
                        if datadict[name][airline].get(hour):
                            count += 1
                            density += datadict[name][airline][hour]["count"]
                if count:
                    rowc.append(count)
                    rowd.append(density / len(title["dates"]))
                else:
                    rowc.append(None)
                    rowd.append(None)
            wsc.append(rowc)
            wsd.append(rowd)
        
        ws = wb["航线航司 - 机票折扣总览"]
        ws.append(["航线", "平均折扣"] + title["airlines"])
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(3/4) >>", int(idct / total * 100), end = "%")
            row = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["rate"] / datadict[name][airline]["count"])
                else:
                    row.append(None)
            ws.append(row)
        
        idct = 0
        total *= len(title["airlines"])
        for airline in title["airlines"]:
            ws = wb[airline]
            ws.append(["航线", "平均折扣"] + title["hours"])
            for name in datadict.keys():
                idct += 1
                print("\rairline sheet(4/4) >>", int(idct / total * 100), end = "%")
                if not datadict[name].get(airline):
                    continue
                row = [name, datadict[name][airline]["rate"] / datadict[name][airline]["count"]]
                for hour in title["hours"]:
                    if datadict[name][airline].get(hour):
                        row.append(datadict[name][airline][hour]["rate"] /
                                   datadict[name][airline][hour]["count"])
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def buyday(self) -> tuple[str, openpyxl.Workbook]:
        '''
        Notes
        -----
        - Recommend input files: on one collect date
        
        - Day limits: Not in use
        
        Outputs
        -----
        - Date: date of flight
        
        '''
        datadict = self.master["buyday"]
        min_day = self.day_limit if self.day_limit else date.fromisoformat(self.__root.name).toordinal()
        max_day = 0
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rbuyday data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                name = f"{self.__airData.from_name(item[1])}-{self.__airData.from_name(item[2])}"
                day = item[0].toordinal()
                if min_day > day:
                    min_day = day
                elif max_day < day:
                    max_day = day
                if datadict.get(name):
                    datadict[name]["rates"] += item[3]
                    datadict[name]["counts"] += 1
                    if datadict[name].get(day):
                        datadict[name][day]["rate"] += item[3]
                        datadict[name][day]["count"] += 1
                    else:
                        datadict[name][day] = {"rate": item[3], "count": 1}
                else:
                    datadict[name] = {day: {"rate": item[3], "count": 1}, 
                                  "rates": item[3], "counts": 1}
        if max_day not in self.__title["buyday"] or min_day not in self.__title["buyday"]:
            self.__title["buyday"] = [[], "航线", "平均折扣", ]
            for day in range(min_day, max_day + 1):
                key = date.fromordinal(day)
                self.__title["buyday"].append(key)
                self.__title["buyday"][0].append(key.isoweekday())
        self.master["buyday"] = datadict
        print()
        return "buyday", self.__excel_format(self.__buyday(datadict, self.__title["buyday"]), 
                                             freeze_panes = 'C3')
    
    @staticmethod
    def __buyday(datadict: dict, title: list) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        wsd = wb.create_sheet("航线日密度")
        wsd.append(["航线", "平均密度"] + title[3:])
        wsd.append([None, "(星期)",] + title[0])
        for row in wsd.iter_rows(1, 1, 3, wsd.max_column):
            for cell in row:
                cell.number_format = "m\"月\"d\"日\""
        for sheet in ("高价", "低价", "均价", "总价"):
            ws = wb.create_sheet(sheet)
            ws.append(title[1:])
            ws.append([None, "(星期)",] + title[0])
            for row in ws.iter_rows(1, 1, 3, ws.max_column):
                for cell in row:
                    cell.number_format = "m\"月\"d\"日\""
        row = {}
        sum = idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rbuyday sheets >>", int(idct / total * 100), end = "%")
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, 0, ]
            countd = 0
            for day in title[3:]:
                day = day.toordinal()
                if datadict[name].get(day):
                    if datadict[name][day]["count"]:
                        countd += 1
                        rowd.append(datadict[name][day]["count"])
                        rowd[1] += datadict[name][day]["count"]
                        row[name].append(datadict[name][day]["rate"] / datadict[name][day]["count"])
                    else:
                        rowd.append(None)
                        row[name].append(None)
                else:
                    row[name].append(None)
            ws.append(row[name])
            rowd[1] /= countd
            wsd.append(rowd)
        sum /= len(datadict)
        for value in row.values():
            if value[1] - sum >= 0.05:
                wb["高价"].append(value)
            elif sum - value[1] <= 0.05:
                wb["低价"].append(value)
            else:
                wb["均价"].append(value)
        return wb
    
    @property
    def city(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["city"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rcity data >>", int(idct / total * 100), end = "%")
            filename = file.name.split('~')
            dcity = filename[0]
            acity = filename[1].strip(".xlsx")
            totalfare = self.__airData.get_airfare(dcity, acity)
            
            dcity = self.__airData.from_code(dcity)
            d_tourism = True if dcity in self.__airData.tourism else False
            acity = self.__airData.from_code(acity)
            a_tourism = True if acity in self.__airData.tourism else False
            flag = self.__airData.is_multiairport(dcity) or self.__airData.is_multiairport(acity)
            
            if datadict.get(dcity):
                if not datadict.get(dcity).get(acity):
                    datadict[dcity][acity] = [totalfare, ]
            else:
                datadict[dcity] = {
                    dcity: [self.airports.get(dcity, 0.05), 
                            self.__airData.cityLocation.get(dcity, 0.5), 
                            self.__airData.cityClass.get(dcity, 0.2), d_tourism],
                    acity: [totalfare, ]}
            
            if datadict.get(acity):
                if not datadict.get(acity).get(dcity):
                    datadict[acity][dcity] = [totalfare, ]
            else:
                datadict[acity] = {
                    acity: [self.airports.get(acity, 0.05), 
                            self.__airData.cityLocation.get(acity, 0.5), 
                            self.__airData.cityClass.get(acity, 0.2), a_tourism],
                    dcity: [totalfare, ]}
            
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                dcity = self.__airData.from_name(item[1], flag)
                acity = self.__airData.from_name(item[2], flag)
                datadict[dcity][acity].append(item[3])
            
        self.master["city"] = datadict
        print()
        return "city", self.__excel_format(self.__city(datadict, self.__title["city"]), 
                                           False, wdA = 14, freeze_panes = 'E2')
    
    @staticmethod
    def __city(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("航线与城市总览")
        ws.append(title)
        cities = sorted(datadict.keys())
        idct = 0
        total = len(cities)
        for d_idx in range(total):
            dcity = cities[d_idx]
            idct += 1
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            for a_idx in range(d_idx + 1, total):
                acity = cities[a_idx]
                if not datadict[dcity].get(acity):
                    continue
                avg = 0
                sum = len(datadict[dcity][acity]) - 1
                for rate in datadict[dcity][acity][1:]:
                    avg += rate
                row = [f"{dcity}-{acity}",] + \
                    [datadict[dcity][acity][0], avg / sum, sum, dcity, ] + \
                    datadict[dcity][dcity] + [acity, ] + datadict[acity][acity]
                ws.append(row)
                
                avg = 0
                sum = len(datadict[acity][dcity]) - 1
                for rate in datadict[acity][dcity][1:]:
                    avg += rate
                row = [f"{acity}-{dcity}",] + \
                    [datadict[acity][dcity][0], avg / sum, sum, acity, ] + \
                    datadict[acity][acity] + [dcity, ] + datadict[dcity][dcity]
                ws.append(row)
        return wb
    
    @property
    def flyday(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["flyday"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rflyday data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = f"{self.__airData.from_name(item[1])}-{self.__airData.from_name(item[2])}"
                if days not in self.__title["flyday"]:
                    self.__title["flyday"].append(days)
                fdate = item[0].date().isoformat()
                if datadict.get(name):
                    if datadict[name].get(fdate):
                        if datadict[name][fdate].get(days):
                            datadict[name][fdate][days].append(item[3])
                        else:
                            datadict[name][fdate][days] = [item[3], ]
                    else:
                        datadict[name][fdate] = {days: [item[3], ]}
                else:
                    datadict[name] = {fdate: {days: [item[3], ]}}
        print()
        self.master["flyday"] = datadict
        return "flyday", self.__excel_format(self.__flyday(datadict, self.__title["flyday"]), False)
    
    @staticmethod
    def __flyday(datadict: dict, title: list) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        title.sort()
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            ws = wb.create_sheet(name)
            ws.append(["航班日期", ] + title)
            for fdate in datadict[name].keys():
                row = [fdate, ]
                for day in title:
                    if datadict[name][fdate].get(day):
                        sum = 0
                        for rate in datadict[name][fdate][day]:
                            sum += rate
                        row.append(sum / len(datadict[name][fdate][day]))
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def time(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["time"]
        idct = 0
        total = len(self.files)
        if not datadict.get("date"):
            datadict["date"] = []
        for file in self.files:
            idct += 1
            print("\rtime data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 6, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                if ordinal not in datadict.get("date"):
                    datadict["date"].append(ordinal)
                days = ordinal - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = f"{self.__airData.from_name(item[1])}-{self.__airData.from_name(item[2])}"
                if not datadict.get(name):
                    datadict[name] = {"rates": 0, "counts": 0}
                hour = 24 if item[3].hour == 0 else item[3].hour
                if datadict[name].get(hour):
                    if datadict[name][hour].get(ordinal):
                        datadict[name][hour][ordinal]["rate"] += item[4]
                        datadict[name][hour][ordinal]["count"] += 1
                    else:
                        datadict[name][hour][ordinal] = {"rate": item[4], "count": 1}
                else:
                    datadict[name][hour] = {ordinal: {"rate": item[4], "count": 1}}
                datadict[name]["rates"] += item[4]
                datadict[name]["counts"] += 1
        print()
        self.master["time"] = datadict
        return "time", self.__excel_format(self.__time(datadict, self.__title["time"]))
    
    @staticmethod
    def __time(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        for sheet in ("航班密度", "每日平均", "高价", "均价", "低价", "总表"):
            ws = wb.create_sheet(sheet)
            ws.append(title)
        row = {}
        sum = idct = 0
        total = len(datadict)
        datadict["date"].sort()
        for name in datadict.keys():
            idct += 1
            print("\rtime sheets >>", int(idct / total * 100), end = "%")
            if not isinstance(datadict[name], dict):
                continue
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if not datadict[name].get(hour):
                    row[name].append(None)
                    rowd.append(None)
                    continue
                days = len(datadict[name][hour])
                if days:
                    avg = sum = 0
                    for day in datadict[name][hour].keys():
                        avg += datadict[name][hour][day]["rate"]
                        sum += datadict[name][hour][day]["count"]
                    row[name].append(avg / sum)
                    rowd.append(sum / days)
                else:
                    row[name].append(None)
                    rowd.append(None)
            ws.append(row[name])
            wb["航班密度"].append(rowd)
            
            rowa = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if datadict[name].get(hour):
                    counts = avg = rates = dates = 0
                    for day in datadict["date"]:
                        if datadict[name].get(hour).get(day):
                            dates += 1
                            for _hour in range(5, 25):
                                if datadict[name].get(_hour):
                                    if datadict[name].get(_hour).get(day):
                                        counts += datadict[name][_hour][day]["count"]
                                        rates += datadict[name][_hour][day]["rate"]
                            avg += datadict[name][hour][day]["rate"] / datadict[name][hour][day]["count"] / (rates / counts)
                    rowa.append(avg / dates)
                else:
                    rowa.append(None)
            
            wb["每日平均"].append(rowa)
            
        sum /= len(datadict)
        for value in row.values():
            if value[1] - sum >= 0.05:
                wb["高价"].append(value)
            elif sum - value[1] <= 0.05:
                wb["低价"].append(value)
            else:
                wb["均价"].append(value)
        return wb
    
    @property
    def type(self) -> tuple[str, openpyxl.Workbook]:
        '''
        Notes
        -----
        - Recommend input files: on one collect date
        
        
        '''
        datadict = self.master["type"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rtype data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 3, 4, 5, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = f"{self.__airData.from_name(item[2])}-{self.__airData.from_name(item[3])}"
                if not datadict.get(name):
                    datadict[name] = {"小": {"rate": 0, "count": 0}, 
                                  "中": {"rate": 0, "count": 0}, 
                                  "大": {"rate": 0, "count": 0},
                                  "dates": set(), "rates": 0, "counts": 0}
                if ordinal not in datadict[name]["dates"]:
                    datadict[name]["dates"].add(ordinal)
                datadict[name][item[1]]["rate"] += item[4]
                datadict[name][item[1]]["count"] += 1
                datadict[name]["rates"] += item[4]
                datadict[name]["counts"] += 1
        print()
        self.master["type"] = datadict
        return "type", self.__excel_format(self.__type(datadict, self.__title["type"]), 
                                           False, freeze_panes = 'B2')
    
    @staticmethod
    def __type(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("去除单一机型")
        ws.append(title)
        ws = wb.create_sheet("总表")
        ws.append(title)
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rtype sheets >>", int(idct / total * 100), end = "%")
            row = [name, ]
            for key in ("小", "中", "大"):
                count = datadict[name][key].get("count")
                if count:
                    row.append(datadict[name][key]["rate"] / count)
                    row.append(count / len(datadict[name]["dates"]))
                else:
                    row += [None, 0]
            row.append(datadict[name]["rates"] / datadict[name]["counts"])
            idx = ws.max_row + 1
            tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
            ws.append(row + tail)
            if row[2] > 0 or row[6] > 0:
                idx = wb["去除单一机型"].max_row + 1
                if row[2] > 0 and row[6] > 0:
                    tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
                elif row[6] > 0:
                    tail = [None, f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
                else:
                    tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}"]
                wb["去除单一机型"].append(row + tail)
        return wb
    
    @staticmethod
    def __excel_format(workbook: openpyxl.Workbook, add_average: bool = True, wdA: int = 11, 
                       wdB: int = 0, freeze_panes: str = 'C2') -> openpyxl.Workbook:
        workbook.remove(workbook.active)
        print("\rformatting sheets...          ")
        for sheet in workbook:
            sheet.freeze_panes = freeze_panes
            if sheet.max_row < 2:
                continue
            if wdA:
                sheet.column_dimensions["A"].width = wdA
            if wdB:
                sheet.column_dimensions["B"].width = wdB
            if add_average:
                sheet.append(("平均", ))
                for col in range(2, sheet.max_column + 1):
                    coordinate = sheet.cell(sheet.max_row, col).coordinate
                    top = sheet.cell(2, col).coordinate
                    bottom = sheet.cell(sheet.max_row - 1, col).coordinate
                    sheet[coordinate] = f"=AVERAGE({top}:{bottom})"
        return workbook
    
    def output(self, *args: tuple[str, openpyxl.Workbook],
               clear: bool = False, path: Path | str = Path('.charts')) -> int:
        """
        Output rebuilt data by property or (name: `str`, excel: `Workbook`).
        
        Parameters
        -----
        clear: `bool`, clear outputed rebuilt data after output.
                default: `False`
        
        path: `Path`, where to output.
                default: `Path('.charts')`
        
        """
        files = 0
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            path.mkdir()
        for arg in args:
            key, file = arg
            name = path / Path(f"{self.__root}_{key}.xlsx")
            if name.exists():
                time = datetime.today().strftime("%H%M%S")
                name = path / Path(f"{self.__root}_{key}_{time}.xlsx")
            file.save(name)
            file.close
            files += 1
            if clear:
                del self.master[key]
                self.master[key] = {}
                if isinstance(self.__title.get(key), dict):
                    del self.__title[key]
                    self.__title[key] = {}
        return files
    


if __name__ == "__main__":
    root = Path("2022-02-17")
    rebuild = Rebuilder(root)
    rebuild.append_zip(root / Path("2022-02-08"))
    rebuild.output(rebuild.time)
    rebuild.reset()