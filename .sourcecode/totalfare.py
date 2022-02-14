from random import random
from pathlib import Path
from pyrsistent import b
from requests import post, get
from json import loads, dumps

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
__lenAgents = len(__userAgents)

def proxy():
    try:
        with get('http://127.0.0.1:5555/random') as proxy:
            proxy = {"http": "http://" + proxy.text.strip()}
    except:
        proxy = None
        print('\tWARN: no proxy', end='')
    finally:
        return proxy

totalfare = {
    ('BJS', 'CAN'): 3060, ('BJS', 'CKG'): 2170, ('BJS', 'CTU'): 2230, ('BJS', 'DLC'): 930, 
    ('BJS', 'FOC'): 2020, ('BJS', 'HAK'): 3160, ('BJS', 'HGH'): 2660, ('BJS', 'HRB'): 1700, 
    ('BJS', 'JJN'): 1730, ('BJS', 'KMG'): 2550, ('BJS', 'LHW'): 2010, ('BJS', 'LXA'): 3260, 
    ('BJS', 'NKG'): 2230, ('BJS', 'SHA'): 1960, ('BJS', 'SWA'): 1910, ('BJS', 'SYX'): 3680, 
    ('BJS', 'SZX'): 2500, ('BJS', 'URC'): 3480, ('BJS', 'WUH'): 2510, ('BJS', 'WUX'): 2110, 
    ('BJS', 'XIY'): 2450, ('BJS', 'XMN'): 2120, ('CAN', 'HAK'): 1890, ('CAN', 'SYX'): 1590, 
    ('CAN', 'ZHA'): 970, ('CGO', 'CAN'): 1700, ('CGO', 'CKG'): 1270, ('CGO', 'CTU'): 1220, 
    ('CGO', 'FOC'): 1370, ('CGO', 'HAK'): 2220, ('CGO', 'HGH'): 940, ('CGO', 'JJN'): 1360, 
    ('CGO', 'KMG'): 2060, ('CGO', 'LHW'): 1100, ('CGO', 'SHA'): 1280, ('CGO', 'SYX'): 2470, 
    ('CGO', 'SZX'): 2360, ('CGO', 'URC'): 2560, ('CGO', 'XMN'): 1360, ('CKG', 'CAN'): 1650, 
    ('CKG', 'HAK'): 1900, ('CKG', 'KMG'): 1180, ('CKG', 'LXA'): 2730, ('CKG', 'SWA'): 1740, 
    ('CKG', 'SYX'): 2230, ('CKG', 'SZX'): 1940, ('CKG', 'URC'): 2750, ('CKG', 'WUH'): 1250, 
    ('CTU', 'CAN'): 2070, ('CTU', 'HAK'): 1740, ('CTU', 'KMG'): 1410, ('CTU', 'LHW'): 1110, 
    ('CTU', 'LXA'): 2590, ('CTU', 'SYX'): 2680, ('CTU', 'SZX'): 2350, ('CTU', 'URC'): 2860, 
    ('CTU', 'WUH'): 1470, ('CZX', 'CAN'): 1460, ('CZX', 'CTU'): 1600, ('CZX', 'SZX'): 1540, 
    ('DLC', 'CAN'): 2190, ('DLC', 'CGO'): 960, ('DLC', 'CKG'): 1950, ('DLC', 'CTU'): 2130, 
    ('DLC', 'FOC'): 1680, ('DLC', 'HAK'): 2700, ('DLC', 'HGH'): 1240, ('DLC', 'KMG'): 2880, 
    ('DLC', 'NKG'): 1000, ('DLC', 'SHA'): 1130, ('DLC', 'SZX'): 2460, ('DLC', 'TAO'): 1000, 
    ('DLC', 'WUH'): 1490, ('DLC', 'XIY'): 1410, ('DLC', 'XMN'): 1890, ('FOC', 'CAN'): 1480, 
    ('FOC', 'CKG'): 1610, ('FOC', 'CTU'): 1920, ('FOC', 'KMG'): 2260, ('FOC', 'LHW'): 2060, 
    ('FOC', 'WUH'): 1050, ('FOC', 'XIY'): 1680, ('HGH', 'CAN'): 1550, ('HGH', 'CKG'): 2000, 
    ('HGH', 'CTU'): 2230, ('HGH', 'HAK'): 1940, ('HGH', 'JHG'): 2200, ('HGH', 'KMG'): 2390, 
    ('HGH', 'LHW'): 1760, ('HGH', 'SYX'): 2510, ('HGH', 'SZX'): 1650, ('HGH', 'URC'): 3280, 
    ('HGH', 'XIY'): 1540, ('HRB', 'CAN'): 3780, ('HRB', 'CGO'): 1820, ('HRB', 'CKG'): 2480, 
    ('HRB', 'CTU'): 3050, ('HRB', 'CZX'): 1740, ('HRB', 'FOC'): 2350, ('HRB', 'HAK'): 3330, 
    ('HRB', 'HGH'): 2230, ('HRB', 'KMG'): 4100, ('HRB', 'NKG'): 1740, ('HRB', 'SHA'): 1810, 
    ('HRB', 'SYX'): 3480, ('HRB', 'SZX'): 3360, ('HRB', 'TAO'): 1570, ('HRB', 'TSN'): 1250, 
    ('HRB', 'WUH'): 2050, ('HRB', 'XIY'): 1980, ('HRB', 'XMN'): 2550, ('JJN', 'CAN'): 1120, 
    ('JJN', 'CKG'): 1510, ('JJN', 'CTU'): 1750, ('JJN', 'KMG'): 1890, ('KMG', 'CAN'): 1970, 
    ('KMG', 'HAK'): 1440, ('KMG', 'JHG'): 2010, ('KMG', 'LHW'): 2050, ('KMG', 'LXA'): 2480, 
    ('KMG', 'SWA'): 1830, ('KMG', 'SYX'): 1810, ('KMG', 'SZX'): 2220, ('KMG', 'URC'): 3400, 
    ('KMG', 'WUH'): 1660, ('KMG', 'XIY'): 2060, ('LHW', 'CAN'): 2210, ('LHW', 'SZX'): 2100, 
    ('NKG', 'CAN'): 1710, ('NKG', 'CKG'): 1620, ('NKG', 'CTU'): 2150, ('NKG', 'FOC'): 920, 
    ('NKG', 'HAK'): 1940, ('NKG', 'JJN'): 1020, ('NKG', 'KMG'): 2160, ('NKG', 'LHW'): 1650, 
    ('NKG', 'SYX'): 1960, ('NKG', 'SZX'): 2030, ('NKG', 'URC'): 3380, ('NKG', 'XIY'): 1180, 
    ('NKG', 'XMN'): 1110, ('SHA', 'CAN'): 1780, ('SHA', 'CKG'): 1870, ('SHA', 'CTU'): 2560, 
    ('SHA', 'FOC'): 1030, ('SHA', 'HAK'): 1750, ('SHA', 'JHG'): 2350, ('SHA', 'JJN'): 1350, 
    ('SHA', 'LHW'): 1860, ('SHA', 'SWA'): 1220, ('SHA', 'SYX'): 2620, ('SHA', 'SZX'): 2030, 
    ('SHA', 'TAO'): 1660, ('SHA', 'URC'): 3280, ('SHA', 'WUH'): 2060, ('SHA', 'XIY'): 1520, 
    ('SHA', 'XMN'): 1820, ('SHA', 'ZHA'): 1760, ('SZX', 'HAK'): 1220, ('SZX', 'SYX'): 1120, 
    ('TAO', 'CAN'): 2010, ('TAO', 'CGO'): 930, ('TAO', 'CKG'): 1910, ('TAO', 'CTU'): 1690, 
    ('TAO', 'HAK'): 2300, ('TAO', 'HGH'): 900, ('TAO', 'KMG'): 2660, ('TAO', 'LHW'): 1750, 
    ('TAO', 'NKG'): 1200, ('TAO', 'SYX'): 2640, ('TAO', 'SZX'): 2870, ('TAO', 'WUH'): 1300, 
    ('TAO', 'XIY'): 1510, ('TAO', 'XMN'): 1590, ('TSN', 'CAN'): 2260, ('TSN', 'CKG'): 1540, 
    ('TSN', 'CTU'): 2380, ('TSN', 'FOC'): 1630, ('TSN', 'HAK'): 2470, ('TSN', 'HGH'): 1770, 
    ('TSN', 'KMG'): 2750, ('TSN', 'SHA'): 2120, ('TSN', 'SZX'): 2360, ('TSN', 'URC'): 2780, 
    ('TSN', 'WUH'): 1150, ('TSN', 'XIY'): 1410, ('TSN', 'XMN'): 1900, ('URC', 'CAN'): 3410, 
    ('URC', 'HAK'): 3850, ('URC', 'LHW'): 1920, ('URC', 'SZX'): 3460, ('URC', 'WUH'): 2800, 
    ('URC', 'XIY'): 2660, ('WUH', 'CAN'): 1930, ('WUH', 'HAK'): 1410, ('WUH', 'SYX'): 1690, 
    ('WUH', 'SZX'): 2080, ('WUX', 'CAN'): 1540, ('WUX', 'CKG'): 1410, ('WUX', 'CTU'): 2090, 
    ('WUX', 'KMG'): 2640, ('WUX', 'SZX'): 1690, ('XIY', 'CAN'): 1850, ('XIY', 'HAK'): 2210, 
    ('XIY', 'LXA'): 2500, ('XIY', 'SYX'): 2660, ('XIY', 'SZX'): 2380, ('XMN', 'CAN'): 1670, 
    ('XMN', 'CKG'): 1840, ('XMN', 'CTU'): 2060, ('XMN', 'HAK'): 1180, ('XMN', 'KMG'): 2170, 
    ('XMN', 'LHW'): 2150, ('XMN', 'URC'): 3730, ('XMN', 'WUH'): 990, ('XMN', 'XIY'): 2270, 
    ('BJS', 'CGQ'): 2000, ('BJS', 'CSX'): 1780, ('BJS', 'HFE'): 1710, ('BJS', 'INC'): 1410, 
    ('CAN', 'INC'): 2030, ('CGQ', 'CAN'): 3010, ('CGQ', 'CKG'): 2560, ('CGQ', 'CSX'): 2250, 
    ('CGQ', 'CTU'): 2700, ('CGQ', 'HAK'): 3410, ('CGQ', 'HGH'): 2140, ('CGQ', 'NKG'): 1550, 
    ('CGQ', 'SHA'): 1850, ('CGQ', 'SJW'): 1360, ('CGQ', 'SYX'): 3310, ('CGQ', 'SZX'): 3320, 
    ('CGQ', 'TAO'): 1130, ('CGQ', 'WUH'): 2040, ('CGQ', 'XIY'): 1910, ('CGQ', 'XMN'): 2430, 
    ('CSX', 'CKG'): 1400, ('CSX', 'CTU'): 1470, ('CSX', 'DLC'): 1790, ('CSX', 'KMG'): 1400, 
    ('CSX', 'TAO'): 1620, ('CSX', 'URC'): 3270, ('CSX', 'XIY'): 1500, ('HFE', 'CAN'): 1290, 
    ('HFE', 'CKG'): 1210, ('HFE', 'CTU'): 1430, ('HFE', 'KMG'): 2100, ('HFE', 'SZX'): 1190, 
    ('HRB', 'CSX'): 2250, ('HRB', 'HFE'): 1840, ('NKG', 'CSX'): 970, ('SHA', 'CSX'): 2200, 
    ('SHA', 'INC'): 1980, ('SHA', 'KMG'): 2340, ('SHE', 'CAN'): 2730, ('SHE', 'CGO'): 1380, 
    ('SHE', 'CKG'): 2250, ('SHE', 'CSX'): 2100, ('SHE', 'CTU'): 2690, ('SHE', 'CZX'): 1340, 
    ('SHE', 'HAK'): 2880, ('SHE', 'HGH'): 2180, ('SHE', 'KMG'): 3200, ('SHE', 'NKG'): 1640, 
    ('SHE', 'SHA'): 2030, ('SHE', 'SYX'): 3410, ('SHE', 'SZX'): 3300, ('SHE', 'TAO'): 1150, 
    ('SHE', 'URC'): 2940, ('SHE', 'WUH'): 1830, ('SHE', 'WUX'): 1390, ('SHE', 'XIY'): 1840, 
    ('SHE', 'XMN'): 2150, ('SJW', 'CAN'): 1790, ('SJW', 'SHA'): 1200, ('SYX', 'CSX'): 1890, 
    ('TSN', 'CSX'): 1390}

