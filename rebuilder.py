import pandas
from pandas import Timestamp
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.formatting.rule import CellIsRule
from datetime import datetime
from zipfile import ZipFile
from pathlib import Path
from civilaviation import CivilAviation

class Rebuilder():
    '''
    Rebuilder
    -----
    Rebuild all data by filtering factors that influence ticket rate.
    
    Here are 3 significant factors can be rebuilt in class methods:
    - `airline`: Show density and ratio by routes and hours; show flight count by airports.
    - `route`: Show mean and std by dates and days advanced; show density and ratio by hours.
    - `date`: Show mean rate by flight dates and collect dates (with day of week and days advanced).
    
    Time are included as a detailed view. 
    Aircraft types are ignored for little contribution.
    
    Merger
    -----
    Merge all rebuilt data to `pandas.DataFrame`
    
    - `merge`: Merge all loaded file to a `pandas.DataFrame`.
    
            Note: Save the merged data to a csv file manually for further usage.
    
    
    Data
    -----
    - `append_file`: Append an excel file.
    - `append_folder`: Append excel files from folders in `Path`.
    - `append_zip`: Append excel files from zip files in `Path`.
    - `append_data`: Append saved `pandas.DataFrame` from a `.csv` file.
    
    Parameters
    -----
    root: `Path`, path of collection. 
    
    This should be the same for a class unless their data 
    are continuous or related.
    
    day_limit: `int`, limit of processing days.
            default: `0`, no limits
    
    '''
    def __init__(self, root: Path | str = Path(), day_limit: int = 0) -> None:
        
        self.__airData = CivilAviation()
        self.__merge = []
        
        self.__header = {
            'date_flight': '航班日期', 'day_week': '星期', 
            'date_coll': '收集日期', 'day_adv': '提前天数', 
            'airline': '航司', 'airlines': '运营航司', 'type': '机型', 
            
            'dep': '出发机场', 'arr': '到达机场', 'route': '航线', 
            'time_dep': '出发时刻', 'time_arr': '到达时刻', 'hour_dep': '出发时段', 
            'density_day': '日航班数', 'hour_comp': '时段竞争', 
            
            
            'count': '总计', 'route_count': '航线计数', 'type_count': '机型计数', 
            'date_flight_count': '日期计数', 'date_coll_count': '收集计数', 
            
            'price_total': '全价', 'price': '价格', 'price_rate': '折扣', 
            
            'ratio_daily': '当日系数', 
            'mid_price_rate': '折扣中位', 'avg_price_rate': '折扣平均', 
            'mid_ratio_price': '系数中位', 'avg_ratio_price': '系数平均', 
        }
        
        self.__day_limit = day_limit
        self.__root = Path(root)
        
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
    
    
    def append_data(self, path: Path | str = '') -> int:
        '''Load / append merged pandas file
        
        Return appended data rows count in `int`'''
        if path == '':
            path = f'merged_{self.__root.name}.csv'
        print('loading data >>', Path(path).name)
        data = pandas.read_csv(Path(path))
        if self.__day_limit:
            data.drop(data[data['day_adv'] > self.__day_limit].index, inplace = True)
        row, col = data.shape
        if col == 14 and row > 0:
            self.__merge = pandas.concat([data, self.__merge]) if len(self.__merge) else data
            return row
        else:
            return 0
    
    
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
            self.__merge = []
        warn = self.__warn
        self.__warn = 0
        return warn
    
    
    def merge(self) -> pandas.DataFrame:
        total = len(self.__files)
        if total == 0:
            raise ValueError("ERROR: NO FILE / DATA LOADED!")
        frame = []
        header = (
            'date_flight', 'day_week', 'airline', 'type', 'dep',                            #04
            'arr', 'time_dep', 'time_arr', 'price', 'price_rate')                           #09
        idct, percent = 0, -1
        for file in self.__files:
            idct += 1
            if percent != int(idct / total * 100):
                percent = int(idct / total * 100)
                print(f"\rmerging >> {percent:03d}", end = '%')
            date_coll = Timestamp.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file, names = header).assign(date_coll = date_coll)    #10
            if self.__day_limit:
                data.drop(data[data['day_adv'] > self.__day_limit].index, inplace = True)
            
            data['date_flight'] = data['date_flight'].map(lambda x: x.toordinal())
            data['day_adv'] = data['date_flight'] - date_coll                               #11
            data['hour_dep'] = data['time_dep'].map(lambda x: x.hour if x.hour else 24)     #12
            
            if self.__airData.is_multiairport(file.name[:3]) or \
                self.__airData.is_multiairport(file.name[4:7]):
                data['route'] = data['dep'].map(lambda x: self.__airData.from_name(x)) + \
                    '-' + data['arr'].map(lambda x: self.__airData.from_name(x))
            else:
                data['route'] = data['dep'] + '-' + data['arr']                             #13
            
            frame.append(data)
        print()
        return pandas.concat(frame)
    
    
    def overview_date(self, path: Path | str = '.charts', file: str = '') -> None:
        '''Date overview
        
        Output excel with conditional formats'''
        if not len(self.__merge):
            self.__merge = self.merge()
        data = self.__merge.sort_values('date_flight')
        total_dates = []
        for item in data['date_flight'].unique():
            total_dates.append(Timestamp.fromordinal(item).date())
        sheets = data.groupby(["date_coll"])
        percent = 50
        total, idct = len(data.groupby(["date_coll", "route"])), -1
        
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
                if percent != int(idct / total * 80):
                    percent = int(idct / total * 80)
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
        total, idct = len(wb.sheetnames), 0
        for ws in wb:
            idct += 1
            if percent != int(idct / total * 20 + 80):
                percent = int(idct / total * 20 + 80)
                print(f"\rmerging dates >> {percent:03d}", end = '%')
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
        print("\r saving")
        wb.save(Path(path) / Path(file))
        wb.close
    
    
    def overview_route(self, path: Path | str = '.charts', file: str = ''):
        '''Route overview'''
        if not len(self.__merge):
            self.__merge = self.merge()
        data = self.__merge.copy(False)
        
        if 'density_day' not in data.keys():
            data['density_day'] = data.groupby(["date_flight", \
                "route", "date_coll"])['date_flight'].transform("count")
        if 'ratio_daily' not in data.keys():
            data['ratio_daily'] = data["price_rate"] / data.groupby(["date_coll", \
                "date_flight", "route"])["price_rate"].transform("mean")
        if 'hour_comp' not in data.keys():
            data['hour_comp'] = data.groupby(["date_coll","date_flight", \
                "hour_dep", "route"])["airline"].transform("nunique")
        
        overview, total = data.groupby(["route"]), data['route'].nunique()
        title = [
            '航线', '总计', '航班日数', '收集日数', '机型数量', '全价', 
            '折扣平均', '折扣中位', '运营航司', '时段竞争', '日航班数']
        title_adv = {"overview": title + list(data['day_adv'].unique())}
        title_hour = title + list(range(5, 25))
        title_date = title + list(Timestamp.fromordinal(day).date() \
            for day in data['date_flight'].unique())
        
        route_density = {}
        route_ratio = {}
        route_comp = {}
        route_adv_mean = {}
        route_adv_std = {}
        route_date = {}
        route_date_mean = {}
        route_date_std = {}
        headers = {}
        idct, percent = 0, -1
        for name, group in overview:
            idct += 1
            if percent != int(idct / total * 100):
                percent = int(idct / total * 100)
                print(f"\rmerging routes >> {percent:03d}", end = '%')
            
            headers[name] = [
                name, len(group), group['date_flight'].nunique(), 
                group['date_coll'].nunique(), group['type'].nunique(), 
                self.__airData.get_airfare(*name.split('-', 1)), group['price_rate'].mean(), 
                group['price_rate'].median(), group['airline'].nunique(), 
                round(group['hour_comp'].mean(), 2), round(group['density_day'].mean())]
            route_comp[name] = []
            route_density[name] = []
            route_ratio[name] = []
            route_adv_mean[name] = []
            route_adv_std[name] = []
            route_date[name] = {}
            route_date_mean[name] = []
            route_date_std[name] = []
            title_adv[name] = list(group['day_adv'].unique())
            
            for hour in range(5, 25):
                group: pandas.DataFrame
                hour_airline = group.loc[group['hour_dep'] == hour, : ].get('hour_comp', 0).mean()
                route_comp[name].append(hour_airline if hour_airline else None)
                hour_count = group['hour_dep'].value_counts().get(hour, 0)
                route_density[name].append(round(hour_count / len(group['hour_dep']), 2) \
                    if hour_count else None)
                hour_ratio = group.loc[group['hour_dep'] == hour, : ].get('ratio_daily', 0).mean()
                route_ratio[name].append(round(hour_ratio, 2) if hour_ratio else None)
            for day in data['day_adv'].unique():
                mean = group.loc[group['day_adv'] == day, : ].get('price_rate', 0).mean()
                route_adv_mean[name].append(mean if mean else None)
                std = group.loc[group['day_adv'] == day, : ].get('price_rate', 0).std()
                route_adv_std[name].append(std if std else None)
            for day in data['date_flight'].unique():
                mean = group.loc[group['date_flight'] == day, : ].get('price_rate', 0).mean()
                route_date_mean[name].append(mean if mean else None)
                std = group.loc[group['date_flight'] == day, : ].get('price_rate', 0).std()
                route_date_std[name].append(std if std else None)
            for day in group['date_flight'].unique():
                route_date[name][day] = list(None for _ in title_adv[name])
            for targets, _group in group.groupby(['date_flight', 'day_adv']):
                day, adv = targets
                route_date[name][day][title_adv[name].index(adv)] = _group['price_rate'].mean()
        
        
        wb = Workbook()
        for sheet in ('航线 - 时刻密度', '航线 - 时刻竞争', '航线 - 时刻系数'):
            ws = wb.create_sheet(sheet)
            ws.append(title_hour)
            for idx in range(1, len(title_hour) + 1):
                ws.cell(1, idx).font = Font(bold = "b")
                ws.cell(1, idx).alignment = Alignment("center", "center")
        for sheet in ('航线 - 提前平均折扣', '航线 - 提前标准差'):
            ws = wb.create_sheet(sheet)
            ws.append(title_date)
            for idx in range(1, len(title_date) + 1):
                if idx > len(title):
                    ws.cell(1, idx).number_format = "mm\"-\"dd"
                ws.cell(1, idx).font = Font(bold = "b")
                ws.cell(1, idx).alignment = Alignment("center", "center")
        for sheet in ('航线 - 单日平均折扣', '航线 - 单日标准差'):
            ws = wb.create_sheet(sheet)
            ws.append(title_adv["overview"])
            for idx in range(1, len(title_adv["overview"]) + 1):
                ws.cell(1, idx).font = Font(bold = "b")
                ws.cell(1, idx).alignment = Alignment("center", "center")
        wb.remove(wb.active)
        
        for name in headers.keys():
            wb['航线 - 时刻密度'].append(headers[name] + route_density[name])
            wb['航线 - 时刻竞争'].append(headers[name] + route_comp[name])
            wb['航线 - 时刻系数'].append(headers[name] + route_ratio[name])
            wb['航线 - 提前平均折扣'].append(headers[name] + route_adv_mean[name])
            wb['航线 - 提前标准差'].append(headers[name] + route_adv_std[name])
            wb['航线 - 单日平均折扣'].append(headers[name] + route_date_mean[name])
            wb['航线 - 单日标准差'].append(headers[name] + route_date_std[name])
        for ws in wb:
            ws.freeze_panes = 'L2'
            ws.column_dimensions["A"].width = 14
            for idx in range(2, ws.max_row + 1):
                cell = ws.cell(idx, 1)
                cell.hyperlink = f'#\'{cell.value}\'!B1'
                cell.font = Font(u = 'single', color = "0070C0")
        
        for name in headers.keys():
            ws = wb.create_sheet(name)
            ws.append(['日期\提前天', '(星期)', ] + title_adv[name])
            for ordinal in route_date[name]:
                day = Timestamp.fromordinal(ordinal).date()
                ws.append([day, day.isoweekday()] + route_date[name][ordinal])
            ws.cell(1, 1).hyperlink = "#'航线 - 时刻密度'!A1"
            ws.cell(1, 1).font = Font(u = 'single', color = "0070C0")
            ws.freeze_panes = 'C2'
            ws.column_dimensions["A"].width = 13
            ws.column_dimensions["A"].width = 6
            for idx in range(3, ws.max_column + 1):
                ws.cell(idx, 1).number_format = "mm\"-\"dd"
            for cols in ws.iter_cols(3, ws.max_column, 2, ws.max_row):
                for cell in cols:
                    cell.number_format = "0.00%"
            cell = ws.cell(ws.max_row + 1, 1, '返回索引')
            cell.hyperlink = "#'航线 - 时刻密度'!A1"
            cell.font = Font(u = 'single', color = "0070C0")
        
        '''Output merged data and return the number of sheets generated'''
        if file == '' or file is None:
            file = f"overview_{self.__root.name}_routes.xlsx"
        if not file.endswith(".xlsx"):
            file += ".xlsx"
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents = True, exist_ok = True)
        if (path / Path(file)).exists():
            time = datetime.today().strftime("%H%M%S")
            file = file.replace(".xlsx", f"_{time}.xlsx")
        print("\r saving")
        wb.save(path / Path(file))
        wb.close()
    
    
    def overview_airline(self, path: Path | str = '.charts', file: str = ''):
        '''Airline overview'''
        if not len(self.__merge):
            self.__merge = self.merge()
        data = self.__merge.copy(False)
        
        if 'ratio_daily' not in data.keys():
            data['ratio_daily'] = data["price_rate"] / data.groupby(["date_coll", \
                "date_flight", "route"])["price_rate"].transform("mean")
        
        overview, total = data.groupby(["airline"]), data["airline"].nunique()
        overviews = {
            'airline': [], 'count': [], 'date_flight_count': [], 
            'date_coll_count': [], 'route_count': [], 'type_count': [], 
            'avg_ratio_price': [], 'mid_ratio_price': []}
        hour_density = {}
        hour_ratio = {}
        route_density = {}
        route_ratio = {}
        dep_ap = {}
        for hour in range(5, 25):
            hour_density[hour] = []
            hour_ratio[hour] = []
        for route in data['route'].unique():
            route_density[route] = []
            route_ratio[route] = []
        for dep in data['dep'].unique():
            dep_ap[dep] = []
        for item in (dep_ap, route_ratio, route_density):
            for value in item.values():
                for airline in data['airline'].unique():
                    value.append(None)
        idx, item = 0, ['date_coll', 'date_flight']
        idct, percent = 0, -1
        for name, group in overview:
            idct += 1
            if percent != int(idct / total * 100):
                percent = int(idct / total * 100)
                print(f"\rmerging routes >> {percent:03d}", end = '%')
            overviews['airline'].append(name)
            overviews['count'].append(len(group))
            overviews['date_flight_count'].append(group['date_flight'].nunique())
            overviews['date_coll_count'].append(group['date_coll'].nunique())
            overviews['route_count'].append(group['route'].nunique())
            overviews['type_count'].append(group['type'].nunique())
            overviews['avg_ratio_price'].append(group['ratio_daily'].mean())
            overviews['mid_ratio_price'].append(group['ratio_daily'].median())
            for hour in range(5, 25):
                count = group['hour_dep'].value_counts().get(hour, 0)
                hour_density[hour].append(round(count / len(group['hour_dep']), 2) \
                    if count else None)
                ratio = group.loc[group['hour_dep'] == hour, : ].get('ratio_daily').mean()
                hour_ratio[hour].append(round(ratio, 2) if ratio else None)
            for route in group['route'].unique():
                count = group['route'].value_counts().get(route)
                days = len(group.loc[group['route'] == route, : ][item].drop_duplicates())
                route_density[route][idx] = count / days
                ratio = group.loc[group['route'] == route, : ].get('ratio_daily').mean()
                route_ratio[route][idx] = round(ratio, 2)
            for dep in group['dep'].unique():
                count = group['dep'].value_counts().get(dep) 
                dep_ap[dep][idx] = (
                    count / len(group.loc[group['dep'] == dep, : ][item].drop_duplicates()))
            idx += 1
        
        airline_overview = pandas.DataFrame(overviews)
        hour_density = pandas.DataFrame(hour_density)
        hour_ratio = pandas.DataFrame(hour_ratio)
        route_density = pandas.DataFrame(route_density)
        route_ratio = pandas.DataFrame(route_ratio)
        dep_ap = pandas.DataFrame(dep_ap)
        del overview, overviews
        
        groups = (
            ('航司 - 时刻密度', pandas.concat([airline_overview, hour_density], axis = 1)), 
            ('航司 - 时刻系数', pandas.concat([airline_overview, hour_ratio], axis = 1)), 
            
            ('航司 - 航线密度', pandas.concat([airline_overview, route_density], axis = 1)),
            ('航司 - 航线系数', pandas.concat([airline_overview, route_ratio], axis = 1)),
            ('航司 - 机场计数', pandas.concat([airline_overview, dep_ap], axis = 1)))
        
        '''Output merged data and return the number of sheets generated'''
        if file == '' or file is None:
            file = f"overview_{self.__root.name}_airlines.xlsx"
        if not file.endswith(".xlsx"):
            file += ".xlsx"
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents = True, exist_ok = True)
        if (path / Path(file)).exists():
            time = datetime.today().strftime("%H%M%S")
            file = file.replace(".xlsx", f"_{time}.xlsx")
        writer = pandas.ExcelWriter(path / Path(file), engine = "openpyxl")
        for name, group in groups:
            group.rename(columns = self.__header).to_excel(
                writer, sheet_name = name, index = False, freeze_panes = (1, 8))
        print("\r saving")
        writer.save()
    
    
if __name__ == '__main__':
    rebuild = Rebuilder('2022-03-29')
    rebuild.append_data()
    rebuild.overview_route()
    rebuild.reset(True, True)
    rebuild.root('2022-02-17')
    rebuild.append_data()
    rebuild.overview_route()
    rebuild.reset(True, True)
    