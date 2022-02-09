import pandas
import datetime
from pathlib import Path

class Preprocessor:
    '''
    Import data from excel or list or dict, and preprocess all data
    
    Use `run` to process!
    
    Parameters
    -----
    path: `Path` where to export excel
    
            default: `Path()`, current folder
    
    collect_date: `datetime.date` date of collection
    
            default: `datetime.datetime.today()` or `from path`
    
    chinese_header: `bool` whether the keywords show in Chinese, 
    
            default: `False`, raw keywords
    
    filename: `str` name of export file
    
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
    __airports = {'北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, '广州': 1, 
                  '成都双流': 0.8, '成都天府': 0.8, '深圳': 0.75, '昆明': 0.7, '西安': 0.65, 
                  '重庆': 0.65, '杭州': 0.6, '南京': 0.45, '郑州': 0.4, '厦门': 0.4, 
                  '武汉': 0.4, '长沙': 0.4, '青岛': 0.4, '海口': 0.35, '乌鲁木齐': 0.35, 
                  '天津': 0.35, '贵阳': 0.3, '哈尔滨': 0.3, '沈阳': 0.3, '三亚': 0.3, 
                  '大连': 0.3, '济南': 0.25, '南宁': 0.25, '兰州': 0.2, '福州': 0.2, 
                  '太原': 0.2, '长春': 0.2, '南昌': 0.2, '呼和浩特': 0.2, '宁波': 0.2, 
                  '温州': 0.2, '珠海': 0.2, '合肥': 0.2, '石家庄': 0.15, '银川': 0.15, 
                  '烟台': 0.15, '桂林': 0.1, '泉州': 0.1, '无锡': 0.1, '揭阳': 0.1, 
                  '西宁': 0.1, '丽江': 0.1, '西双版纳': 0.1, '南阳': 0.1,}
    __cityClass =  {'北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, 
                   '广州': 1, '重庆': 0.8, '成都': 0.8, '北京': 1, '上海': 1, 
                   '深圳': 1, '成都双流': 0.8, '成都天府': 0.8, '杭州': 0.8, 
                   '武汉': 0.8, '西安': 0.8, '苏州': 0.8, '南京': 0.8, '天津': 0.8, 
                   '长沙': 0.8, '郑州': 0.8, '青岛': 0.8, '沈阳': 0.8, '宁波': 0.8, 
                   '佛山': 0.8, '东莞': 0.8, '无锡': 0.7, '合肥': 0.6, '昆明': 0.6, 
                   '大连': 0.6, '福州': 0.6, '厦门': 0.6, '哈尔滨': 0.6, '济南': 0.6, 
                   '温州': 0.6, '南宁': 0.6, '长春': 0.6, '泉州': 0.6, '石家庄': 0.6, 
                   '贵阳': 0.6, '南昌': 0.6, '金华': 0.6, '常州': 0.6, '南通': 0.6, 
                   '嘉兴': 0.6, '太原': 0.6, '徐州': 0.6, '惠州': 0.6, '珠海': 0.6, 
                   '中山': 0.6, '台州': 0.6, '烟台': 0.6, '兰州': 0.6, '绍兴': 0.6, 
                   '海口': 0.6, '临沂': 0.6, '汕头': 0.4, '湖州': 0.4, '潍坊': 0.4, 
                   '盐城': 0.4, '保定': 0.4, '镇江': 0.4, '洛阳': 0.4, '泰州': 0.4, 
                   '乌鲁木齐': 0.4, '扬州': 0.4, '唐山': 0.4, '漳州': 0.4, '赣州': 0.4, 
                   '廊坊': 0.4, '呼和浩特': 0.4, '芜湖': 0.4, '桂林': 0.4, '银川': 0.4, 
                   '揭阳': 0.4, '三亚': 0.4, '遵义': 0.4, '江门': 0.4, '济宁': 0.4, 
                   '莆田': 0.4, '湛江': 0.4, '绵阳': 0.4, '淮安': 0.4, '连云港': 0.4, 
                   '淄博': 0.4, '宜昌': 0.4, '邯郸': 0.4, '上饶': 0.4, '柳州': 0.4, 
                   '舟山': 0.4, '咸阳': 0.4, '九江': 0.4, '衡阳': 0.4, '威海': 0.4, 
                   '宁德': 0.4, '阜阳': 0.4, '株洲': 0.4, '丽水': 0.4, '南阳': 0.4, 
                   '襄阳': 0.4, '大庆': 0.4, '沧州': 0.4, '信阳': 0.4, '岳阳': 0.4, 
                   '商丘': 0.4, '肇庆': 0.4, '清远': 0.4, '滁州': 0.4, '龙岩': 0.4, 
                   '荆州': 0.4, '蚌埠': 0.4, '新乡': 0.4, '鞍山': 0.4, '湘潭': 0.4, 
                   '马鞍山': 0.4, '三明': 0.4, '潮州': 0.4, '梅州': 0.4, '秦皇岛': 0.4, 
                   '南平': 0.4, '吉林': 0.4, '安庆': 0.4, '泰安': 0.4, '宿迁': 0.4, 
                   '包头': 0.4, '郴州': 0.4, '南充': 0.4, }
    __cityLocation = {'北京首都': 0.2, '北京大兴': 0.2, '上海虹桥': 0, '上海浦东': 0, 
                      '北京': 0.2, '成都': 0.8, '上海': 0, '广州': 0, '重庆': 0.7, 
                      '深圳': 0, '成都双流': 0.8, '成都天府': 0.8, '杭州': 0.1, 
                      '武汉': 0.5, '西安': 0.6, '苏州': 0.1, '南京': 0.2, '天津': 0, 
                      '长沙': 0.5, '郑州': 0.4, '青岛': 0, '沈阳': 0.1, '宁波': 0, 
                      '佛山': 0, '东莞': 0, '无锡': 0.1, '合肥': 0.3, '昆明': 0.7, 
                      '大连': 0, '福州': 0, '厦门': 0, '哈尔滨': 0.5, '济南': 0.2, 
                      '温州': 0, '南宁': 0.1, '长春': 0.3, '泉州': 0, '石家庄': 0.2, 
                      '贵阳': 0.7, '南昌': 0.4, '金华': 0.1, '常州': 0.2, '南通': 0, 
                      '嘉兴': 0, '太原': 0.2, '徐州': 0.2, '惠州': 0.1, '珠海': 0, 
                      '中山': 0, '台州': 0, '烟台': 0, '兰州': 0.8, '绍兴': 0, 
                      '海口': 0.1, '临沂': 0.1, '汕头': 0, '湖州': 0.1, '潍坊': 0.1, 
                      '盐城': 0, '保定': 0.2, '镇江': 0.2, '洛阳': 0.5, '泰州': 0.2, 
                      '乌鲁木齐': 1, '扬州': 0.2, '唐山': 0.1, '漳州': 0, '赣州': 0.4, 
                      '廊坊': 0.1, '呼和浩特': 0.6, '芜湖': 0.3, '桂林': 0.2, '银川': 0.7, 
                      '揭阳': 0, '三亚': 0.1, '遵义': 0.7, '江门': 0.1, '济宁': 0.2, 
                      '莆田': 0, '湛江': 0, '绵阳': 0.8, '淮安': 0.1, '连云港': 0, 
                      '淄博': 0.1, '宜昌': 0.6, '邯郸': 0.3, '上饶': 0.3, '柳州': 0.2, 
                      '舟山': 0, '西宁': 0.9, '九江': 0.4, '衡阳': 0.5, '威海': 0, 
                      '宁德': 0, '阜阳': 0.4, '株洲': 0.5, '丽水': 0.1, '南阳': 0.5, 
                      '襄阳': 0.6, '大庆': 0.6, '沧州': 0.1, '信阳': 0.5, '岳阳': 0.5, 
                      '商丘': 0.3, '肇庆': 0.1, '清远': 0.1, '滁州': 0.3, '龙岩': 0.2, 
                      '荆州': 0.6, '蚌埠': 0.3, '新乡': 0.4, '鞍山': 0.1, '湘潭': 0.5, 
                      '马鞍山': 0.3, '三明': 0.2, '潮州': 0, '梅州': 0.2, '秦皇岛': 0, 
                      '南平': 0.2, '吉林': 0.3, '安庆': 0.4, '泰安': 0.2, '宿迁': 0.2, 
                      '包头': 0.7, '郴州': 0.4, '南充': 0.8, '丽江': 0.8, '西双版纳': 0.8, 
                      '张家界': 0.7, '大理': 0.8, '呼伦贝尔': 0.7, '德宏': 0.8, '拉萨': 1, }
    __tourism = {'桂林', '西双版纳', '丽江', '张家界', '鄂尔多斯', '呼伦贝尔', '德宏', '大理', 
                 '拉萨', '乌鲁木齐', '成都', '重庆', '贵阳', '昆明',}
    __springFest = {2022: datetime.date(2022, 1, 31), 2023: datetime.date(2023, 1, 21)}
    __dragonBoat = {2022: datetime.date(2022, 6, 3), 2023: datetime.date(2023, 6, 22)}
    __midAutumn = {2022: datetime.date(2022, 9, 10), 2023: datetime.date(2023, 9, 29)}
    __holidaysDefault = {1: (1, 3), 4: (4, 3), 5: (1, 5), 7: (7, 25), 8: (1, 24), 10: (1, 7)}
    __holidays = dict()
    # {year: [(ordinal, holiday duration), ...], ...}   --all in int, Spring Festival duration is 0

    def __init__(self, **kwargs) -> None:
        self.__path: Path = kwargs.get('path', Path())
        self.__filename: str = kwargs.get('filename', '')
        self.header: list[str] = kwargs.get('chinese_header', False)
        self.__collDate: datetime.date = kwargs.get('collect_date', datetime.datetime.now().date())
        try:
            if kwargs.get('excel', False):
                self.data = pandas.read_excel(kwargs.get('excel')).iloc[ : , [0, 1, 2, 3, 4, 5, 6, 9]]
                self.__filename: str = kwargs.get('excel').name
                try:
                    self.__collDate = datetime.datetime.fromisoformat(self.__path.parts[0])
                except:
                    self.__collDate = kwargs.get('collect_date', datetime.datetime.now().date())
            elif kwargs.get('list', False):
                self.data = pandas.DataFrame(kwargs.get('list'), columns =
                            ('日期', '星期', '航司', '机型', '出发机场', '到达机场', '出发时间', '到达时间', '价格', '折扣'))
                self.data = self.data.droplevel(('到达时间', '价格'), 'columns')
            elif kwargs.get('dict', False):
                self.data = pandas.DataFrame(kwargs.get('dict'))
            else:
                print('  ---------------------------  ')
                print('  WARNING: No data is loaded!  ')
                print('  ---------------------------  ')
        except:
            raise ValueError('')
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
                citydict[i]['airport'] = self.__airports.get(i, 0.05)
                citydict[i]['loc'] = self.__cityLocation.get(i, 0.5)
                citydict[i]['class'] = self.__cityClass.get(i, 0.2)
                if i in self.__tourism:
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
                citydict[j]['airport'] = self.__airports.get(j, 0.05)
                citydict[j]['loc'] = self.__cityLocation.get(j, 0.5)
                citydict[j]['class'] = self.__cityClass.get(j, 0.2)
                if j in self.__tourism:
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
            self.__filename = i + j + '_预处理.xlsx'
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


    def run(self):
        self.exporter(self.converter())


if __name__ == '__main__':

    folders = ['2022-01-28', ]
    
    for strings in folders:
        path = Path(strings)
        for file in path.iterdir():
            if file.match('*.xlsx') and 'preproc' not in file.name:
                print('\r' + file.name, 'excel initializing...', end = '')
                debugging = Preprocessor(path = path, excel = file, chinese_header = True)
                print('\r' + file.name, 'preprocess running...', end = '')
                debugging.run()
                print('\r' + file.name, 'preprocess completed.', end = '')
        print(f'\n{strings} finished at', datetime.datetime.now().time().isoformat('seconds'))
