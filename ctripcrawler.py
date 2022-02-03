import datetime
import time
from typing import Generator
from requests import get, post
from json import dumps, loads
from re import match
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.cell import Cell
from pathlib import Path
from random import random

class CtripCrawler:
    """
    Ctrip flight tickets crawler
    
    Use `run` to process!
    """

    __dayOfWeek = {1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六', 7:'星期日'}
    __airportCity = {
        'BJS':'北京','CAN':'广州','SHA':'上海','CTU':'成都','TFU':'成都','SZX':'深圳','KMG':'昆明','XIY':'西安','PEK':'北京',
        'PKX':'北京','PVG':'上海','CKG':'重庆','HGH':'杭州','NKG':'南京','CGO':'郑州','XMN':'厦门','WUH':'武汉','CSX':'长沙',
        'TAO':'青岛','HAK':'海口','URC':'乌鲁木齐','TSN':'天津','KWE':'贵阳','HRB':'哈尔滨','SHE':'沈阳','SYX':'三亚','DLC':'大连',
        'TNA':'济南','NNG':'南宁','LHW':'兰州','FOC':'福州','TYN':'太原','CGQ':'长春','KHN':'南昌','HET':'呼和浩特','NGB':'宁波',
        'WNZ':'温州','ZUH':'珠海','HFE':'合肥','SJW':'石家庄','INC':'银川','YNT':'烟台','KWL':'桂林','JJN':'泉州','WUX':'无锡',
        'SWA':'揭阳','XNN':'西宁','LJG':'丽江','JHG':'西双版纳','NAY':'北京','LXA':'拉萨','MIG':'绵阳','CZX':'常州','NTG':'南通',
        'YIH':'宜昌','WEH':'威海','XUZ':'徐州','ZHA':'湛江','YTY':'扬州','DYG':'张家界','DSN':'鄂尔多斯','BHY':'北海','LYI':'临沂',
        'HLD':'呼伦贝尔','HUZ':'惠州','UYN':'榆林','YCU':'运城','KHG':'喀什','HIA':'淮安','BAV':'包头','ZYI':'遵义','KRL':'库尔勒',
        'LUM':'德宏','YNZ':'盐城','KOW':'赣州','YIW':'义乌','LYG':'连云港','XFN':'襄阳','CIF':'赤峰','LZO':'泸州','DLU':'大理',
        'AKU':'阿克苏','YNJ':'延吉','ZYI':'遵义','HTN':'和田','LZH':'柳州','LYA':'洛阳','WDS':'十堰','HSN':'舟山','JNG':'济宁',
        'YIN':'伊宁','ENH':'恩施','ACX':'兴义','HYN':'台州','TCZ':'腾冲','DAT':'大同','BSD':'保山','BFJ':'毕节','NNY':'南阳',
        'WXN':'万州','TGO':'通辽','CGD':'常德','HNY':'衡阳','XIC':'西昌','MDG':'牡丹江','RIZ':'日照','NAO':'南充','YBP':'宜宾',}
    __userAgents = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.4.727 Yowser/2.5 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.58',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 OPR/82.0.4227.33',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (X11; CrOS x86_64 14268.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36',
        'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',)

    def __init__(self, cityList: list, flightDate: datetime.date = datetime.datetime.now().date(), days: int = 1, day_limit: int = 0, 
                 ignore_cities: set = None, ignore_threshold: int = 3, with_return: bool = True) -> None:

        try:
            self.__codesum = len(cityList)
        except:
            self.exits(1) #exit for empty or incorrect data
        if self.__codesum <= 1:
            self.exits(2) #exit for no city tuple

        self.cityList = cityList
        self.flightDate = flightDate

        self.days = days
        self.day_limit = day_limit

        self.ignore_cities = ignore_cities
        self.ignore_threshold = ignore_threshold
        self.with_return = with_return

        '''Day range preprocess'''
        currDate = datetime.datetime.now().toordinal()
        if currDate >= self.flightDate.toordinal():   # If collect day is behind today, change the beginning date and days of collect.
            self.ignore_threshold = 0
            self.days -= currDate - self.flightDate.toordinal() + 1
            self.flightDate = self.flightDate.fromordinal(currDate + 1)
            if self.day_limit:   # If there's a limit for days in advance, change the days of collect.
                if self.days > self.day_limit:
                    self.days = self.day_limit
        else:
            if self.day_limit:   # If there's a limit for days in advance, change the days of collect.
                total = self.flightDate.toordinal() + self.days - currDate
                if total > self.day_limit:
                    self.days -= total - self.day_limit
        if self.days <= 0:
            self.exits(3) #exit for day limit error
        self.__total = self.__codesum * (self.__codesum - 1) * self.days / 2

        if self.__total == 0:
            self.exits(4)   #exit for ignored

        self.url = "https://flights.ctrip.com/itinerary/api/12808/products"
        self.header = {"Content-Type": "application/json;charset=utf-8",
                       "Accept": "application/json",
                       "Accept-Language": "zh-cn",
                       "Origin": "https://flights.ctrip.com",
                       "Host": "flights.ctrip.com"}
        self.payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1}

        self.__idct = 0
        self.__avgTime = 3.5 if with_return else 1.7


    def __sizeof__(self) -> int:
        return self.__total


    @property
    def skip(self) -> set:
        '''Ignore cities with few flights.
        If two cities given are too close or not in analysis range, skip, by returning matrix coordinates in set. '''
        if self.ignore_threshold == 0:
            return set()
        else:
            ignoreSet = {('BJS','TSN'),('BJS','SJW'),('BJS','TYN'),('BJS','TNA'),('BJS','SHE'),('BJS','HET'),
                        ('SJW','TYN'),('SJW','TNA'),('TSN','TNA'),('TSN','TYN'),('TYN','TNA'),('SJW','TSN'),
                        ('SHE','CGQ'),('CGQ','HRB'),('SHE','HRB'),('DLC','SHE'),('DLC','CGQ'),('TSN','DLC'),
                        ('BJS','SHE'),('BJS','CGO'),('TNA','CGO'),('BJS','TAO'),('TNA','TAO'),('TSN','TAO'),
                        ('CGO','SJW'),('CGO','XIY'),('CGO','HFE'),('CGO','TYN'),('CGO','WUH'),('CGO','NKG'),
                        ('XIY','INC'),('XIY','LHW'),('CTU','XIY'),('XIY','TYN'),('XIY','SJW'),('XIY','WUH'),
                        ('WUH','HFE'),('WUH','NKG'),('NKG','HFE'),('WUH','CSX'),('WUH','HGH'),('WUH','KHN'),
                        ('NKG','WUX'),('NKG','CZX'),('NKG','NTG'),('NKG','YTY'),('NKG','SHA'),('NKG','HGH'),
                        ('SHA','HGH'),('SHA','WUX'),('SHA','NTG'),('SHA','CZX'),('SHA','YTY'),('HGH','WUX'),
                        ('HGH','CZX'),('HGH','NTG'),('HGH','YTY'),('WUX','CZX'),('WUX','NTG'),('WUX','YTY'),
                        ('CZX','NTG'),('CZX','YTY'),('NTG','YTY'),('SHA','HFE'),('HGH','HFE'),('HFE','CZX'),
                        ('HFE','WUX'),('HFE','YTY'),('HFE','NTG'),('WUH','CZX'),('WUH','WUX'),('WUH','NTG'),
                        ('WUH','YTY'),('KHN','CSX'),('KHN','HGH'),('KHN','FOC'),('KHN','XMN'),('KHN','KWE'),
                        ('CSX','CAN'),('CSX','NNG'),('CSX','FOC'),('CSX','XMN'),('HGH','FOC'),('HGH','XMN'),
                        ('CAN','SZX'),('CAN','ZUH'),('ZUH','SZX'),('CAN','SWA'),('ZUH','SWA'),('SZX','SWA'),
                        ('SWA','FOC'),('SWA','XMN'),('CAN','NNG'),('FOC','NNG'),('KWE','NNG'),('KWE','KMG'),
                        ('KMG','NNG'),('KWE','CTU'),('KWE','CSX'),('CKG','KWE'),('CTU','CKG'),('CKG','XIY'),
                        ('LHW','XNN'),('XNN','INC'),('INC','LHW'),('HET','INC'),('HET','TYN'),('HET','SJW'),
                        ('JJN','XMN'),('JJN','FOC'),('JJN','ZHA'),('SZX','JJN'),('SWA','ZHA'),('FOC','ZHA'),
                        ('HAK','SYX'),('HRB','HLD'),('SZX','ZHA'),('FOC','SYX'),('FOC','SZX'),('FOC','XMN')}
        if self.ignore_threshold >= 3:
            ignoreExt = {('LXA','ZHA'),('LXA','SZX'),('LXA','JJN'),('CTU','SWA'),('SHA','LXA'),('TSN','LXA'),
                        ('LXA','XMN'),('LXA','CZX'),('LXA','WUX'),('LXA','HLD'),('LXA','JHG'),('LXA','SWA'),
                        ('LXA','TAO'),('LXA','DLC'),('LXA','SYX'),('LXA','HAK'),('LXA','FOC'),('LXA','JJN'),
                        ('JHG','CZX'),('JHG','WUX'),('JHG','XMN'),('JHG','JJN'),('JHG','HRB'),('JHG','ZHA'),
                        ('JHG','SWA'),('JHG','SYX'),('JHG','HLD'),('JHG','URC'),('JHG','TAO'),('JHG','DLC'),
                        ('HLD','KMG'),('WUX','LHW'),('XMN','ZHA'),('WUH','JHG'),('TAO','JJN'),('TSN','ZHA'),
                        ('HRB','WUX'),('ZHA','HAK'),('XIY','SWA'),('CTU','ZHA'),('LHW','JJN'),('TAO','CZX'),
                        ('WUX','XMN'),('CZX','CGO'),('HLD','SHA'),('WUH','JJN'),('JHG','SZX'),('HLD','LHW'),
                        ('TSN','SWA'),('CGO','ZHA'),('CZX','SYX'),('TSN','NKG'),('LHW','SYX'),('HGH','SWA'),
                        ('HLD','DLC'),('URC','LXA'),('TSN','CGO'),('WUX','SWA'),('HLD','XMN'),('XMN','SYX'),
                        ('HLD','FOC'),('CGO','SWA'),('HLD','ZHA'),('HRB','JJN'),('DLC','ZHA'),('HLD','HGH'),
                        ('HLD','XIY'),('XIY','ZHA'),('WUX','HAK'),('CKG','JHG'),('HLD','SWA'),('HGH','LXA'),
                        ('HLD','WUH'),('HLD','NKG'),('DLC','SWA'),('JHG','LHW'),('URC','FOC'),('NKG','ZHA'),
                        ('HLD','CAN'),('TSN','CZX'),('SWA','HAK'),('CZX','JJN'),('URC','ZHA'),('ZHA','SYX'),
                        ('HLD','CGO'),('WUX','FOC'),('CKG','LHW'),('LXA','CAN'),('WUH','LHW'),('WUX','ZHA'),
                        ('TAO','FOC'),('HLD','HAK'),('CTU','JHG'),('CZX','CKG'),('TAO','ZHA'),('JJN','SYX'),
                        ('NKG','SWA'),('BJS','HLD'),('BJS','CZX'),('WUX','XIY'),('URC','SWA'),('NKG','LXA'),
                        ('BJS','JHG'),('JHG','XIY'),('NKG','JHG'),('XMN','SZX'),('TAO','SWA'),('CGO','LXA'),
                        ('TSN','SYX'),('HGH','JJN'),('HRB','LHW'),('CZX','KMG'),('HLD','URC'),('HLD','TAO'),
                        ('DLC','CZX'),('WUX','CGO'),('JHG','CAN'),('DLC','URC'),('TSN','WUX'),('LHW','SWA'),
                        ('URC','JJN'),('HRB','DLC'),('WUH','SWA'),('LHW','LXA'),('WUH','LXA'),('JHG','HAK'),
                        ('HRB','ZHA'),('SWA','SYX'),('CZX','LHW'),('TSN','JHG'),('LHW','HAK'),('KMG','ZHA'),
                        ('HLD','TSN'),('XIY','JJN'),('FOC','HAK'),('JHG','FOC'),('HLD','CKG'),('HLD','SYX'),
                        ('HLD','SZX'),('HRB','SWA'),('WUX','URC'),('DLC','SYX'),('CZX','XMN'),('CZX','FOC'),
                        ('HRB','LXA'),('TSN','JJN'),('TAO','URC'),('TSN','LHW'),('CZX','ZHA'),('HLD','WUX'),
                        ('CGO','JHG'),('LHW','ZHA'),('DLC','WUX'),('CKG','ZHA'),('WUH','ZHA'),('HLD','CTU'),
                        ('CZX','XIY'),('WUX','JJN'),('HLD','CZX'),('CZX','SWA'),('JJN','SWA'),('URC','SYX'),
                        ('WUX','SYX'),('HGH','ZHA'),('HLD','JJN'),('CZX','HAK'),('HRB','URC'),('CZX','URC'),
                        ('DLC','JJN'),('DLC','LHW'),('JJN','HAK'),('TAO','WUX'),('BJS','ZHA'),}
            ignoreSet = ignoreSet.union(ignoreExt)
  
        skipSet = set()
        if self.ignore_cities is not None and isinstance(self.ignore_cities, set):
            ignoreSet = ignoreSet.union(self.ignore_cities, ignoreSet)
        for i in range(self.__codesum):
            for j in range(i, self.__codesum):
                if i == j:
                    continue
                if (self.cityList[i], self.cityList[j]) in ignoreSet or (self.cityList[j], self.cityList[i]) in ignoreSet or self.cityList[i] == self.cityList[j]:
                    # If the city tuple is the same or found in the set, it shouldn't be processed.
                    skipSet.add((i, j))
        self.__total -= self.days * len(skipSet)
        return skipSet

    @staticmethod
    def exits(code: int = 0) -> None:
        '''Exit program with a massage'''
        import sys
        errorCode = {0: 'reaching exit point', 1: 'empty or incorrect data', 2: 'city tuple error',
                     3:'day limit error', 4: 'no flight', -1: 'Unknown error'}
        print(f' Exited for {errorCode[code]}')
        sys.exit()

    @property
    def proxy(self) -> dict | None:
        '''Get a random proxy from Proxy Pool'''
        try:
            with get('http://127.0.0.1:5555/random') as proxy:
                proxy = {"http": "http://" + proxy.text.strip()}
        except:
            proxy = None
            print('\tNo porxy warn', end='')
            time.sleep((round(3 * random(), 2)))
        finally:
            return proxy


    def collector(self, flightDate: datetime.date, dcity: str, acity: str) -> list():
        datarows = list()
        dcityname = self.__airportCity.get(dcity, None)
        acityname = self.__airportCity.get(acity, None)
        dow = self.__dayOfWeek[flightDate.isoweekday()]
        self.header["User-Agent"] =  self.__userAgents[int(len(self.__userAgents) * random())]
        self.header["Referer"] = "https://flights.ctrip.com/itinerary/oneway/" + acity + '-' + dcity
        self.payload["airportParams"] = [{"dcity": dcity, "acity": acity, "dcityname": dcityname,
                                          "acityname": acityname, "date": flightDate.isoformat(), "dcityid": 1, "acityid": 2}]

        try:
            response = post(self.url, data = dumps(self.payload), headers = self.header, proxies = self.proxy)   # -> json()
            routeList = loads(response.text).get('data').get('routeList')   # -> list
            response.close
            #print(routeList)
        except:
            try:
                response.close
            finally:
                return datarows
        if routeList is None:   # No data, ignore these flights in the future.
            return datarows

        d_multiairport = True if dcityname == '北京' or dcityname == '上海' or dcityname== '成都' else False
        a_multiairport = True if acityname == '北京' or acityname == '上海' or acityname== '成都' else False
        try:
            for route in routeList:
                legs = route.get('legs')
                if len(legs) == 1: # Flights that need to transfer is ignored.
                    #print(legs,end='\n\n')
                    flight = legs[0].get('flight')
                    if flight.get('sharedFlightNumber'):
                        continue    # Shared flights not collected
                    airlineName = flight.get('airlineName')
                    if '旗下' in airlineName:   # Airline name should be as simple as possible
                        airlineName = airlineName.split('旗下', 1)[1]
                    departureTime = datetime.time().fromisoformat(flight.get('departureDate').split(' ', 1)[1])  # Convert the time string to a time class
                    arrivalTime = datetime.time().fromisoformat(flight.get('arrivalDate').split(' ', 1)[1])  # Convert the time string to a time class
                    if d_multiairport:
                        departureName = flight.get('departureAirportInfo').get('airportName')
                        departureName = dcityname + match('成?都?(.*?)国?际?机场', departureName).groups()[0]
                    elif dcityname: # If dcityname exists, that means the code-name is in the default code-name dict
                        departureName = dcityname   # Multi-airport cities need the airport name while others do not
                    else:   # If dcityname is None, that means the code-name is not in the default code-name dict
                        departureName = flight.get('departureAirportInfo').get('cityName')
                        self.__airportCity[dcity] = departureName  # ...therefore it is added now 
                    if a_multiairport:
                        arrivalName = flight.get('arrivalAirportInfo').get('airportName')
                        arrivalName = acityname + match('成?都?(.*?)国?际?机场', arrivalName).groups()[0]
                    elif acityname:
                        arrivalName = acityname
                    else:
                        arrivalName = flight.get('arrivalAirportInfo').get('cityName')
                        self.__airportCity[acity] = arrivalName
                    craftType = flight.get('craftTypeKindDisplayName').strip('型')
                    ticket = legs[0].get('cabins')[0]   # Price info in cabins dict
                    price = ticket.get('price').get('price')
                    rate = ticket.get('price').get('rate')
                    datarows.append([flightDate, dow, airlineName, craftType, departureName, arrivalName, 
                                    departureTime, arrivalTime, price, rate, ])
                    #日期，星期，航司，机型，出发机场，到达机场，出发时间，到达时间，价格，折扣
        except:
            return list()
        return datarows


    def show_progress(self, dcity: str, acity: str, collectDate: datetime.date) -> float:
        '''Progress indicator with a current time (float) return'''
        print('\r{}% >> '.format(int(self.__idct / self.__total * 100)), end='')
        m, s = divmod(int((self.__total - self.__idct) * self.__avgTime), 60)
        h, m = divmod(m, 60)    #show est. remaining process time: eta
        print('eta {0:02d}:{1:02d}:{2:02d} >> '.format(h, m, s), end='')
        print(dcity + '-' + acity + ': ' + collectDate.isoformat(), end='')   #current processing flights
        return time.time()

    @staticmethod
    def output_excel(datarows: list, dcity: str, acity: str, path: Path = Path(), values_only: bool = False, with_return: bool = True) -> bool:
        wbook = openpyxl.Workbook()
        wsheet = wbook.active
        wsheet.append(('日期', '星期', '航司', '机型', '出发机场', '到达机场', '出发时', '到达时', '价格', '折扣'))
        
        if values_only:
            for data in datarows:
                wsheet.append(data)
        else:
            wsheet.column_dimensions['A'].width = 11
            wsheet.column_dimensions['B'].width = 7
            wsheet.column_dimensions['C'].width = 12
            wsheet.column_dimensions['G'].width = wsheet.column_dimensions['H'].width = 7.5
            wsheet.column_dimensions['D'].width = wsheet.column_dimensions['I'].width = wsheet.column_dimensions['J'].width = 6
            for row in wsheet.iter_rows(1, 1, 1, 10):
                for cell in row:
                    cell.alignment = Alignment(vertical = 'center', horizontal = 'center')
                    cell.font = Font(bold = True)
            
            for data in datarows:
                row = []
                for item in data:   # Put value
                    row.append(Cell(worksheet = wsheet, value = item))
                for i in range(2, 8):
                    row[i].alignment = Alignment(vertical='center',horizontal='center') # Adjust alignment
                row[6].number_format = row[7].number_format = 'HH:MM'  # Adjust the dep time and arr time formats
                row[9].number_format = '0%' # Make the rate show as percentage
                wsheet.append(row)

        if with_return:
            wbook.save(path / f'{dcity}~{acity}.xlsx')
        else:
            wbook.save(path / f'{dcity}-{acity}.xlsx')
        wbook.close
        return values_only


    def output_new_ignorance(self, ignoreNew: set = set()) -> bool:
        if len(ignoreNew) > 0:
            with open('CityTuples_FlightsLessThan{}.txt'.format(self.ignore_threshold), 'a', encoding = 'UTF-8') as updates:
                updates.write(str(ignoreNew) + '\n')
            return True
        else:
            return False


    def run(self, with_output: bool = True, **kwargs) -> Generator:
        '''Collect all data, output and yield data of city tuple flights collected in list.'''
        print('\rGetting data...')
        skipSet = self.skip
        filesum = 0
        if with_output:
            path: Path = kwargs.get('path', Path())
            values_only: bool = kwargs.get('values_only', False)
        else:
            path = Path()

        for dcity in range(self.__codesum):
            for acity in range(dcity,self.__codesum):
                if acity == dcity:
                    continue    # Same city tuple should not be processed.
                if Path(path / f'{self.cityList[dcity]}~{self.cityList[acity]}.xlsx').exists():
                    print(f'{self.cityList[dcity]}-{self.cityList[acity]} already collected, skip')
                    self.__total -= self.days
                    continue    # Already processed.
                if (dcity, acity) not in skipSet:   # If the city tuple key / coordinate is not found, process.
                    collectDate = self.flightDate   #reset
                    datarows = []
                    ignoreNew = set()
                    for i in range(self.days):
                        dcityname = self.cityList[dcity]
                        acityname = self.cityList[acity]
                        currTime = self.show_progress(dcityname, acityname, collectDate)

                        '''Get OUTbound flights data, 3 attempts for ample data'''
                        for j in range(3):
                            dataLen = len(datarows)
                            datarows.extend(self.collector(collectDate, dcityname, acityname))
                            if len(datarows) - dataLen >= self.ignore_threshold:
                                break
                            elif i != 0 and len(datarows) - dataLen > 0:
                                break
                        else:
                            if i == 0 and len(datarows) < self.ignore_threshold:
                                self.__total -= self.days # In the first round, ignore the cities whose flight data is less than 3.
                                print(' ...ignored')
                                ignoreNew.add((dcityname, acityname))
                                break

                        '''Get INbound flights data, 3 attempts for ample data'''
                        if self.with_return:
                            for j in range(3):
                                dataLen = len(datarows)
                                datarows.extend(self.collector(collectDate, acityname, dcityname))
                                if len(datarows) - dataLen >= self.ignore_threshold:
                                    break
                                elif i != 0 and len(datarows) - dataLen > 0:
                                    break
                            else:
                                if i == 0 and len(datarows) - dataLen < self.ignore_threshold:
                                    self.__total -= self.days # In the first round, ignore the cities whose flight data is less than 3.
                                    print(' ...ignored')
                                    ignoreNew.add((acityname, dcityname))
                                    break

                        collectDate = collectDate.fromordinal(collectDate.toordinal() + 1)    #one day forward
                        self.__idct += 1
                        self.__avgTime = (time.time() - currTime + self.__avgTime * (self.__total - 1)) / self.__total
                    else:
                        if with_output:
                            print(f'\r{dcityname}-{acityname} generated', end = '') 
                            print('!                         ') if self.output_excel(datarows, dcityname, acityname, path, values_only, self.with_return) else print(' and formatted!           ')
                            filesum += 1
                        else:
                            print(f'\r{dcityname}-{acityname} collected!                         ') 
                        yield datarows

        if with_output:
            if self.output_new_ignorance(ignoreNew):
                print('Ignorance set updated, ', end = '')
            print(filesum, 'new files in', path.name) if filesum > 1 else print(filesum, 'new file in', path.name)


