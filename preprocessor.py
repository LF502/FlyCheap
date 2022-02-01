import pandas
import datetime
from pathlib import Path

class Preprocessor:
    '''
    Import data from excel path or list or dict, and preprocess all data
    
    Use `run` to process!
    '''
    __dayOfWeek = {'星期二': 0, '星期三': 0, '星期四': 0, '星期一': 0.5, '星期五': 0.5, '星期六': 1, '星期日': 1}
    __craftType = {'大': True, '中': True, '小': False}
    __fsAirlines = {'中国国航','厦门航空','海南航空','东方航空','南方航空','四川航空','深圳航空','吉祥航空','山东航空',}
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
    __cityType = {}
    __cityLocation = {}
    __springFest = {2022: datetime.date(2022, 2, 1), 2023: datetime.date(2023, 1, 22)}
    __midAutumn = {2022: datetime.date(2022, 9, 10), 2023: datetime.date(2023, 9, 29)}


    def __init__(self, **kwargs) -> None:
        try:
            if kwargs.get('path', False):
                self.__path: Path = kwargs.get('path')
                self.data = pandas.read_excel(self.__path).iloc[ : , [0, 1, 2, 3, 4, 5, 6, 9]]
                self.__collDate = self.__path.parts[0].split('-', 2)
                self.__collDate: int = datetime.date(int(self.__collDate[0]), int(self.__collDate[1]), int(self.__collDate[2])).toordinal()
            elif kwargs.get('list', False):
                self.data = pandas.DataFrame(kwargs.get('list'), columns =
                            ('日期', '星期', '航司', '机型', '出发机场', '到达机场', '出发时间', '到达时间', '价格', '折扣'))
                self.data = self.data.droplevel(('到达时间', '价格'), 'columns')
                self.__collDate = datetime.datetime.now().date()
                self.__path = Path(self.__collDate.isoformat())
                self.__collDate: int = self.__collDate.toordinal()
            elif kwargs.get('dict', False):
                self.data = pandas.DataFrame(kwargs.get('dict'))
                self.__collDate = datetime.datetime.now().date()
                self.__path = Path(self.__collDate.isoformat())
                self.__collDate: int = self.__collDate.toordinal()
            else:
                raise AttributeError('Keyword must be path, list or dict!')
        except:
            raise ValueError()


    def exporter(self):
        self.data.to_excel(Path(self.__path.name.replace('.xlsx','_preproc.xlsx')), index = True, header = True, encoding = 'GBK')


    def converter(self, data: pandas.DataFrame) -> pandas.DataFrame:
        '''Convert data'''
        alterlist = []
        datelist = []
        airlinedict = dict()

        '''current dates, defined by how many days remain before the departure of flights (int, collect date - dep date)'''
        for item in data.get('日期'):
            currdate = item.toordinal()
            alterlist.append(currdate - self.__collDate)
            if currdate not in airlinedict:
                airlinedict[currdate] = set()   #initialize airline set of currdate for detecting competition between airlines
            datelist.append(currdate)
        data.loc[:, '日期'] = alterlist

        '''holiday factors including: long holidays, spring festival'''
        '''假日因素: 长假和春节'''
        holidaydict = {'假期前': [], '长假': [], '春节': [], '假期后': []}
        for item in datelist:
            day = datetime.date.fromordinal(item)
            month = day.month
            day = day.day
            if month == 3 or month == 11:
                holidaydict['假期前'].append(False)
                holidaydict['长假'].append(False)
                holidaydict['春节'].append(False)
                holidaydict['假期后'].append(False)
            elif month == 1:
                pass
            elif month == 2:
                pass
            elif month == 4:
                pass
            elif month == 5:
                pass
            elif month == 6:
                pass
            elif month == 7:
                pass
            elif month == 8:
                pass
            elif month == 9:
                pass
            elif month == 10:
                pass
            else:
                pass
            

        '''weekends -> 1, Mon and Fri -> 0.5, other weekdays -> 0'''
        alterlist = []
        for item in data.get('星期'):
            alterlist.append(self.__dayOfWeek[item])
        data.loc[:, '星期'] = alterlist

        '''airline type seted above, defined by bool: Full service -> True, Low-cost -> False'''
        alterlist = []
        i = 0
        for item in data.get('航司'):
            if item in self.__fsAirlines:
                alterlist.append(True)
            else:
                alterlist.append(False)
            if item not in airlinedict[datelist[i]]:
                airlinedict[datelist[i]].add(item)  #detect the competition between airlines
            i += 1
        data.loc[:, '航司'] = alterlist

        '''competition in dict, defined by how many airlines fly the route in the same day (int)'''
        alterlist = []
        for item in datelist:
            alterlist.append(len(airlinedict[item]))
        data.loc[:, '竞争'] = alterlist

        '''craft type defined by bool: L -> True, M/S -> False'''
        alterlist = []
        for item in data.get('机型'):
            alterlist.append(self.__craftType[item])
        data.loc[:, '机型'] = alterlist

        '''airport ratio defined above, calculated from passenger throughput'''
        alterlist = []
        dep = None
        for item in data.get('出发机场'):
            if dep == item[:2]:
                pass
            else:
                dep = item[:2]
                
            i = self.__airports.get(item, 0.05)
            alterlist.append(i)
        data.loc[:, '出发机场'] = alterlist

        '''airport ratio defined above, calculated from passenger throughput'''
        alterlist = []
        arr = None
        for item in data.get('到达机场'):
            if arr == item[:2]:
                pass
            else:
                arr = item[:2]
                
            j = self.__airports.get(item, 0.05)
            alterlist.append(j)
        data.loc[:, '到达机场'] = alterlist

        '''route type is the sum of dep and arr airport ratios'''
        '''航线类型 - 出发与到达机场参数之和: 干线 <= 1.4 < 小干线 <= 0.9 < 支线'''

        '''time-rate calculation'''
        alterlist = []
        for item in data.get('出发时'):
            alterlist.append(item.hour + round(item.minute/60, 2))
        data.loc[:, '出发时'] = alterlist
        alterlist.sort()    #sort dep time list in ascending order
        data = data.sort_values('出发时')   #sort data by dep time too, so the alterlist and data are coordinated

        rtdict = {'小时段': '均率'}
        for i in range(24):
            rtdict[i] = 0    #initialize all keys (hour) of the time-rate dict to 0
        i = total = sum =0
        fcount = 1
        curr = int(alterlist[0])
        for item in data.get('折扣'):
            sum+= item  #sum every rate for avg
            dtime = int(alterlist[i]) #dep time in int
            diff = dtime - curr #time difference
            if diff:    #more than one hour passed
                rtdict[curr] = total/fcount #avg rate of current time added
                curr += diff
                fcount = total = 0  #flights counted and flight rates sumed
            total += item    #rate added
            fcount += 1  #flight +1
            i+= 1   #dep time list item and rate sumed +1
        else:
            rtdict[curr] = total/fcount
            sum /= i #rate avg
        #time-rate.py combined

        '''dep time is defined by the percentage of avg rate'''
        i = 0
        for item in alterlist:
            alterlist[i] = round(rtdict[int(item)]/sum, 2)
            i += 1
        data.loc[:, '出发时'] = alterlist
        
        return data


if __name__ == '__main__':
    Preprocessor()