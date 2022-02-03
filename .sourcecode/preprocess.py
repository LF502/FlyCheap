import pandas
import datetime
from pathlib import Path

def main(path: str):
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
    
    collDate = path.split('-', 2)
    collDate = datetime.date(int(collDate[0]), int(collDate[1]), int(collDate[2])).toordinal()
    path = Path(path)
    for file in path.iterdir():
    #if True:   #for debugging
    
        # 原表格格式
        # 日期，星期，航司，机型，出发机场，到达机场，出发时间，到达时间，价格，折扣
        #  0     1    2     3      4        5        6        7      8     9
        if not file.match('*.xlsx') or '_' in file.name:
            continue
        print('\r' + file.name, end=' preprocessing...')
        data = pandas.read_excel(file).iloc[ : , [0, 1, 2, 3, 4, 5, 6, 9]]

        alterlist = []
        datelist = []
        airlinedict = dict()
        
        '''current dates, defined by how many days remain before the departure of flights (int, collect date - dep date)'''
        for item in data.get('日期'):
            currdate = item.toordinal()
            alterlist.append(currdate - collDate)
            if currdate not in airlinedict:
                airlinedict[currdate] = set()   #initialize airline set of currdate for detecting competition between airlines
            datelist.append(currdate)
        data.loc[:, '日期'] = alterlist

        '''weekends -> 1, Mon and Fri -> 0.5, other weekdays -> 0'''
        alterlist = []
        for item in data.get('星期'):
            alterlist.append(dayOfWeek[item])
        data.loc[:, '星期'] = alterlist

        '''airline type seted above, defined by bool: Full service -> True, Low-cost -> False'''
        alterlist = []
        i = 0
        for item in data.get('航司'):
            if item in fsAirlines:
                alterlist.append(True)
            else:
                alterlist.append(False)
            if item not in airlinedict[datelist[i]]:
                airlinedict[datelist[i]].add(item)  #detect the competition between airlines
            i += 1
        data.loc[:, '航司'] = alterlist

        '''competition in dict, defined by how many airlines fly the route in the same day (int)'''
        alterlist = []
        for item in datelist:
            alterlist.append(len(airlinedict[item]))
        data.loc[:, '竞争'] = alterlist

        '''craft type defined by bool: L -> True, M/S -> False'''
        alterlist = []
        for item in data.get('机型'):
            alterlist.append(craftType[item])
        data.loc[:, '机型'] = alterlist

        '''airport ratio defined above, calculated from passenger throughput'''
        alterlist = []
        for item in data.get('出发机场'):
            i = airports.get(item, 0.05)
            alterlist.append(i)
        data.loc[:, '出发机场'] = alterlist

        '''airport ratio defined above, calculated from passenger throughput'''
        alterlist = []
        for item in data.get('到达机场'):
            j = airports.get(item, 0.05)
            alterlist.append(j)
        data.loc[:, '到达机场'] = alterlist

        '''route type by calculating the sum of dep and arr airport ratio'''
        if i+j >= 1.4:
            i = '干线'
        elif i+j >= 0.9:
            i = '小干线'
        else:
            i = '支线'
        j = int(j)
        for j in range(len(alterlist)):
            alterlist[j] = i
        data.loc[:, '航线类型'] = alterlist

        '''time-rate calculation'''
        alterlist = []
        for item in data.get('出发时'):
            alterlist.append(item.hour + round(item.minute/60, 2))
        data.loc[:, '出发时'] = alterlist
        alterlist.sort()    #sort dep time list in ascending order
        data = data.sort_values('出发时')   #sort data by dep time too, so the alterlist and data are coordinated
        
        rtdict = {'小时段': '均率'}
        for i in range(24):
            rtdict[i] = 0    #initialize all keys (hour) of the time-rate dict to 0
        i = total = sum =0
        fcount = 1
        curr = int(alterlist[0])
        for item in data.get('折扣'):
            sum+= item  #sum every rate for avg
            dtime = int(alterlist[i]) #dep time in int
            diff = dtime - curr #time difference
            if diff:    #more than one hour passed
                rtdict[curr] = total/fcount #avg rate of current time added
                curr += diff
                fcount = total = 0  #flights counted and flight rates sumed
            total += item    #rate added
            fcount += 1  #flight +1
            i+= 1   #dep time list item and rate sumed +1
        else:
            rtdict[curr] = total/fcount
            sum /= i #rate avg
        #time-rate.py combined
        
        '''dep time is defined by the percentage of avg rate'''
        i = 0
        for item in alterlist:
            alterlist[i] = round(rtdict[int(item)]/sum, 2)
            i += 1
        data.loc[:, '出发时'] = alterlist
            
        #print(data)
        #pandas.DataFrame(rtdict).to_excel('time-rate.xlsx', index=False, encoding='GBK')
        
        
        # 输出表格式
        # 日期   星期    航司     机型  出发机场  到达机场   出发时    折扣  竞争 航线类型
        data.to_excel(path / ("preproc_" + file.name), index = True, header = True, encoding = 'GBK')



if __name__ == '__main__':
    main("2022-01-27")
    print('\nDone!')