if __name__ == "__main__":

    # 务必先设置代理: Docker Desktop / cmd -> cd ProxyPool -> docker-compose up -> (idle) -> start

    # 初始化
    print('Initializing...', end='')
    
    # 文件夹名设置为当前日期
    #path = Path('debugging')   #测试用例
    path = Path(str(datetime.datetime.now().date()))
    if not path.exists():
        Path.mkdir(path)

    # 城市列表，处理表中各城市对的航班（第一天少于3个则忽略），分类有: 华北+东北、华东、西南、西北+新疆、中南
    cities = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]
    
    # 忽略阈值，低于该值则不统计航班，0为都爬取并统计
    ignore_threshold = 3
    ignore_cities = None

    # 航班爬取: 机场三字码列表、起始年月日、往后天数
    # 其他参数: 提前天数限制、手动忽略集、忽略阈值 -> 暂不爬取共享航班与经停 / 转机航班数据、是否双向爬取
    # 运行参数：是否输出文件（否：生成列表）、存储路径、是否带格式
    crawler = CtripCrawler(cities, datetime.date(2022,2,17), 30, 0, ignore_cities, ignore_threshold)
    #crawler = CtripCrawler(['NKG','CKG','CTU'], datetime.date(2022,2,20), 2, 0, ignore_cities, ignore_threshold, False)
    for data in crawler.run(path = path):
        pass
    else:
        print(' - - - COMPLETE AND EXIT - - - ')
