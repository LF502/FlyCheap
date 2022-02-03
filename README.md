# FlyCheap
**Flight Tickets Price Statistics and Analysis**

All folders' names are the data collecting date. A very beginning project :D

# 流程说明
## 数据收集（CtripCrawler）

### 特性

- 单线程
- 代理池
- 防丢包
- 忽略集
- 矩阵化
- 定日期
- 带格式

### 缺点

- 爬取慢
- 无纠错
- 忽略共享航班和有经停的航班

### 输出

- **文件夹**：收集日期
- **文件名**：航线（双向）
- **表头**：航班日期、星期、航司、机型、出发到达机场及时刻、价格、折扣

### 爬取计划

- [x] 2022年春节期间、春节后，具有地域代表性的航班数据（2022年1月28日已完成－一次足够）
- [ ] 2022年2月17日以后30日部分客流较高（2019年旅客吞吐量前100名）城市间航班数据（2022年1月21日起开始爬取，作为项目初始数据）
- [ ] 2022年3月15日至5月15日部分客流较高（2019年旅客吞吐量前100名）城市间航班数据（2022年1月29日起开始爬取，提前天数不超过45天）
- [ ] 项目建模、训练、优化等工作完成后的测试和验证用例

## 数据预处理（Preprocessor）

### 折扣影响

——航线距离与机票全价成正比，可通过 价格 / 折扣 换算。在此不研究价格，而是机票折扣。

- 同一日期、同一航线中：航司（包括航司性质和航司间竞争）、时刻影响
- 同一时段、同一航线中：航司（包括航司性质和航司间竞争）、日期（包括星期和节假日）影响
- 同一日期、同一时段中：航司（包括航司性质和航司间竞争）、航线（起飞到达机场）

### 表达影响因素

——以同一航线为范围

#### 日期

- **距航班起飞时间**：天数。趋势：随着航班时间临近，票价由全价降低；后随旅客购买，舱位售罄，略升高；后出现更低价舱位机票，随供需呈不规则变化
- **星期几**：One-hot。趋势：**周日** - 周一（降） - **周中**（最低） - 周五（升） - **周六**
- **假期**：矩阵。趋势：春节与寒假（寒假开始、春节前、春节期间、春节后、寒假结束）；短假（五一、国庆等）；长假（暑假开始、暑运期间、暑假结束）

#### 航司

- **全服务 - 混合 - 廉价**：One-hot。趋势：票价越来越低
- **竞争**：同日航司数量。趋势：同时段 / 同日期航司越多，竞争越激烈，廉价航司越便宜；反之则差异不大

#### 时段

- **起飞时间**：One-hot / 待定。趋势：**最早班**（最低） - **早上**（大升） - **中午**（较低） - **下午**（略升） - **晚上**（大降） - **最晚班**（最低）

### 量化影响程度

#### 航线主导

- **起降机场**：One-hot。通过机场系数表达：机场国际枢纽、大型枢纽、中型机场、支线机场
- **城市级别**：One-hot。通过级别系数表达：一线、准一线、二线等
- **地理位置**：One-hot。通过距东海岸距离系数表达远近
- **航线客流**：起降机场系数之和。进一步分为干线、小干线、支线
- **时刻密度**：同时段 / 同日期航班数量。进一步分为高、中、低

#### 显著程度

- **星期、距航班起飞时间**：任意、非假期期间的航线，影响明显。
- **假期**：连接不同地理位置或连接不同级别城市的航线，以及旅游航线，影响明显。其余航线不明显。
- **航司**：高客流和高密度航线，对廉价航司的影响明显。其余航线不明显。
- **竞争**：高客流和高密度航线（干线和小干线），竞争越多，对廉价航司的折扣影响越明显；竞争越少，各个航司在该时段内折扣越趋同。其余航线不明显。
- **时段**：高客流或高密度航线，折扣影响明显。低客流或低密度航线不明显。

#### 量化形式

TBC