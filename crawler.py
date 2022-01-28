import datetime
import time
from requests import get, post
from json import dumps, loads
from re import match
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.cell import Cell
from pathlib import Path

def exits(code: int = 0) -> None:
    errorCode = {1: 'empty or incorrect data', 2: 'city tuple error', 3:'day limit error', 4: 'no flight',}
    print(' Exited for '+errorCode[code])
    import sys
    sys.exit()
def ignore(codeList: list, ignore_cities: set = None, ignore_threshold: int = 3) -> set:
    '''Default ignore threshold: 3. If two cities given are too close or not in analysis range, skip, 
    by key-ing the coordinates and value-ing False of the coordinate in set. '''
    if ignore_threshold == 0:
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
    if ignore_threshold >= 3:
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
    
    codesum = len(codeList)
    skipSet = set()
    if ignore_cities is not None:
        ignoreSet = ignoreSet.union(ignore_cities, ignoreSet)
    for i in range(codesum):
        for j in range(i, codesum):
            if i == j:
                continue
            if (codeList[i], codeList[j]) in ignoreSet or (codeList[j], codeList[i]) in ignoreSet or codeList[i] == codeList[j]:
                # If the city tuple is the same or found in the set, it shouldn't be processed.
                skipSet.add((i, j))
                skipSet.add((j, i))
    #print(skipSet)
    return skipSet


def getTickets(fdate: datetime.date, dcity: str, acity: str) -> list():
    "Get tickets from dep city to arr city on one date, put all data to a data list and return."
    try:
        dcityname = airportCity.get(dcity, None)
        acityname = airportCity.get(acity, None)
        dow = dayOfWeek[fdate.isoweekday()]
        datarows = []
        url = "https://flights.ctrip.com/itinerary/api/12808/products"
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
                  "Referer": "https://flights.ctrip.com/itinerary/oneway/" + acity + '-' + dcity,
                  "Content-Type": "application/json"}
        payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1,
                           "airportParams": [{"dcity": dcity, "acity": acity, "dcityname": dcityname, "acityname": acityname,
                                              "date": fdate.isoformat(), "dcityid": 1, "acityid": 2}]}

        try:
            with get('http://127.0.0.1:5555/random') as proxy:
                proxy = proxy.text.strip()
                proxy = {"http": "http://" + proxy}  # Set proxy: run in Docker / cmd -> cd ProxyPool -> docker-compose up -> (idle)
        except:
            from random import random
            proxy = None    #sleep time activates for no proxy running
            print('\tNo porxy warn', end='\t')
            time.sleep((round(3 * random(), 2)))
        reply = post(url, data = dumps(payload), headers = header, proxies = proxy)   # -> json()
        response = reply.text
        #print(response)
        routeList = loads(response).get('data').get('routeList')   # -> list
        #print(routeList)
    except:
        try:
            reply.close
        finally:
            return list()
    reply.close
    if routeList is None:   # No data, ignore these flights in the future.
        return list()
    elif len(routeList) == 0:
        return list()

    try:
        for route in routeList:
            if len(route.get('legs')) == 1: # Flights that need to transfer is ignored.
                legs = route.get('legs')
                #print(legs,end='\n\n')
                flight = legs[0].get('flight')
                if flight.get('sharedFlightNumber'):
                    continue    # Shared flights not collected
                airlineName = flight.get('airlineName')
                if '旗下' in airlineName:   # Airline name should be as simple as possible
                    airlineName = airlineName.split('旗下', 1)[1]
                departureTime = flight.get('departureDate').split(' ', 1)[1].split(':', 2)
                departureTime = datetime.time(int(departureTime[0]), int(departureTime[1]))   # Convert the time string to a time class
                arrivalTime = flight.get('arrivalDate').split(' ', 1)[1].split(':', 2)
                arrivalTime = datetime.time(int(arrivalTime[0]), int(arrivalTime[1])) # Convert the time string to a time class
                if dcityname == '北京' or dcityname == '上海' or dcityname== '成都':
                    departureName = flight.get('departureAirportInfo').get('airportName')
                    departureName = dcityname + match('成?都?(.*?)国?际?机场', departureName).groups()[0]
                elif dcityname: # If dcityname exists, that means the code-name is in the default code-name dict
                    departureName = dcityname   # Multi-airport cities need the airport name while others do not
                else:   # If dcityname is None, that means the code-name is not in the default code-name dict
                    departureName = flight.get('departureAirportInfo').get('cityName')
                    airportCity[dcity] = departureName  # ...therefore it is added now 
                if acityname == '北京' or acityname == '上海' or acityname== '成都':
                    arrivalName = flight.get('arrivalAirportInfo').get('airportName')
                    arrivalName = acityname + match('成?都?(.*?)国?际?机场', arrivalName).groups()[0]
                elif acityname:
                    arrivalName = acityname
                else:
                    arrivalName = flight.get('arrivalAirportInfo').get('cityName')
                    airportCity[acity] = arrivalName
                craftType = flight.get('craftTypeKindDisplayName').strip('型')
                ticket = legs[0].get('cabins')[0]   # Price info in cabins dict
                price = ticket.get('price').get('price')
                rate = ticket.get('price').get('rate')
                datarows.append([fdate, dow, airlineName, craftType, departureName, arrivalName, 
                                 departureTime, arrivalTime, price, rate, ])
                #日期，星期，航司，机型，出发机场，到达机场，出发时间，到达时间，价格，折扣
    except:
        return list()
    return datarows


