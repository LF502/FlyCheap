import pandas
import datetime
from pathlib import Path
from civilaviation import CivilAviation

class Preprocessor(CivilAviation):
    '''
    Import data from excel or list or dict, and preprocess all data
    
    Use `run` to process!
    
    Parameters
    -----
    path: `Path` | `str` where to export excel
    
    
    collect_date: `datetime.date` date of collection
    
            default: `datetime.datetime.today()` or `from path`
    
    chinese_header: `bool` whether the keywords show in Chinese, 
    
            default: `False`, raw keywords
    
    file_name: `str` name of export file
    
            default: `the last city tuple in Chinese` or `excel name`
    
    Required data
    -----
    DataFrame, like `excel` or `list` or `dict`
    
    Input data keywords
    -----
    date, weekday, airline, craft_type, from, to, dep_time, rate
    
    Output data keywords
    -----
    (index), date, weekday, day_density, spring_festival, in_holiday, 
    
    before_holiday, after_holiday, craft_type, airline, competition, 
    
    from, from_loc, from_class, from_tourism, to, to_loc, 
    
    to_class, to_tourism, rate, dep_time, hour_density, hour_ratio
    
    中文输出表头
    -----
    (序号), 日期, 星期, 日密度, 春节, 长假, 假期前, 假期后, 机型, 
    
    航司, 竞争, 出发机场, 出发位置, 出发地级, 出发旅游, 到达机场, 到达位置, 
    
    到达地级, 到达旅游, 机票折扣, 出发时刻, 时刻密度, 时刻系数

    '''
    __dayOfWeek = {'星期二': 0, '星期三': 0, '星期四': 0, '星期一': 0.5, '星期五': 0.5, '星期六': 1, '星期日': 1}
    __craftType = {'大': True, '中': True, '小': False, 'L': True, 'M': True, 'S': False,}
    __fsAirlines = {'中国国航', 'CA', '厦门航空', 'MF', '海南航空', 'HU', '东方航空', 'MU', '南方航空', 'CZ', 
                    '四川航空', '3U', '深圳航空', 'ZH', '吉祥航空', 'HO', '山东航空', 'SC', }
    __springFest = {2022: datetime.date(2022, 1, 31), 2023: datetime.date(2023, 1, 21)}
    __dragonBoat = {2022: datetime.date(2022, 6, 3), 2023: datetime.date(2023, 6, 22)}
    __midAutumn = {2022: datetime.date(2022, 9, 10), 2023: datetime.date(2023, 9, 29)}
    __holidaysDefault = {1: (1, 3), 4: (4, 3), 5: (1, 5), 7: (7, 25), 8: (1, 24), 10: (1, 7)}
    __holidays = dict()
    # {year: [(ordinal, holiday duration), ...], ...}   --all in int, Spring Festival duration is 0

    def __init__(self, path: Path, **kwargs) -> None:
        
        self.__airData = CivilAviation()
        
        self.__path = path
        if not isinstance(self.__path, Path):
            self.__path = Path(str(self.__path))
        if not self.__path.exists():
            raise ValueError(self.__path.name, 'does not exist!')
        self.__filename: str = kwargs.get('file_name', '')
        self.header: list[str] = kwargs.get('chinese_header', False)
        self.__collDate: datetime.date = kwargs.get('collect_date', datetime.datetime.now().date())
        try:
            cols = [0, 1, 2, 3, 4, 5, 6, 9]
            if kwargs.get('excel', False):
                self.data = pandas.read_excel(kwargs.get('excel')).iloc[ : , cols]
                self.__filename: str = kwargs.get('excel').name
                try:
                    self.__collDate = datetime.datetime.fromisoformat(self.__path.name)
                except:
                    self.__collDate = kwargs.get('collect_date', datetime.datetime.now().date())
            elif kwargs.get('list', False):
                header = ('日期', '星期', '航司', '机型', '出发机场', '到达机场', '出发时', '到达时', '价格', '折扣')
                self.data = pandas.DataFrame(kwargs.get('list'), columns = header)
                self.data = self.data.iloc[ : , cols]
            elif kwargs.get('dict', False):
                self.data = pandas.DataFrame(kwargs.get('dict'))
            else:
                print('WARN: No data!')
        except:
            print('WARN: No data!')
        self.__collDate: int = self.__collDate.toordinal()

    @property
    def default_holiday(self) -> dict:
        '''Show default holidays'''
        return self.__holidaysDefault


    @staticmethod
    def __add_holiday(args):
        __pending = dict()
        for item in args:
            if isinstance(item, datetime.date):
                __pending[item.year] = item
            else:
                raise ValueError('All args should be a datetime.date:', item)
        return __pending

    @classmethod
    def springFest(cls, *args: datetime.date) -> dict:
        '''Input the date of New year's Eve.
        Add holiday by `*args`, returns default or changed dates.'''
        if args:
            cls.__springFest.update(cls.__add_holiday(args))
        return cls.__springFest

    @classmethod
    def dragonBoat(cls, *args: datetime.date) -> dict:
        '''Input the date of Dragon Boat Festival.
        Add holiday by `*args`, returns default or changed dates'''
        if args:
            cls.__dragonBoat.update(cls.__add_holiday(args))
        return cls.__dragonBoat

    @classmethod
    def midAutumn(cls, *args: datetime.date) -> dict:
        '''Input the date of Mid-Autumn Festival.
        Add holiday by `*args`, returns default or changed dates'''
        if args:
            cls.__midAutumn.update(cls.__add_holiday(args))
        return cls.__midAutumn


    def get_holidays(self, year: int) -> dict:
        self.__holidays[year] = list()
        for month in self.__holidaysDefault.keys():
            item = self.__holidaysDefault.get(month)
            self.__holidays[year].append((datetime.date(year, month, item[0]).toordinal(), item[1]))

        if year in self.__springFest.keys():
            springFest = self.__springFest.get(year)
            self.__holidays[year].append((springFest.toordinal(), 0))
        else:
            raise KeyError('Spring Festival of', year, 'is not found!')
        if year in self.__dragonBoat.keys():
            dragonBoat = self.__dragonBoat.get(year)
            self.__holidays[year].append((dragonBoat.toordinal(), 3))
        else:
            raise KeyError('Dragon Boat Festival of', year, 'is not found!')
        if year in self.__midAutumn.keys():
            midAutumn = self.__midAutumn.get(year)
            self.__holidays[year].append((midAutumn.toordinal(), 3))
        else:
            raise KeyError('Mid-Autumn Festival of', year, 'is not found!')

        self.__holidays[year].sort(key = lambda item: item[0])
        return self.__holidays[year]


    def __convert_holiday(self, ordinal: int) -> dict[str, bool]:
        date = datetime.date.fromordinal(ordinal)
        holidays = self.__holidays.get(date.year) if self.__holidays.get(date.year) else self.get_holidays(date.year)

        holidaydict = {'spring_festival': False, 'in_holiday': False, 
                       'before_holiday': False, 'after_holiday': False}
        for holiday in holidays:
            if ordinal - holiday[0] < -7:
                continue
            elif holiday[1] and ordinal - holiday[0] - holiday[1] > 7:
                continue
            elif not holiday[1] and ordinal - holiday[0] - 8 > 7:
                continue
            
            if holiday[1] and -7 <= ordinal - holiday[0] < 0:
                holidaydict['before_holiday'] = True    #before holiday
            elif not holiday[1] and -7 <= ordinal - holiday[0] < 0:
                holidaydict['spring_festival'] = True   #spring festival
                holidaydict['before_holiday'] = True    #before holiday
            
            elif holiday[1] and 0 <= ordinal - holiday[0] < holiday[1]:
                holidaydict['in_holiday'] = True        #in holiday
            elif not holiday[1] and 0 <= ordinal - holiday[0] < 8:
                holidaydict['spring_festival'] = True   #spring festival
                holidaydict['in_holiday'] = True        #in holiday
            
            elif holiday[1] and 0 <= ordinal - holiday[0] - holiday[1] <= 7:
                holidaydict['after_holiday'] = True     #after holiday
            elif not holiday[1] and 0 <= ordinal - holiday[0] - 8 <= 7:
                holidaydict['spring_festival'] = True   #spring festival
                holidaydict['after_holiday'] = True     #after holiday
        return holidaydict


    def exporter(self, data: pandas.DataFrame) -> None:
        '''
        Output data keywords
        -----
        DATES: date, weekday, day_density, spring_festival, in_holiday, before_holiday, after_holiday, 
        
        AIRLINES: craft_type, airline, competition, 
        
        AIRPORTS: from, to, 
        
        CITIES: from_loc, from_class, from_tourism, to_loc, to_class, to_tourism, 
        
        PRICE: rate, 
        
        TIME: dep_time, hour_density, hour_ratio
        '''
        if self.header:
            header = {'date': '日期', 'weekday': '星期', 'day_density': '日密度', 
                      'spring_festival': '春节', 'in_holiday': '长假', 
                      'before_holiday': '假期前', 'after_holiday': '假期后', 
                      'craft_type': '机型', 'airline': '航司', 'competition': '竞争', 
                      'from': '出发机场', 'from_loc': '出发位置', 
                      'from_class': '出发地级', 'from_tourism': '出发旅游', 
                      'to': '到达机场', 'to_loc': '到达位置', 
                      'to_class': '到达地级', 'to_tourism': '到达旅游', 
                      'rate': '机票折扣', 'dep_time': '出发时刻', 
                      'hour_density': '时刻密度', 'hour_ratio': '时刻系数'}
            data.rename(header, axis = 'columns', inplace = True)
            index_label = '序号'
        else:
            index_label = 'index'
        data.to_excel(Path(self.__path / self.__filename), index = True, header = True, 
                      encoding = 'GBK', freeze_panes = (1, 1), index_label = index_label)
        


    def converter(self) -> pandas.DataFrame:
        '''Convert data'''
        data = pandas.DataFrame()
        datelist = list()
        airlinedict = dict()
        holidaydict = dict()
        daydict = dict()
        hourdict = dict()

        '''current dates, defined by how many days remain before the departure of a flight'''
        '''日期通过数据收集时间距航班起飞时间定义, 为整数'''
        alterlist = []
        for item in self.data.get('日期'):
            ordinal = item.toordinal()
            alterlist.append(ordinal - self.__collDate)
            if ordinal not in airlinedict:
                airlinedict[ordinal] = set()    #airline set - competition
            if not holidaydict.get(ordinal):    #holiday dict - holiday process
                holidaydict[ordinal] = self.__convert_holiday(ordinal)
            if daydict.get(ordinal):            #day dict - day density
                daydict[ordinal] += 1
            else:
                hourdict[ordinal] = dict()      #hour dict - hour density / time-rate
                daydict[ordinal] = 1
            datelist.append(ordinal)
        data.loc[:, 'date'] = alterlist
        del alterlist

        '''weekends -> 1, Mon and Fri -> 0.5, other weekdays -> 0'''
        '''周末 -> 1  周一周五 -> 0.5  周中 -> 0 '''
        alterlist = []
        for item in self.data.get('星期'):
            alterlist.append(self.__dayOfWeek[item])
        data.loc[:, 'weekday'] = alterlist
        del alterlist
        
        '''day density -> flights between cities every day'''
        '''日密度: 每天往返城市对间航班数量, 为整数'''
        alterlist = []
        for ordinal in datelist:
            alterlist.append(daydict.get(ordinal))
        data.loc[:, 'day_density'] = alterlist
        del alterlist
        del daydict

        '''holiday factors including: long holidays, spring festival'''
        '''假日因素: 长假和春节  真 / 假'''
        alterdict = {'spring_festival': [], 'in_holiday': [], 'before_holiday': [], 'after_holiday': []}
        for ordinal in datelist:
            for key in alterdict.keys():
                alterdict[key].append(holidaydict[ordinal][key])
        data.loc[:, alterdict.keys()] = alterdict.values()
        del alterdict
        del holidaydict

        '''craft type defined by bool: L/M -> True, S -> False'''
        '''大 中型机为真  小型机为假'''
        alterlist = []
        for item in self.data.get('机型'):
            alterlist.append(self.__craftType[item])
        data.loc[:, 'craft_type'] = alterlist
        del alterlist

        '''airline type seted above, defined by bool: Full service -> True, Low-cost -> False'''
        '''全服务为真  低成本为假'''
        alterlist = []
        i = 0
        for item in self.data.get('航司'):
            if item in self.__fsAirlines:
                alterlist.append(True)
            else:
                alterlist.append(False)
            if item not in airlinedict[datelist[i]]:
                airlinedict[datelist[i]].add(item)  #detect the competition between airlines
            i += 1
        data.loc[:, 'airline'] = alterlist
        del alterlist

        '''competition in dict, defined by how many airlines fly the route in the same day (int)'''
        '''航司竞争按航线每日执飞航空公司数量定义, 为整数'''
        alterlist = []
        for item in datelist:
            alterlist.append(len(airlinedict[item]))
        data.loc[:, 'competition'] = alterlist
        del alterlist
        del airlinedict

        '''airport ratio: calculated from passenger throughput'''
        '''city location ratio: calculated from distance to east coast'''
        '''city class ratio: calculated from city classification by officals'''
        '''city tourism: Inland tour city (or tourism center) -> True, else -> False'''
        '''机场系数按2019年旅客总吞吐量换算为0~1'''
        '''城市级别系数按城市分级 (一线 准一线 二线等) 换算'''
        '''地理位置系数按城市到东海岸距离换算'''
        '''内陆旅游城市 (或集散中心) 为真 其余为假'''
        citydict = dict()
        alterdict = {'from': [], 'from_loc': [], 'from_class': [], 'from_tourism': []}
        for i in self.data.get('出发机场'):
            if not citydict.get(i):
                citydict[i] = dict()
                citydict[i]['airport'] = self.__airData.airports.get(i, 0.05)
                citydict[i]['loc'] = self.__airData.cityLocation.get(i, 0.5)
                citydict[i]['class'] = self.__airData.cityClass.get(i, 0.2)
                if i in self.__airData.tourism:
                    citydict[i]['tourism'] = True
                else:
                    citydict[i]['tourism'] = False
            alterdict['from'].append(citydict.get(i).get('airport'))
            alterdict['from_loc'].append(citydict.get(i).get('loc'))
            alterdict['from_class'].append(citydict.get(i).get('class'))
            alterdict['from_tourism'].append(citydict.get(i).get('tourism'))
        data.loc[:, alterdict.keys()] = alterdict.values()
        del alterdict

        alterdict = {'to': [], 'to_loc': [], 'to_class': [], 'to_tourism': []}
        for j in self.data.get('到达机场'):
            if not citydict.get(j):
                citydict[j] = dict()
                citydict[j]['airport'] = self.__airData.airports.get(j, 0.05)
                citydict[j]['loc'] = self.__airData.cityLocation.get(j, 0.5)
                citydict[j]['class'] = self.__airData.cityClass.get(j, 0.2)
                if j in self.__airData.tourism:
                    citydict[j]['tourism'] = True
                else:
                    citydict[j]['tourism'] = False
            alterdict['to'].append(citydict.get(j).get('airport'))
            alterdict['to_loc'].append(citydict.get(j).get('loc'))
            alterdict['to_class'].append(citydict.get(j).get('class'))
            alterdict['to_tourism'].append(citydict.get(j).get('tourism'))
        data.loc[:, alterdict.keys()] = alterdict.values()
        del alterdict
        del citydict

        if self.__filename == '':
            i = i[:2] if '北京' in i or '上海' in i or '成都' in i else i
            j = j[:2] if '北京' in j or '上海' in j or '成都' in j else j
            self.__filename = i + '~' + j + '_预处理.xlsx'
        else:
            self.__filename = self.__filename.replace('.xlsx', '_preproc.xlsx')

        '''route type is the sum of dep and arr airport ratios, no need to process here.'''
        '''航线类型 (此处不处理) - 出发与到达机场参数之和: 干线 <= 1.4 < 小干线 <= 0.9 < 支线'''

        '''time-rate calculation'''
        '''出发时刻系数计算'''
        alterlist = []
        hourlist = []
        i = 0
        for item in self.data.get('出发时'):
            item = item.hour + round(item.minute/60, 2)
            alterlist.append(item)
            if hourdict[datelist[i]].get(int(item)):
                hourdict[datelist[i]][int(item)] += 1
            else:
                hourdict[datelist[i]][int(item)] = 1
            i += 1
        data.loc[:, 'rate'] = self.data.get('折扣')
        data.loc[:, 'dep_time'] = alterlist
        for i in range(len(alterlist)):
            hourlist.append(hourdict.get(datelist[i]).get(int(alterlist[i])))
        data.loc[:, 'hour_density'] = hourlist
        alterlist.sort()    #sort dep time list in ascending order
        data = data.sort_values('dep_time')   #sort data by dep time too, so the alterlist and data are coordinated
        del datelist
        del hourlist

        '''dep time is defined by the percentage of avg rate'''
        '''出发时系数通过同时段折扣平均数 / 日平均折扣换算为1附近系数'''
        alterdict = dict()
        i = sum = 0
        for item in data.get('rate'):
            dtime = int(alterlist[i])
            i += 1
            sum += item
            if alterdict.get(dtime):
                alterdict[dtime].append(item)
            else:
                alterdict[dtime] = [item, ]
        for key in alterdict.keys():
            hoursum = 0
            for item in alterdict[key]:
                hoursum += item
            else:
                alterdict[key] = round(hoursum / len(alterdict[key]) / sum * len(alterlist), 2)

        i = 0
        for item in alterlist:
            alterlist[i] = alterdict[int(item)]
            i += 1
        data.loc[:, 'hour_ratio'] = alterlist
        del alterlist
        del alterdict

        return data


    def run(self) -> bool:
        try:
            self.exporter(self.converter())
            return True
        except:
            return False


if __name__ == '__main__':

    first_date = "2022-02-17"
    folders = ['2022-01-28', ]
    
    for folder in folders:
        path = Path(first_date) / Path(folder)
        for file in path.iterdir():
            if file.match('*.xlsx') and '_' not in file.name:
                print('\r' + file.name, 'excel initializing...', end = '')
                debugging = Preprocessor(path = path, excel = file, chinese_header = True)
                print('\r' + file.name, 'preprocess running...', end = '')
                debugging.run()
                print('\r' + file.name, 'preprocess completed.', end = '')
        print(f'\n{folder} finished at', datetime.datetime.now().time().isoformat('seconds'))
