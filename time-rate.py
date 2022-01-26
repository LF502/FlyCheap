import pandas
import pathlib
dayOfWeek = {'星期二': 0, '星期三': 0, '星期四': 0, '星期一': 0.5, '星期五': 0.5, '星期六': 1, '星期日': 1}
craftType = {'大': True, '中': False, '小': False}
fsAirlines = {'中国国航','厦门航空','海南航空','东方航空','南方航空','四川航空','深圳航空','吉祥航空','山东航空',}
airports = {'北京首都': 1, '北京大兴': 1, '上海虹桥': 1, '上海浦东': 1, '广州': 1, 
            '成都双流': 0.8, '成都天府': 0.8, '深圳': 0.75, '昆明': 0.7, '西安': 0.65, 
            '重庆': 0.65, '杭州': 0.6, '南京': 0.45, '郑州': 0.4, '厦门': 0.4, 
            '武汉': 0.4, '长沙': 0.4, '青岛': 0.4, '海口': 0.35, '乌鲁木齐': 0.35, 
            '天津': 0.35, '贵阳': 0.3, '哈尔滨': 0.3, '沈阳': 0.3, '三亚': 0.3, 
            '大连': 0.3, '济南': 0.25, '南宁': 0.25, '兰州': 0.2, '福州': 0.2, 
            '太原': 0.2, '长春': 0.2, '南昌': 0.2, '呼和浩特': 0.2, '宁波': 0.2, 
            '温州': 0.2, '珠海': 0.2, '合肥': 0.2, '石家庄': 0.15, '银川': 0.15, 
            '烟台': 0.15, '桂林': 0.1, '泉州': 0.1, '无锡': 0.1, '揭阳': 0.1, 
            '西宁': 0.1, '丽江': 0.1, '西双版纳': 0.1, '南阳': 0.1,}
rtdict = {'小时段': []}
for i in range(25):
    rtdict[i]=[]

path = './/2022-01-26'
#collDate = path.split('-', 2)
#collDate = datetime.date(int(collDate[0]), int(collDate[1]), int(collDate[2])).toordinal()
for file in pathlib.Path(path).iterdir():
    # 原表格格式
    # 日期，星期，航司，机型，出发机场，到达机场，出发时间，到达时间，价格，折扣
    #  0     1    2     3      4        5        6        7      8     9
    if not file.match('*.xlsx'):
        continue
    data = pandas.read_excel(file.joinpath()).iloc[ : , [6, 9]]
    rtdict['小时段'].append(file.name.replace('~','-').strip('.xlsx'))

    alterlist = []
    for item in data.get('出发时'):
        alterlist.append(item.hour + round(item.minute/60, 2))
    data.loc[:, '出发时'] = alterlist
    alterlist.sort()
    data = data.sort_values('出发时')

    i = total = corr =0
    j = 1
    for item in data.get('折扣'):
        dtime = int(alterlist[i])
        diff = dtime - corr
        if diff == 1:
            rtdict[corr].append(total/j)
            corr+= 1
            j = 0
            total = 0
        elif diff >=1:
            for k in range(diff):
                rtdict[corr].append(0)
                corr+= 1
        total+= item
        j+= 1
        i+= 1
    else:
        rtdict[corr].append(total/j)
        if corr < 24:
            for j in range(24-corr):
                corr+= 1
                rtdict[corr].append(0)
pandas.DataFrame(rtdict).to_excel('.//time-rate.xlsx', index=False, encoding='GBK')
