import pandas
import openpyxl
from openpyxl import styles
from datetime import datetime, date
from zipfile import ZipFile
from pathlib import Path

class Rebuilder():
    '''
    Rebuilder
    -----
    Rebuild all data by filtering factors that influence ticket rate.
    
    Here are 6 significant factors in class property:
    - `airline`: Airlines' rates, competition and flight time;
    - `city`: City class, location and airport throughput;
    - `buyday`: Day of purchase before flights;
    - `flyday`: Date and weekday of flights;
    - `time`: Dep time of flights;
    - `type`: Aircraft Type.
    
    Data
    -----
    `append`: Append a excel file in `Path`.
    
    `zip`: Load excel files from a zip file in the given path.
    
    Parameters
    -----
    root: `Path`, path of collection. 
    
    This should be the same for a class unless their data 
    are continuous or related.
    
    day_limit: `int`, limit of processing days.
            default: `0`, no limits
    
    '''
    def __init__(self, root: Path = Path(), day_limit: int = 0) -> None:
        self.day_limit = day_limit
        self.__root = root
        self.__title = {
            "airline": {"airlines": [], "dates": [], 
                        "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                  16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
            "city": ("航线", "总价", "平均折扣", "航班总量",
                     "出发地", "机场系数", "地理位置", "城市级别", "旅游", 
                     "到达地", "机场系数", "地理位置", "城市级别", "旅游", ), 
            "buyday": [], 
            "flyday": [], 
            "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                     13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
            "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                     "日均数量", "大型折扣", "日均数量", "平均折扣", 
                     "小型", "中型", "大型")}
        
        self.master = {"airline": {}, "city": {}, "buyday": {}, 
                       "flyday": {}, "time": {}, "type": {},}
        
        self.files: list[Path] = []
        self.__unlink: list[Path] = []
        
        self.__warn = 0
        
        self.__airportCity = {
            'BJS':'北京','CAN':'广州','SHA':'上海','CTU':'成都',
            'SZX':'深圳','KMG':'昆明','XIY':'西安','CKG':'重庆',
            'HGH':'杭州','NKG':'南京','CGO':'郑州','XMN':'厦门',
            'WUH':'武汉','CSX':'长沙','TAO':'青岛','HAK':'海口',
            'URC':'乌鲁木齐','TSN':'天津','KWE':'贵阳','SHE':'沈阳',
            'HRB':'哈尔滨','SYX':'三亚','DLC':'大连','TNA':'济南',
            'NNG':'南宁','LHW':'兰州','FOC':'福州','TYN':'太原',
            'CGQ':'长春','KHN':'南昌','HET':'呼和浩特','NGB':'宁波',
            'WNZ':'温州','ZUH':'珠海','HFE':'合肥','SJW':'石家庄',
            'INC':'银川','YTY':'扬州','KHG':'喀什','LYG':'连云港',
            'YNT':'烟台','KWL':'桂林','JJN':'泉州','WUX':'无锡',
            'SWA':'揭阳','XNN':'西宁','LJG':'丽江','JHG':'西双版纳',
            'LXA':'拉萨','MIG':'绵阳','CZX':'常州','NTG':'南通',
            'YIH':'宜昌','WEH':'威海','XUZ':'徐州','DYG':'张家界',
            'ZHA':'湛江','DSN':'鄂尔多斯','BHY':'北海','LYI':'临沂',
            'HLD':'呼伦贝尔','HUZ':'惠州','UYN':'榆林','YCU':'运城',
            'HIA':'淮安','BAV':'包头','ZYI':'遵义','KRL':'库尔勒',
            'LUM':'德宏','YNZ':'盐城','KOW':'赣州','YIW':'义乌',
            'XFN':'襄阳','CIF':'赤峰','LZO':'泸州','DLU':'大理',
            'AKU':'阿克苏','YNJ':'延吉','ZYI':'遵义','HTN':'和田',
            'LYA':'洛阳','WDS':'十堰','HSN':'舟山','JNG':'济宁',
            'YIN':'伊宁','ENH':'恩施','ACX':'兴义','HYN':'台州',
            'DAT':'大同','BSD':'保山','BFJ':'毕节','NNY':'南阳',
            'WXN':'万州','TGO':'通辽','CGD':'常德','HNY':'衡阳',
            'MDG':'牡丹江','RIZ':'日照','NAO':'南充','YBP':'宜宾',
            'LZH':'柳州','XIC':'西昌','TCZ':'腾冲',}
        
        self.__airports = {'北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, '广州': 1, 
                           '成都双流': 0.8, '成都天府': 0.8, '深圳': 0.75, '昆明': 0.7, '西安': 0.65, 
                           '重庆': 0.65, '杭州': 0.6, '南京': 0.45, '郑州': 0.4, '厦门': 0.4, 
                           '武汉': 0.4, '长沙': 0.4, '青岛': 0.4, '海口': 0.35, '乌鲁木齐': 0.35, 
                           '天津': 0.35, '贵阳': 0.3, '哈尔滨': 0.3, '沈阳': 0.3, '三亚': 0.3, 
                           '大连': 0.3, '济南': 0.25, '南宁': 0.25, '兰州': 0.2, '福州': 0.2, 
                           '太原': 0.2, '长春': 0.2, '南昌': 0.2, '呼和浩特': 0.2, '宁波': 0.2, 
                           '温州': 0.2, '珠海': 0.2, '合肥': 0.2, '石家庄': 0.15, '银川': 0.15, 
                           '烟台': 0.15, '桂林': 0.1, '泉州': 0.1, '无锡': 0.1, '揭阳': 0.1, 
                           '西宁': 0.1, '丽江': 0.1, '西双版纳': 0.1, '南阳': 0.1,}
        self.__cityClass =  {'北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, 
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
        self.__cityLocation = {'北京首都': 0.2, '北京大兴': 0.2, '上海虹桥': 0, '上海浦东': 0, 
                               '北京': 0.2, '成都': 0.8, '上海': 0, '广州': 0.1, '重庆': 0.7, 
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
        self.__tourism = {'桂林', '西双版纳', '丽江', '张家界', '鄂尔多斯', '呼伦贝尔', '德宏', '大理', 
                          '拉萨', '乌鲁木齐', '成都', '重庆', '贵阳', '昆明',}
        self.__totalfare = {
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
    
    def append_file(self, file: Path) -> Path:
        '''Append data to rebuilder for further processes.
        
        Return `None` for loading failure or none-excel file.'''
        try:
            datetime.fromisoformat(file.parent.name)
        except:
            print("WARN: File not in a standard path name of collecting date!")
            return None
        if file.match("*.xlsx"):
            self.files.append(file)
            return file
        else:
            return None
    
    def append_folder(self, path: Path) -> int:
        '''Load files from a folder, 
        whose name should be data's collecting date.
        
        Return the number of excels loaded.'''
        files = 0
        try:
            datetime.fromisoformat(path.name)
        except:
            print("WARN: File not in a standard path name of collecting date!")
            return files
        for file in path.iterdir():
            if file.match("*.xlsx") and "_" not in file.name:
                self.files.append(file)
                files += 1
        return files
    
    def append_zip(self, path: Path, file: Path | str = "orig.zip") -> int:
        '''
        Append data from a zip file to process.
        
        - path: `Path`, where to extract the zip file.
        
        - file: `Path` | `str`, the zip file path or name.
        
                default: `orig.zip` as a collection's extract.
        
        return the number of excels loaded.
        '''
        try:
            if path.is_dir:
                datetime.fromisoformat(path.name)
            else:
                raise ValueError("Parameter `path` should be a folder!")
        except:
            raise ValueError("Not a standard path name of collecting date!")
        files = 0
        try:
            if isinstance(file, str):
                zip = ZipFile(Path(path / Path(file)), "r")
            elif isinstance(file, Path):
                zip = ZipFile(file, "r")
            else:
                print(f"Warn: {file} is not a Path or str!")
                return file
            zip.extractall(path)
            zip.close
        except:
            print(f"Warn: {file} not found in", path.name)
            self.__warn += 1
        for file in path.iterdir():
            files += 1
            if file.match("*.xlsx"):
                self.files.append(file)
                self.__unlink.append(file)
        return files
    
    def reset(self, unlink_file: bool = True, clear_data: bool = True) -> None:
        '''- Clear all files in the data process queue
        - Unlink excels zip file extracted if unlink_file == `True`
        - Clear all rebuilt data if clear_data == `True`'''
        if unlink_file and len(self.__unlink):
            for file in self.__unlink:
                file.unlink()
        self.files.clear()
        self.__unlink.clear()
        if clear_data:
            self.__title = {
                "airline": {"airlines": [], "dates": [], 
                            "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                                    16, 17, 18, 19, 20, 21, 22, 23, 24]}, 
                "city": ("航线", "总价", "平均折扣", "航班总量", 
                         "出发地", "机场系数", "地理位置", "城市级别", "旅游", 
                         "到达地", "机场系数", "地理位置", "城市级别", "旅游", ), 
                "buyday": [], 
                "flyday": [], 
                "time": ("航线", "平均折扣", 5, 6, 7, 8, 9, 10, 11, 12, 
                        13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24),  
                "type": ("航线", "小型折扣", "日均数量", "中型折扣", 
                        "日均数量", "大型折扣", "日均数量", "平均折扣", 
                        "小型", "中型", "大型")}
            
            self.master = {"airline": {}, "city": {}, "buyday": {}, 
                           "flyday": {}, "time": {}, "type": {},}
    
    @property
    def airline(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["airline"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rairline data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 2, 4, 5, 6, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[2][:2] + "-" + item[3][:2]
                date = item[0].date()
                if item[1] not in self.__title["airline"]["airlines"]:
                    self.__title["airline"]["airlines"].append(item[1])
                if date not in self.__title["airline"]["dates"]:
                    self.__title["airline"]["dates"].append(date)
                if datadict.get(name):
                    datadict[name]["counts"] += 1
                    datadict[name]["rates"] += item[5]
                    if datadict[name].get(item[1]):
                        datadict[name][item[1]]["rate"] += item[5]
                        datadict[name][item[1]]["count"] += 1
                        if datadict[name][item[1]].get(item[4].hour):
                            datadict[name][item[1]][item[4].hour]["rate"] += item[5]
                            datadict[name][item[1]][item[4].hour]["count"] += 1
                        else:
                            datadict[name][item[1]][item[4].hour] = {"rate": item[5], "count": 1}
                    else:
                        datadict[name][item[1]] = {"rate": item[5], "count": 1, 
                                               item[4].hour: {"rate": item[5], "count": 1},}
                else:
                    datadict[name] = {item[1]: {"rate": item[5], "count": 1, 
                                            item[4].hour: {"rate": item[5], "count": 1},},
                                  "counts": 1, "rates": item[5],}
        print()
        self.master["airline"] = datadict
        return "airline", self.__excel_format(self.__airline(datadict, self.__title["airline"]), 
                                              B_width = 12)
    
    @staticmethod
    def __airline(datadict: dict, title: dict) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        sheets = ["航线航司 - 每日航班密度", "航线时刻 - 时刻航班密度", 
                  "航线时刻 - 航司竞争", "航线航司 - 机票折扣总览", ]
        for airline in title["airlines"]:
            sheets.append(airline)
        for sheet in sheets:
            wb.create_sheet(sheet)
        del sheets
        
        ws = wb["航线航司 - 每日航班密度"]
        ws.append(["航线", "运营航司数量"] + title["airlines"])
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(1/4) >>", int(idct / total * 100), end = "%")
            row = [name, len(datadict[name]) - 2]
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["count"] / len(title["dates"]))
                else:
                    row.append(None)
            ws.append(row)
        
        wsd = wb["航线时刻 - 时刻航班密度"]
        wsd.append(["航线", "运营航司数量"] + title["hours"])
        wsc = wb["航线时刻 - 航司竞争"]
        wsc.append(["航线", "运营航司数量"] + title["hours"])
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(2/4) >>", int(idct / total * 100), end = "%")
            rowc = [name, len(datadict[name]) - 2]
            rowd = [name, len(datadict[name]) - 2]
            for hour in title["hours"]:
                count = 0
                density = 0
                for airline in title["airlines"]:
                    if datadict[name].get(airline):
                        if datadict[name][airline].get(hour):
                            count += 1
                            density += datadict[name][airline][hour]["count"]
                if count:
                    rowc.append(count)
                    rowd.append(density / len(title["dates"]))
                else:
                    rowc.append(None)
                    rowd.append(None)
            wsc.append(rowc)
            wsd.append(rowd)
        
        ws = wb["航线航司 - 机票折扣总览"]
        ws.append(["航线", "平均折扣"] + title["airlines"])
        idct = 0
        for name in datadict.keys():
            idct += 1
            print("\rairline sheet(3/4) >>", int(idct / total * 100), end = "%")
            row = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for airline in title["airlines"]:
                if datadict[name].get(airline):
                    row.append(datadict[name][airline]["rate"] / datadict[name][airline]["count"])
                else:
                    row.append(None)
            ws.append(row)
        
        idct = 0
        total *= len(title["airlines"])
        for airline in title["airlines"]:
            ws = wb[airline]
            ws.append(["航线", "平均折扣"] + title["hours"])
            for name in datadict.keys():
                idct += 1
                print("\rairline sheet(4/4) >>", int(idct / total * 100), end = "%")
                if not datadict[name].get(airline):
                    continue
                row = [name, datadict[name][airline]["rate"] / datadict[name][airline]["count"]]
                for hour in title["hours"]:
                    if datadict[name][airline].get(hour):
                        row.append(datadict[name][airline][hour]["rate"] /
                                   datadict[name][airline][hour]["count"])
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def buyday(self) -> tuple[str, openpyxl.Workbook]:
        '''
        Notes
        -----
        - Recommend input files: on one collect date
        
        - Day limits: Not in use
        
        Outputs
        -----
        - Date: date of flight
        
        '''
        datadict = self.master["buyday"]
        min_day = self.day_limit if self.day_limit else date.fromisoformat(self.__root.name).toordinal()
        max_day = 0
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rbuyday data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                name = item[1][:2] + "-" + item[2][:2]
                day = item[0].toordinal()
                if min_day > day:
                    min_day = day
                elif max_day < day:
                    max_day = day
                if datadict.get(name):
                    datadict[name]["rates"] += item[3]
                    datadict[name]["counts"] += 1
                    if datadict[name].get(day):
                        datadict[name][day]["rate"] += item[3]
                        datadict[name][day]["count"] += 1
                    else:
                        datadict[name][day] = {"rate": item[3], "count": 1}
                else:
                    datadict[name] = {day: {"rate": item[3], "count": 1}, 
                                  "rates": item[3], "counts": 1}
        if max_day not in self.__title["buyday"] or min_day not in self.__title["buyday"]:
            self.__title["buyday"] = [[], "航线", "平均折扣", ]
            for day in range(min_day, max_day + 1):
                key = date.fromordinal(day)
                self.__title["buyday"].append(key)
                self.__title["buyday"][0].append(key.isoweekday())
        self.master["buyday"] = datadict
        print()
        return "buyday", self.__excel_format(self.__buyday(datadict, self.__title["buyday"]), 
                                             freeze_panes = 'C3')
    
    @staticmethod
    def __buyday(datadict: dict, title: list) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        wsd = wb.create_sheet("航线日密度")
        wsd.append(["航线", "平均密度"] + title[3:])
        wsd.append([None, "(星期)",] + title[0])
        for row in wsd.iter_rows(1, 1, 3, wsd.max_column):
            for cell in row:
                cell.number_format = "m\"月\"d\"日\""
        for sheet in ("高价", "低价", "均价", "总价"):
            ws = wb.create_sheet(sheet)
            ws.append(title[1:])
            ws.append([None, "(星期)",] + title[0])
            for row in ws.iter_rows(1, 1, 3, ws.max_column):
                for cell in row:
                    cell.number_format = "m\"月\"d\"日\""
        row = {}
        sum = idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rbuyday sheets >>", int(idct / total * 100), end = "%")
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, 0, ]
            countd = 0
            for day in title[3:]:
                day = day.toordinal()
                if datadict[name].get(day):
                    if datadict[name][day]["count"]:
                        countd += 1
                        rowd.append(datadict[name][day]["count"])
                        rowd[1] += datadict[name][day]["count"]
                        row[name].append(datadict[name][day]["rate"] / datadict[name][day]["count"])
                    else:
                        rowd.append(None)
                        row[name].append(None)
                else:
                    row[name].append(None)
            ws.append(row[name])
            rowd[1] /= countd
            wsd.append(rowd)
        sum /= len(datadict)
        for value in row.values():
            if value[1] - sum >= 0.05:
                wb["高价"].append(value)
            elif sum - value[1] <= 0.05:
                wb["低价"].append(value)
            else:
                wb["均价"].append(value)
        return wb
    
    @property
    def city(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["city"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rcity data >>", int(idct / total * 100), end = "%")
            filename = file.name.split('~')
            dcity = filename[0]
            acity = filename[1].strip(".xlsx")
            flag = True if acity == "BJS" or acity == "SHA" or acity == "CTU" or \
                dcity == "BJS" or dcity == "SHA" or dcity == "CTU" else False
            
            if self.__totalfare.get((dcity, acity), 0):
                totalfare = self.__totalfare.get((dcity, acity))
            elif self.__totalfare.get((acity, dcity), 0):
                totalfare = self.__totalfare.get((acity, dcity))
            else:
                totalfare = 0
            
            dcity = self.__airportCity.get(dcity)
            d_tourism = True if dcity in self.__tourism else False
            acity = self.__airportCity.get(acity)
            a_tourism = True if acity in self.__tourism else False
            
            if datadict.get(dcity):
                if not datadict.get(dcity).get(acity):
                    datadict[dcity][acity] = [totalfare, ]
            else:
                datadict[dcity] = {
                    dcity: [self.__airports.get(dcity, 0.05), 
                            self.__cityLocation.get(dcity, 0.5), 
                            self.__cityClass.get(dcity, 0.2), d_tourism],
                    acity: [totalfare, ]}
            
            if datadict.get(acity):
                if not datadict.get(acity).get(dcity):
                    datadict[acity][dcity] = [totalfare, ]
            else:
                datadict[acity] = {
                    acity: [self.__airports.get(acity, 0.05), 
                            self.__cityLocation.get(acity, 0.5), 
                            self.__cityClass.get(acity, 0.2), a_tourism],
                    dcity: [totalfare, ]}
            
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                if flag:
                    dcity = item[1][:2] if item[1][:2] == "北京" or item[1][:2] \
                        == "上海" or item[1][:2] == "成都" else item[1]
                    acity = item[2][:2] if item[2][:2] == "北京" or item[2][:2] \
                        == "上海" or item[2][:2] == "成都" else item[2]
                else:
                    dcity, acity = item[1], item[2]
                datadict[dcity][acity].append(item[3])
            
        self.master["city"] = datadict
        print()
        return "city", self.__excel_format(self.__city(datadict, self.__title["city"]), 
                                           False, wdA = 14, freeze_panes = 'E2')
    
    @staticmethod
    def __city(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("航线与城市总览")
        ws.append(title)
        cities = sorted(datadict.keys())
        idct = 0
        total = len(cities)
        for d_idx in range(total):
            dcity = cities[d_idx]
            idct += 1
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            for a_idx in range(d_idx + 1, total):
                acity = cities[a_idx]
                if not datadict[dcity].get(acity):
                    continue
                avg = 0
                sum = len(datadict[dcity][acity]) - 1
                for rate in datadict[dcity][acity][1:]:
                    avg += rate
                row = [f"{dcity}-{acity}",] + \
                    [datadict[dcity][acity][0], avg / sum, sum, dcity, ] + \
                    datadict[dcity][dcity] + [acity, ] + datadict[acity][acity]
                ws.append(row)
                
                avg = 0
                sum = len(datadict[acity][dcity]) - 1
                for rate in datadict[acity][dcity][1:]:
                    avg += rate
                row = [f"{acity}-{dcity}",] + \
                    [datadict[acity][dcity][0], avg / sum, sum, acity, ] + \
                    datadict[acity][acity] + [dcity, ] + datadict[dcity][dcity]
                ws.append(row)
        return wb
    
    @property
    def flyday(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["flyday"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rflyday data >>", int(idct / total * 100), end = "%")
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 9]]
            for item in data.values:
                days = item[0].toordinal() - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
                if days not in self.__title["flyday"]:
                    self.__title["flyday"].append(days)
                fdate = item[0].date().isoformat()
                if datadict.get(name):
                    if datadict[name].get(fdate):
                        if datadict[name][fdate].get(days):
                            datadict[name][fdate][days].append(item[3])
                        else:
                            datadict[name][fdate][days] = [item[3], ]
                    else:
                        datadict[name][fdate] = {days: [item[3], ]}
                else:
                    datadict[name] = {fdate: {days: [item[3], ]}}
        print()
        self.master["flyday"] = datadict
        return "flyday", self.__excel_format(self.__flyday(datadict, self.__title["flyday"]), False)
    
    @staticmethod
    def __flyday(datadict: dict, title: list) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        title.sort()
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rflyday sheets >>", int(idct / total * 100), end = "%")
            ws = wb.create_sheet(name)
            ws.append(["航班日期", ] + title)
            for fdate in datadict[name].keys():
                row = [fdate, ]
                for day in title:
                    if datadict[name][fdate].get(day):
                        sum = 0
                        for rate in datadict[name][fdate][day]:
                            sum += rate
                        row.append(sum / len(datadict[name][fdate][day]))
                    else:
                        row.append(None)
                ws.append(row)
        return wb
    
    @property
    def time(self) -> tuple[str, openpyxl.Workbook]:
        datadict = self.master["time"]
        idct = 0
        total = len(self.files)
        if not datadict.get("date"):
            datadict["date"] = []
        for file in self.files:
            idct += 1
            print("\rtime data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 4, 5, 6, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                if ordinal not in datadict.get("date"):
                    datadict["date"].append(ordinal)
                days = ordinal - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[1][:2] + "-" + item[2][:2]
                if not datadict.get(name):
                    datadict[name] = {"rates": 0, "counts": 0}
                hour = 24 if item[3].hour == 0 else item[3].hour
                if datadict[name].get(hour):
                    if datadict[name][hour].get(ordinal):
                        datadict[name][hour][ordinal]["rate"] += item[4]
                        datadict[name][hour][ordinal]["count"] += 1
                    else:
                        datadict[name][hour][ordinal] = {"rate": item[4], "count": 1}
                else:
                    datadict[name][hour] = {ordinal: {"rate": item[4], "count": 1}}
                datadict[name]["rates"] += item[4]
                datadict[name]["counts"] += 1
        print()
        self.master["time"] = datadict
        return "time", self.__excel_format(self.__time(datadict, self.__title["time"]))
    
    @staticmethod
    def __time(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        for sheet in ("航班密度", "每日平均", "高价", "均价", "低价", "总表"):
            ws = wb.create_sheet(sheet)
            ws.append(title)
        row = {}
        sum = idct = 0
        total = len(datadict)
        datadict["date"].sort()
        for name in datadict.keys():
            idct += 1
            print("\rtime sheets >>", int(idct / total * 100), end = "%")
            if not isinstance(datadict[name], dict):
                continue
            sum += datadict[name]["rates"] / datadict[name]["counts"]
            
            row[name] = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            rowd = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if not datadict[name].get(hour):
                    row[name].append(None)
                    rowd.append(None)
                    continue
                days = len(datadict[name][hour])
                if days:
                    avg = sum = 0
                    for day in datadict[name][hour].keys():
                        avg += datadict[name][hour][day]["rate"]
                        sum += datadict[name][hour][day]["count"]
                    row[name].append(avg / sum)
                    rowd.append(sum / days)
                else:
                    row[name].append(None)
                    rowd.append(None)
            ws.append(row[name])
            wb["航班密度"].append(rowd)
            
            rowa = [name, datadict[name]["rates"] / datadict[name]["counts"]]
            for hour in range(5, 25):
                if datadict[name].get(hour):
                    counts = avg = rates = dates = 0
                    for day in datadict["date"]:
                        if datadict[name].get(hour).get(day):
                            dates += 1
                            for _hour in range(5, 25):
                                if datadict[name].get(_hour):
                                    if datadict[name].get(_hour).get(day):
                                        counts += datadict[name][_hour][day]["count"]
                                        rates += datadict[name][_hour][day]["rate"]
                            avg += datadict[name][hour][day]["rate"] / datadict[name][hour][day]["count"] / (rates / counts)
                    rowa.append(avg / dates)
                else:
                    rowa.append(None)
            
            wb["每日平均"].append(rowa)
            
        sum /= len(datadict)
        for value in row.values():
            if value[1] - sum >= 0.05:
                wb["高价"].append(value)
            elif sum - value[1] <= 0.05:
                wb["低价"].append(value)
            else:
                wb["均价"].append(value)
        return wb
    
    @property
    def type(self) -> tuple[str, openpyxl.Workbook]:
        '''
        Notes
        -----
        - Recommend input files: on one collect date
        
        
        '''
        datadict = self.master["type"]
        idct = 0
        total = len(self.files)
        for file in self.files:
            idct += 1
            print("\rtype data >>", int(idct / total * 100), end = "%")
            data = pandas.read_excel(file).iloc[ : , [0, 3, 4, 5, 9]]
            collDate = datetime.fromisoformat(file.parent.name).toordinal()
            for item in data.values:
                ordinal = item[0].toordinal()
                days = ordinal - collDate
                if self.day_limit and days > self.day_limit:
                    continue
                name = item[2][:2] + "-" + item[3][:2]
                if not datadict.get(name):
                    datadict[name] = {"小": {"rate": 0, "count": 0}, 
                                  "中": {"rate": 0, "count": 0}, 
                                  "大": {"rate": 0, "count": 0},
                                  "dates": set(), "rates": 0, "counts": 0}
                if ordinal not in datadict[name]["dates"]:
                    datadict[name]["dates"].add(ordinal)
                datadict[name][item[1]]["rate"] += item[4]
                datadict[name][item[1]]["count"] += 1
                datadict[name]["rates"] += item[4]
                datadict[name]["counts"] += 1
        print()
        self.master["type"] = datadict
        return "type", self.__excel_format(self.__type(datadict, self.__title["type"]), 
                                           False, freeze_panes = 'B2')
    
    @staticmethod
    def __type(datadict: dict, title: tuple) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.create_sheet("去除单一机型")
        ws.append(title)
        ws = wb.create_sheet("总表")
        ws.append(title)
        idct = 0
        total = len(datadict)
        for name in datadict.keys():
            idct += 1
            print("\rtype sheets >>", int(idct / total * 100), end = "%")
            row = [name, ]
            for key in ("小", "中", "大"):
                count = datadict[name][key].get("count")
                if count:
                    row.append(datadict[name][key]["rate"] / count)
                    row.append(count / len(datadict[name]["dates"]))
                else:
                    row += [None, 0]
            row.append(datadict[name]["rates"] / datadict[name]["counts"])
            idx = ws.max_row + 1
            tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
            ws.append(row + tail)
            if row[2] > 0 or row[6] > 0:
                idx = wb["去除单一机型"].max_row + 1
                if row[2] > 0 and row[6] > 0:
                    tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
                elif row[6] > 0:
                    tail = [None, f"=D{idx}/H{idx}", f"=F{idx}/H{idx}"]
                else:
                    tail = [f"=B{idx}/H{idx}", f"=D{idx}/H{idx}"]
                wb["去除单一机型"].append(row + tail)
        return wb
    
    @staticmethod
    def __excel_format(workbook: openpyxl.Workbook, add_average: bool = True, wdA: int = 11, 
                       wdB: int = 0, freeze_panes: str = 'C2') -> openpyxl.Workbook:
        workbook.remove(workbook.active)
        print("\rformatting sheets...          ")
        for sheet in workbook:
            sheet.freeze_panes = freeze_panes
            if sheet.max_row < 2:
                continue
            if wdA:
                sheet.column_dimensions["A"].width = wdA
            if wdB:
                sheet.column_dimensions["B"].width = wdB
            if add_average:
                sheet.append(("平均", ))
                for col in range(2, sheet.max_column + 1):
                    coordinate = sheet.cell(sheet.max_row, col).coordinate
                    top = sheet.cell(2, col).coordinate
                    bottom = sheet.cell(sheet.max_row - 1, col).coordinate
                    sheet[coordinate] = f"=AVERAGE({top}:{bottom})"
        return workbook
    
    def output(self, *args: tuple[str, openpyxl.Workbook],
               clear: bool = False, path: Path | str = Path('.charts')) -> int:
        """
        Output rebuilt data by property or (name: `str`, excel: `Workbook`).
        
        Parameters
        -----
        clear: `bool`, clear outputed rebuilt data after output.
                default: `False`
        
        path: `Path`, where to output.
                default: `Path('.charts')`
        
        """
        files = 0
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            path.mkdir()
        for arg in args:
            key, file = arg
            name = path / Path(f"{self.__root}_{key}.xlsx")
            if name.exists():
                time = datetime.today().strftime("%H%M%S")
                name = path / Path(f"{self.__root}_{key}_{time}.xlsx")
            file.save(name)
            file.close
            files += 1
            if clear:
                del self.master[key]
                self.master[key] = {}
                if isinstance(self.__title.get(key), dict):
                    del self.__title[key]
                    self.__title[key] = {}
        return files
    


if __name__ == "__main__":
    root = Path("2022-02-17")
    rebuild = Rebuilder(root)
    rebuild.append_zip(root / Path("2022-02-08"))
    rebuild.output(rebuild.time)
    rebuild.reset()