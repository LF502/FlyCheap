from datetime import datetime, date, time
from time import sleep
from requests import get, post
from json import dumps, loads
from random import random
from typing import Generator
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.cell import Cell
from pathlib import Path
from civilaviation import CivilAviation

class CtripCrawler():
    """
    Ctrip flight tickets crawler
    
    Use `run` to process!
    """

    def __init__(self, cityList: list, flightDate: date = date.today(), 
                 days: int = 1, day_limit: int = 0, ignore_routes: set = None, 
                 ignore_threshold: int = 3,
                 with_return: bool = True, proxy: str | bool = None) -> None:
        
        self.__airData = CivilAviation()
        
        self.__dayOfWeek = {
            1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六', 7:'星期日'}
        
        try:
            self.__codesum = len(cityList)
        except:
            self.exits(1) #exit for empty or incorrect data
        if self.__codesum <= 1:
            self.exits(2) #exit for no city tuple

        self.cityList = cityList
        self.flightDate = flightDate
        self.first_date = flightDate.isoformat()

        self.days = days
        self.day_limit = day_limit

        self.ignore_routes = ignore_routes
        self.ignore_threshold = ignore_threshold
        self.with_return = with_return

        '''Day range preprocess'''
        currDate = date.today().toordinal()
        if currDate >= self.flightDate.toordinal():
            # If collect day is behind today, change the beginning date and days of collect.
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
        self.__total = self.__codesum * (self.__codesum + 1) * self.days / 2

        if self.__total == 0:
            self.exits(4)   #exit for ignored

        self.__warn = 0
        self.__idct = 0
        self.__avgTime = 2.9 if with_return else 1.3

        self.url = "https://flights.ctrip.com/itinerary/api/12808/products"
        self.header = {"Content-Type": "application/json;charset=utf-8", 
                       "Accept": "application/json", 
                       "Accept-Language": "zh-cn", 
                       "Origin": "https://flights.ctrip.com", 
                       "Host": "flights.ctrip.com", 
                       "Referer": "https://flights.ctrip.com/international/search/domestic", }
        self.payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1}

        if proxy == False:
            self.proxylist = False
        elif isinstance(proxy, str):
            try:
                with get(proxy) as proxy:
                    proxy = proxy.json().get("data")
                self.proxylist = []
                for item in proxy:
                    self.proxylist.append(f"http://{item.get('ip')}:{item.get('port')}")
            except:
                self.proxylist = None
        else:
            self.proxylist = None
    
        self.__userAgents = (
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
        self.__lenAgents = len(self.__userAgents)

    @property
    def skips(self) -> set[tuple[str, str]]:
        '''Ignore cities with few flights.
        If two cities given are too close or not in analysis range, skip, 
        by returning matrix routes in set. '''
        if self.ignore_threshold >= 3:
            ignores = self.__airData.routes_inactive | self.__airData.routes_low
        elif self.ignore_threshold > 0:
            ignores = self.__airData.routes_inactive
        else:
            ignores = set()
        if self.ignore_routes is not None and isinstance(self.ignore_routes, set):
            ignores |= self.ignore_routes
        
        skips = set()
        for dep in self.cityList:
            for arr in self.cityList[self.cityList.index(dep): ]:
                # If the city tuple is the same or found in the set, do not process.
                if dep == arr or (dep, arr) in ignores or (arr, dep) in ignores:
                    skips.add((dep, arr))
        return skips

    @property
    def routes(self) -> list[tuple[str, str]]:
        '''Get matrix-like routes in list of tuple(dep city, arr city)'''
        routes = []
        for dep in self.cityList:
            for arr in self.cityList[self.cityList.index(dep): ]:
                if (dep, arr) not in self.skips:
                    routes.append((dep, arr))
        return routes

    @staticmethod
    def exits(__code: int = 0) -> None:
        '''Exit program with a massage'''
        import sys
        error_code = {0: 'reaching exit point', 1: 'empty or incorrect data', 
                      2: 'city tuple error',3:'day limit error', 4: 'no flight'}
        print(f' Exited for {error_code[__code]}')
        sys.exit()

    @property
    def proxypool(self) -> dict | None:
        '''Get a random proxy from Proxy Pool'''
        for _ in range(3):
            try:
                with get('http://127.0.0.1:5555/random', timeout = 3) as proxy:
                    proxy = proxy.text.strip()
                    if len(proxy):
                        return {"http": "http://" + proxy}
            except:
                continue
        else:
            print(' WARN: no proxy', end = '')
            return sleep(3 * random())

    @property
    def proxy(self) -> dict:
        return {"http": self.proxylist[int(len(self.proxylist) * random())]}

    @property
    def userAgent(self) -> str:
        '''Get a random User Agent'''
        return self.__userAgents[int(self.__lenAgents * random())]


    def collector(self, flightDate: date, dcity: str, acity: str) -> list[list]:
        proxy = None if self.proxylist == False else self.proxy if self.proxylist else self.proxypool
        datarows = list()
        departureName = dcityname = self.__airData.from_code(dcity)
        arrivalName = acityname = self.__airData.from_code(acity)
        header, payload = self.header, self.payload
        dow = self.__dayOfWeek[flightDate.isoweekday()]
        header["User-Agent"] = self.userAgent
        payload["airportParams"] = [{"dcity": dcity, "acity": acity, "dcityname": dcityname,
                                     "acityname": acityname, "date": flightDate.isoformat(),}]

        try:
            response = post(
                self.url, data = dumps(payload), headers = header, proxies = proxy, timeout = 10)
            routeList = loads(response.text).get('data').get('routeList')   # -> list
        except:
            try:
                response.close
            finally:
                return datarows
        response.close
        #print(routeList)
        if routeList is None:   # No data, return empty and ignore these flights in the future.
            return datarows

        d_multiairport = self.__airData.is_multiairport(dcity)
        a_multiairport = self.__airData.is_multiairport(acity)
        for route in routeList:
            legs = route.get('legs')
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
                    if d_multiairport:  # Multi-airport cities need the airport name while others do not
                        departureName = flight.get('departureAirportInfo').get('airportName')
                        departureName = dcityname + departureName.strip('成都')[:2]
                    elif not departureName:
                        departureName = flight.get('departureAirportInfo').get('cityName')
                    if a_multiairport:
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
                        flightDate, dow, airlineName, craftType, departureName, 
                        arrivalName, departureTime, arrivalTime, price, rate])
            except Exception as error:
                print(' WARN:', error, f'in {dcity}-{acity} ', end = flightDate.isoformat())
                self.__warn += 1
        return datarows


    def show_progress(self, dcity: str, acity: str) -> float:
        '''Progress indicator with a current time (float) return'''
        m, s = divmod(int((self.__total - self.__idct) * self.__avgTime), 60)
        h, m = divmod(m, 60)
        print(f'\r{dcity}-{acity} >> eta {h:02d}:{m:02d}:{s:02d} >> ', 
              end = f'{int(self.__idct / self.__total * 100):03d}%')
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
        - Where to store? 
        - With format or not?
        
        with_output: `bool`, default: `True`
        
        path: `Path` | `str`, default: `Path("First Flight Date" / "Current Date")`
        
        values_only: `bool`, default: `False`
        
        
        Collect Parameters
        -----
        - Parts of data collection, for multi-threading.
        
        parts: `int`, the total number of parts, default: 0
        
        part: `int`, the index of the running part, default: 0
        '''
        filesum = 0
        __ignores = set()
        limits = self.ignore_threshold if self.ignore_threshold else 1

        '''Initialize running parameters'''
        path = kwargs.get('path', Path(self.first_date) / Path(date.today().isoformat()))
        if not isinstance(path, Path):
            path = Path(str(path))
        if not path.exists():
            path.mkdir(parents = True, exist_ok = True)
        values_only: bool = kwargs.get('values_only', False)
        parts: int = kwargs.get('parts', 0)
        part: int = kwargs.get('part', 0)
        
        '''Part separates'''
        routes = []
        for dep, arr in self.routes:
            if not Path(path / f'{dep}~{arr}.xlsx').exists():
                routes.append((dep, arr))
        try:
            if part > 0 and parts > 1:
                part_len = int(len(routes) / parts)
                routes = routes[(parts - 1) * part_len : ] if part >= parts \
                    else routes[(part - 1) * part_len : part * part_len]
        finally:
            self.__total = len(routes) * self.days
        
        '''Data collecting controller'''
        for dep, arr in routes:
            if Path(path / f'{dep}~{arr}.xlsx').exists():
                print(f'{dep}-{arr} already collected, skip')
                self.__total -= self.days
                continue    # Already processed.
            collectDate = self.flightDate   #reset
            datarows = []
            for i in range(self.days):
                currTime = self.show_progress(dep, arr)

                '''Get OUTbound flights data, 3 attempts for ample data'''
                for j in range(3):
                    data_diff = len(datarows)
                    datarows.extend(self.collector(collectDate, dep, arr))
                    data_diff = len(datarows) - data_diff
                    if data_diff >= limits:
                        break
                    elif i != 0 and data_diff > 0:
                        break
                    elif j == 1:
                        print(' ...retry', end = '')
                else:
                    if i == 0 and data_diff < self.ignore_threshold:
                        self.__total -= self.days
                        print(f'\r{dep}-{arr} has {data_diff} flight(s), ignored. ')
                        __ignores.add((dep, arr))
                        break
                    elif data_diff < limits:
                        print(f' WARN: few data in {dep}-{arr} ', end = collectDate.isoformat())
                        self.__warn += 1

                '''Get INbound flights data, 3 attempts for ample data'''
                if self.with_return:
                    for j in range(3):
                        data_diff = len(datarows)
                        datarows.extend(self.collector(collectDate, arr, dep))
                        if data_diff >= limits:
                            break
                        elif i != 0 and data_diff > 0:
                            break
                        elif j == 1:
                            print(' ...retry', end = '')
                    else:
                        if i == 0 and data_diff < self.ignore_threshold:
                            self.__total -= self.days
                            print(f'\r{arr}-{dep} has {data_diff} flight(s), ignored. ')
                            __ignores.add((arr, dep))
                            break
                        elif data_diff < limits:
                            print(f' WARN: few data in {arr}-{dep} ', end = collectDate.isoformat())
                            self.__warn += 1

                collectDate = collectDate.fromordinal(collectDate.toordinal() + 1)  #one day forward
                self.__idct += 1
                self.__avgTime = (datetime.now().timestamp() - currTime + self.__avgTime \
                    * (self.__total - 1)) / self.__total
            else:
                if len(datarows) and with_output:
                    self.file = self.output_excel(datarows, dep, arr, path, values_only, self.with_return)
                    if values_only:
                        print(f'\r{dep}-{arr} collected!               ')
                    else:
                        print(f'\r{dep}-{arr} collected and formatted! ')
                    filesum += 1
                elif len(datarows):
                    print(f'\r{dep}-{arr} generated!               ')
                else:
                    print(f'\r{dep}-{arr} WARN: no data!           ')
                    self.__warn += 1
                    continue
                yield datarows

        if with_output:
            if len(__ignores) > 0:
                with open(f'IgnoredOrError_{self.ignore_threshold}.txt', 'a') as updates:
                    updates.write(str(__ignores) + '\n')
                    print('Ignorance set updated, ', end = '')
            print(filesum, 'routes collected in', path.name) if filesum > 1 else \
                print(filesum, 'route collected in', path.name)
        print('Total warnings:', self.__warn) if self.__warn > 1 else \
            print('Total warning:', self.__warn) if self.__warn else print()
        self.__warn = 0


if __name__ == "__main__":

    # 务必先设置代理: Docker Desktop / cmd -> cd ProxyPool -> docker-compose up -> (idle) -> start

    # 城市列表, 处理表中各城市对的航班 (第一天少于3个则忽略) , 分类有: 华北+东北、华东、西南、西北+新疆、中南
    cities = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]

    # 忽略阈值, 低于该值则不统计航班, 0为都爬取并统计
    ignore_threshold = 3
    ignore_routes = {('BJS', 'LXA'), ('DLC', 'XIY')}

    # 代理: 字符串 - 代理网址API / False - 禁用 / 不填 - 使用ProxyPool
    proxyurl = None

    # 航班爬取: 机场三字码列表、起始年月日、往后天数
    # 其他参数: 提前天数限制、手动忽略集、忽略阈值 -> 暂不爬取共享航班与经停 / 转机航班数据、是否双向爬取
    # 运行参数: 是否输出文件 (否: 生成列表) 、存储路径、是否带格式
    crawler = CtripCrawler(cities, date(2022,2,17), 30, 0, ignore_routes, ignore_threshold, True, proxyurl)
    for data in crawler.run():
        pass
