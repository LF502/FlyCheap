import pandas
import openpyxl
from datetime import datetime
from zipfile import ZipFile
from pathlib import Path

class Rebuilder():
    '''
    Rebuilder
    -----
    Rebuild all data by filtering factors that influence ticket rate.
    
    Here are 7 significant factors in class property:
    - `airline`: Airlines' rates, competition and flight time
    - `city`: City class, location and airport throughput
    - `buyday`: Date of purchase 
    - `flyday`: Date of flight 
    - `time`: Dep time of flight 
    - `type`: Aircraft Type 
    - `week`: Day of week 
    
    Data
    -----
    `append`: Append a excel file in `Path`.
    
    Methods using original data: 
    - `airline`, `flyday`, `time`, `type`, `week`
    
    Methods using preprocessed data: 
    - `buyday`, `city`
    
    Parameters
    -----
    root: `Path`, path of collection. 
    
    This should be the same for a class unless their data 
    are continuous or related.
    
    day_limit: `int`, limit of processing days.
            default: `0`, no limits
    
    '''
    def __init__(self, root: Path = Path(), day_limit: int = 0) -> None:
        self.day_limit = day_limit
        self.__root = root
        self.__airportCity = {
            'BJS':'北京','CAN':'广州','SHA':'上海','CTU':'成都',
            'SZX':'深圳','KMG':'昆明','XIY':'西安','CKG':'重庆',
            'HGH':'杭州','NKG':'南京','CGO':'郑州','XMN':'厦门',
            'WUH':'武汉','CSX':'长沙','TAO':'青岛','HAK':'海口',
            'URC':'乌鲁木齐','TSN':'天津','KWE':'贵阳','SHE':'沈阳',
            'HRB':'哈尔滨','SYX':'三亚','DLC':'大连','TNA':'济南',
            'NNG':'南宁','LHW':'兰州','FOC':'福州','TYN':'太原',
            'CGQ':'长春','KHN':'南昌','HET':'呼和浩特','NGB':'宁波',
            'WNZ':'温州','ZUH':'珠海','HFE':'合肥','SJW':'石家庄',
            'INC':'银川','YTY':'扬州','KHG':'喀什','LYG':'连云港',
            'YNT':'烟台','KWL':'桂林','JJN':'泉州','WUX':'无锡',
            'SWA':'揭阳','XNN':'西宁','LJG':'丽江','JHG':'西双版纳',
            'LXA':'拉萨','MIG':'绵阳','CZX':'常州','NTG':'南通',
            'YIH':'宜昌','WEH':'威海','XUZ':'徐州','DYG':'张家界',
            'ZHA':'湛江','DSN':'鄂尔多斯','BHY':'北海','LYI':'临沂',
            'HLD':'呼伦贝尔','HUZ':'惠州','UYN':'榆林','YCU':'运城',
            'HIA':'淮安','BAV':'包头','ZYI':'遵义','KRL':'库尔勒',
            'LUM':'德宏','YNZ':'盐城','KOW':'赣州','YIW':'义乌',
            'XFN':'襄阳','CIF':'赤峰','LZO':'泸州','DLU':'大理',
            'AKU':'阿克苏','YNJ':'延吉','ZYI':'遵义','HTN':'和田',
            'LYA':'洛阳','WDS':'十堰','HSN':'舟山','JNG':'济宁',
            'YIN':'伊宁','ENH':'恩施','ACX':'兴义','HYN':'台州',
            'DAT':'大同','BSD':'保山','BFJ':'毕节','NNY':'南阳',
            'WXN':'万州','TGO':'通辽','CGD':'常德','HNY':'衡阳',
            'MDG':'牡丹江','RIZ':'日照','NAO':'南充','YBP':'宜宾',
            'LZH':'柳州','XIC':'西昌','TCZ':'腾冲',}
        self.__title = {
            "airline": {"airlines": [], "dates": [], 
                        "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                  16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
            "city": {}, 
            "buyday": [], 
            "flyday": {}, 
            "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                     13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
            "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                     "日均数量", "大型折扣", "日均数量", "平均折扣", 
                     "小型", "中型", "大型"), 
            "week": {}}
        
        self.master = {"airline": {}, "city": {}, "buyday": {}, 
                       "flyday": {}, "time": {}, "type": {}, "week": {}}
        
        self.orig: list[Path] = []
        self.preproc: list[Path] = []
        self.__paths: list[Path] = []
        
        self.__warn = 0
    
    def append(self, file: Path) -> Path:
        '''Append data to rebuilder for further processes'''
        try:
            datetime.fromisoformat(file.parent.name)
        except:
            raise ValueError("File not in a standard path name of collecting date!")
        if file.match("*_preproc.xlsx") or file.match("*_预处理.xlsx"):
            self.preproc.append(file)
        elif file.match("*.xlsx"):
            self.orig.append(file)
        else:
            raise ValueError("Not an excel file!")
        return file
    
    def zip(self, path: Path) -> None:
        '''
        Append data from zip file(s) to processes
        
        return `True, True` if both orig.zip and preproc.zip are loaded.
        '''
        try:
            datetime.fromisoformat(path.name)
        except:
            raise ValueError("Not a standard path name of collecting date!")
        try:
            zip = ZipFile(Path(path / Path("orig.zip")), "r")
            zip.extractall(path)
            zip.close
        except:
            print("Warn: orig.zip not found in", path.name)
            self.__warn += 1
        try:
            zip = ZipFile(Path(path / Path("preproc.zip")), "r")
            zip.extractall(path)
            zip.close
        except:
            print("Warn: preproc.zip not found in", path.name)
            self.__warn += 1
            
        for file in path.iterdir():
            if file.match("*_preproc.xlsx") or file.match("*_预处理.xlsx"):
                self.preproc.append(file)
            elif file.match("*.xlsx"):
                self.orig.append(file)
        if path not in self.__paths:
            self.__paths.append(path)
    
    def reset(self, unlink: bool = True) -> None:
        '''- Clear all data in the process list
        - Unlink excels zip file extracted if unlink == `True`'''
        if unlink:
            for path in self.__paths:
                for file in path.iterdir():
                    if file in self.orig or file in self.preproc:
                        file.unlink()
        self.orig.clear()
        self.preproc.clear()
    
    @property
    def airline(self) -> tuple[str, openpyxl.Workbook]:
        dict = self.master["airline"]
        idct = 0
        total = len(self.orig)
        for file in self.orig:
            idct += 1
            print("\rairline data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 2, 4, 5, 6, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[2][:2] + "-" + item[3][:2]
                date = item[0].date()
                if item[1] not in self.__title["airline"]["airlines"]:
                    self.__title["airline"]["airlines"].append(item[1])
                if date not in self.__title["airline"]["dates"]:
                    self.__title["airline"]["dates"].append(date)
                if dict.get(name):
                    dict[name]["counts"] += 1
                    dict[name]["rates"] += item[5]
                    if dict[name].get(item[1]):
                        dict[name][item[1]]["rate"] += item[5]
                        dict[name][item[1]]["count"] += 1
                        if dict[name][item[1]].get(item[4].hour):
                            dict[name][item[1]][item[4].hour]["rate"] += item[5]
                            dict[name][item[1]][item[4].hour]["count"] += 1
                        else:
                            dict[name][item[1]][item[4].hour] = {"rate": item[5], "count": 1}
                    else:
                        dict[name][item[1]] = {"rate": item[5], "count": 1, 
                                               item[4].hour: {"rate": item[5], "count": 1},}
                else:
                    dict[name] = {item[1]: {"rate": item[5], "count": 1, 
                                            item[4].hour: {"rate": item[5], "count": 1},},
                                  "counts": 1, "rates": item[5],}
        print()
        self.master["airline"] = dict
        return "airline", self.__excel_format(self.__airline(dict, self.__title["airline"]), 
                                              B_width = 12)
    
    @staticmethod
    def __airline(dict: dict, title: dict) -> openpyxl.Workbook:
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
        total = len(dict)
        for name in dict.keys():
            idct += 1
            print("\rairline sheet(1/4) >>", int(idct / total * 100), end = "%")
            row = [name, len(dict[name]) - 2]
            for airline in title["airlines"]:
                if dict[name].get(airline):
                    row.append(dict[name][airline]["count"] / len(title["dates"]))
                else:
                    row.append(None)
            ws.append(row)
        
        wsd = wb["航线时刻 - 时刻航班密度"]
        wsd.append(["航线", "运营航司数量"] + title["hours"])
        wsc = wb["航线时刻 - 航司竞争"]
        wsc.append(["航线", "运营航司数量"] + title["hours"])
        idct = 0
        for name in dict.keys():
            idct += 1
            print("\rairline sheet(2/4) >>", int(idct / total * 100), end = "%")
            rowc = [name, len(dict[name]) - 2]
            rowd = [name, len(dict[name]) - 2]
            for hour in title["hours"]:
                count = 0
                density = 0
                for airline in title["airlines"]:
                    if dict[name].get(airline):
                        if dict[name][airline].get(hour):
                            count += 1
                            density += dict[name][airline][hour]["count"]
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
        for name in dict.keys():
            idct += 1
            print("\rairline sheet(3/4) >>", int(idct / total * 100), end = "%")
            row = [name, dict[name]["rates"] / dict[name]["counts"]]
            for airline in title["airlines"]:
                if dict[name].get(airline):
                    row.append(dict[name][airline]["rate"] / dict[name][airline]["count"])
                else:
                    row.append(None)
            ws.append(row)
        
        idct = 0
        total *= len(title["airlines"])
        for airline in title["airlines"]:
            ws = wb[airline]
            ws.append(["航线", "平均折扣"] + title["hours"])
            for name in dict.keys():
                idct += 1
                print("\rairline sheet(4/4) >>", int(idct / total * 100), end = "%")
                if not dict[name].get(airline):
                    continue
                row = [name, dict[name][airline]["rate"] / dict[name][airline]["count"]]
                for hour in title["hours"]:
                    if dict[name][airline].get(hour):
                        row.append(dict[name][airline][hour]["rate"] /
                                   dict[name][airline][hour]["count"])
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def buyday(self) -> tuple[str, openpyxl.Workbook]:
        dict = self.master["buyday"]
        min_day = self.day_limit if self.day_limit else 90
        max_day = 0
        idct = 0
        total = len(self.preproc)
        for file in self.preproc:
            idct += 1
            print("\rbuyday data >>", int(idct / total * 100), end = "%")
            cols = [0, 2, 10, 11, 12, 13, 18]
            data = pandas.read_excel(file, index_col = 0).iloc[ : , cols]
            data.sort_index(inplace = True)
            name = file.name.split('~')
            dcity = self.__airportCity.get(name[0])
            acity = self.__airportCity.get(name[1].split('_', 1)[0])
            to_name = dcity + ' - ' + acity
            return_name = acity + ' - ' + dcity
            city = data.loc[0]
            city = (city[2], city[3], city[4], city[5])
            for item in data.values:
                rcity = (item[2], item[3], item[4], item[5])
                name = to_name if city == rcity else return_name
                if self.day_limit and item[0] > self.day_limit:
                    max_day = self.day_limit
                    continue
                if min_day > item[0]:
                    min_day = item[0]
                elif max_day < item[0]:
                    max_day = item[0]
                if dict.get(name):
                    dict[name]["rates"] += item[6]
                    dict[name]["counts"] += 1
                    if dict[name].get(item[0]):
                        dict[name][item[0]]["rate"] += item[6]
                    else:
                        dict[name][item[0]] = {"rate": item[6], "count": int(item[1] / 2)}
                else:
                    dict[name] = {item[0]: {"rate": item[6], "count": int(item[1] / 2)}, 
                                  "rates": item[6], "counts": 1}
        if max_day not in self.__title["buyday"] or min_day not in self.__title["buyday"]:
            self.__title["buyday"] = ["航线", "平均折扣"]
            for day in range(min_day, max_day + 1):
                self.__title["buyday"].append(day)
        self.master["buyday"] = dict
        print()
        return "buyday", self.__excel_format(self.__buyday(dict, self.__title["buyday"]), 
                                             True, 16)
    
    @staticmethod
    def __buyday(dict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("高价")
        ws.append(title)
        ws = wb.create_sheet("均价")
        ws.append(title)
        ws = wb.create_sheet("低价")
        ws.append(title)
        ws = wb.create_sheet("总表")
        ws.append(title)
        row = {}
        sum = idct = 0
        total = len(dict)
        for name in dict.keys():
            idct += 1
            print("\rbuyday sheets >>", int(idct / total * 100), end = "%")
            sum += dict[name]["rates"] / dict[name]["counts"]
            row[name] = [name, dict[name]["rates"] / dict[name]["counts"]]
            for day in title:
                if isinstance(day, str):
                    continue
                if dict[name].get(day):
                    if dict[name][day]["count"]:
                        row[name].append(dict[name][day]["rate"] / dict[name][day]["count"])
                    else:
                        row[name].append(None)
                else:
                    row[name].append(None)
            ws.append(row[name])
        sum /= len(dict)
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
        dict = self.master["city"]
        for file in self.preproc:
            cols = [0, 2, 10, 11, 12, 13, 18]
            data = pandas.read_excel(file, index_col = 0).iloc[ : , cols]
            data.sort_index(inplace = True)
            name = file.name.split('~')
            dcity = self.__airportCity.get(name[0])
            acity = self.__airportCity.get(name[1].split('_', 1)[0])
            to_name = dcity + ' - ' + acity
            return_name = acity + ' - ' + dcity
            city = data.loc[0]
            city = (city[2], city[3], city[4], city[5])
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
        
        self.master["city"] = dict
        print()
        return "city"
    
    @property
    def flyday(self) -> tuple[str, openpyxl.Workbook]:
        dict = self.master["flyday"]
        idct = 0
        total = len(self.orig)
        for file in self.orig:
            idct += 1
            print("\rflyday data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
                if self.__title["flyday"].get(name):
                    if days not in self.__title["flyday"][name]:
                        self.__title["flyday"][name].append(days)
                else:
                    self.__title["flyday"][name] = [days, ]
                fdate = item[0].date().isoformat()
                if dict.get(name):
                    if dict[name].get(fdate):
                        if dict[name][fdate].get(days):
                            dict[name][fdate][days].append(item[3])
                        else:
                            dict[name][fdate][days] = [item[3], ]
                    else:
                        dict[name][fdate] = {days: [item[3], ]}
                else:
                    dict[name] = {fdate: {days: [item[3], ]}}
        print()
        self.master["flyday"] = dict
        return "flyday", self.__excel_format(self.__flyday(dict, self.__title["flyday"]), False)
    
    @staticmethod
    def __flyday(dict: dict, title: dict) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        idct = 0
        total = len(dict)
        for name in dict.keys():
            idct += 1
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            ws = wb.create_sheet(name)
            title[name].sort()
            ws.append(["航班日期", ] + title[name])
            for fdate in dict[name].keys():
                row = [fdate, ]
                for day in title[name]:
                    if dict[name][fdate].get(day):
                        sum = 0
                        for rate in dict[name][fdate][day]:
                            sum += rate
                        row.append(sum / len(dict[name][fdate][day]))
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def time(self) -> tuple[str, openpyxl.Workbook]:
        dict = self.master["time"]
        idct = 0
        total = len(self.orig)
        for file in self.orig:
            idct += 1
            print("\rtime data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 6, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
                if not dict.get(name):
                    dict[name] = {"rates": 0, "counts": 0}
                    for hour in range(5, 25):
                        dict[name][hour] = {"rate": 0, "count": 0}
                if dict[name].get(item[3].hour):
                    dict[name][item[3].hour]["rate"] += item[4]
                    dict[name][item[3].hour]["count"] += 1
                elif item[3].hour == 0:
                    dict[name][24]["rate"] += item[4]
                    dict[name][24]["count"] += 1
                else:
                    continue
                dict[name]["rates"] += item[4]
                dict[name]["counts"] += 1
        print()
        self.master["time"] = dict
        return "time", self.__excel_format(self.__time(dict, self.__title["time"]))
    
    @staticmethod
    def __time(dict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("高价")
        ws.append(title)
        ws = wb.create_sheet("均价")
        ws.append(title)
        ws = wb.create_sheet("低价")
        ws.append(title)
        ws = wb.create_sheet("总表")
        ws.append(title)
        row = {}
        sum = idct = 0
        total = len(dict)
        for name in dict.keys():
            idct += 1
            print("\rtime sheets >>", int(idct / total * 100), end = "%")
            sum += dict[name]["rates"] / dict[name]["counts"]
            row[name] = [name, dict[name]["rates"] / dict[name]["counts"]]
            for hour in range(5, 25):
                if dict[name][hour]["count"]:
                    row[name].append(dict[name][hour]["rate"] / dict[name][hour]["count"])
                else:
                    row[name].append(None)
            ws.append(row[name])
        sum /= len(dict)
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
        dict = self.master["type"]
        idct = 0
        total = len(self.orig)
        for file in self.orig:
            idct += 1
            print("\rtype data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 3, 4, 5, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[2][:2] + "-" + item[3][:2]
                if not dict.get(name):
                    dict[name] = {"小": {"rate": 0, "count": 0}, 
                                  "中": {"rate": 0, "count": 0}, 
                                  "大": {"rate": 0, "count": 0},
                                  "dates": set(), "rates": 0, "counts": 0}
                if ordinal not in dict[name]["dates"]:
                    dict[name]["dates"].add(ordinal)
                dict[name][item[1]]["rate"] += item[4]
                dict[name][item[1]]["count"] += 1
                dict[name]["rates"] += item[4]
                dict[name]["counts"] += 1
        print()
        self.master["type"] = dict
        return "type", self.__excel_format(self.__type(dict, self.__title["type"]), False)
    
    @staticmethod
    def __type(dict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("去除单一机型")
        ws.append(title)
        ws = wb.create_sheet("总表")
        ws.append(title)
        idct = 0
        total = len(dict)
        for name in dict.keys():
            idct += 1
            print("\rtype sheets >>", int(idct / total * 100), end = "%")
            row = [name, ]
            for key in ("小", "中", "大"):
                count = dict[name][key].get("count")
                if count:
                    row.append(dict[name][key]["rate"] / count)
                    row.append(count / len(dict[name]["dates"]))
                else:
                    row += [None, 0]
            row.append(dict[name]["rates"] / dict[name]["counts"])
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
    
    @property
    def week(self) -> tuple[str, openpyxl.Workbook]:
        dict = self.master["week"]
        for file in self.orig:
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
        
        self.master["week"] = dict
        print()
        return "week"
    
    @staticmethod
    def __excel_format(workbook: openpyxl.Workbook, add_average: bool = True,
                       A_width: int = 11, B_width: int = 0) -> openpyxl.Workbook:
        workbook.remove(workbook.active)
        print("\rformatting sheets...          ")
        for sheet in workbook:
            if sheet.max_row < 2:
                continue
            sheet.freeze_panes = 'B2'
            if A_width:
                sheet.column_dimensions["A"].width = A_width
            if B_width:
                sheet.column_dimensions["B"].width = B_width
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
        clear: `bool`, clear rebuilt data after output.
                default: `False`
        
        path: `Path`, where to output
                default: `Path('.charts')`
        
        """
        files = 0
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            path.mkdir()
        for arg in args:
            key, file = arg
            file.save(path / Path(f"{self.__root}_{key}.xlsx"))
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
    rebuild.zip(root / Path("2022-02-09"))
    rebuild.output(rebuild.buyday, path = "debugging")
    rebuild.reset()