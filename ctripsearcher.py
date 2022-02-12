import datetime
import time
import hashlib
import random
from requests import get, post
from json import dumps
from pathlib import Path
from ctripcrawler import CtripCrawler

class CtripSearcher(CtripCrawler):
    """
    Ctrip flight tickets crawler using batch search method
    
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

    def __init__(self, cityList: list, flightDate: datetime.date = datetime.datetime.now().date(), 
                 days: int = 1, day_limit: int = 0, ignore_cities: set = None, ignore_threshold: int = 3, 
                 with_return: bool = True, proxy: str | bool = None) -> None:

        CtripCrawler.__init__(self, cityList, flightDate, days, day_limit, ignore_cities, ignore_threshold, with_return, proxy)

        self.__codesum = len(cityList)
        self.__total = self.__codesum * (self.__codesum - 1) * self.days / 2
        self.url = "https://flights.ctrip.com/international/search/api/search/batchSearch"


    def __sizeof__(self) -> int:
        return self.__total

    @property
    def cookie(self) -> str:
        random_str = "abcdefghijklmnopqrstuvwxyz1234567890"
        random_id = ""
        for _ in range(6):
            random_id += random.choice(random_str)
        t = str(int(round(time.time() * 1000)))

        bfa_list = ["1", t, random_id, "1", t, t, "1", "1"]
        bfa = "_bfa={}".format(".".join(bfa_list))
        return bfa

    @staticmethod
    def sign(transaction_id, dep: str, arr: str, flightDate: str):
        sign_value = transaction_id + dep + arr + flightDate
        _sign = hashlib.md5()
        _sign.update(sign_value.encode('utf-8'))
        return _sign.hexdigest()

    @staticmethod
    def transaction_id(dep: str, arr: str, date: str, proxy: dict = None):
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



    def collector(self, flightDate: datetime.date, dcity: str, acity: str) -> list():
        datarows = list()
        departureName = dcityname = self.__airportCity.get(dcity, None)
        arrivalName = acityname = self.__airportCity.get(acity, None)
        dow, date = self.__dayOfWeek[flightDate.isoweekday()], flightDate.isoformat()
        proxy = None if self.proxylist == False else self.proxy if self.proxylist else self.proxypool
        transaction_id, data = self.transaction_id(dcity, acity, date, proxy)
        if transaction_id == "" or data is None:
            return datarows
        header = {"origin": "https://flights.ctrip.com", 
                  "referer": f"https://flights.ctrip.com/online/list/oneway-{dcity}-{acity}?_=1&depdate={date}&cabin=y&containstax=1", 
                  "transactionid": transaction_id, 
                  "sign": self.sign(transaction_id, dcity, acity, date), 
                  "scope": data["scope"], 
                  "content-type": "application/json;charset=UTF-8",
                  "user-agent": self.userAgent, 
                  "cookie": self.cookie, }

        try:
            response = post(self.url, data = dumps(data), headers = header, proxies = proxy)
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

        d_multiairport = True if dcityname == '北京' or dcityname == '上海' or dcityname== '成都' else False
        a_multiairport = True if acityname == '北京' or acityname == '上海' or acityname== '成都' else False
        for route in routeList:
            flightSegments = route.get('flightSegments')
            priceList = route.get('priceList')
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
                    if d_multiairport:  # Multi-airport cities need the airport name while others do not
                        departureName = flight.get('departureAirportShortName')
                        departureName = dcityname + departureName[:2]
                    elif not departureName: # If dcityname exists, that means the code-name is in the default code-name dict
                        departureName = flight.get('departureCityName') # Otherwise the code-name is not
                        self.__airportCity[dcity] = departureName   # ...in the code-name dict, therefore it is added now 
                    if a_multiairport:
                        arrivalName = flight.get('arrivalAirportShortName')
                        arrivalName = acityname + arrivalName[:2]
                    elif not arrivalName:
                        arrivalName = flight.get('arrivalCityName')
                        self.__airportCity[acity] = arrivalName
                    craftType = flight.get('aircraftSize')
                    priceList = priceList[0]
                    price = priceList.get('sortPrice')
                    rate = priceList.get('priceUnitList')[0].get('flightSeatList')[0].get('discountRate')
                    datarows.append([flightDate, dow, airlineName, craftType, departureName, arrivalName, 
                                     departureTime, arrivalTime, price, rate, ])
                    # 日期, 星期, 航司, 机型, 出发机场, 到达机场, 出发时间, 到达时间, 价格, 折扣
            except Exception as dataError:
                print('\tWARN:', dataError, 'at', {flightDate.isoformat()}, end = '')
                self.__warn += 1
        return datarows

if __name__ == "__main__":

    # 务必先设置代理: Docker Desktop / cmd -> cd ProxyPool -> docker-compose up -> (idle) -> start

    # 初始化
    print('Initializing...', end='')
    
    # 文件夹名设置为当前日期
    #path = Path('debugging')   #测试用例
    path = Path(str(datetime.datetime.now().date()))
    if not path.exists():
        Path.mkdir(path)

    # 城市列表, 处理表中各城市对的航班（第一天少于3个则忽略）, 分类有: 华北+东北、华东、西南、西北+新疆、中南
    cities = ['BJS','HRB','HLD','TSN','DLC','TAO','CGO',
              'SHA','NKG','HGH','CZX','WUX','FOC','XMN','JJN',
              'CTU','CKG','KMG','JHG',
              'URC','XIY','LHW','LXA',
              'WUH','CAN','ZHA','SZX','SWA','HAK','SYX',]
    
    # 忽略阈值, 低于该值则不统计航班, 0为都爬取并统计
    ignore_threshold = 3
    ignore_cities = None

    # 代理API
    proxyurl = None

    # 航班爬取: 机场三字码列表、起始年月日、往后天数
    # 其他参数: 提前天数限制、手动忽略集、忽略阈值 -> 暂不爬取共享航班与经停 / 转机航班数据、是否双向爬取
    # 运行参数: 是否输出文件（否: 生成列表）、存储路径、是否带格式
    crawler = CtripSearcher(cities, datetime.date(2022,2,17), 30, 0, ignore_cities, ignore_threshold)
    #crawler = CtripSearcher(['SHA','CTU'], datetime.date(2022,2,11), 1, 0, ignore_cities, ignore_threshold)
    for data in crawler.run(path = path):
        pass
    else:
        print(' - - - COMPLETE AND EXIT - - - ')
