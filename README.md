# FlyCheap

**Flight Tickets Price Statistics and Analysis**

All folders' names are the data collecting date. A very beginning project :D

# 流程与功能说明
## 数据收集－CtripCrawler

### 特性

- 单线程（多线程通过外部实现）
- 代理池（使用[ProxyPool](https://github.com/Python3WebSpider/ProxyPool)）
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

### 爬取计划

- [x] 2022年春节期间、春节后，具有地域代表性的航班数据（2022年1月28日、2月10日完成）
- [x] 2022年2月17日以后30日部分客流较高（2019年旅客吞吐量前100名）城市间航班数据（2022年1月21日起开始，作为项目初始数据）
- [ ] **2022年3月29日以后45日部分客流较高（2019年旅客吞吐量前100名）城市间航班数据（2022年2月12日起开始，提前天数不超过45天）**
- [ ] 项目建模、训练、优化等工作完成后的测试和验证用例

### 数据量统计

| 数据集收集范围 | 所含日期 |             爬取日期             | 航线总量 |          航班总量          |                      备注                      |
| :------------: | :------: | :------------------------------: | :------: | :------------------------: | :--------------------------------------------: |
| 01-29 ~ 02-15  |    18    |              01-28               |    48    |           26,113           |                  春节假期数据                  |
| 02-10 ~ 02-16  |    7     |              02-09               |    55    |           12,846           |                  春节假期数据                  |
| 02-17 ~ 03-18  |    30    | 01-21 ~ 02-02<br />02-08 ~ 03-17 |   214    | 4,878,001<br />截止2月28日 | 由于网络问题间断五天<br />与以上两个数据集合并 |
| 03-29 ~ 05-13  |    45    |          02-12 ~ 05-12           |   288    |         （爬取中）         |                  国内干线为主                  |

### 附加程序：CtripSearcher

通过当前携程搜索页面的搜索api编写，参考CSDN，但爬取较为缓慢，未使用

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

### 附加功能

- 四种数据导入方式
- 整合数据的重复利用
- Rebuilder已整合数据预处理模块，见下文

## 数据预处理－Preprocessor

### 折扣影响

> 航线距离与机票价格成正比，且机票价格 = 全价 × 折扣，即
> $$
>  Price = Rate \times Airfare_{total} 
> $$
> 由于每条航线全价固定不变（一市多场近似相等），故在此不研究价格，而是机票折扣

- 每个航线机票折扣的不同，是**航线**、**时刻**、**航司**三个因素相互影响的结果
- 同一条航线上机票价格随日期的波动，是**航班日期**和**购买提前日期**两个因素独立影响的结果
- 本项目研究的正是以上五种因素对机票折扣的影响，并通过多种方式表达

### 影响因素（按影响程度排序）

#### 航线

- **航线固有性质**：城市间地级、城市地理位置、旅游城市、每日航班量和运营航司
- **航线日期特征**（通过统计分析得出）：票价随日期、周几、提前天数、假期的变化特点，受固有性质影响
- **航线时段特征**（通过统计分析得出）：票价随时段的变化特点，受固有性质、航司竞争影响

#### 日期

- **月份**：距航班起飞一周以外时间，次月票价往往高于本月票价
- **距航班起飞时间**：距航班起飞天数小于7天时，票价通常呈现大幅上涨趋势，包括于航线日期特征
- **星期几**：每周五出现票价小高峰，包括于航线日期特征
- **春节**：春节前后东西向客流差异导致价格变化反常；且除夕、春节期间票价极低，包括于航线日期特征
- **假期**：将寒暑假、短长假（清明、五一、端午、中秋、国庆等）划为假期，所有票价有所上升，包括于航线日期特征

#### 时段

- **起飞时间**：**最早班**（最低） - **早上**（大升） - **中午**（最高） - **下午**（略降） - **晚上**（大降） - **最晚班**（最低）
- **时段密度与竞争**：该航线在本时段上的密度将影响不同航司定价，包括于航线的时段特征

### 其他影响因素

- **机型**：非主导因素，不同机型票价仍主要随航班所在航线、日期、时刻、航司变化，忽略不计
- **航司**：受航线类型与特点、航班时刻及该竞争情况而变化

### 预处理结果表达

| 属性名称 | 解释                         | 意义                                 | 类型        |
| -------- | ---------------------------- | ------------------------------------ | ----------- |
| 出发地   | 出发城市、出发机场属性       | 反映航线特性                         | One-hot向量 |
| 到达地   | 到达城市、到达机场属性       | 反映航线特性                         | One-hot向量 |
| 每日密度 | 该航线每日航班数量平均值     | 反映航线繁忙程度                     | 浮点数      |
| 提前天数 | 购买机票日距航班起飞日期天数 | 反映机票折扣随航班时间临近的变化趋势 | 整型数      |
| 星期     | 航班起飞所在日期的星期       | 反映机票折扣的每周变化趋势           | One-hot向量 |
| 月份     | 航班起飞所在日期是否在本月后 | 反映机票折扣的月份变化趋势           | 布尔值      |
| 时间     | 航班起飞所在时段             | 反映时刻对机票折扣的影响             | One-hot向量 |
| 竞争     | 航班起飞所在时段的航司数量   | 反映航司竞争对机票折扣的影响         | 整型数      |



## 其他功能

### 自动化任务（Routine）

- 可实现分配范围后多线程爬取或多机多线程爬取
- 生成原数据表格后，加入待整合数据集
- 文件分类打包、整合数据集

### 爬取记录（Log）

- 记录终端输出的提示文字及输出时间
- 记录忽略或异常的城市对

# 尚未实现的功能

- [ ] 数学建模实验
- [ ] 机器学习实验
- [ ] 用户UI