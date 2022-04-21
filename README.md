# FlyCheap

## 中国民航数据库－CivilAviation

### 航空公司（Airline）

- **包含**：全球九百余家航空公司及国内航空公司
- **定义**：支持航司全名、ICAO、IATA代码定义
- **成员**：航司英语全称、呼号、国家
- **==运算**：支持互相比较、字符串比较是否等于IATA、ICAO、航空公司名之一

### 机场（Airport）

- **包含**：包含国内定期航班机场、港澳台机场，也可手动添加
- **定义**：支持城市名（多机场城市需 + 机场名）、ICAO、IATA代码定义
- **成员**：经纬度、中英文城市与机场名、所在省份、机场大小等
- **+运算**：生成项目使用航线（城市对航线）字符串
- **-运算**：生成航线（Route）
- **==运算**：支持互相比较、字符串比较是否等于IATA、ICAO、机场名之一

### 航线（Route）

- **定义**：支持机场、元组、字符串
- **成员**：部分航线的全价和大圆航线距离
- **拆分**：生成出发、到达机场对应成员元组
- **格式化**：生成出发、到达机场对应成员构成的航线（如城市对航线）字符串

## 数据收集－CtripCrawler

### 特性

- 单线程（多线程通过外部实现）
- 代理池（可使用[ProxyPool](https://github.com/Python3WebSpider/ProxyPool)，亦可使用自定义函数）
- 防丢包（数据偏少三次重试）
- 忽略集（跳过低航班量航线）
- 矩阵化（全连接航线）
- 定日期（忽略今日和之前日期）
- 带格式（输出表格带有格式）

### 缺点

- 爬取慢（一天、一个城市对、所有往返航班：平均用时2~3秒，低速网络、高密度航线不超过8秒）
- 忽略共享航班和有经停的航班

### 输出

- **文件夹**：起始爬取航班日期 / 收集日期
- **文件名**：航线（ ~ 代表双向， - 代表单向）
- **表头**：航班日期、星期、航司、机型、出发到达机场及时刻、价格、折扣

### 附加程序

- **CtripSearcher**: 通过当前携程搜索页面的搜索api编写，参考CSDN，但爬取较为缓慢，未使用
- **ItineraryCollector**: 随机收集航程（某日某航线所有航班信息），反爬使用

## 数据重构－Rebuilder

### 特性

- 使用 pandas 数据结构
- 加载数据较快
- 处理速度随数据量和数据复杂度变化

### 数据重构功能

#### 数据整合（merge）

- [x] 数据总集，整合所有收集的航班原始信息

#### 总览（overview）

- [x] **航司**：按时刻、航线，总览密度与系数；按起飞机场总览航班数量
- [x] **航线**：按日期、提前天数，总览均值和标准差；按时刻总览密度与系数
- [x] **日期**：按航线，以收集日期或航线日期，总览每日折扣均值

#### 相关系数（correlation）

- [x] **月份**：确定某月机票折扣“跳跃”的相关系数与航线、航司、采集日期关系
- [x] **提前天数**：确定提前x~y天内机票折扣随提前天数减少的相关系数与航线、航司、航班日期关系
- [x] **星期**：确定每个星期在各个周期内的相关系数与航线、航司关系
- [x] **时刻**：确定每个时刻在一个航程内的相关系数与航线、航司关系

### 附加功能

- 四种数据导入方式
- 整合数据的重复利用

## 数据结构示例

```python
>>> from flycheap import Airport, Route
>>> route = Airport('广州') - Airport('PEK')	#构造航线
>>> route
flycheap.civilaviation.Route(广州, 北京首都)

>>> route.airfare	#航线全价
2540

>>> route.separates()	#分解为机场数据结构
(flycheap.civilaviation.Airport('CAN', 'ZGGG', '广州白云', ...), civilaviation.flycheap.Airport('PEK', 'ZBAA', '北京首都', ...))

>>> route.separates('icao')	#分解为机场成员
('ZGGG', 'ZBAA')

>>> route.format('iata')	#生成航线字符格式
'CAN-PEK'

>>> route = Route.fromformat('成都天府-NKG')	#从字符串获得航线
>>> route.separates('airport')	#分解为成员：机场名
('成都天府', '南京禄口')
```

## 多线程爬取示例

### 设置python文件  (D:\routine.py)

```python
from datetime import date
from flycheap import CtripCrawler
from pandas import DataFrame
from argparse import ArgumentParser

flight_date = date.today()
kwargs = {
    'targets': ["BJS", "SHA", "CAN", "CTU", "DLC"], 
    'flight_date': flight_date, 
    'ignore_threshold': 3, 
    'ignore_routes': set(), 
    'days': 7}
crawler = CtripCrawler(**kwargs)

parser = ArgumentParser()
parser.add_argument("--part", type = int, default = 1)
parser.add_argument("--parts", type = int, default = 1)
parser.add_argument("--attempt", type = int, default = 3)
parser.add_argument("-reverse", action = 'store_true')
parser.add_argument("-overwrite", action = 'store_true')
parser.add_argument("-nopreskip", action = 'store_true')
parser.add_argument("--antiempty", type = int, default = 0)
parser.add_argument("--noretry", type = str, action = 'append', default = [])

title = ['出发日期', '星期', '航司', '机型', '出发', '到达', '出发时刻', '到达时刻', '价格', '折扣']
for data in crawler.run(**vars(parser.parse_args())):
	print(DataFrame(data, columns = title).assign(**{'收集日期': date.today()}))
```

### 设置batch文件 (routine.bat)

```bash
@echo off
start python D:\routine.py -nopreskip --part 3 --parts 3 --noretry SHA --attempt 2 --antiempty 2
start python D:\routine.py -nopreskip --part 2 --parts 3 --noretry SHA --attempt 2 --antiempty 2
start python D:\routine.py -nopreskip --part 1 --parts 3 --noretry SHA --attempt 2 --antiempty 2
```

## 数据重构示例

```python
from flycheap import Rebuilder
if __name__ == '__main__':
    rebuild = Rebuilder('2022-2-17')
    #rebuild.append_data('dataset.csv')
    rebuild.append_folder()
    rebuild.adv(1, 7)
```

