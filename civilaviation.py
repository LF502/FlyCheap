class CivilAviation: 
    '''
    Database for Civil Aviation
    -----
    - airportCity: `dict[str, str]`, 3-digit code to city name
    - airpotyCode: `dict[str, str]`, city / airport name to 3-digit code
    - airports: `dict[str, float]`, airport factor
    - cityClass: `dict[str, float]`, city class factor
    - cityLocation: `dict[str, float]`, city location factor
    - tourism: `set`, inland tourism cities
    - airfare: `dict[tuple[str, str], int]`, 100% route price
    - routes: `set[tuple[str, str]]`, inactive / low-density routes
    
    Methods
    -----
    - Converter: convert city code, city name, airport code...
    - Multi-airport: BJS, SHA, CTU, city name...
    - Routes: routes that can be skipped...
    '''
    def __init__(self) -> None: 

        self.__striptemp = {
            '北京首都', '北京大兴', 
            '上海虹桥', '上海浦东', 
            '成都双流', '成都天府'
            }
        
        self.__airportCity = {
            'BJS': '北京', 'PEK': '北京', 'PKX': '北京', 'SHA': '上海', 
            'PVG': '上海', 'CAN': '广州', 'CTU': '成都', 'TFU': '成都', 
            'SZX': '深圳', 'KMG': '昆明', 'XIY': '西安', 'CKG': '重庆', 
            'HGH': '杭州', 'NKG': '南京', 'CGO': '郑州', 'XMN': '厦门', 
            'WUH': '武汉', 'CSX': '长沙', 'TAO': '青岛', 'HAK': '海口', 
            'URC': '乌鲁木齐', 'TSN': '天津', 'KWE': '贵阳', 'SHE': '沈阳', 
            'HRB': '哈尔滨', 'SYX': '三亚', 'DLC': '大连', 'TNA': '济南', 
            'NNG': '南宁', 'LHW': '兰州', 'FOC': '福州', 'TYN': '太原', 
            'CGQ': '长春', 'KHN': '南昌', 'HET': '呼和浩特', 'NGB': '宁波', 
            'WNZ': '温州', 'ZUH': '珠海', 'HFE': '合肥', 'SJW': '石家庄', 
            'INC': '银川', 'YTY': '扬州', 'KHG': '喀什', 'LYG': '连云港', 
            'YNT': '烟台', 'KWL': '桂林', 'JJN': '泉州', 'WUX': '无锡', 
            'SWA': '揭阳', 'XNN': '西宁', 'LJG': '丽江', 'JHG': '西双版纳', 
            'LXA': '拉萨', 'MIG': '绵阳', 'CZX': '常州', 'NTG': '南通', 
            'YIH': '宜昌', 'WEH': '威海', 'XUZ': '徐州', 'DYG': '张家界', 
            'ZHA': '湛江', 'DSN': '鄂尔多斯', 'BHY': '北海', 'LYI': '临沂', 
            'HLD': '呼伦贝尔', 'HUZ': '惠州', 'UYN': '榆林', 'YCU': '运城', 
            'HIA': '淮安', 'BAV': '包头', 'ZYI': '遵义', 'KRL': '库尔勒', 
            'LUM': '德宏', 'YNZ': '盐城', 'KOW': '赣州', 'YIW': '义乌', 
            'XFN': '襄阳', 'CIF': '赤峰', 'LZO': '泸州', 'DLU': '大理', 
            'AKU': '阿克苏', 'YNJ': '延吉', 'ZYI': '遵义', 'HTN': '和田', 
            'LYA': '洛阳', 'WDS': '十堰', 'HSN': '舟山', 'JNG': '济宁', 
            'YIN': '伊宁', 'ENH': '恩施', 'ACX': '兴义', 'HYN': '台州', 
            'DAT': '大同', 'BSD': '保山', 'BFJ': '毕节', 'NNY': '南阳', 
            'WXN': '万州', 'TGO': '通辽', 'CGD': '常德', 'HNY': '衡阳', 
            'MDG': '牡丹江', 'RIZ': '日照', 'NAO': '南充', 'YBP': '宜宾', 
            'LZH': '柳州', 'XIC': '西昌', 'TCZ': '腾冲', 
            }
        
        self.__airportCode = {
            '成都天府': 'TFU', '成都双流': 'CTU', '北京大兴': 'PKX', 
            '北京首都': 'PEK', '上海浦东': 'PVG', '上海虹桥': 'SHA', 
            '阿尔山': 'YIE', '阿克苏': 'AKU', '阿拉善右旗': 'RHT', 
            '阿拉善左旗': 'AXF', '阿勒泰': 'AAT', '阿里': 'NGQ', '澳门': 'MFM',
            '安庆': 'AQG', '安顺': 'AVA', '鞍山': 'AOG', '巴彦淖尔': 'RLK', 
            '百色': 'AEB', '包头': 'BAV', '保山': 'BSD', '北海': 'BHY',
            '北京': 'BJS', '白城': 'DBC', '白山': 'NBS', '毕节': 'BFJ', 
            '博乐': 'BPL', '重庆': 'CKG', '昌都': 'BPX', '常德': 'CGD',
            '常州': 'CZX', '朝阳': 'CHG', '成都': 'CTU', '池州': 'JUH', 
            '赤峰': 'CIF', '揭阳': 'SWA', '长春': 'CGQ', '长沙': 'CSX',
            '长治': 'CIH', '承德': 'CDE', '沧源': 'CWJ', '达县': 'DAX', 
            '大理': 'DLU', '大连': 'DLC', '大庆': 'DQA', '大同': 'DAT',
            '丹东': 'DDG', '稻城': 'DCY', '东营': 'DOY', '敦煌': 'DNH', 
            '芒市': 'LUM', '额济纳旗': 'EJN', '鄂尔多斯': 'DSN', '恩施': 'ENH',
            '二连浩特': 'ERL', '佛山': 'FUO', '福州': 'FOC', '抚远': 'FYJ', 
            '阜阳': 'FUG', '赣州': 'KOW', '格尔木': 'GOQ', '固原': 'GYU',
            '广元': 'GYS', '广州': 'CAN', '贵阳': 'KWE', '桂林': 'KWL', 
            '哈尔滨': 'HRB', '哈密': 'HMI', '海口': 'HAK', '海拉尔': 'HLD',
            '邯郸': 'HDG', '汉中': 'HZG', '杭州': 'HGH', '合肥': 'HFE', 
            '和田': 'HTN', '黑河': 'HEK', '呼和浩特': 'HET', '淮安': 'HIA',
            '怀化': 'HJJ', '黄山': 'TXN', '惠州': 'HUZ', '鸡西': 'JXA', 
            '济南': 'TNA', '济宁': 'JNG', '加格达奇': 'JGD', '佳木斯': 'JMU',
            '嘉峪关': 'JGN', '金昌': 'JIC', '金门': 'KNH', '锦州': 'JNZ', 
            '嘉义': 'CYI', '西双版纳': 'JHG', '建三江': 'JSJ', '泉州': 'JJN',
            '井冈山': 'JGS', '景德镇': 'JDZ', '九江': 'JIU', '九寨沟': 'JZH', 
            '喀什': 'KHG', '凯里': 'KJH', '康定': 'KGT', '克拉玛依': 'KRY',
            '库车': 'KCA', '库尔勒': 'KRL', '昆明': 'KMG', '拉萨': 'LXA', 
            '兰州': 'LHW', '黎平': 'HZH', '丽江': 'LJG', '荔波': 'LLB',
            '连云港': 'LYG', '六盘水': 'LPF', '临汾': 'LFQ', '林芝': 'LZY', 
            '临沧': 'LNJ', '临沂': 'LYI', '柳州': 'LZH', '泸州': 'LZO',
            '洛阳': 'LYA', '吕梁': 'LLV', '澜沧': 'JMJ', '龙岩': 'LCX', 
            '满洲里': 'NZH', '梅州': 'MXZ', '绵阳': 'MIG', '漠河': 'OHE',
            '牡丹江': 'MDG', '马祖': 'MFK', '南昌': 'KHN', '南充': 'NAO', 
            '南京': 'NKG', '南宁': 'NNG', '南通': 'NTG', '南阳': 'NNY',
            '宁波': 'NGB', '宁蒗': 'NLH', '攀枝花': 'PZI', '普洱': 'SYM', 
            '齐齐哈尔': 'NDG', '黔江': 'JIQ', '且末': 'IQM', '秦皇岛': 'BPE',
            '青岛': 'TAO', '庆阳': 'IQN', '衢州': 'JUZ', '日喀则': 'RKZ', 
            '日照': 'RIZ', '三亚': 'SYX', '厦门': 'XMN', '上海': 'SHA',
            '深圳': 'SZX', '神农架': 'HPG', '沈阳': 'SHE', '石家庄': 'SJW', 
            '塔城': 'TCG', '台州': 'HYN', '太原': 'TYN', '扬州': 'YTY',
            '唐山': 'TVS', '腾冲': 'TCZ', '天津': 'TSN', '天水': 'THQ', 
            '通辽': 'TGO', '铜仁': 'TEN', '吐鲁番': 'TLQ', '万州': 'WXN',
            '威海': 'WEH', '潍坊': 'WEF', '温州': 'WNZ', '文山': 'WNH', 
            '乌海': 'WUA', '乌兰浩特': 'HLH', '乌鲁木齐': 'URC', '无锡': 'WUX',
            '梧州': 'WUZ', '武汉': 'WUH', '武夷山': 'WUS', '西安': 'XIY', 
            '西昌': 'XIC', '西宁': 'XNN', '锡林浩特': 'XIL', '迪庆': 'DIG', 
            '襄阳': 'XFN', '兴义': 'ACX', '徐州': 'XUZ', '香港': 'HKG', 
            '烟台': 'YNT', '延安': 'ENY', '延吉': 'YNJ', '盐城': 'YNZ',
            '伊春': 'LDS', '伊宁': 'YIN', '宜宾': 'YBP', '宜昌': 'YIH', 
            '宜春': 'YIC', '义乌': 'YIW', '银川': 'INC', '永州': 'LLF', 
            '榆林': 'UYN', '玉树': 'YUS', '运城': 'YCU', '湛江': 'ZHA', 
            '张家界': 'DYG', '张家口': 'ZQZ', '张掖': 'YZY', '昭通': 'ZAT', 
            '郑州': 'CGO', '中卫': 'ZHY', '舟山': 'HSN', '珠海': 'ZUH', 
            '遵义(茅台)': 'WMT', '遵义(新舟)': 'ZYI', '遵义': 'ZYI',
            '香格里拉(迪庆)': 'DIG', '香格里拉': 'DIG', '呼伦贝尔': 'HLD',
            }

        self.airports = {
            '北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, '广州': 1, 
            '成都双流': 0.8, '成都天府': 0.8, '深圳': 0.75, '昆明': 0.7, 
            '西安': 0.65, '重庆': 0.65, '杭州': 0.6, '南京': 0.45, '郑州': 0.4, 
            '厦门': 0.4, '武汉': 0.4, '长沙': 0.4, '青岛': 0.4, '海口': 0.35, 
            '乌鲁木齐': 0.35, '天津': 0.35, '贵阳': 0.3, '哈尔滨': 0.3, 
            '沈阳': 0.3, '三亚': 0.3, '大连': 0.3, '济南': 0.25, '南宁': 0.25, 
            '兰州': 0.2, '福州': 0.2, '太原': 0.2, '长春': 0.2, '南昌': 0.2, 
            '呼和浩特': 0.2, '宁波': 0.2, '温州': 0.2, '珠海': 0.2, '合肥': 0.2, 
            '石家庄': 0.15, '银川': 0.15, '烟台': 0.15, '桂林': 0.1, '泉州': 0.1, 
            '无锡': 0.1, '揭阳': 0.1, '西宁': 0.1, '丽江': 0.1, '西双版纳': 0.1, 
            '南阳': 0.1, 
            }

        self.cityClass =  {
            '北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, 
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
            '包头': 0.4, '郴州': 0.4, '南充': 0.4, 
            }

        self.cityLocation = {
            '北京首都': 0.2, '北京大兴': 0.2, '上海虹桥': 0, '上海浦东': 0, 
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
            '张家界': 0.7, '大理': 0.8, '呼伦贝尔': 0.7, '德宏': 0.8, '拉萨': 1, 
            }

        self.tourism = {
            '桂林', '西双版纳', '丽江', '张家界', '鄂尔多斯', '呼伦贝尔', '德宏', 
            '大理', '拉萨', '乌鲁木齐', '成都', '重庆', '贵阳', '昆明', '迪庆', 
            '香格里拉', '西安', '稻城'
            }

        self.__airfare = {
            ('BJS', 'CAN'): 3060, ('BJS', 'CKG'): 2170, ('BJS', 'CTU'): 2230, 
            ('BJS', 'DLC'): 930, ('BJS', 'FOC'): 2020, ('BJS', 'HAK'): 3160, 
            ('BJS', 'HGH'): 2660, ('BJS', 'HRB'): 1700, ('BJS', 'JJN'): 1730, 
            ('BJS', 'KMG'): 2550, ('BJS', 'LHW'): 2010, ('BJS', 'LXA'): 3260, 
            ('BJS', 'NKG'): 2230, ('BJS', 'SHA'): 1960, ('BJS', 'SWA'): 1910, 
            ('BJS', 'SYX'): 3680, ('BJS', 'SZX'): 2500, ('BJS', 'URC'): 3480, 
            ('BJS', 'WUH'): 2510, ('BJS', 'WUX'): 2110, ('BJS', 'XIY'): 2450, 
            ('BJS', 'XMN'): 2120, ('CAN', 'HAK'): 1890, ('CAN', 'SYX'): 1590, 
            ('CAN', 'ZHA'): 970, ('CGO', 'CAN'): 1700, ('CGO', 'CKG'): 1270, 
            ('CGO', 'CTU'): 1220, ('CGO', 'FOC'): 1370, ('CGO', 'HAK'): 2220, 
            ('CGO', 'HGH'): 940, ('CGO', 'JJN'): 1360, ('CGO', 'KMG'): 2060, 
            ('CGO', 'LHW'): 1100, ('CGO', 'SHA'): 1280, ('CGO', 'SYX'): 2470, 
            ('CGO', 'SZX'): 2360, ('CGO', 'URC'): 2560, ('CGO', 'XMN'): 1360, 
            ('CKG', 'CAN'): 1650, ('CKG', 'HAK'): 1900, ('CKG', 'KMG'): 1180, 
            ('CKG', 'LXA'): 2730, ('CKG', 'SWA'): 1740, ('CKG', 'SYX'): 2230, 
            ('CKG', 'SZX'): 1940, ('CKG', 'URC'): 2750, ('CKG', 'WUH'): 1250, 
            ('CTU', 'CAN'): 2070, ('CTU', 'HAK'): 1740, ('CTU', 'KMG'): 1410, 
            ('CTU', 'LHW'): 1110, ('CTU', 'LXA'): 2590, ('CTU', 'SYX'): 2680, 
            ('CTU', 'SZX'): 2350, ('CTU', 'URC'): 2860, ('CTU', 'WUH'): 1470, 
            ('CZX', 'CAN'): 1460, ('CZX', 'CTU'): 1600, ('CZX', 'SZX'): 1540, 
            ('DLC', 'CAN'): 2190, ('DLC', 'CGO'): 960, ('DLC', 'CKG'): 1950, 
            ('DLC', 'CTU'): 2130, ('DLC', 'FOC'): 1680, ('DLC', 'HAK'): 2700, 
            ('DLC', 'HGH'): 1240, ('DLC', 'KMG'): 2880, ('DLC', 'NKG'): 1000, 
            ('DLC', 'SHA'): 1130, ('DLC', 'SZX'): 2460, ('DLC', 'TAO'): 1000, 
            ('DLC', 'WUH'): 1490, ('DLC', 'XIY'): 1410, ('DLC', 'XMN'): 1890, 
            ('FOC', 'CAN'): 1480, ('FOC', 'CKG'): 1610, ('FOC', 'CTU'): 1920, 
            ('FOC', 'KMG'): 2260, ('FOC', 'LHW'): 2060, ('FOC', 'WUH'): 1050, 
            ('FOC', 'XIY'): 1680, ('HGH', 'CAN'): 1550, ('HGH', 'CKG'): 2000, 
            ('HGH', 'CTU'): 2230, ('HGH', 'HAK'): 1940, ('HGH', 'JHG'): 2200, 
            ('HGH', 'KMG'): 2390, ('HGH', 'LHW'): 1760, ('HGH', 'SYX'): 2510, 
            ('HGH', 'SZX'): 1650, ('HGH', 'URC'): 3280, ('HGH', 'XIY'): 1540, 
            ('HRB', 'CAN'): 3780, ('HRB', 'CGO'): 1820, ('HRB', 'CKG'): 2480, 
            ('HRB', 'CTU'): 3050, ('HRB', 'CZX'): 1740, ('HRB', 'FOC'): 2350, 
            ('HRB', 'HAK'): 3330, ('HRB', 'HGH'): 2230, ('HRB', 'KMG'): 4100, 
            ('HRB', 'NKG'): 1740, ('HRB', 'SHA'): 1810, ('HRB', 'SYX'): 3480, 
            ('HRB', 'SZX'): 3360, ('HRB', 'TAO'): 1570, ('HRB', 'TSN'): 1250, 
            ('HRB', 'WUH'): 2050, ('HRB', 'XIY'): 1980, ('HRB', 'XMN'): 2550, 
            ('JJN', 'CAN'): 1120, ('JJN', 'CKG'): 1510, ('JJN', 'CTU'): 1750, 
            ('JJN', 'KMG'): 1890, ('KMG', 'CAN'): 1970, ('KMG', 'HAK'): 1440, 
            ('KMG', 'JHG'): 2010, ('KMG', 'LHW'): 2050, ('KMG', 'LXA'): 2480, 
            ('KMG', 'SWA'): 1830, ('KMG', 'SYX'): 1810, ('KMG', 'SZX'): 2220, 
            ('KMG', 'URC'): 3400, ('KMG', 'WUH'): 1660, ('KMG', 'XIY'): 2060, 
            ('LHW', 'CAN'): 2210, ('LHW', 'SZX'): 2100, ('NKG', 'CAN'): 1710, 
            ('NKG', 'CKG'): 1620, ('NKG', 'CTU'): 2150, ('NKG', 'FOC'): 920, 
            ('NKG', 'HAK'): 1940, ('NKG', 'JJN'): 1020, ('NKG', 'KMG'): 2160, 
            ('NKG', 'LHW'): 1650, ('NKG', 'SYX'): 1960, ('NKG', 'SZX'): 2030, 
            ('NKG', 'URC'): 3380, ('NKG', 'XIY'): 1180, ('NKG', 'XMN'): 1110, 
            ('SHA', 'CAN'): 1780, ('SHA', 'CKG'): 1870, ('SHA', 'CTU'): 2560, 
            ('SHA', 'FOC'): 1030, ('SHA', 'HAK'): 1750, ('SHA', 'JHG'): 2350, 
            ('SHA', 'JJN'): 1350, ('SHA', 'LHW'): 1860, ('SHA', 'SWA'): 1220, 
            ('SHA', 'SYX'): 2620, ('SHA', 'SZX'): 2030, ('SHA', 'TAO'): 1660, 
            ('SHA', 'URC'): 3280, ('SHA', 'WUH'): 2060, ('SHA', 'XIY'): 1520, 
            ('SHA', 'XMN'): 1820, ('SHA', 'ZHA'): 1760, ('SZX', 'HAK'): 1220, 
            ('SZX', 'SYX'): 1120, ('TAO', 'CAN'): 2010, ('TAO', 'CGO'): 930, 
            ('TAO', 'CKG'): 1910, ('TAO', 'CTU'): 1690, ('TAO', 'HAK'): 2300, 
            ('TAO', 'HGH'): 900, ('TAO', 'KMG'): 2660, ('TAO', 'LHW'): 1750, 
            ('TAO', 'NKG'): 1200, ('TAO', 'SYX'): 2640, ('TAO', 'SZX'): 2870, 
            ('TAO', 'WUH'): 1300, ('TAO', 'XIY'): 1510, ('TAO', 'XMN'): 1590, 
            ('TSN', 'CAN'): 2260, ('TSN', 'CKG'): 1540, ('TSN', 'CTU'): 2380, 
            ('TSN', 'FOC'): 1630, ('TSN', 'HAK'): 2470, ('TSN', 'HGH'): 1770, 
            ('TSN', 'KMG'): 2750, ('TSN', 'SHA'): 2120, ('TSN', 'SZX'): 2360, 
            ('TSN', 'URC'): 2780, ('TSN', 'WUH'): 1150, ('TSN', 'XIY'): 1410, 
            ('TSN', 'XMN'): 1900, ('URC', 'CAN'): 3410, ('URC', 'HAK'): 3850, 
            ('URC', 'LHW'): 1920, ('URC', 'SZX'): 3460, ('URC', 'WUH'): 2800, 
            ('URC', 'XIY'): 2660, ('WUH', 'CAN'): 1930, ('WUH', 'HAK'): 1410, 
            ('WUH', 'SYX'): 1690, ('WUH', 'SZX'): 2080, ('WUX', 'CAN'): 1540, 
            ('WUX', 'CKG'): 1410, ('WUX', 'CTU'): 2090, ('WUX', 'KMG'): 2640, 
            ('WUX', 'SZX'): 1690, ('XIY', 'CAN'): 1850, ('XIY', 'HAK'): 2210, 
            ('XIY', 'LXA'): 2500, ('XIY', 'SYX'): 2660, ('XIY', 'SZX'): 2380, 
            ('XMN', 'CAN'): 1670, ('XMN', 'CKG'): 1840, ('XMN', 'CTU'): 2060, 
            ('XMN', 'HAK'): 1180, ('XMN', 'KMG'): 2170, ('XMN', 'LHW'): 2150, 
            ('XMN', 'URC'): 3730, ('XMN', 'WUH'): 990, ('XMN', 'XIY'): 2270, 
            ('BJS', 'CGQ'): 2000, ('BJS', 'CSX'): 1780, ('BJS', 'HFE'): 1710, 
            ('BJS', 'INC'): 1410, ('CAN', 'INC'): 2030, ('CGQ', 'CAN'): 3010, 
            ('CGQ', 'CKG'): 2560, ('CGQ', 'CSX'): 2250, ('CGQ', 'CTU'): 2700, 
            ('CGQ', 'HAK'): 3410, ('CGQ', 'HGH'): 2140, ('CGQ', 'NKG'): 1550, 
            ('CGQ', 'SHA'): 1850, ('CGQ', 'SJW'): 1360, ('CGQ', 'SYX'): 3310, 
            ('CGQ', 'SZX'): 3320, ('CGQ', 'TAO'): 1130, ('CGQ', 'WUH'): 2040, 
            ('CGQ', 'XIY'): 1910, ('CGQ', 'XMN'): 2430, ('CSX', 'CKG'): 1400, 
            ('CSX', 'CTU'): 1470, ('CSX', 'DLC'): 1790, ('CSX', 'KMG'): 1400, 
            ('CSX', 'TAO'): 1620, ('CSX', 'URC'): 3270, ('CSX', 'XIY'): 1500, 
            ('HFE', 'CAN'): 1290, ('HFE', 'CKG'): 1210, ('HFE', 'CTU'): 1430, 
            ('HFE', 'KMG'): 2100, ('HFE', 'SZX'): 1190, ('HRB', 'CSX'): 2250, 
            ('HRB', 'HFE'): 1840, ('NKG', 'CSX'): 970, ('SHA', 'CSX'): 2200, 
            ('SHA', 'INC'): 1980, ('SHA', 'KMG'): 2340, ('SHE', 'CAN'): 2730, 
            ('SHE', 'CGO'): 1380, ('SHE', 'CKG'): 2250, ('SHE', 'CSX'): 2100, 
            ('SHE', 'CTU'): 2690, ('SHE', 'CZX'): 1340, ('SHE', 'HAK'): 2880, 
            ('SHE', 'HGH'): 2180, ('SHE', 'KMG'): 3200, ('SHE', 'NKG'): 1640, 
            ('SHE', 'SHA'): 2030, ('SHE', 'SYX'): 3410, ('SHE', 'SZX'): 3300, 
            ('SHE', 'TAO'): 1150, ('SHE', 'URC'): 2940, ('SHE', 'WUH'): 1830, 
            ('SHE', 'WUX'): 1390, ('SHE', 'XIY'): 1840, ('SHE', 'XMN'): 2150, 
            ('SJW', 'CAN'): 1790, ('SJW', 'SHA'): 1200, ('SYX', 'CSX'): 1890, 
            ('TSN', 'CSX'): 1390, ('SHE', 'SJW'): 920, ('SHE', 'HFE'): 1610, 
            ('SHE', 'FOC'): 1980, ('HRB', 'SJW'): 1490, ('CGQ', 'WUX'): 1940, 
            ('CGQ', 'HFE'): 1700, ('CGQ', 'KMG'): 3540, ('CGQ', 'FOC'): 2210, 
            ('CGQ', 'CGO'): 1700, ('SJW', 'NKG'): 1040, ('SJW', 'HGH'): 1650, 
            ('SJW', 'SYX'): 2620, ('SJW', 'HAK'): 2230, ('SJW', 'XMN'): 1760, 
            ('SJW', 'CTU'): 1830, ('SJW', 'CKG'): 1310, ('SJW', 'KMG'): 2030, 
            ('SJW', 'LHW'): 1180, ('SJW', 'URC'): 2610, ('SJW', 'FOC'): 1600, 
            ('NKG', 'INC'): 1650, ('HGH', 'CSX'): 970, ('HGH', 'INC'): 1740, 
            ('WUX', 'CSX'): 1370, ('HFE', 'SYX'): 2100, ('HFE', 'HAK'): 1990, 
            ('HFE', 'XMN'): 940, ('HFE', 'URC'): 2840, ('HFE', 'TAO'): 800, 
            ('HFE', 'DLC'): 1220, ('HAK', 'CSX'): 1410, ('CSX', 'LHW'): 1680, 
            ('CSX', 'INC'): 1630, ('CTU', 'INC'): 1260, ('CKG', 'INC'): 1230, 
            ('INC', 'URC'): 1730, ('INC', 'TAO'): 1550, ('INC', 'CGO'): 1040, 
            ('KWE', 'BJS'): 1980, ('KWE', 'HRB'): 2730, ('KWE', 'SHA'): 1850, 
            ('KWE', 'NKG'): 1560, ('KWE', 'HGH'): 1700, ('KWE', 'CAN'): 1510, 
            ('KWE', 'XIY'): 1010, ('KWE', 'FOC'): 1620
            }
        
        self.routes_inactive = {
            ('BJS', 'TSN'), ('BJS', 'SJW'), ('BJS', 'TYN'), ('BJS', 'TNA'), 
            ('BJS', 'SHE'), ('CGO', 'NKG'), ('TYN', 'TNA'), ('DLC', 'CGQ'), 
            ('BJS', 'HET'), ('SJW', 'TSN'), ('TSN', 'DLC'), ('TSN', 'TAO'), 
            ('SJW', 'TYN'), ('SJW', 'TNA'), ('TSN', 'TNA'), ('TSN', 'TYN'), 
            ('SHE', 'CGQ'), ('CGQ', 'HRB'), ('SHE', 'HRB'), ('DLC', 'SHE'), 
            ('BJS', 'SHE'), ('BJS', 'CGO'), ('TNA', 'CGO'), ('BJS', 'TAO'), 
            ('TNA', 'TAO'), ('CGO', 'WUH'), ('XIY', 'SJW'), ('WUX', 'YTY'), 
            ('CGO', 'SJW'), ('CGO', 'XIY'), ('CGO', 'HFE'), ('CGO', 'TYN'), 
            ('XIY', 'INC'), ('XIY', 'LHW'), ('CTU', 'XIY'), ('XIY', 'TYN'), 
            ('XIY', 'WUH'), ('WUH', 'KHN'), ('NKG', 'HGH'), ('HGH', 'WUX'), 
            ('WUH', 'HFE'), ('WUH', 'NKG'), ('NKG', 'HFE'), ('WUH', 'CSX'), 
            ('WUH', 'HGH'), ('NKG', 'SHA'), ('SHA', 'YTY'), ('WUX', 'NTG'), 
            ('NKG', 'WUX'), ('NKG', 'CZX'), ('NKG', 'NTG'), ('NKG', 'YTY'), 
            ('SHA', 'HGH'), ('SHA', 'WUX'), ('SHA', 'NTG'), ('SHA', 'CZX'), 
            ('HGH', 'CZX'), ('HGH', 'NTG'), ('HGH', 'YTY'), ('WUX', 'CZX'), 
            ('CZX', 'NTG'), ('CZX', 'YTY'), ('NTG', 'YTY'), ('SHA', 'HFE'), 
            ('HGH', 'HFE'), ('SZX', 'SWA'), ('WUH', 'WUX'), ('KHN', 'XMN'), 
            ('HFE', 'CZX'), ('WUH', 'NTG'), ('KHN', 'KWE'), ('HGH', 'XMN'), 
            ('HFE', 'WUX'), ('HFE', 'YTY'), ('HFE', 'NTG'), ('WUH', 'CZX'), 
            ('WUH', 'YTY'), ('KHN', 'CSX'), ('KHN', 'HGH'), ('KHN', 'FOC'), 
            ('CSX', 'CAN'), ('CSX', 'NNG'), ('CSX', 'FOC'), ('CSX', 'XMN'), 
            ('HGH', 'FOC'), ('ZUH', 'SWA'), ('KWE', 'NNG'), ('FOC', 'XMN'), 
            ('CAN', 'SZX'), ('CAN', 'ZUH'), ('ZUH', 'SZX'), ('CAN', 'SWA'), 
            ('SWA', 'FOC'), ('SWA', 'XMN'), ('CAN', 'NNG'), ('FOC', 'NNG'), 
            ('CKG', 'XIY'), ('KWE', 'KMG'), ('HET', 'SJW'), ('FOC', 'ZHA'), 
            ('KMG', 'NNG'), ('KWE', 'CTU'), ('KWE', 'CSX'), ('CKG', 'KWE'), 
            ('CTU', 'CKG'), ('HET', 'TYN'), ('SWA', 'ZHA'), ('FOC', 'SZX'), 
            ('LHW', 'XNN'), ('XNN', 'INC'), ('INC', 'LHW'), ('HET', 'INC'), 
            ('JJN', 'XMN'), ('JJN', 'FOC'), ('JJN', 'ZHA'), ('SZX', 'JJN'), 
            ('HAK', 'SYX'), ('HRB', 'HLD'), ('SZX', 'ZHA'), ('FOC', 'SYX'), 
            ('HFE', 'CSX'), ('CGQ', 'TSN'), ('TSN', 'JJN'), 
            }
        
        self.routes_low = {
            ('LXA', 'ZHA'), ('LXA', 'SZX'), ('LXA', 'JJN'), ('CTU', 'SWA'), 
            ('SHA', 'LXA'), ('TSN', 'LXA'), ('URC', 'SWA'), ('NKG', 'LXA'), 
            ('LXA', 'XMN'), ('LXA', 'CZX'), ('LXA', 'WUX'), ('LXA', 'HLD'), 
            ('LXA', 'JHG'), ('LXA', 'SWA'), ('TAO', 'SWA'), ('CGO', 'LXA'), 
            ('LXA', 'TAO'), ('LXA', 'DLC'), ('LXA', 'SYX'), ('LXA', 'HAK'), 
            ('LXA', 'FOC'), ('LXA', 'JJN'), ('WUH', 'LXA'), ('JHG', 'HAK'), 
            ('JHG', 'CZX'), ('JHG', 'WUX'), ('JHG', 'XMN'), ('JHG', 'JJN'), 
            ('JHG', 'HRB'), ('JHG', 'ZHA'), ('TSN', 'WUX'), ('LHW', 'SWA'), 
            ('JHG', 'SWA'), ('JHG', 'SYX'), ('JHG', 'HLD'), ('JHG', 'URC'), 
            ('JHG', 'TAO'), ('JHG', 'DLC'), ('HLD', 'URC'), ('HLD', 'TAO'), 
            ('HLD', 'KMG'), ('WUX', 'LHW'), ('XMN', 'ZHA'), ('WUH', 'JHG'), 
            ('TAO', 'JJN'), ('TSN', 'ZHA'), ('LHW', 'HAK'), ('KMG', 'ZHA'),
            ('HRB', 'WUX'), ('ZHA', 'HAK'), ('XIY', 'SWA'), ('CTU', 'ZHA'), 
            ('LHW', 'JJN'), ('TAO', 'CZX'), ('HLD', 'CKG'), ('HLD', 'SYX'), 
            ('WUX', 'XMN'), ('CZX', 'CGO'), ('HLD', 'SHA'), ('WUH', 'JJN'), 
            ('JHG', 'SZX'), ('HLD', 'LHW'), ('CZX', 'XMN'), ('CZX', 'FOC'), 
            ('TSN', 'SWA'), ('CGO', 'ZHA'), ('CZX', 'SYX'), ('TSN', 'NKG'), 
            ('LHW', 'SYX'), ('HGH', 'SWA'), ('HLD', 'WUX'), ('CGQ', 'CZX'), 
            ('HLD', 'DLC'), ('URC', 'LXA'), ('TSN', 'CGO'), ('WUX', 'SWA'), 
            ('HLD', 'XMN'), ('XMN', 'SYX'), ('WUH', 'ZHA'), ('HLD', 'CTU'), 
            ('HLD', 'FOC'), ('CGO', 'SWA'), ('HLD', 'ZHA'), ('HRB', 'JJN'), 
            ('DLC', 'ZHA'), ('HLD', 'HGH'), ('JJN', 'SWA'), ('URC', 'SYX'), 
            ('HLD', 'XIY'), ('XIY', 'ZHA'), ('WUX', 'HAK'), ('CKG', 'JHG'), 
            ('HLD', 'SWA'), ('HGH', 'LXA'), ('HRB', 'URC'), ('CZX', 'URC'), 
            ('HLD', 'WUH'), ('HLD', 'NKG'), ('DLC', 'SWA'), ('JHG', 'LHW'), 
            ('URC', 'FOC'), ('NKG', 'ZHA'), ('TAO', 'ZHA'), ('JJN', 'SYX'), 
            ('HLD', 'CAN'), ('TSN', 'CZX'), ('SWA', 'HAK'), ('CZX', 'JJN'), 
            ('URC', 'ZHA'), ('ZHA', 'SYX'), ('WUH', 'LHW'), ('WUX', 'ZHA'), 
            ('HLD', 'CGO'), ('WUX', 'FOC'), ('CKG', 'LHW'), ('LXA', 'CAN'), 
            ('TAO', 'FOC'), ('HLD', 'HAK'), ('CTU', 'JHG'), ('CZX', 'CKG'), 
            ('NKG', 'SWA'), ('BJS', 'HLD'), ('BJS', 'CZX'), ('WUX', 'XIY'), 
            ('BJS', 'JHG'), ('JHG', 'XIY'), ('NKG', 'JHG'), ('XMN', 'SZX'), 
            ('TSN', 'SYX'), ('HGH', 'JJN'), ('HRB', 'LHW'), ('CZX', 'KMG'), 
            ('DLC', 'CZX'), ('WUX', 'CGO'), ('JHG', 'CAN'), ('DLC', 'URC'), 
            ('URC', 'JJN'), ('HRB', 'DLC'), ('WUH', 'SWA'), ('LHW', 'LXA'), 
            ('HRB', 'ZHA'), ('SWA', 'SYX'), ('CZX', 'LHW'), ('TSN', 'JHG'), 
            ('HLD', 'TSN'), ('XIY', 'JJN'), ('FOC', 'HAK'), ('JHG', 'FOC'), 
            ('HLD', 'SZX'), ('HRB', 'SWA'), ('WUX', 'URC'), ('DLC', 'SYX'), 
            ('HRB', 'LXA'), ('TAO', 'URC'), ('TSN', 'LHW'), ('CZX', 'ZHA'), 
            ('CGO', 'JHG'), ('LHW', 'ZHA'), ('DLC', 'WUX'), ('CKG', 'ZHA'), 
            ('CZX', 'XIY'), ('WUX', 'JJN'), ('HLD', 'CZX'), ('CZX', 'SWA'), 
            ('WUX', 'SYX'), ('HGH', 'ZHA'), ('HLD', 'JJN'), ('CZX', 'HAK'), 
            ('DLC', 'JJN'), ('DLC', 'LHW'), ('JJN', 'HAK'), ('TAO', 'WUX'), 
            ('HRB', 'INC'), ('KMG', 'INC'), ('INC', 'FOC'), ('SZX', 'CSX'), 
            ('XMN', 'INC'), ('HFE', 'XIY'), ('SJW', 'SZX'), ('TSN', 'SHE'), 
            ('CGQ', 'INC'), ('SJW', 'HFE'), ('HFE', 'FOC'), ('TSN', 'HFE'), 
            ('XMN', 'LHW'), ('SJW', 'WUH'), ('SZX', 'INC'), ('INC', 'WUH'), 
            ('SYX', 'INC'), ('SJW', 'TAO'), ('CSX', 'CGO'), ('TSN', 'INC'), 
            ('CGQ', 'LHW'), ('SJW', 'CZX'), ('SJW', 'WUX'), ('SJW', 'INC'), 
            ('SJW', 'CSX'), ('HFE', 'INC'), ('HAK', 'INC'), ('CZX', 'INC'), 
            ('SHE', 'INC'), ('CGQ', 'URC'), ('HFE', 'LHW'), ('CZX', 'CSX'), 
            ('WUX', 'INC'), ('INC', 'DLC'), ('SJW', 'DLC'), ('SHE', 'LHW'), 
            }
    
    def get_airfare(self, *args: str) -> int:
        '''Get route's airfare from dep city to arr city'''
        if len(args) == 1:
            arg = args[0]
            if not isinstance(arg, str):
                return 0
            return self.get_airfare(arg.upper()[:3], arg.upper()[4:7])
        elif len(args) == 2:
            arr, dep = (arg.upper() for arg in args)
            if not dep.isupper():
                dep = self.to_code(self.from_name(dep))
            if not arr.isupper():
                arr = self.to_code(self.from_name(arr))
            if (dep, arr) in self.__airfare.keys():
                return self.__airfare.get((dep, arr))
            else:
                return self.__airfare.get((arr, dep), 0)
        else:
            return None
    
    @staticmethod
    def is_multiairport(__str: str) -> bool:
        return True if '北京' in __str or '上海' in __str \
            or '成都' in __str or __str == 'BJS' or __str == 'PEK' \
                or __str == 'PKX' or __str == 'SHA'or __str == 'PVG' \
                    or __str == 'TFU' or __str == 'CTU' else False
    
    def from_name(self, __str: str, __strip: bool = True, /) -> str:
        '''Get city name from airport name'''
        if __strip:
            if __str in self.__striptemp:
                return __str[:2]
            elif self.is_multiairport(__str):
                self.__striptemp.add(__str)
                return __str[:2]
        return __str
    
    def from_code(self, __str: str, /) -> str:
        '''Get city name from airport code'''
        return self.__airportCity.get(__str, None)
    
    def to_code(self, __str: str, __multi: bool = False, /) -> str:
        '''Get city code from given name
        
        `True`: For multi-airport cities, get airport code if given airport name'''
        return self.__airportCode.get(__str, None) if __multi else \
            self.__airportCode.get(self.from_name(__str), None)
    
    @property
    def skipped_routes(self):
        return self.routes_inactive | self.routes_low
    