from datetime import datetime, date, time, timedelta
from time import sleep
from requests import get, post
from json import dumps, loads
from random import random, choice
from typing import Generator, Literal
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.cell import Cell
from pathlib import Path
from civilaviation import Airport, Route

class CtripCrawler():
    """
    Ctrip flight tickets crawler
    
    Use `run` to process!
    """

    url = "https://flights.ctrip.com/itinerary/api/12808/products"
    header = {
        "Content-Type": "application/json;charset=utf-8", 
        "Accept": "application/json", 
        "Accept-Language": "zh-cn", 
        "Host": "flights.ctrip.com", 
        "Origin": "https://flights.ctrip.com", 
        "Referer": "https://flights.ctrip.com/international/search/domestic", }
    payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1}
    dayOfWeek = {1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六', 7:'星期日'}
    userAgents = [
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
        self, targets: list[str | Airport | Route], flight_date: date = date.today() + timedelta(1), 
        days: int = 1, day_limit: int = 0, ignore_routes: set = set(), ignore_threshold: int = 3, 
        with_return: bool = True, proxy: str | bool | None = None) -> None:

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
        self.flight_date, self.first_date = flight_date, flight_date.isoformat()

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

        self.__warn = self.__idct = 0
        self.__avgTime = 2.9 if with_return else 1.3
        self.with_return = with_return
        self.__limits = self.__threshold if self.__threshold else 1
        self.flag = (200, 'V2')

        if proxy is False:
            self.__proxy == False
        elif isinstance(proxy, str):
            try:
                with get(proxy) as proxy:
                    proxy = proxy.json().get("data")
                self.proxylist = []
                for item in proxy:
                    self.proxylist.append(f"http://{item.get('ip')}:{item.get('port')}")
                self.__proxy = 'proxy' if len(self.proxylist) else 'proxypool'
            except:
                self.__proxy = 'proxypool'
        else:
            self.__proxy = 'proxypool'

    def proxy(self, key: Literal['proxy', 'proxypool'] = None) -> dict | None:
        '''Get a random proxy from either proxylist or proxypool'''
        if self.__proxy == 'proxy' or key == 'proxy':
            return {"http": choice(self.proxylist)}
        elif self.__proxy == 'proxypool' or key == 'proxypool':
            for _ in range(3):
                try:
                    with get('http://127.0.0.1:5555/random', timeout = 3) as proxy:
                        proxy = proxy.text.strip()
                    if len(proxy):
                        return {"http": "http://" + proxy}
                except:
                    continue
            else:
                print(' ERROR: no proxy', end = '')
                return sleep(3 * random())
        else:
            return None

    def collector(self, flight_date: date, route: Route) -> list[list]:
        '''Web crawler main'''
        datarows = list()
        dcity, acity = route.separates('code')
        departureName = dcityname = route.dep.city
        arrivalName = acityname = route.arr.city
        header, payload = self.header, self.payload
        dow = self.dayOfWeek[flight_date.isoweekday()]
        header["User-Agent"] = choice(self.userAgents)
        header["Referer"] = "https://flights.ctrip.com/online/list/oneway-" + \
            f"{acity}-{dcity}?depdate={flight_date}"
        payload["airportParams"] = [{"dcity": dcity, "acity": acity, "dcityname": dcityname,
                                     "acityname": acityname, "date": flight_date.isoformat()}]

        try:
            response = post(
                self.url, data = dumps(payload), headers = header, proxies = self.proxy(), timeout = 10)
            data = loads(response.text).get('data')
            self.flag = response.status_code, data.get('version')
            routeList = data.get('routeList')
        except:
            self.flag = (0, 'Unknown')
            try:
                response.close()
            finally:
                return datarows
        response.close()
        #print(routeList)
        if routeList is None:
            # No data or version error (anti web crawler, etc)
            return datarows

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
                        airlineName = airlineName.split('旗下', 1)[1]   # Convert time
                    departureTime = time.fromisoformat(flight.get('departureDate').split(' ', 1)[1])
                    arrivalTime = time.fromisoformat(flight.get('arrivalDate').split(' ', 1)[1])
                    if route.dep.multi:  # Multi-airport cities need the airport name while others do not
                        departureName = flight.get('departureAirportInfo').get('airportName')
                        departureName = dcityname + departureName.strip('成都')[:2]
                    elif not departureName:
                        departureName = flight.get('departureAirportInfo').get('cityName')
                    if route.arr.multi:
                        arrivalName = flight.get('arrivalAirportInfo').get('airportName')
                        arrivalName = acityname + arrivalName.strip('成都')[:2]
                    elif not arrivalName:
                        arrivalName = flight.get('arrivalAirportInfo').get('cityName')
                    craftType = flight.get('craftTypeKindDisplayName')
                    craftType = craftType.strip('型') if craftType else "中"
                    ticket = legs[0].get('cabins')[0]   # Price info in cabins dict
                    price = ticket.get('price').get('price')
                    rate = ticket.get('price').get('rate')
                    datarows.append([
                        flight_date, dow, airlineName, craftType, departureName, 
                        arrivalName, departureTime, arrivalTime, price, rate])
            except Exception as error:
                print(' WARN:', error, f'in {dcity}-{acity} ', end = flight_date.strftime('%m/%d'))
                self.__warn += 1
        return datarows


    def show_progress(self, dcity: str, acity: str) -> float:
        '''Progress indicator with a current time (float) return'''
        m, s = divmod(int((self.total - self.__idct) * self.__avgTime), 60)
        h, m = divmod(m, 60)
        print(f'\r{dcity}-{acity} >> eta {h:02d}:{m:02d}:{s:02d} >> ', 
              end = f'{int(self.__idct / self.total * 100):03d}%')
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
            - antiempty: `int`, skip output few flights in the last flight days , default: `0`
            - noretry: `list`, routes connecting the city has no retry, default: `list()`
        
        File Detection Parameters
        -----
        - overwrite: `bool`, collect and overwrite existing files, default: `False`
        - nopreskip: `bool`, keep the orignal collect route without detection, default: `False`
        '''
        filesum = 0
        __ignores = set()
        '''Initialize running parameters'''
        path = kwargs.get('path', Path(self.first_date) / Path(date.today().isoformat()))
        if not isinstance(path, Path):
            path = Path(path)
        path.mkdir(parents = True, exist_ok = True)
        values_only: bool = kwargs.get('values_only', False)
        parts: int = kwargs.get('parts', 1)
        part: int = kwargs.get('part', 1)
        overwrite: bool = kwargs.get('overwrite', False)
        noretry: list = kwargs.get('noretry', [])
        attempt: int = kwargs.get('attempt', 3) if kwargs.get('attempt', 3) > 1 else 1
        antiempty: int = kwargs.get('antiempty') if kwargs.get('antiempty', 0) >= 1 else 0

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
            collect_date = last_date = self.flight_date   #reset
            datarows = []
            for i in range(self.days):
                curr = self.show_progress(dep, arr)

                '''Get OUTbound flights data, attempts for ample data'''
                for j in range(attempt):
                    data_diff = len(datarows)
                    datarows.extend(self.collector(collect_date, route))
                    data_diff = len(datarows) - data_diff
                    if data_diff >= self.__limits or (i != 0 and data_diff > 0):
                        last_date = collect_date
                        break
                    elif dep in noretry or arr in noretry:
                        print(f' ...few data in {dep}-{arr} ', 
                                end = collect_date.strftime('%m/%d'))
                        break
                    elif j == 1:
                        print(' ...retry', end = '')
                else:
                    if i == 0 and data_diff < self.__threshold:
                        self.total -= self.days
                        print(f'\r{dep}-{arr} has {data_diff} flight(s), ignored. ')
                        __ignores.add((dep, arr))
                        break
                    elif data_diff < self.__limits:
                        print(f' WARN: few data in {dep}-{arr} ', 
                              end = collect_date.strftime('%m/%d'))
                        self.__warn += 1

                '''Get INbound flights data, attempts for ample data'''
                if self.with_return:
                    for j in range(attempt):
                        data_diff = len(datarows)
                        datarows.extend(self.collector(collect_date, route.returns))
                        data_diff = len(datarows) - data_diff
                        if data_diff >= self.__limits or (i != 0 and data_diff > 0):
                            last_date = collect_date
                            break
                        elif dep in noretry or arr in noretry:
                            print(f' ...few data in {arr}-{dep} ', 
                                  end = collect_date.strftime('%m/%d'))
                            break
                        elif j == 1:
                            print(' ...retry', end = '')
                    else:
                        if i == 0 and data_diff < self.__threshold:
                            self.total -= self.days
                            print(f'\r{arr}-{dep} has {data_diff} flight(s), ignored. ')
                            __ignores.add((arr, dep))
                            break
                        elif data_diff < self.__limits:
                            print(f' WARN: few data in {arr}-{dep} ', 
                                  end = collect_date.strftime('%m/%d'))
                            self.__warn += 1

                collect_date += timedelta(1)  #one day forward
                self.__idct += 1
                self.__avgTime = (datetime.now().timestamp() - curr + self.__avgTime \
                    * (self.total - 1)) / self.total
            else:
                antiflag = last_date + timedelta(antiempty) >= collect_date if antiempty else True
                msg = f'\r{dep}-{arr} '
                if len(datarows) and with_output and antiflag:
                    self.file = self.output_excel(datarows, dep, arr, path, values_only, self.with_return)
                    print(msg + 'collected' + ('!               ' if values_only else ' and formatted! '))
                    filesum += 1
                elif len(datarows) and antiflag:
                    print(msg + 'generated!               ')
                elif len(datarows) and not antiflag:
                    print(msg + 'WARN: output disabled, code: {0}, version: {1}'.format(*self.flag))
                    if self.flag != (200, 'V2'):
                        input('Continue / Exit')
                    self.__warn += 1
                    continue
                else:
                    print(msg + 'WARN: no data, code: {0}, version: {1}'.format(*self.flag))
                    if self.flag != (200, 'V2'):
                        input('Continue / Exit')
                    self.__warn += 1
                    continue
                yield datarows

        if with_output:
            if len(__ignores) > 0:
                with open(f'IgnoredOrError_{self.__threshold}.txt', 'a') as updates:
                    updates.write(str(__ignores) + '\n')
                    print('Ignorance set updated, ', end = '')
            print(filesum, 'routes collected in', path.name) if filesum > 1 else \
                print(filesum, 'route collected in', path.name)
        print('Total warnings:', self.__warn) if self.__warn > 1 else \
            print('Total warning:', self.__warn) if self.__warn else print()
        self.__warn = 0


if __name__ == "__main__":

    # 务必先设置代理: Docker Desktop / cmd -> cd ProxyPool -> docker-compose up -> (idle) -> start

    # 城市列表, 支持输入IATA/ICAO代码或城市名称；亦可输入 Route / Airport 类
    cities = [Route('CTU', 'BJS')]

    # 忽略阈值, 低于该值则不统计航班, 0为都爬取并统计
    ignore_threshold = 3
    #忽略的航线，可用Route或tuple表示
    ignore_routes = set()

    # 代理: 字符串 - 代理网址API / False - 禁用 / 不填 - 使用ProxyPool
    proxyurl = None

    # 航班爬取: 机场三字码列表、起始年月日、往后天数
    # 其他参数: 提前天数限制、手动忽略集、忽略阈值 -> 暂不爬取共享航班与经停 / 转机航班数据、是否双向爬取
    # 运行参数: 是否输出文件 (否: 生成列表) 、存储路径、是否带格式
    crawler = CtripCrawler(cities, date(2022, 3, 31), 2, 0, ignore_routes, ignore_threshold, True)
    for data in crawler.run():
        pass
