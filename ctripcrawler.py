__all__ = ('CtripCrawler', 'CtripSearcher', 'ItineraryCollector')

from time import sleep
from datetime import datetime, date, time, timedelta
from urllib.parse import urlencode
from pandas import DataFrame, concat, read_csv
from requests import get, post
from requests.exceptions import RequestException, Timeout, JSONDecodeError
from json import dumps
from hashlib import md5
from numpy.random import random, seed
from random import choice
from sys import exit
from typing import Callable, Generator, Iterable, Literal
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.cell import Cell
from pathlib import Path
from civilaviation import Airport, Route

class CtripCrawler():
    """
    Ctrip flight tickets crawler
    =====
    Get flight data from API: https://flights.ctrip.com/itinerary/api/12808/products
    
    Parameters
    -----
    - `targets`: All routes / cities to be collected
    - `flight_date`: The starting date of collection (allow past dates), default: `date.today() + timedelta(1)` == tomorrow
    - `days`: The number of days to be collected - date range: [flight_date, flight_date + days), default: 1
    - `day_limit`: Maximum days advanced of flights - flight_date + days_maximum <= flight_date + day_limit, default: `0` == no limits
    - `ignore_routes`: Routes to be ignored, default: `set()`
    - `ignore_threshold`: Routes whose flights are less than this value are not collected and noted, default: `3`
    - `with_return`: Collect return flights, default: `True`
    
    Methods
    -----
    - `run`: Start the crawler in an order of itinerary (each route and each flight date)
    - `proxy`: Return a proxy dict by the pre-set proxy parameter or ProxyPool
    
    See Also
    -----
    - `CtripSearcher`: Batch search method (Another API)
    - `ItineraryCollector`: Collect data by random itineraries
    
    Examples
    -----
    构建城市列表, 支持输入IATA/ICAO代码或城市名称; 亦可输入 Route / Airport 类: 北京, 南京, 上海之间航线
    >>> targets = ['BJS', 'NKG', 'SHA']

    设置起始爬取日期: 从今天开始 (今日将跳过)
    >>> from datetime import date
    >>> flight_date = date.today()
    
    设置爬取天数: 7天
    >>> days = 7
    
    设置最多爬取天数 (防止爬取的航班出发日期过远): 无限制 (0)
    >>> day_limit = 0
    
    设置忽略阈值, 低于该值则不统计航班, 0为都爬取并统计: 忽略3条及以下
    >>> ignore_threshold = 3
    
    设置忽略的往返航线, 可用Route或tuple表示: 北京-上海航线
    >>> ignore_routes = set(('BJS', 'SHA'))

    设置是否爬取返程: 是
    >>> with_return = True

    构建爬虫
    >>> from flycheap import CtripCrawler
    >>> crawler = CtripCrawler(targets, flight_date, days, day_limit, 
    ...     ignore_routes, ignore_threshold, with_return)

    爬虫输出标题行
    >>> title = ['出发日期', '星期', '航司', '机型', '出发', '到达', '出发时刻', '到达时刻', '价格', '折扣']

    运行爬虫
    >>> from pandas import DataFrame
    >>> for data in crawler.run():
    ...     DataFrame(data, columns = title).assign(**{'收集日期': date.today()})
    """
    
    url = "https://flights.ctrip.com/itinerary/api/12808/products"
    header = {
        "Content-Type": "application/json;charset=utf-8", 
        "Accept": "application/json", 
        "Accept-Language": "zh-cn", 
        "Origin": "https://flights.ctrip.com", 
        "Referer": "https://flights.ctrip.com/international/search/domestic", }
    payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1}
    day_week = {1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六', 7:'星期日'}
    ua = [
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
        'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0']
    
    def __init__(
        self, 
        targets: Iterable[str | Airport | Route], 
        flight_date: date | tuple = date.today() + timedelta(1), 
        days: int = 1, 
        day_limit: int = 0, 
        ignore_routes: set = set(), 
        ignore_threshold: int = 3, 
        with_return: bool = True, ) -> None:

        self.routes, cities = [], []
        for item in targets:
            if isinstance(item, str):
                cities.append(Airport(item))
            elif isinstance(item, Airport):
                cities.append(item)
            elif isinstance(item, Route):
                if not ((ignore_threshold >= 3 and item.islow()) or item.isinactive() or \
                    item in ignore_routes or item.returns in ignore_routes):
                    self.routes.append(item)
            else:
                raise TypeError('Support city inputs: String(ICAO, IATA, City name), Airport, Route')
        for dep in cities:
            for arr in cities:
                if not dep == arr:
                    _oneway = Route(dep, arr)
                    _return = Route(arr, dep)
                    if not ((ignore_threshold >= 3 and _oneway.islow()) or _oneway.isinactive() or \
                        _oneway.separates('code') in ignore_routes or _return in self.routes or \
                        _return.separates('code') in ignore_routes):
                        self.routes.append(_oneway)
        del cities
        self.routes: list[Route]
        self.total = len(self.routes)
        if not self.total:
            raise IndexError('No valid routes!')

        self.days = days
        self.flight_date = flight_date if isinstance(flight_date, date) else \
            date(*flight_date) if isinstance(flight_date, tuple) else (date.today() + timedelta (1))
        self.first_date = self.flight_date.isoformat()

        '''Day range preprocess'''
        curr_date = date.today()
        if curr_date >= self.flight_date:
            # If collect day is behind today, change the beginning date and days of collect.
            self.__threshold = 0
            self.days -= (curr_date - self.flight_date).days + 1
            self.flight_date = curr_date + timedelta(1)
            if day_limit > 0 and self.days > day_limit:
                # If there's a limit for days in advance, change the days of collect.
                self.days = day_limit
        else:
            self.__threshold = ignore_threshold
            total = (self.flight_date - curr_date).days + self.days
            if day_limit > 0 and total > day_limit:
                # If there's a limit for days in advance, change the days of collect.
                self.days -= total - day_limit
        if self.days < 0:
            raise ValueError(f'{curr_date} + {self.days} days exceeds {flight_date}')

        self.warn = self.idct = 0
        self.avg = 2.9 if with_return else 1.3
        self.with_return = with_return
        self.limits = self.__threshold if self.__threshold else 1
        self.file = None

    @staticmethod
    def proxy(key: Literal['proxypool'] | str | Iterable[str] | int = None) -> dict | None:
        '''Get a random proxy from either proxylist or proxypool'''
        if isinstance(key, str):
            for _ in range(3):
                try:
                    with get('http://127.0.0.1:5555/random' if key.lower() == 'proxypool' \
                        else key, timeout = 3) as proxy:
                        proxy = proxy.text.strip()
                    if len(proxy):
                        return {"http": "http://" + proxy}
                except:
                    continue
            else:
                print(' ERROR: no proxy pool detected', end = '')
                return sleep(3 * random())
        elif isinstance(key, Iterable):
            return {"http": choice(key)}
        elif isinstance(key, (int, float)):
            return sleep(key * random())
        else:
            return None


    @staticmethod
    def referers(route: Route) -> str:
        rand = 10 * random()
        if rand > 5:
            dates = date.today() + timedelta(int(30 * random()))
            route = route.returns if random() > 0.5 else route
            if rand > 8:
                return "https://flights.ctrip.com/online/channel/domestic"
            elif rand > 6:
                return f"https://flights.ctrip.com/online/list/oneway-{route.format()}?depdate={dates}"
            else:
                return "https://www.ctrip.com/"
        else:
            query = f"{route.dep.city} {route.arr.city} 机票" if random() > 0.5 else f"{route.dep.city}到{route.arr.city}机票"
            if rand > 4:
                return "https://cn.bing.com/search?" + urlencode({"q": query})
            elif rand > 3:
                return "https://www.sogou.com/web?" + urlencode({"query": query})
            elif rand > 2:
                return "https://www.so.com/s?" + urlencode({"ie": "utf8", "q": query})
            elif rand > 1:
                return "https://www.baidu.com/s?" + urlencode({"wd": query})
            else:
                return "https://www.sogou.com/tx?" + urlencode({"ie": "utf8", "query": query})


    def collector(self, flight_date: date, route: Route, proxy) -> tuple[tuple, list[list]]:
        '''Web crawler main'''
        datarows = list()
        dcity, acity = route.separates('code')
        departureName, arrivalName = route.separates('city')
        header, payload = self.header, self.payload
        dow = self.day_week[flight_date.isoweekday()]
        header["User-Agent"] = choice(self.ua)
        header["Referer"] = self.referers(route if random() > 0.3 else Route.random())
        payload["airportParams"] = [{"dcity": dcity, "acity": acity, "dcityname": departureName,
                                     "acityname": arrivalName, "date": flight_date.isoformat()}]

        try:
            proxy = proxy() if isinstance(proxy, Callable) else self.proxy(proxy)
            response = post(
                self.url, data = dumps(payload), headers = header, proxies = proxy, timeout = 10)
            code, url = response.status_code, response.url
            data = response.json().get('data', {})
            response.close()
            flag = code, data.get('version', 'Unknown')
            routeList = data.get('routeList')
            if not isinstance(routeList, list):
                routeList = []
            for routes in routeList:
                legs = routes.get('legs')
                try:
                    if len(legs) == 1: # Flights that need to transfer is ignored.
                        #print(legs,end='\n\n')
                        flight = legs[0].get('flight')
                        if flight.get('sharedFlightNumber'):
                            continue    # Shared flights not collected
                        airlineName = flight.get('airlineName')
                        if '旗下' in airlineName:   # Airline name should be as simple as possible
                            airlineName = airlineName.split('旗下', 1)[1]
                        departureTime = time.fromisoformat(flight.get('departureDate').split(' ', 1)[1])
                        arrivalTime = time.fromisoformat(flight.get('arrivalDate').split(' ', 1)[1])
                        if route.dep.multi:  # Multi-airport cities need the airport name while others do not
                            departureName = route.dep.city + \
                                flight.get('departureAirportInfo').get('airportName').strip('成都')[:2]
                        if route.arr.multi:
                            arrivalName = route.arr.city + \
                                flight.get('arrivalAirportInfo').get('airportName').strip('成都')[:2]
                        craftType = flight.get('craftTypeKindDisplayName')
                        craftType = craftType.strip('型') if craftType else "中"
                        ticket = legs[0].get('cabins')[0]   # Price info in cabins dict
                        price = ticket.get('price').get('price')
                        rate = ticket.get('price').get('rate')
                        datarows.append([
                            flight_date, dow, airlineName, craftType, departureName, 
                            arrivalName, departureTime, arrivalTime, price, rate])
                except Exception as error:
                    print(f"  WARN: {error} in {dcity}-{acity} {flight_date.strftime('%m/%d')}")
                    self.warn += 1
            if len(datarows):
                datarows.sort(key = lambda x: x[6])
        except JSONDecodeError:
            response.close()
            flag = code, 'Not a json response ' + url if url != self.url else ''
        except RequestException or Timeout:
            flag = 0, 'Timeout'
        except Exception as error:
            flag = code if 'code' in dir() else 0, error
        finally:
            return flag, datarows


    def show_progress(self, flight_date: date, route: Route) -> float:
        '''Progress indicator with a current time (float) return'''
        m, s = divmod(int((self.total - self.idct) * self.avg), 60)
        h, m = divmod(m, 60)
        print(f"\r{route.format()} {flight_date.strftime('%m/%d')} >> eta {h:02d}:{m:02d}:{s:02d} >> ", 
              end = f'{int(self.idct / self.total * 100):03d}%')
        return datetime.now().timestamp()

    @staticmethod
    def output_excel(datarows: list, dcity: str, acity: str, path: Path = Path(), 
                     values_only: bool = False, with_return: bool = True) -> Path:
        wbook = Workbook()
        wsheet = wbook.active
        wsheet.append(('日期', '星期', '航司', '机型', '出发机场', '到达机场', \
            '出发时', '到达时', '价格', '折扣'))
        
        if values_only:
            for data in datarows:
                wsheet.append(data)
        else:
            wsheet.column_dimensions['A'].width = 11
            wsheet.column_dimensions['B'].width = 7
            wsheet.column_dimensions['C'].width = 12
            wsheet.column_dimensions['G'].width = wsheet.column_dimensions['H'].width = 7.5
            wsheet.column_dimensions['D'].width = wsheet.column_dimensions['I'].width = \
                wsheet.column_dimensions['J'].width = 6
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
                row[6].number_format = row[7].number_format = 'HH:MM'  # Adjust time formats
                row[9].number_format = '0%' # Make the rate show as percentage
                wsheet.append(row)

        file = Path(path / f'{dcity}~{acity}.xlsx') if with_return else Path(path / f'{dcity}-{acity}.xlsx')
        wbook.save(file)
        wbook.close
        return file


    def run(self, with_output: bool = True, **kwargs) -> Generator:
        '''
        Collect all data, output and yield data of city tuple flights collected in list.
        
        Output Parameters
        -----
        - Store data or generate list? 
            - with_output: `bool`, default: `True`
        - Where to store? 
            - path: `Path` | `str`, default: `Path("First Flight Date" / "Current Date")`
        - With format or not?
            - values_only: `bool`, default: `False`
        
        Collect Parameters
        -----
        - Parts of data collection, for multi-threading.
            - parts: `int`, the total number of parts, default: `0`
            - part: `int`, the index of the running part, default: `0`
            - reverse: `bool`, reverse collecting order, default: `False`
        - In case of city with few flights...
            - attempt: `int`, the number of attempt to get ample data, default: `3`
            - antiempty: `int`, skip output few flights in the last flight days, default: `0`
            - noretry: `list`, routes connecting the city has no retry, default: `list()`
        
        File Detection Parameters
        -----
        - overwrite: `bool`, collect and overwrite existing files, default: `False`
        - nopreskip: `bool`, keep the orignal collect route without detection, default: `False`
        
        Set Proxy
        -----
        - proxy: `Callable[[], dict[str, str]]`, a function that returns proxy in dict (used by requests)
        - proxy: `Literal['proxypool']`, using default API of ProxyPool (https://github.com/Python3WebSpider/ProxyPool) as proxy
        - proxy: `str`, other proxy pool API that returns a proxy url each time (like default API of ProxyPool)
        - proxy: `Iterable[str]`, list of proxy urls
        - proxy: `int` | 'float', random sleep time within this seconds
        '''
        files = 0
        __ignores = set()

        '''Initialize running parameters'''
        path = Path(kwargs.get('path', Path(self.first_date) / Path(date.today().isoformat())))
        path.mkdir(parents = True, exist_ok = True)
        values_only: bool = kwargs.get('values_only', False)
        parts: int = kwargs.get('parts', 1)
        part: int = kwargs.get('part', 1)
        overwrite: bool = kwargs.get('overwrite', False)
        noretry: list = kwargs.get('noretry', [])
        attempt: int = kwargs.get('attempt', 3) if kwargs.get('attempt', 3) > 1 else 1
        antiempty: int = kwargs.get('antiempty') if kwargs.get('antiempty', 0) >= 1 else 0
        proxy = kwargs['proxy'] if isinstance(kwargs.get('proxy'), (Callable, Iterable, int, float)) else None

        '''Part separates'''
        if overwrite or kwargs.get('nopreskip'):
            routes = self.routes
        else:
            routes = []
            for route in self.routes:
                exist = Path(path / f'{route.dep.code}~{route.arr.code}.xlsx').exists() or \
                    Path(path / f'{route.arr.code}~{route.dep.code}.xlsx').exists() or \
                    Path(path / f'{route.dep.code}-{route.arr.code}.xlsx').exists()
                if not exist:
                    routes.append(route)
        try:
            if part > 0 and parts > 1:
                part_len = int(len(routes) / parts)
                routes = routes[(parts - 1) * part_len : ] if part >= parts \
                    else routes[(part - 1) * part_len : part * part_len]
        finally:
            if kwargs.get('reverse'):
                routes.reverse()
            self.total = len(routes) * self.days
        dates = list((self.flight_date + timedelta(i)) for i in range(self.days))

        '''Data collecting controller'''
        for route in routes:
            dep, arr = route.separates('code')
            exist = Path(path / f'{dep}~{arr}.xlsx').exists() or \
                Path(path / f'{dep}-{arr}.xlsx').exists() or \
                Path(path / f'{arr}~{dep}.xlsx').exists()
            if not overwrite and exist:
                print(f'{dep}-{arr} already collected, skip')
                self.total -= self.days
                continue    # Already processed.
            last_date = self.flight_date   #reset
            datarows = []
            for collect_date in dates:
                curr = self.show_progress(collect_date, route)

                '''Get OUTbound flights data, attempts for ample data'''
                for _ in range(attempt):
                    flag, datarow = self.collector(collect_date, route, proxy)
                    while flag[1] != 'V2':
                        if flag[1] == 'Timeout' or flag[0] != 200:
                            print(f'  ...timeout, code: {flag[0]}', end = '')
                            sleep(5)
                        else:
                            try:
                                print('  WARN: code {0} [200], {1} [V2]'.format(*flag))
                                input('\r\nContinue (Any) / Exit (*nix: Ctrl-D, Windows: Ctrl-Z+Return): ')
                            except EOFError:
                                exit(0)
                        curr = datetime.now().timestamp()
                        flag, datarow = self.collector(collect_date, route, proxy)
                    if len(datarow) >= self.limits or (collect_date != self.flight_date and len(datarow)):
                        if collect_date > last_date:
                            last_date = collect_date
                        datarows.extend(datarow)
                        break
                    elif dep in noretry or arr in noretry:
                        print(f' ...few data in {dep}-{arr} ', 
                                end = collect_date.strftime('%m/%d'))
                        break
                else:
                    if collect_date == self.flight_date and len(datarow) < self.__threshold:
                        self.total -= self.days
                        print(f'\r{dep}-{arr} has {len(datarow)} flight(s), ignored. ')
                        __ignores.add((dep, arr))
                        break
                    elif len(datarow) < self.limits:
                        print(f'  WARN: few data in {dep}-{arr} ', 
                              end = collect_date.strftime('%m/%d'))
                        self.warn += 1

                '''Get INbound flights data, attempts for ample data'''
                if self.with_return:
                    for _ in range(attempt):
                        flag, datarow = self.collector(collect_date, route.returns, proxy)
                        while flag[1] != 'V2':
                            if flag[1] == 'Timeout' or flag[0] != 200:
                                print(f'  ...timeout, code: {flag[0]}', end = '')
                                sleep(5)
                            else:
                                try:
                                    print('  WARN: code {0} [200], {1} [V2]'.format(*flag))
                                    input('\r\nContinue (Any) / Exit (*nix: Ctrl-D, Windows: Ctrl-Z+Return): ')
                                except EOFError:
                                    exit(0)
                            curr = datetime.now().timestamp()
                            flag, datarow = self.collector(collect_date, route, proxy)
                        if len(datarow) >= self.limits or (collect_date != self.flight_date and len(datarow) > 0):
                            if collect_date > last_date:
                                last_date = collect_date 
                            datarows.extend(datarow)
                            break
                        elif dep in noretry or arr in noretry:
                            print(f' ...few data in {arr}-{dep} ', 
                                  end = collect_date.strftime('%m/%d'))
                            break
                    else:
                        if collect_date == self.flight_date and len(datarow) < self.__threshold:
                            self.total -= self.days
                            print(f'\r{arr}-{dep} has {len(datarow)} flight(s), ignored. ')
                            __ignores.add((arr, dep))
                            break
                        elif len(datarow) < self.limits:
                            print(f'  WARN: few data in {arr}-{dep} ', 
                                  end = collect_date.strftime('%m/%d'))
                            self.warn += 1

                self.idct += 1
                self.avg = (datetime.now().timestamp() - curr + self.avg \
                    * (self.total - 1)) / self.total
            else:
                antiflag = last_date + timedelta(antiempty) >= collect_date if antiempty else True
                msg = f'\r{dep}-{arr} '
                if len(datarows) and with_output and antiflag:
                    self.file = self.output_excel(datarows, dep, arr, path, values_only, self.with_return)
                    yield datarows
                    print(msg + 'collected' + ('!               ' if values_only else ' and formatted! '))
                    files += 1
                elif len(datarows) and antiflag:
                    yield datarows
                    print(msg + 'generated!               ')
                elif len(datarows) and not antiflag:
                    print(msg + 'WARN: output disabled, code: {0}, version: {1}'.format(*flag))
                    self.warn += 1
                else:
                    print(msg + 'WARN: no data, code: {0}, version: {1}'.format(*flag))
                    self.warn += 1

        if with_output:
            if len(__ignores) > 0:
                with open(f'IgnoredOrError_{self.__threshold}.txt', 'a') as updates:
                    updates.write(str(__ignores) + '\n')
                    print('Ignorance set updated, ', end = '')
            print(files, 'routes collected in', path.name) if files > 1 else \
                print(files, 'route collected in', path.name)
        print('Total warnings:', self.warn) if self.warn > 1 else \
            print('Total warning:', self.warn) if self.warn else print()
        self.warn = 0

class CtripSearcher(CtripCrawler):
    """
    Ctrip flight tickets crawler using batch search method.
    
    API: https://flights.ctrip.com/international/search/api/search/batchSearch
    
    Parameters see class `CtripCrawler`
    """
    def __init__(self, **kwargs) -> None:
        CtripCrawler.__init__(self, **kwargs)
        self.url = "https://flights.ctrip.com/international/search/api/search/batchSearch"
        self.header = {"origin": "https://flights.ctrip.com", 
                       "content-type": "application/json;charset=UTF-8"}

    @staticmethod
    def cookie() -> str:
        random_str = "abcdefghijklmnopqrstuvwxyz1234567890"
        random_id = ""
        for _ in range(6):
            random_id += choice(random_str)
        t = str(int(round(datetime.now().timestamp() * 1000)))
        return "_bfa={}".format(".".join(["1", t, random_id, "1", t, t, "1", "1"]))

    @staticmethod
    def sign(transaction_id: str, dep: str, arr: str, dates: str | date) -> str:
        sign_value = transaction_id + dep + arr + str(dates)
        _sign = md5()
        _sign.update(sign_value.encode('utf-8'))
        return _sign.hexdigest()

    @staticmethod
    def transaction_id(dep: str, arr: str, dates: str | date, proxy: dict = None) -> tuple[str, dict]:
        url = f"https://flights.ctrip.com/international/search/api/flightlist/oneway-{dep}-{arr}?_=1&depdate={dates}&cabin=y&containstax=1"
        response = get(url, proxies = proxy)
        if response.status_code != 200:
            print("  WARN: get transaction id failed, status code", response.status_code, end = '')
            return "", None
        try:
            data = response.json().get("data")
            response.close()
            return data["transactionID"], data
        except Exception as error:
            print("  WARN: get transaction id failed,", error, end = '')
            return "", None


    def collector(self, flight_date: date, route: Route, proxy) -> tuple[tuple, list[list]]:
        datarows = list()
        dcity, acity = route.separates('code')
        departureName, arrivalName = route.separates('city')
        dow = self.day_week[flight_date.isoweekday()]
        transaction_id, data = self.transaction_id(dcity, acity, flight_date, self.proxy())
        if transaction_id == "" or data is None:
            return datarows
        self.header["referer"] = self.referers(Route.random() if random() > 0.5 else route)
        self.header["transactionid"] = transaction_id
        self.header["sign"] = self.sign(transaction_id, dcity, acity, flight_date)
        self.header["scope"] = data["scope"]
        self.header["user-agent"] = choice(self.ua)
        self.header["cookie"] = self.cookie()

        try:
            proxy = proxy() if isinstance(proxy, Callable) else self.proxy(proxy)
            response = post(self.url, data = dumps(data), headers = self.header, proxies = proxy, timeout = 10)
            code, url = response.status_code, response.url
            routeList = response.json()
            response.close()
            flag = code, 'V2'
            if routeList["data"]["context"]["flag"] == 0:
                routeList = routeList.get('data').get('flightItineraryList')
            else:
                print('  WARN: data return error', routeList["data"]["context"]["flag"], end = '')
                return datarows
            for routes in routeList:
                flightSegments = routes.get('flightSegments')
                priceList = routes.get('priceList')
                try:
                    if len(flightSegments) == 1:    # Flights that need to transfer is ignored.
                        flight = flightSegments[0].get('flightList')[0]
                        if flight.get('operateAirlineCode'):
                            continue    # Shared flights not collected
                        if flight.get('stopList') != [] or flight.get('stopList') is not None:
                            continue    # Flights with a stop not collected
                        airlineName = flight.get('marketAirlineName')
                        departureTime = time.fromisoformat(flight.get('departureDateTime').split(' ', 1)[1])
                        arrivalTime = time.fromisoformat(flight.get('arrivalDateTime').split(' ', 1)[1])
                        if route.dep.multi:  # Multi-airport cities need the airport name while others do not
                            departureName = route.dep.city + flight.get('departureAirportShortName')[:2]
                        if route.arr.multi:
                            arrivalName = route.arr.city + flight.get('arrivalAirportShortName')[:2]
                        craftType = flight.get('aircraftSize')
                        priceList = priceList[0]
                        price = priceList.get('sortPrice')
                        rate = priceList.get('priceUnitList')[0].get('flightSeatList')[0].get('discountRate')
                        datarows.append([flight_date, dow, airlineName, craftType, departureName, arrivalName, 
                                        departureTime, arrivalTime, price, rate, ])
                        # 日期, 星期, 航司, 机型, 出发机场, 到达机场, 出发时间, 到达时间, 价格, 折扣
                    if len(datarows):
                        datarows.sort(key = lambda x: x[6])
                except Exception as error:
                    print(f"  WARN: {error} in {dcity}-{acity} {flight_date.strftime('%m/%d')}")
                    self.warn += 1
        except JSONDecodeError:
            response.close()
            flag = code, 'Not a json response ' + url if url != self.url else ''
        except Timeout or RequestException:
            flag = 0, 'Timeout'
        except Exception as error:
            flag = code if 'code' in dir() else 0, error
        finally:
            return flag, datarows

class ItineraryCollector(CtripCrawler):
    '''
    Collect itineraries (each route and each flight date) in a random order.
    
    Parameters see class `CtripCrawler`
    '''
    def __init__(self, **kwargs) -> None:
        CtripCrawler.__init__(self, **kwargs)
        self.itineraries = []
        for flight_date in ((self.flight_date + timedelta(i)) for i in range(self.days)):
            self.itineraries += list((flight_date, route) for route in self.routes)
            if self.with_return:
                self.itineraries += list((flight_date, route.returns) for route in self.routes)
        self.avg = 1.4
    
    def run(self, tempfile: Path | str, **kwargs):
        '''
        Collect Parameters
        -----
        - Parts of data collection, for multi-threading.
            - parts: `int`, the total number of parts, default: `0`
            - part: `int`, the index of the running part, default: `0`
        - In case of city with few flights...
            - attempt: `int`, the number of attempt to get ample data, default: `3`
            - noretry: `list`, routes connecting the city has no retry, default: `list()`
        
        Running Parameters
        -----
        - tempfile: `Path | str`, where the data stores.
        - skips: `List-like | Set-like`, itineraries to be skiped in format of 
            `f'{Route.format()} {date}' | tuple[date, Route]`.
        - randomseed: `int | None`, seed of randomizing itineraries, 
        default: `date.today().toordinal() % 100`
        
        Set Proxy
        -----
        - proxy: `Callable[[], dict[str, str]]`, a function that returns proxy in dict (used by requests)
        - proxy: `Literal['proxypool']`, using default API of ProxyPool (https://github.com/Python3WebSpider/ProxyPool) as proxy
        - proxy: `str`, other proxy pool API that returns a proxy url each time (like default API of ProxyPool)
        - proxy: `Iterable[str]`, list of proxy urls
        - proxy: `int` | 'float', random sleep time within this seconds
        '''
        
        header = ['flight_date', 'dow', 'airlineName', 'craftType', 'departureName', 'arrivalName', 
                  'departureTime', 'arrivalTime', 'price', 'rate', 'itinerary']
        if Path(tempfile).exists():
            skips = set(read_csv(Path(tempfile))['itinerary'].unique())
        else:
            DataFrame(columns = header).to_csv(Path(tempfile), index = False)
            skips = set()
        
        parts: int = kwargs.get('parts', 1)
        part: int = kwargs.get('part', 1)
        noretry: list = kwargs.get('noretry', [])
        attempt: int = kwargs.get('attempt', 3) if kwargs.get('attempt', 3) > 1 else 1
        skips |= set(kwargs.get('skips', []))
        proxy = kwargs['proxy'] if isinstance(kwargs.get('proxy'), (Callable, Iterable, int, float)) else None
        
        itineraries = []
        for itinerary in self.itineraries:
            formatted = f'{itinerary[1].format()} {itinerary[0]}'
            if formatted not in skips and itinerary not in skips:
                itineraries.append(itinerary)
        seed(kwargs.get('randomseed', date.today().toordinal() % 100))
        itineraries.sort(key = lambda x: random())
        seed()  # reset all random
        try:
            if part > 0 and parts > 1:
                part_len = int(len(itineraries) / parts)
                itineraries = itineraries[(parts - 1) * part_len : ] if part >= parts \
                    else itineraries[(part - 1) * part_len : part * part_len]
        finally:
            self.total = len(itineraries)
            collected = 0
        
        for itinerary in itineraries:
            dep, arr = itinerary[1].separates('code')
            curr = self.show_progress(*itinerary)
            for _ in range(attempt):
                flag, datarow = self.collector(*itinerary, proxy)
                while flag[1] != 'V2':
                    if flag[1] == 'Timeout' or flag[0] != 200:
                        print(f'  ...timeout, code: {flag[0]}', end = '')
                        sleep(5)
                    else:
                        try:
                            print('  WARN: code {0} [200], {1} [V2]'.format(*flag))
                            input('\r\nContinue (Any) / Exit (*nix: Ctrl-D, Windows: Ctrl-Z+Return): ')
                        except EOFError:
                            exit(0)
                    curr = datetime.now().timestamp()
                    flag, datarow = self.collector(*itinerary, proxy)
                if len(datarow) >= self.limits or (itinerary[0] != self.flight_date and len(datarow)):
                    DataFrame(datarow).assign(
                        itinerary = f'{dep}-{arr} {itinerary[0]}').to_csv(
                        tempfile, mode = 'a', header = False, index = False)
                    collected += 1
                    break
                elif dep in noretry or arr in noretry:
                    print(f" ...few data in {dep}-{arr} {itinerary[0].strftime('%m/%d')}")
                    break
            else:
                if len(datarow) < self.limits:
                    print(f"  WARN: few data in {dep}-{arr} {itinerary[0].strftime('%m/%d')}")
                    self.warn += 1
            
            self.idct += 1
            self.avg = (datetime.now().timestamp() - curr + self.avg * (self.total - 1)) / self.total
        else:
            print(f'{collected} itineraries collected in {tempfile}')
    
    def organize(self, *tempfile: Path | str, **kwargs) -> Generator:
        '''
        Transfer temporary csv files `*tempfile` to `CtripCrawler` base output excels.
        Same as Ctrip Crawler Output Parameters: `path`, `values_only`, `with_return`
        '''
        path = Path(kwargs.get('path', Path(self.first_date) / Path(date.today().isoformat())))
        path.mkdir(parents = True, exist_ok = True)
        headers = ['flight_date', 'dow', 'airlineName', 'craftType', 'departureName', 'arrivalName', 
                   'departureTime', 'arrivalTime', 'price', 'rate']

        tempdata = concat(list(read_csv(Path(file)) for file in tempfile)) \
            if len(tempfile) > 1 else read_csv(Path(*tempfile))
        tempdata['flight_date'] = tempdata['flight_date'].map(date.fromisoformat)
        tempdata['departureTime'] = tempdata['departureTime'].map(time.fromisoformat)
        tempdata['arrivalTime']= tempdata['arrivalTime'].map(time.fromisoformat)
        tempdata['route'] = (tempdata['departureName'].map(Airport) - \
            tempdata['arrivalName'].map(Airport)).map(lambda x: x.separates('code'))
        groups = tempdata.groupby(['route'])
        rroutes = []
        for route in tempdata['route'].unique():
            group = groups.get_group(route).sort_values('flight_date')[headers].to_numpy().tolist()
            if self.with_return:
                if route in rroutes:
                    continue
                rroute = (route[1], route[0])
                rroutes.append(rroute)
                group += groups.get_group(rroute).sort_values('flight_date')[headers].to_numpy().tolist()
            if kwargs.get('with_output', True):
                self.file = self.output_excel(
                    group, *route, path, kwargs.get('values_only', False), self.with_return)
            yield group