if __name__ == "__main__":
    folders: list[Path] = [Path("2022-02-17") / Path("2022-01-25"), Path("2022-03-29") / Path("2022-02-13")]
    
    url = "https://flights.ctrip.com/itinerary/api/12808/products"
    header = {"Content-Type": "application/json;charset=utf-8", 
              "Accept": "application/json", 
              "Accept-Language": "zh-cn", 
              "Origin": "https://flights.ctrip.com", 
              "Host": "flights.ctrip.com", 
              "Referer": "https://flights.ctrip.com/international/search/domestic", }
    payload = {"flightWay": "Oneway", "classType": "ALL", "hasChild": False, "hasBaby": False, "searchIndex": 1}
    
    for folder in folders:
        for file in folder.iterdir():
            if not file.match("*.xlsx") or '_' in file.name:
                continue
            print(f"\r{folder.name}: {file.name} ", end = "getting...")
            filename = file.name.split('~')
            dcity = filename[0]
            acity = filename[1].strip(".xlsx")
            if totalfare.get((dcity, acity)) or totalfare.get((acity, dcity)):
                continue
            totalfare[(dcity, acity)] = 0
            dcityname = __airportCity.get(dcity)
            acityname = __airportCity.get(acity)
            
            header["User-Agent"] = __userAgents[int(__lenAgents * random())]
            payload["airportParams"] = [{"dcity": dcity, "acity": acity, "dcityname": dcityname,
                                                "acityname": acityname, "date": "2022-02-22",}]

            try:
                for _ in range(3):
                    response = post(url, data = dumps(payload), headers = header, proxies = proxy(), timeout = 10)
                    try:
                        routeList = loads(response.text).get('data').get('routeList')
                        response.close
                        break
                    except:
                        continue
                else:
                    print("\n...no data")
                    break
            except:
                print("\n...error")
                break
            
            for route in routeList:
                if route.get('legs'):
                    if len(route.get('legs')) == 1:
                        try:
                            for cabin in route['legs'][0]["characteristic"]["standardPrices"]:
                                if cabin["cabinClass"] == "Y":
                                    totalfare[(dcity, acity)] = cabin["price"]
                                    break
                            else:
                                continue
                            break
                        except:
                            continue
            else:
                print("\n...failed")
    with open("totalfare.txt", "a", encoding = "UTF-8") as file:
        file.write(str(totalfare) + "\n")
