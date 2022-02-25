from sqlite3 import Timestamp
from numpy import average as mean
import pandas
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.formatting.rule import CellIsRule
from datetime import datetime, date
from zipfile import ZipFile
from pathlib import Path
from civilaviation import CivilAviation

class Rebuilder():
    '''
    Rebuilder
    -----
    Rebuild all data by filtering factors that influence ticket rate.
    
    Here are 6 significant factors can be rebuilt in class methods:
    - `airline`: Airlines' rates, competition and flight time;
    - `city`: City and route information overview;
    - `buyday`: The number of days before flights are fixed;
    - `flyday`: Dates and weekdays of flight are fixed;
    - `time`: Dep time of flights;
    - `type`: Aircraft type.
    
    Merger
    -----
    Merge all rebuilt data to `pandas.DataFrame`
    
    Data
    -----
    `append_file`: Append a excel file in `Path`.
    
    `append_folder`: Append excel files from folders in `Path`.
    
    `append_zip`: Load excel files from zip files in `Path`.
    
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
        self.__merged = []
        self.__merging = []
        
        self.__header = {
            'date_flight': '航班日期', 'day_week': '星期', 
            'date_coll': '收集日期', 'day_adv': '提前天数', 
            'airline': '航司', 'airlines': '运营航司', 'type': '机型', 
            
            'dep': '出发机场', 'arr': '到达机场', 'route': '航线', 
            'time_dep': '出发时刻', 'time_arr': '到达时刻', 'hour_dep': '出发时段', 
            'density_day': '日航班数', 'density_hour': '时段密度', 
            'comp_hour': '时段竞争', 'comp_day': '日竞争', 
            
            
            'count': '总计', 'route_count': '航线计数', 'type_count': '机型计数', 
            'date_flight_count': '日期计数', 'date_coll_count': '收集计数', 
            
            'price_total': '全价', 'price': '价格', 'price_rate': '折扣', 
            
            'ratio_daily': '当日系数', 
            'mid_price_rate': '折扣中位', 'avg_price_rate': '折扣平均', 
            'mid_ratio_price': '系数中位', 'avg_ratio_price': '系数平均', 
        }
        
        self.__day_limit = day_limit
        self.__root = root
        self.__title = {
            "airline": {"airlines": [], "dates": set(), 
                        "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                  16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
            "city": ("航线", "总价", "平均折扣", "航班总量",
                     "出发地", "机场系数", "地理位置", "城市级别", "内陆旅游", 
                     "到达地", "机场系数", "地理位置", "城市级别", "内陆旅游", ), 
            "flyday": [], 
            "buyday": [], 
            "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                     13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
            "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                     "日均数量", "大型折扣", "日均数量", "平均折扣", 
                     "小型", "中型", "大型")}
        
        self.master = {"airline": {}, "city": {}, "flyday": {}, 
                       "buyday": {}, "time": {}, "type": {},}
        
        self.__files: list[Path] = []
        self.__unlink: list[Path] = []
        
        self.__warn = 0
    
    
    def root(self, __root: Path | str = None, /) -> Path:
        '''Change root path if root path is given.
        
        Return seted root path in `Path`.'''
        if Path(__root).exists() and __root:
            self.__root = Path(__root)
        return self.__root
    
    
    def append_file(self, file: Path) -> Path:
        '''Append data to rebuilder for further processes.
        
        Return `None` for loading failure or none-excel file.'''
        try:
            datetime.fromisoformat(file.parent.name)
        except:
            print(f"WARN: {file.name} is not a standard path name of collecting date!")
            return None
        if file.match("*.xlsx"):
            self.__files.append(file)
            return file
        else:
            return None
    
    def append_folder(self, *paths: Path | str, count: int = 0) -> int:
        '''Load files from a folder, 
        whose name should be data's collecting date.
        
        Return the number of excels loaded.'''
        files = 0
        if len(paths) == 0:
            paths = []
            for path in self.__root.iterdir():
                if path.is_dir():
                    paths.append(path)
        for path in paths:
            path = Path(path)
            if self.__root != path.parent:
                path = self.__root / path
            try:
                if path.is_dir():
                    datetime.fromisoformat(path.name)
                else:
                    print(f"WARN: {path.name} should be an existing folder!")
                    self.__warn += 1
                    continue
            except:
                print(f"WARN: {path.name} is not a standard path name of collecting date!")
                self.__warn += 1
                continue
            
            for file in path.iterdir():
                if file.match("*.xlsx") and "_" not in file.name:
                    self.__files.append(file)
                    files += 1
                if count and files >= count:
                    break
        return files
    
    def append_zip(self, *paths: Path | str, file_name: str = "orig.zip") -> int:
        '''
        Append data from a zip file to process.
        
        - paths: `Path`, where to find and extract the zip file in `root`.
        
                default: all folders in the `root`
        
        - file: `Path` | `str`, the zip file path or name.
        
                default: `orig.zip` as a collection's extract.
        
        Return the number of excels loaded.
        '''
        files = 0
        if len(paths) == 0:
            paths = []
            for path in self.__root.iterdir():
                if path.is_dir():
                    paths.append(path)
        for path in paths:
            path = Path(path)
            if self.__root != path.parent:
                path = self.__root / path
            try:
                if path.is_dir():
                    datetime.fromisoformat(path.name)
                else:
                    print(f"WARN: {path.name} should be an existing folder!")
                    self.__warn += 1
                    continue
            except:
                print(f"WARN: {path.name} is not a standard path name of collecting date!")
                self.__warn += 1
                continue
            
            try:
                zip = ZipFile(path / Path(file_name), "r")
                zip.extractall(path)
                zip.close
            except:
                print(f"WARN: {file_name} cannot be loaded in", path.name)
                self.__warn += 1
                continue
            for item in path.iterdir():
                if item.match("*.xlsx") and "_" not in item.name:
                    files += 1
                    self.__files.append(item)
                    self.__unlink.append(item)
        return files
    
    def reset(self, unlink_file: bool = True, clear_rebuilt: bool = False) -> int:
        '''
        Clear all files in the data process queue
        -----
        - unlink_file: `True`, unlink excels zip file extracted
        - clear_rebuilt: `True`, clear all rebuilt data
        - Return current count of total warnings and reset to 0
        '''
        if unlink_file and len(self.__unlink):
            for file in self.__unlink:
                file.unlink()
        self.__files.clear()
        self.__unlink.clear()
        if clear_rebuilt:
            self.__title.clear()
            self.__title = {
                "airline": {"airlines": [], "dates": set(), 
                            "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                    16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
                "city": ("航线", "总价", "平均折扣", "航班总量", 
                         "出发地", "机场系数", "地理位置", "城市级别", "内陆旅游", 
                         "到达地", "机场系数", "地理位置", "城市级别", "内陆旅游", ), 
                "flyday": [], 
                "buyday": [], 
                "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                        13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
                "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                        "日均数量", "大型折扣", "日均数量", "平均折扣", 
                        "小型", "中型", "大型")}
            
            self.master.clear()
            self.master = {"airline": {}, "city": {}, "flyday": {}, 
                           "buyday": {}, "time": {}, "type": {},}
            self.__merged = []
        warn = self.__warn
        self.__warn = 0
        return warn
    
    
    def merging(self) -> pandas.DataFrame:
        total = len(self.__files)
        if total == 0:
            return None
        frame = []
        header = (
            'date_flight', 'day_week', 'airline', 'type', 'dep',                            #04
            'arr', 'time_dep', 'time_arr', 'price', 'price_rate')                           #09
        idct, percent = 0, -1
        for file in self.__files:
            idct += 1
            if percent != int(idct / total * 50):
                percent = int(idct / total * 50)
                print(f"\rmerging >> {percent:03d}", end = '%')
            date_coll = pandas.Timestamp.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file, names = header).assign(date_coll = date_coll)    #10
            
            data['date_flight'] = data['date_flight'].map(lambda x: x.toordinal())
            data['day_adv'] = data['date_flight'] - date_coll                               #11
            data['hour_dep'] = data['time_dep'].map(lambda x: x.hour if x.hour else 24)     #12
            
            if self.__airData.is_multiairport(file.name[:3]) or \
                self.__airData.is_multiairport(file.name[4:7]):
                data['route'] = data['dep'].map(lambda x: self.__airData.from_name(x)) + \
                    '-' + data['arr'].map(lambda x: self.__airData.from_name(x))
            else:
                data['route'] = data['dep'] + '-' + data['arr']                             #13
            if self.__day_limit:
                data.drop(data[data['day_adv'] > self.__day_limit].index, inplace = True)
            frame.append(data)
        return pandas.concat(frame)
    
    
    def read_data(self, path: Path | str) -> tuple[str, int, int] | None:
        '''Read pandas file
        
        Return `tuple` with file type of merged or merging and size
        
        Return `None` for data in incorrect shape'''
        print('reading data >> ', end = '...')
        data = pandas.read_csv(Path(path))
        if self.__day_limit:
            data.drop(data[data['day_adv'] > self.__day_limit].index, inplace = True)
        row, col = data.shape
        if col == 14:
            self.__merging = data
            return "merging", row, col
        elif col == 17:
            self.__merged = data
            return "merged", row, col
        else:
            return None
    
    
    def merge_all(self) -> tuple[str, pandas.DataFrame]:
        if not len(self.__merging):
            self.__merging = self.merging()
        data = self.__merging
        
        '''hour ratio'''
        '''day density'''
        '''airline day competition'''
        '''hour density'''
        '''airline hour competition'''
        hour_density = []
        ratio_daily = []
        day_density = []
        groups = data.groupby(["date_coll", "date_flight", "route"])
        percent = 50
        total, idct = len(data.values), 0
        
        for value in data.values:
            idct += 1
            if percent != int(idct / total * 50 + 50):
                percent = int(idct / total * 50 + 50)
                print(f"\rmerging overview >> {percent:03d}", end = '%')
            
            group = groups.get_group((value[10], value[0], value[13]))
            ratio_daily.append(value[9] / group['price_rate'].mean())
            day_density.append(len(group))
            hour_density.append(len(group['hour_dep'].unique()))
        
        data.loc[: , 'ratio_daily'] = ratio_daily
        data.loc[: , 'density_day'] = day_density
        data.loc[: , 'density_hour'] = hour_density
        
        self.__merged = data
        print()
        return "全部", data
    
    def merge_date(self, path: Path | str = '.charts', file: str = '') -> None:
        '''Date overview
        
        Output excel with conditional formats'''
        if not len(self.__merging):
            self.__merging = self.merging()
        data = self.__merging.sort_values('date_flight')
        total_dates = []
        for item in data['date_flight'].unique():
            total_dates.append(Timestamp.fromordinal(item).date())
        idct = 0
        sheets = data.groupby(["date_coll"])
        percent = 50
        total, idct = len(data.groupby(["date_coll", "route"])), 0
        
        '''Add index aka menu'''
        wb = Workbook()
        menu = wb.active
        menu.title = "索引-INDEX"
        menu.column_dimensions["A"].width = 11
        menu.freeze_panes = 'E2'
        menu.append(["收集日期", "航班总数", "航线总数", "日期总数"] + total_dates)
        for idx in range(1, 5):
            menu.cell(1, idx).font = Font(bold = "b")
            menu.cell(1, idx).alignment = Alignment("center", "center")
        for idx in range(5, menu.max_column + 1):
            menu.cell(1, idx).number_format = "mm\"-\"dd"
            menu.cell(1, idx).alignment = Alignment("center", "center")
        
        '''Append data'''
        for coll_date, group in sheets:
            sheet = Timestamp.fromordinal(coll_date).date()
            ws = wb.create_sheet(sheet.strftime("%m-%d"))
            row = {}
            footer = ['平均', group["price_rate"].median(), group["price_rate"].mean()]
            routes = group.groupby(["route"])
            feat = [sheet, len(group), len(group["route"].unique()), len(group["date_flight"].unique())]
            flight_dates = group["date_flight"].unique()
            headers = {
                'date': ["航线 \ 日期", "折扣中位", "折扣均值"], 
                'week': ["(星期)", None, None], 
                'adv': ["(提前天数)", None, None]}
            for item in flight_dates:
                headers['date'].append(Timestamp.fromordinal(item).date())
                headers['week'].append(Timestamp.fromordinal(item).isoweekday())
                headers['adv'].append(item - coll_date)
                try:
                    footer.append(group.groupby(["date_flight"]).get_group(item)["price_rate"].mean())
                except:
                    footer.append(None)
                
            
            for route, group in routes:
                group.sort_values('date_flight', inplace = True)
                idct += 1
                if percent != int(idct / total * 40 + 50):
                    percent = int(idct / total * 40 + 50)
                    print(f"\rmerging dates >> {percent:03d}", end = '%')
                row[route] = [route, group["price_rate"].median(), group["price_rate"].mean()]
                rows = group.groupby(["date_flight"])
                for item in flight_dates:
                    try:
                        row[route].append(rows.get_group(item)["price_rate"].mean())
                    except:
                        row[route].append(None)
                del rows
            del routes
            
            '''Format sheet'''
            for header in headers.values():
                ws.append(header)
            ws.cell(1, 1).hyperlink = f'#\'{menu.title}\'!A1'
            ws.cell(1, 1).font = Font(u = 'single', color = "0070C0")
            for idx in range(4, ws.max_column + 1):
                ws.cell(1, idx).number_format = "mm\"-\"dd"
            
            for route in row.values():
                ws.append(route)
            for cols in ws.iter_cols(2, ws.max_column, 4, ws.max_row):
                for cell in cols:
                    cell.number_format = "0.00%"
            ws.freeze_panes = 'D4'
            ws.column_dimensions["A"].width = 14
            
            ws.append(footer)
            for idx in range(2, ws.max_column + 1):
                ws.cell(ws.max_row, idx).number_format = "0.00%"
            
            ratios = []
            for item in total_dates:
                ratios.append(None)
            for item in headers["date"][3:]:
                idx = total_dates.index(item)
                _idx = headers["date"].index(item)
                ratios[idx] = f"='{ws.title}'!{ws.cell(ws.max_row, _idx + 1).coordinate}"
            menu.append(feat + ratios)
            cell = menu.cell(menu.max_row, 1)
            cell.hyperlink = f'#\'{ws.title}\'!C3'
            cell.font = Font(u = 'single', color = "0070C0")
        
        
        '''Sheets condition format'''
        del sheets
        for cols in menu.iter_cols(5, menu.max_column, 2, menu.max_row):
            for cell in cols:
                cell.number_format = "0.00%"
        fill_even = PatternFill(bgColor = "FFCCCC", fill_type = "solid")
        fill_odd = PatternFill(bgColor = "FFEBCD", fill_type = "solid")
        idct, total = 0, len(wb.sheetnames)
        for ws in wb:
            idct += 1
            if percent != int(idct / total * 10 + 90):
                percent = int(idct / total * 10 + 90)
                print(f"\rmerging sheets >> {percent:03d}", end = '%')
            if ws.title == menu.title:
                continue
            cell = ws.cell(3, 3, "返回索引")
            cell.hyperlink = f'#\'{menu.title}\'!A1'
            cell.font = Font(u = 'single', color = "0070C0")
            med_string = f"B4:B{ws.max_row - 1}"
            med_rule = CellIsRule('>', [f"$B${ws.max_row}"], False, Font(bold = "b"))
            ws.conditional_formatting.add(med_string, med_rule)
            avg_string = f"C4:C{ws.max_row - 1}"
            avg_rule = CellIsRule('>', [f"$C${ws.max_row}"], False, Font(bold = "b"))
            ws.conditional_formatting.add(avg_string, avg_rule)
            for row in range(5, ws.max_row, 2):
                rule_odd = CellIsRule('>', ["$C$" + str(row)], False, 
                                      Font(color = "CC6600"), fill = fill_odd)
                rstring = f"{ws.cell(row, 4).coordinate}:{ws.cell(row, ws.max_column).coordinate}"
                ws.conditional_formatting.add(rstring, rule_odd)
            for row in range(4, ws.max_row, 2):
                rule_even = CellIsRule('>', ["$C$" + str(row)], False, 
                                       Font(color = "CC0000"), fill = fill_even)
                rstring = f"{ws.cell(row, 4).coordinate}:{ws.cell(row, ws.max_column).coordinate}"
                ws.conditional_formatting.add(rstring, rule_even)
        if file == '' or file is None:
            file = f"overview_{self.__root.name}_dates.xlsx"
        if not file.endswith(".xlsx"):
            file += ".xlsx"
        if (Path(path) / Path(file)).exists():
            file = file.replace(".xlsx", f"_{datetime.today().strftime('%H%M%S')}.xlsx")
        wb.save(Path(path) / Path(file))
        wb.close
        print()
    
    
    def merge_route(self) -> tuple[tuple[str, pandas.DataFrame]]:
        '''Route overview'''
        if not len(self.__merged):
            _, self.__merged = self.merge_all()
        data = self.__merged
        overview = data.groupby(["route"])
        overviews = {
            'route': [], 'count': [], 'date_flight_count': [], 'date_coll_count': [], 
            'price_total': [], 'avg_price_rate': [], 'mid_price_rate': [], 
            'airlines': [], 'density_hour': [], 'density_day': []}
        route_density = {}
        route_ratio = {}
        route_adv_mean = {}
        route_adv_std = {}
        route_fdate_mean = {}
        route_fdate_std = {}
        for hour in range(5, 25):
            route_density[hour] = []
            route_ratio[hour] = []
        for day in sorted(data['day_adv'].unique()):
            route_adv_mean[day] = []
            route_adv_std[day] = []
        for day in sorted(data['date_flight'].unique()):
            route_fdate_mean[day] = []
            route_fdate_std[day] = []
        for name, group in overview:
            overviews['route'].append(name)
            overviews['count'].append(len(group))
            overviews['date_flight_count'].append(len(group['date_flight'].unique()))
            overviews['date_coll_count'].append(len(group['date_coll'].unique()))
            overviews['price_total'].append(self.__airData.get_airfare(*name.split('-', 1)))
            overviews['avg_price_rate'].append(group['price_rate'].mean())
            overviews['mid_price_rate'].append(group['price_rate'].median())
            overviews['airlines'].append(len(group['airline'].unique()))
            overviews['density_hour'].append(round(group['density_hour'].mean(), 2))
            overviews['density_day'].append(round(group['density_day'].mean()))
            for hour in range(5, 25):
                hour_count = group['hour_dep'].value_counts().get(hour, 0)
                route_density[hour].append(round(hour_count / len(group['hour_dep']), 2) \
                    if hour_count else None)
                hour_ratio = group.loc[group['hour_dep'] == hour, : ].get('ratio_daily', 0).mean()
                route_ratio[hour].append(round(hour_ratio, 2) if hour_ratio else None)
            for day in route_adv_mean.keys():
                mean = group.loc[group['day_adv'] == day, : ].get('price_rate', 0).mean()
                route_adv_mean[day].append(mean if mean else None)
                std = group.loc[group['day_adv'] == day, : ].get('price_rate', 0).std()
                route_adv_std[day].append(std if std else None)
            fdate_header = []
            for day in route_fdate_mean.keys():
                mean = group.loc[group['date_flight'] == day, : ].get('price_rate', 0).mean()
                route_fdate_mean[day].append(mean if mean else None)
                std = group.loc[group['date_flight'] == day, : ].get('price_rate', 0).std()
                route_fdate_std[day].append(std if std else None)
                fdate_header.append(pandas.Timestamp.fromordinal(day).date())
                
        route_overview = pandas.DataFrame(overviews)
        route_density = pandas.DataFrame(route_density)
        route_ratio = pandas.DataFrame(route_ratio)
        route_adv_mean = pandas.DataFrame(route_adv_mean)
        route_adv_std = pandas.DataFrame(route_adv_std)
        route_fdate_mean = pandas.DataFrame(route_fdate_mean)
        route_fdate_mean.set_axis(fdate_header, inplace = True, axis = 'columns')
        route_fdate_std = pandas.DataFrame(route_fdate_std)
        route_fdate_std.set_axis(fdate_header, inplace = True, axis = 'columns')
        
        return(
            ('航线 - 时刻密度', pandas.concat([route_overview, route_density], axis = 1)), 
            ('航线 - 时刻系数', pandas.concat([route_overview, route_ratio], axis = 1)), 
            
            ('航线 - 提前平均折扣', pandas.concat([route_overview, route_adv_mean], axis = 1)), 
            ('航线 - 提前标准差', pandas.concat([route_overview, route_adv_std], axis = 1)), 
            
            ('航线 - 单日平均折扣', pandas.concat([route_overview, route_fdate_mean], axis = 1)), 
            ('航线 - 单日标准差', pandas.concat([route_overview, route_fdate_std], axis = 1)), 
        )
        
    
    def merge_airline(self) -> tuple[tuple[str, pandas.DataFrame]]:
        '''Airline overview'''
        if not len(self.__merged):
            _, self.__merged = self.merge_all()
        data = self.__merged
        overview = data.groupby(["airline"])
        overviews = {
            'airline': [], 'count': [], 'date_flight_count': [], 
            'date_coll_count': [], 'route_count': [], 'type_count': [], 
            'density_day':[], 'avg_ratio_price': [], 'mid_ratio_price': []}
        airline_density = {}
        airline_ratio = {}
        for hour in range(5, 25):
            airline_density[hour] = []
            airline_ratio[hour] = []
        for name, group in overview:
            overviews['airline'].append(name)
            overviews['count'].append(len(group))
            overviews['date_flight_count'].append(len(group['date_flight'].unique()))
            overviews['date_coll_count'].append(len(group['date_coll'].unique()))
            overviews['density_day'].append(mean(group[['date_coll', 'date_flight']].value_counts().values))
            overviews['route_count'].append(round(len(group[['dep', 'arr']].drop_duplicates()) / 2))
            overviews['type_count'].append(len(group['type'].unique()))
            overviews['avg_ratio_price'].append(group['ratio_daily'].mean())
            overviews['mid_ratio_price'].append(group['ratio_daily'].median())
            for hour in range(5, 25):
                hour_count = group['hour_dep'].value_counts().get(hour, 0)
                airline_density[hour].append(round(hour_count / len(group['hour_dep']), 2) \
                    if hour_count else None)
                hour_ratio = group.loc[group['hour_dep'] == hour, : ].get('ratio_daily', 0).mean()
                airline_ratio[hour].append(round(hour_ratio, 2) if hour_ratio else None)
        
        airline_overview = pandas.DataFrame(overviews)
        airline_density = pandas.DataFrame(airline_density)
        airline_ratio = pandas.DataFrame(airline_ratio)
        del overview, overviews
        
        return (
            ('航司 - 时刻密度', pandas.concat([airline_overview, airline_density], axis = 1)), 
            ('航司 - 时刻系数', pandas.concat([airline_overview, airline_ratio], axis = 1)), 
        )
    
    
    def merge_output(self, *args: tuple[str, pandas.DataFrame], 
                     path: Path | str = '.charts') -> int:
        '''Output merged data and return the number of sheets generated'''
        sheets = 0
        file = f"overview_{self.__root.name}.xlsx"
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents = True, exist_ok = True)
        if (path / Path(file)).exists():
            time = datetime.today().strftime("%H%M%S")
            file = file.replace(".xlsx", f"_{time}.xlsx")
        writer = pandas.ExcelWriter(path / Path(file), engine = "openpyxl")
        for name, data in args:
            data.rename(columns = self.__header).to_excel(
                writer, sheet_name = name, index = False, freeze_panes = (1, 1))
            sheets += 1
        writer.save()
        return sheets
    
    
    def airline(self, *folders: str, sep: bool = False) -> tuple[str, Workbook]:
        '''Airlines' rates, competition and flight time'''
        datadict = self.master["airline"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        idct = 0
        total = len(files)
        if not total:
            return "airline", None
        
        for file in files:
            idct += 1
            print("\rairline data >>", int(idct / total * 100), end = "%")
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 2, 4, 5, 6, 9]]
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                if sep:
                    name = f'{item[2]}-{item[3]}'
                else:
                    name = f"{self.__airData.from_name(item[2])}-{self.__airData.from_name(item[3])}"
                
                if item[1] not in self.__title["airline"]["airlines"]:
                    self.__title["airline"]["airlines"].append(item[1])
                if (ordinal, coll_date) not in self.__title["airline"]["dates"]:
                    self.__title["airline"]["dates"].add((ordinal, coll_date))
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
        non_percent = ("航线航司 - 每日航班密度", "航线时刻 - 时刻航班密度", "航线时刻 - 航司竞争")
        return "airline", self.format_excel(self.__airline(datadict, self.__title["airline"]), 
                                            False, 'E2', non_percent)
    
    @staticmethod
    def __airline(datadict: dict, title: dict) -> Workbook:
        wb = Workbook()
        sheets = ["航线时刻 - 航司竞争", "航线时刻 - 时刻航班密度", 
                  "航线航司 - 每日航班密度", "航线航司 - 机票折扣总览", ]
        for airline in title["airlines"]:
            sheets.append(airline)
        for sheet in sheets:
            wb.create_sheet(sheet)
        del sheets
        
        header = {"title": ["航线", "运营航司", "日航班量", "平均折扣"]}
        ws = wb["航线航司 - 每日航班密度"]
        ws.append(header["title"] + title["airlines"])
        for idx in range(len(title["airlines"])):
            cell = ws.cell(1, idx + 5)
            cell.hyperlink = f'#\'{title["airlines"][idx]}\'!B1'
            cell.font = Font(u = 'single', color = "0070C0")
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet >>", int(idct / total * 100 / 4), end = "%")
            header[name] = [name, len(datadict[name]) - 2, 
                            datadict[name]["counts"] / len(title["dates"]), 
                            datadict[name]["rates"] / datadict[name]["counts"]]
            row = []
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["count"] / len(title["dates"]))
                else:
                    row.append(None)
            ws.append(header[name] + row)
        
        wsd = wb["航线时刻 - 时刻航班密度"]
        wsd.append(header["title"] + title["hours"])
        wsc = wb["航线时刻 - 航司竞争"]
        wsc.append(header["title"] + title["hours"])
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet >>", int(idct / total * 100 / 4 + 25), end = "%")
            rowc = []
            rowd = []
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
            wsc.append(header[name] + rowc)
            wsd.append(header[name] + rowd)
        
        ws = wb["航线航司 - 机票折扣总览"]
        ws.append(header["title"] + title["airlines"])
        for idx in range(len(title["airlines"])):
            cell = ws.cell(1, idx + 5)
            cell.hyperlink = f'#\'{title["airlines"][idx]}\'!B1'
            cell.font = Font(u = 'single', color = "0070C0")
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet >>", int(idct / total * 100 / 4 + 50), end = "%")
            row = []
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["rate"] / datadict[name][airline]["count"])
                else:
                    row.append(None)
            ws.append(header[name] + row)
        
        idct = 0
        total *= len(title["airlines"])
        for airline in title["airlines"]:
            ws = wb[airline]
            ws.append(header["title"] + title["hours"])
            cell = ws.cell(1, 1)
            cell.hyperlink = f'#\'航线航司 - 每日航班密度\'!A1'
            cell.font = Font(u = 'single', color = "0070C0")
            for name in datadict.keys():
                idct += 1
                print("\rairline sheet >>", int(idct / total * 100 / 4 + 75), end = "%")
                if not datadict[name].get(airline):
                    continue
                row = []
                for hour in title["hours"]:
                    if datadict[name][airline].get(hour):
                        row.append(datadict[name][airline][hour]["rate"] /
                                   datadict[name][airline][hour]["count"])
                    else:
                        row.append(None)
                ws.append(header[name] + row)
            cell = ws.cell(1, ws.max_row + 1, "回到目录")
            cell.hyperlink = f'#\'航线航司 - 每日航班密度\'!A1'
            cell.font = Font(u = 'single', color = "0070C0")
        return wb
    
    
    def flyday(self, *folders: str, sep: bool = False) -> tuple[str, Workbook]:
        '''Dates and weekdays of flight are fixed'''
        datadict = self.master["flyday"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        min_day = 2 * date.fromisoformat(self.__root.name).toordinal()
        max_day = 0
        if len(self.__title["flyday"]):
            if isinstance(self.__title["flyday"][0], int):
                if self.__title["flyday"][0] < min_day:
                    min_day = self.__title["flyday"][0]
                if self.__title["flyday"][len(self.__title["flyday"]) - 1] > max_day:
                    max_day = self.__title["flyday"][len(self.__title["flyday"]) - 1]
            elif self.__title["flyday"][3] < min_day:
                min_day = self.__title["flyday"][3]
            elif self.__title["flyday"][len(self.__title["flyday"]) - 1] > max_day:
                max_day = self.__title["flyday"][len(self.__title["flyday"]) - 1]
        idct = 0
        total = len(files)
        if not total:
            return "flyday", None
        
        for file in files:
            idct += 1
            print("\rflyday data >>", int(idct / total * 100), end = "%")
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            if datadict.get("dates"):
                if coll_date not in datadict.get("dates"):
                    datadict["dates"].add(coll_date)
            else:
                datadict["dates"] = {coll_date, }
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                day = item[0].toordinal()
                days = day - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                if sep:
                    name = f'{item[1]}-{item[2]}'
                else:
                    name = f"{self.__airData.from_name(item[1])}-{self.__airData.from_name(item[2])}"
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
        if max_day not in self.__title["flyday"] or min_day not in self.__title["flyday"]:
            self.__title["flyday"] = [[], "航线", "平均折扣", ]
            for day in range(min_day, max_day + 1):
                key = date.fromordinal(day)
                self.__title["flyday"].append(key)
                self.__title["flyday"][0].append(key.isoweekday())
        self.master["flyday"] = datadict
        print()
        return "flyday", self.format_excel(self.__flyday(datadict, self.__title["flyday"]), 
                                           False, 'C3', non_percent = ("每日航班密度",))
    
    @staticmethod
    def __flyday(datadict: dict, title: list) -> Workbook:
        wb = Workbook()
        wsd = wb.create_sheet("每日航班密度")
        wsd.append(["航线", "平均密度"] + title[3:])
        wsd.append([None, "(星期)",] + title[0])
        for row in wsd.iter_rows(1, 1, 3, wsd.max_column):
            for cell in row:
                cell.number_format = "m\"月\"d\"日\""
        for sheet in ("高价", "低价", "均价", "总表"):
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
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            if not isinstance(datadict[name], dict):
                continue
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, 0, ]
            countd = 0
            for day in title[3:]:
                day = day.toordinal()
                if datadict[name].get(day):
                    if datadict[name][day]["count"]:
                        countd += 1
                        rowd.append(datadict[name][day]["count"] / len(datadict["dates"]))
                        rowd[1] += datadict[name][day]["count"]
                        row[name].append(datadict[name][day]["rate"] / datadict[name][day]["count"])
                    else:
                        rowd.append(None)
                        row[name].append(None)
                else:
                    row[name].append(None)
            ws.append(row[name])
            rowd[1] /= countd * len(datadict["dates"])
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
    
    
    def city(self, *folders: str) -> tuple[str, Workbook]:
        '''City and route information overview'''
        datadict = self.master["city"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        idct = 0
        total = len(files)
        if not total:
            return "city", None
        
        for file in files:
            idct += 1
            print("\rcity data >>", int(idct / total * 100), end = "%")
            totalfare = self.__airData.get_airfare(file.name)
            
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
                    dcity: [self.__airData.airports.get(dcity, 0.05), 
                            self.__airData.cityLocation.get(dcity, 0.5), 
                            self.__airData.cityClass.get(dcity, 0.2), d_tourism],
                    acity: [totalfare, ]}
            
            if datadict.get(acity):
                if not datadict.get(acity).get(dcity):
                    datadict[acity][dcity] = [totalfare, ]
            else:
                datadict[acity] = {
                    acity: [self.__airData.airports.get(acity, 0.05), 
                            self.__airData.cityLocation.get(acity, 0.5), 
                            self.__airData.cityClass.get(acity, 0.2), a_tourism],
                    dcity: [totalfare, ]}
            
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                dcity = self.__airData.from_name(item[1], flag)
                acity = self.__airData.from_name(item[2], flag)
                datadict[dcity][acity].append(item[3])
            
        self.master["city"] = datadict
        print()
        return "city", self.format_excel(self.__city(datadict, self.__title["city"]), 
                                         False, 'E2')
    
    @staticmethod
    def __city(datadict: dict, title: tuple) -> Workbook:
        wb = Workbook()
        ws = wb.create_sheet("航线与城市总览")
        ws.append(title)
        cities = sorted(datadict.keys())
        idct = 0
        total = len(cities)
        for d_idx in range(total):
            dcity = cities[d_idx]
            idct += 1
            print("\rbuyday sheets >>", int(idct / total * 100), end = "%")
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
    
    
    def buyday(self, *folders: str, sep: bool = False) -> tuple[str, Workbook]:
        '''The number of days before flights are fixed'''
        datadict = self.master["buyday"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        idct = 0
        total = len(files)
        if not total:
            return "buyday", None
        
        for file in files:
            idct += 1
            print("\rbuyday data >>", int(idct / total * 100), end = "%")
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                if sep:
                    name = f'{item[1]}-{item[2]}'
                else:
                    name = f"{self.__airData.from_name(item[1])}-{self.__airData.from_name(item[2])}"
                if days not in self.__title["buyday"]:
                    self.__title["buyday"].append(days)
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
        self.master["buyday"] = datadict
        return "buyday", self.format_excel(self.__buyday(datadict, self.__title["buyday"]), 
                                           False, 'B2', ('所有航线目录', ))
    
    @staticmethod
    def __buyday(datadict: dict, title: list) -> Workbook:
        wb = Workbook()
        ws = wb.create_sheet('所有航线目录')
        names = list(datadict.keys())
        for row in range(2, 42):
            for column in range(2, int(len(names) / 40) + 3):
                try:
                    value = names[40 * (column - 2) + row - 2]
                    cell = ws.cell(row, column, value)
                    cell.hyperlink = f'#\'{value}\'!A1'
                    cell.font = Font(u = 'single', color = "0070C0")
                except:
                    break
            for i in range(26):
                ws.column_dimensions[chr(i + 65)].width = 15
        title.sort()
        idct = 0
        total = len(datadict)
        for name in names:
            idct += 1
            print("\rbuyday sheets >>", int(idct / total * 100), end = "%")
            ws = wb.create_sheet(name)
            ws.append(["航班日期\距起飞", ] + title)
            cell = ws.cell(1, 1)
            cell.hyperlink = f'#\'所有航线目录\'!A1'
            cell.font = Font(u = 'single', color = "0070C0")
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
    
    
    def time(self, *folders: str, sep: bool = False) -> tuple[str, Workbook]:
        '''`SINGLE FOLDER` Dep time of flights'''
        datadict = self.master["time"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        idct = 0
        total = len(files)
        if not total:
            return "time", None
        
        for file in files:
            idct += 1
            print("\rtime data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 6, 9]]
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            if datadict.get("dates"):
                if coll_date not in datadict.get("dates"):
                    datadict["dates"].add(coll_date)
            else:
                datadict["dates"] = {coll_date, }
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                if datadict.get("date"):
                    datadict["date"].append(ordinal)
                else:
                    datadict["date"] = [ordinal, ]
                if sep:
                    name = f'{item[1]}-{item[2]}'
                else:
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
        return "time", self.format_excel(self.__time(datadict, self.__title["time"]), 
                                         freeze = 'C2', non_percent = ("航班密度", ))
    
    @staticmethod
    def __time(datadict: dict, title: tuple) -> Workbook:
        wb = Workbook()
        for sheet in ("航班密度", "每日平均", "高价", "均价", "低价", "总表"):
            ws = wb.create_sheet(sheet)
            ws.append(title)
        row = {}
        sum = idct = 0
        total = len(datadict)
        datadict["date"].sort()
        for name in datadict.keys():
            rebuilt_data = {}
            idct += 1
            print("\rtime sheets >>", int(idct / total * 100), end = "%")
            if not isinstance(datadict[name], dict):
                continue
            for date in datadict["date"]:
                rebuilt_data[date] = {"rate": 0, "count": 0}
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if not datadict[name].get(hour):
                    row[name].append(None)
                    rowd.append(None)
                    continue
                days = len(datadict[name][hour]) * len(datadict["dates"])
                if days:
                    avg = counts = 0
                    for day in datadict[name][hour].keys():
                        rebuilt_data[day]["rate"] += datadict[name][hour][day]["rate"]
                        avg += datadict[name][hour][day]["rate"]
                        rebuilt_data[day]["count"] += datadict[name][hour][day]["count"]
                        counts += datadict[name][hour][day]["count"]
                        rebuilt_data[day][hour] = datadict[name][hour][day]["rate"] / \
                            datadict[name][hour][day]["count"]
                    row[name].append(avg / counts)
                    rowd.append(counts / days)
                else:
                    row[name].append(None)
                    rowd.append(None)
            ws.append(row[name])
            wb["航班密度"].append(rowd)
            
            rowa = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if datadict[name].get(hour):
                    avg = counts = 0
                    for day in datadict["date"]:
                        if datadict[name].get(hour).get(day):
                            counts += 1
                            avg += rebuilt_data[day][hour] / \
                                rebuilt_data[day]["rate"] * rebuilt_data[day]["count"]
                    rowa.append(avg / counts)
                else:
                    rowa.append(None)
            del rebuilt_data
            
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
    
    
    def type(self, *folders: str, sep: bool = False) -> tuple[str, Workbook]:
        '''`SINGLE FOLDER` Aircraft type'''
        datadict = self.master["type"]
        if len(folders):
            files = []
            for file in self.__files:
                if file.parent.name in folders:
                    files.append(file)
        else:
            files = self.__files
        idct = 0
        total = len(files)
        if not total:
            return "type", None
        
        for file in files:
            idct += 1
            print("\rtype data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 3, 4, 5, 9]]
            coll_date = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - coll_date
                if self.__day_limit and days > self.__day_limit:
                    continue
                if sep:
                    name = f'{item[2]}-{item[3]}'
                else:
                    name = f"{self.__airData.from_name(item[2])}-{self.__airData.from_name(item[3])}"
                if not datadict.get(name):
                    datadict[name] = {"小": {"rate": 0, "count": 0}, 
                                  "中": {"rate": 0, "count": 0}, 
                                  "大": {"rate": 0, "count": 0},
                                  "dates": set(), "rates": 0, "counts": 0}
                if (ordinal, coll_date) not in datadict[name]["dates"]:
                    datadict[name]["dates"].add((ordinal, coll_date))
                datadict[name][item[1]]["rate"] += item[4]
                datadict[name][item[1]]["count"] += 1
                datadict[name]["rates"] += item[4]
                datadict[name]["counts"] += 1
        print()
        self.master["type"] = datadict
        return "type", self.format_excel(self.__type(datadict, self.__title["type"]), False, 'B2')
    
    @staticmethod
    def __type(datadict: dict, title: tuple) -> Workbook:
        wb = Workbook()
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
    def format_excel(workbook: Workbook, add_average: bool = True, freeze: str = None, 
                     non_percent: tuple[str] | bool = True, remove_active: bool = True) -> Workbook:
        print("\rformatting sheets...          ")
        try:
            col = ord(freeze[0]) - 64
            row = int(freeze[1])
        except:
            row = 2
            col = 2
            freeze = None
        if remove_active:
            workbook.remove(workbook.active)
        for sheet in workbook:
            sheet.freeze_panes = freeze
            sheet.column_dimensions["A"].width = 14
            if sheet.max_row < 2:
                continue
            if add_average:
                sheet.append(("平均", ))
                for idx in range(2, sheet.max_column + 1):
                    coordinate = sheet.cell(sheet.max_row, idx).coordinate
                    top = sheet.cell(row, idx).coordinate
                    bottom = sheet.cell(sheet.max_row - 1, idx).coordinate
                    sheet[coordinate] = f"=AVERAGE({top}:{bottom})"
        if isinstance(non_percent, tuple) or non_percent is False:
            for sheet in workbook:
                if non_percent:
                    if sheet.title in non_percent:
                        continue
                for rows in sheet.iter_rows(row, sheet.max_row, col, sheet.max_column):
                    for cell in rows:
                        cell.number_format = '0%'
        return workbook
    
    def output(self, *args: tuple[str, Workbook],
               clear: bool = False, path: Path | str = '.charts') -> int:
        """
        Data
        -----
        Output rebuilt data by methods return (data name: `str`, excel: `Workbook`).
        
        Return the number of files outputed.
        
        Parameters
        -----
        clear: `bool`, clear outputed rebuilt data (not unlink files) after output.
                default: `False`
        
        path: `Path`, where to output.
                default: `Path('.charts')`
        
        """
        files = 0
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents = True, exist_ok = True)
        for arg in args:
            key, excel = arg
            if not excel:
                continue
            file = f"{key}_{self.__root}.xlsx"
            if (path / Path(file)).exists():
                time = datetime.today().strftime("%H%M%S")
                file = file.replace(".xlsx", f"_{time}.xlsx")
            excel.save(path / Path(file))
            excel.close
            files += 1
            if clear:
                del self.master[key]
                self.master[key] = {}
                if isinstance(self.__title.get(key), dict):
                    del self.__title[key]
                    self.__title[key] = {}
                elif isinstance(self.__title.get(key), list):
                    self.__title[key].clear()
            print(f"{key} data of {self.__root} has been rebuilt!")
        return files
    

if __name__ == "__main__":
    rebuild = Rebuilder(Path("2022-03-29"))
    rebuild.read_data('merging_2022-03-29.csv')
    rebuild.merge_date()
    print("Total warning(s):", rebuild.reset())
    