def generateXlsx(path: Path, fdate: datetime.date, days: int = 10, day_limit: int = 0, codeList: list = ['BJS','CAN'], 
                 ignore_cities: set = None, ignore_threshold: int = 3, values_only: bool = False, preproc: bool = False) -> int:
    '''Generate excels of flight tickets info, between the citys given and from the date given and days needed. 
    Return the sum of file generated in int, output new ignorance city tuples in set.'''

    global dayOfWeek, airportCity
    dayOfWeek = {1:'星期一',2:'星期二',3:'星期三',4:'星期四',5:'星期五',6:'星期六',7:'星期日'}
    airportCity = {
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

    try:
        codesum = len(codeList)
    except:
        exits(1) #exit for empty or incorrect data
    if codesum <= 1:
        exits(2) #exit for no city tuple
        
    '''Day range preprocess'''
    currDate = datetime.datetime.now().toordinal()
    if currDate >= fdate.toordinal():   # If collect day is behind today, change the beginning date and days of collect.
        days -= currDate - fdate.toordinal() + 1
        fdate = fdate.fromordinal(currDate + 1)
        if day_limit:   # If there's a limit for days in advance, change the days of collect.
            if days > day_limit:
                days = day_limit
    else:
        if day_limit:   # If there's a limit for days in advance, change the days of collect.
            total = fdate.toordinal() + days - currDate
            if total > day_limit:
                days -= total - day_limit
            if days < 0:
                exits(3) #exit for day limit error
    
    '''Ignore cities with few flights'''
    skipSet = ignore(codeList, ignore_cities, ignore_threshold)  # The set values are the coordinates that should not be processed.
    idct = filesum = 0
    total = (codesum * (codesum - 1) * days - (days * len(skipSet))) / 2
    if total == 0 or codesum <= 1:
        exits(4) #exit for ignored
    ignoreNew = set()
    avgTime = 4.5

    '''Get flights between d(ep)city and a(rr)city of days given'''
    print('\rGetting data...')
    for dcity in range(codesum):
        for acity in range(dcity,codesum):
            if acity == dcity:  # Same values should not be processed.
                continue
            if (dcity,acity) not in skipSet: # If the city tuple key / coordinate is not found, process.
                cdate=fdate #reset
                datarows = []
                for i in range(days):

                    '''Progress Indicator'''
                    print('\r{}% >> '.format(int(idct / total * 100)), end='')
                    m, s = divmod(int((total - idct) * avgTime), 60)
                    h, m = divmod(m, 60)    #show est. remaining process time: eta
                    print('eta {0:02d}:{1:02d}:{2:02d} >> '.format(h, m, s), end='')
                    print(codeList[dcity] + '-'+codeList[acity] + ': ' + cdate.isoformat(), end='')   #current processing flights
                    currTime = time.time()

                    '''Get OUTbound flights data, 3 attempts for ample data'''
                    for j in range(3):
                        dataLen = len(datarows)
                        datarows.extend(getTickets(cdate, codeList[dcity], codeList[acity]))
                        if len(datarows) - dataLen >= ignore_threshold:
                            break
                        elif i != 0 and len(datarows) - dataLen > 0:
                            break
                    else:
                        if i == 0 and len(datarows) < ignore_threshold:
                            total -= days # In the first round, ignore the cities whose flight data is less than 3.
                            print(' ...ignored')
                            ignoreNew.add((codeList[dcity], codeList[acity]))
                            break

                    '''Get INbound flights data, 3 attempts for ample data'''
                    for j in range(3):
                        dataLen = len(datarows)
                        datarows.extend(getTickets(cdate, codeList[acity], codeList[dcity]))
                        if len(datarows) - dataLen >= ignore_threshold:
                            break
                        elif i != 0 and len(datarows) - dataLen > 0:
                            break
                    else:
                        if i == 0 and len(datarows) - dataLen < ignore_threshold:
                            total -= days # In the first round, ignore the cities whose flight data is less than 3.
                            print(' ...ignored')
                            ignoreNew.add((codeList[dcity], codeList[acity]))
                            break

                    cdate = cdate.fromordinal(cdate.toordinal() + 1)    #one day forward
                    idct += 1
                    avgTime = (avgTime * (idct - 1) + time.time() - currTime) / idct

                else:
                    '''Generate (and format) the excel if not ignored'''
                    wbook = openpyxl.Workbook()
                    wsheet = wbook.active
                    wsheet.append(('日期', '星期', '航司', '机型', '出发机场', '到达机场', '出发时', '到达时', '价格', '折扣'))
                    
                    if values_only:
                        for data in datarows:
                            wsheet.append(data)
                        print('\r{0}-{1} generated!                             '.format(codeList[dcity], codeList[acity]))
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
                        print('\r{0}-{1} generated and formatted!               '.format(codeList[dcity], codeList[acity]))
                    
                    wbook.save(path / '{0}~{1}.xlsx'.format(codeList[dcity], codeList[acity]))
                    wbook.close
                    filesum += 1

    # 若有更新忽略集，导出并手动更新（建议）
    if len(ignoreNew) > 0:
        with open('CityTuples_FlightsLessThan{}.txt'.format(ignore_threshold), 'a', encoding = 'UTF-8') as updates:
            updates.write(str(ignoreNew) + '\n')
        print('Ignorance set updated, ', end = '')

    return filesum

if __name__ == "__main__":

    # 务必先设置代理: Docker Desktop / win+R -> cmd -> cd ProxyPool -> docker-compose up -> (idle) -> start

    # 初始化
    global filesum
    filesum = 0
    print('Initializing...', end='')
    
    # 文件夹名设置为当前日期
    currDate = str(datetime.datetime.now().date())
    #currDate = 'debugging' #测试用例
    path = Path(currDate)
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
    
    # 航班爬取参数: 起始年月日、往后天数、机场三字码列表
    # 其他航班参数: 手动忽略集、忽略阈值 -> 暂不爬取共享航班与经停 / 转机航班数据
    # 数据处理参数: 是否录入无格式数据、是否预处理（该功能暂未合并）
    # 返回生成的文件数
    #filesum = generateXlsx(path, datetime.date(2022,2,17), 30, 0, cities, ignore_cities, ignore_threshold)
    filesum = generateXlsx(path, datetime.date(2022,2,19), 3, 0, ['NKG','CKG'], ignore_cities, ignore_threshold)    #测试用例

    print(filesum, 'new files in ', end = currDate) if filesum > 1 else print(filesum, 'new file in ', end = currDate)