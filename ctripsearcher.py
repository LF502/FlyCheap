import datetime
import time
import hashlib
from random import choice
from requests import get, post
from json import dumps
from ctripcrawler import CtripCrawler

class CtripSearcher(CtripCrawler):
    """
    Ctrip flight tickets crawler using batch search method
    
    Use `run` to process!
    """
    def __init__(self, **kwargs) -> None:
        CtripCrawler.__init__(self, **kwargs)
        self.url = "https://flights.ctrip.com/international/search/api/search/batchSearch"

    @property
    def cookie(self) -> str:
        random_str = "abcdefghijklmnopqrstuvwxyz1234567890"
        random_id = ""
        for _ in range(6):
            random_id += choice(random_str)
        t = str(int(round(time.time() * 1000)))

        bfa_list = ["1", t, random_id, "1", t, t, "1", "1"]
        bfa = "_bfa={}".format(".".join(bfa_list))
        return bfa

    @staticmethod
    def sign(transaction_id, dep: str, arr: str, flight_date: str) -> str:
        sign_value = transaction_id + dep + arr + flight_date
        _sign = hashlib.md5()
        _sign.update(sign_value.encode('utf-8'))
        return _sign.hexdigest()

    @staticmethod
    def transaction_id(dep: str, arr: str, date: str, proxy: dict = None) -> tuple[str, dict]:
        url = f"https://flights.ctrip.com/international/search/api/flightlist/oneway-{dep}-{arr}?_=1&depdate={date}&cabin=y&containstax=1"
        response = get(url, proxies = proxy)
        if response.status_code != 200:
            print("\tWARN: get transaction id failed, status code", response.status_code, end = '')
            return "", None

        try:
            data = response.json().get("data")
            response.close
            return data["transactionID"], data
        except Exception as e:
            print("\tWARN: get transaction id failed,", e, end = '')
            return "", None


    def collector(self, flight_date: datetime.date, route) -> list[list]:
        datarows = list()
        dcity, acity = route.separates('code')
        departureName = dcityname = route.dep.city
        arrivalName = acityname = route.arr.city
        dow, date = self.dayOfWeek[flight_date.isoweekday()], flight_date.isoformat()
        transaction_id, data = self.transaction_id(dcity, acity, date, self.proxy())
        if transaction_id == "" or data is None:
            return datarows
        header = {"origin": "https://flights.ctrip.com", 
                  "referer": f"https://flights.ctrip.com/online/list/oneway-{acity}-{dcity}?_=1&depdate={date}&cabin=y&containstax=1", 
                  "transactionid": transaction_id, 
                  "sign": self.sign(transaction_id, dcity, acity, date), 
                  "scope": data["scope"], 
                  "content-type": "application/json;charset=UTF-8",
                  "user-agent": choice(self.userAgents), 
                  "cookie": self.cookie, }

        try:
            response = post(self.url, data = dumps(data), headers = header, proxies = self.proxy())
            routeList = response.json()
            response.close
            if routeList["data"]["context"]["flag"] == 0:
                routeList = routeList.get('data').get('flightItineraryList')
            else:
                print('\tWARN: data return error', routeList["data"]["context"]["flag"], end = '')
                return datarows
        except:
            return datarows
        #print(routeList)
        if routeList is None:   # No data, return empty and ignore these flights in the future.
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
                    departureTime = datetime.time().fromisoformat(flight.get('departureDateTime').split(' ', 1)[1])
                    arrivalTime = datetime.time().fromisoformat(flight.get('arrivalDateTime').split(' ', 1)[1])
                    if route.dep.multi:  # Multi-airport cities need the airport name while others do not
                        departureName = flight.get('departureAirportShortName')
                        departureName = dcityname + departureName[:2]
                    elif not departureName: # If dcityname exists, that means the code-name is in the default code-name dict
                        departureName = flight.get('departureCityName')
                    if route.arr.multi:
                        arrivalName = flight.get('arrivalAirportShortName')
                        arrivalName = acityname + arrivalName[:2]
                    elif not arrivalName:
                        arrivalName = flight.get('arrivalCityName')
                    craftType = flight.get('aircraftSize')
                    priceList = priceList[0]
                    price = priceList.get('sortPrice')
                    rate = priceList.get('priceUnitList')[0].get('flightSeatList')[0].get('discountRate')
                    datarows.append([flight_date, dow, airlineName, craftType, departureName, arrivalName, 
                                     departureTime, arrivalTime, price, rate, ])
                    # 日期, 星期, 航司, 机型, 出发机场, 到达机场, 出发时间, 到达时间, 价格, 折扣
            except Exception as error:
                print(' WARN:', error, f'in {dcity}-{acity} ', end = flight_date.strftime('%m/%d'))
                self.__warn += 1
        return datarows
