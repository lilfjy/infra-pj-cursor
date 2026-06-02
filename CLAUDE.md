# 项目：Infrastructure PW — FSxPOLIMI 铁路 OD 分析

## 项目背景

这是一个与 **FS（意大利国家铁路）× 米兰理工大学（POLIMI）** 合作的数据分析项目。
核心目标：分析意大利铁路乘客的 **OD（出发地-目的地）矩阵**，重点关注坎帕尼亚（Campania）地区。

## 数据说明

| 文件 | 说明 |
|------|------|
| `OD_no_italia.mtx` | 排除意大利本国旅客后的 OD 矩阵 |
| `OD_origin_italia.mtx` | 出发地为意大利的 OD 矩阵 |
| `distance(1).mtx` | 距离矩阵（真实路网距离） |
| `距离矩阵.xlsx` | 距离矩阵的 Excel 版本 |
| `5.11 fjy/distance_real*.mtx` | 通过 OSRM 计算的真实路网距离矩阵 |
| `5.11 fjy/Zones.csv` | 3000 个交通分区的坐标 |
| `5.11 fjy/Lookup/` | 各类编码对照表（模式、国籍、时间段等） |

> ⚠️ 以下超大 CSV 文件（>100MB）**未上传到 GitHub**，保存在本地：
> - `OD-3000-zone-202410-matrice-fondamentale.csv` (124MB)
> - `OD-3000-zone_202410-matrice-integrativa.csv` (99MB)

## 代码文件

| 文件 | 功能 |
|------|------|
| `5.11 fjy/osrm_matrix.py` | 使用 OSRM API 计算 OD 对之间的真实路网距离 |
| `5.11 fjy/!!!osrm_matrix_v2.py` | OSRM 距离矩阵的改进版本 |
| `5.11 fjy/analysis.py` | 主分析脚本，生成可视化图表 |

## 输出结果

`5.11 fjy/output_charts/` 现含 **Part B 的 5 张图**(逐线V/C/敏感性/总览/饱和/可达性,详见「全部产出」节)。
> ⚠️ 早期 6 张 Part A 基础探索图(`chart1-6`,由 `analysis.py` 生成)已于 06-02 删除(被 Part B 取代,需要可重跑 `analysis.py` 再生)。

## 项目真实要求（来自官方 PDF）

> 主题：**用手机信令大数据分析异常大型事件的交通** —— 第 38 届美洲杯帆船赛（2027 春夏，那不勒斯湾）。
> 数据来源：手机信令（MND），非 GPS，基于分区(zone)而非精确坐标。参考期 **2024 年 10 月**。
> 官方 PDF：`Project_Work_FSxPOLIMI_March2026 (1)/` 内的 `20260310 project work v01.pdf` + `DataDeliveryGuide_FSxPOLIMI_March2026.pdf`

**教授要回答的 3 个核心问题**：① 美洲杯期间人流如何变化？② 需求集中在哪？③ **现有系统能否承接，还是会崩溃（collapse）？**

**三步方法论**：
- **Step 1「As is」现状**：OD 矩阵处理 + 异常检测/统计检验 + 地理可视化
- **Step 2 需求预测**：往届访客数据 + 住宿设施 + 估算流向赛事 POI 的新增人流
- **Step 3 服务改进**：现有公交供给分析 + 在建/未来基建 + 服务增强方案

**数据关键点**：
- 222 个 Campania 分区（其中 Napoli 省 77 个），意大利其余聚合为 "Italia"；停留阈值 1h
- OD CSV 用 **AREA_ID** 编码（如 5010），**不是** Zones.csv 的顺序号 NO；二者用 Zones.csv 映射
- 两个矩阵互补（GDPR <15 次掩码）：基础矩阵含**国籍+规律性**，补充矩阵含**交通方式**（仅识别火车/飞机）
- **日均换算**：月度 TRIPS ÷ 该星期在当月出现次数（2024-10：周二/三/四=5 次，其余=4 次）

## As-is 数据盘点（2024-10 两矩阵，已分析 05-31）

> 总量 **187,261,815 次/月**（两矩阵一致）。这是 B 的"分母"=背景基流。

- **区域 O-D**：Campania→Campania 1.763亿(94.1%) ｜ Campania→Italia 550万(2.9%) ｜ Italia→Campania 549万(2.9%)。→ 94% 区内；游客 +11% 是异常负荷
- **时段（双峰通勤）**：05-09 **21.8%** ｜ 16-20 **21.2%** ｜ 09-13 17.2% ｜ 20-24 15.8% ｜ 13-16 15.1% ｜ 00-05 8.9%
- **星期**：周三/四/二最高(~16%)，周日最低(11.9%)；**工作日 74.6% / 非工作日 25.4%**
- **居住地**：起点居民 39.9% / 终点居民 39.8% / **外地居民 16.1%**(最接近"访客") / 未定义 4.2%
- **国籍**：意大利人 96.1% / **外国人仅 3.9%**（反衬美洲杯异常性）
- **规律性**：偶发 55% / 规律(通勤) 45%
- **🔴 交通方式（B 的雷区）**：Altro 其他 **97.2%** / Ferrovia 铁路 2.7% / 航空 0.1%。数据**只识别火车+飞机**，**地铁L1/L6、Cumana、Circumvesuviana、公交、汽车全归 Altro**；且"铁路2.7%"只是 Trenitalia 国铁/区域线(含L2)，**不含城市地铁/EAV** → **不能用此数据推公交分担率**，B 必须用假设+敏感性并写明此局限
- **目的地省**：Napoli 1.026亿(54.8%) ≫ Salerno 3140万 > Caserta 2780万 > Avellino 1250万 > Benevento 750万
- **掩码占比**：规律性 14.9%(最高) > 星期/国籍 8% > 居住地 4.6% > **时段仅 2.0%✓** > 工作日 0.7%。→ 层级符合官方说明；**时段字段最干净 → B 的高峰小时分析数据可靠**

## 小组分工（重要）

| 成员 | 负责 part |
|------|----------|
| 苏艳婷 | Step 1「As is」+ 花哨的图 + 最后的 shuttle bus improvement |
| 李兆杰 (polimi mobility) | Step 2 预测流量（PTV **Visum** 重力模型，已锁定 **β=0.04**） |
| **我（lilfjy）** | **方向 B：容量/崩溃分析（V/C 饱和度）** —— 见下 |

- 小组 report：`INFRA.docx`（根目录）；李兆杰的 Visum 工程+地图在 `1. integrativa/Proj.ver` + 几张 PNG（**无 CSV 数值导出**）
- 答辩话术草稿：`5.11 fjy/答辩话术.docx`

## 我的个人 part —— 方向 B：容量/崩溃分析

> **为什么选 B**：不撞队友（A 标定会影响李兆杰的 β=0.04，已放弃 A）；直接回答教授头号问题"会不会崩溃"；可视化强；Step 3 基本空白。

**方法论**：赛事高峰小时需求 → 叠加到现有轨道线路运力 → 算 **V/C 比** → V/C>1 = 崩溃 → 出饱和度地图 + 各线 V/C 柱状图。

**赛事核心区**（7 个原始 + 补 2 个西部枢纽 = 9 区）：
1→5010, 3→5001, 10→5018(Bagnoli赛场), 71→5006, 73→10195970003(Nocera离群), 195→5055, 216→5071；**补充 2(Napoli-42)、33(Napoli-40) = Fuorigrotta/Mostra 西部轨道枢纽**

**已查到的轨道运力（高峰单向/小时，附 Wikipedia 来源）**：
- Metro L1 ≈ 12,000（1200/列×~10班）｜ Metro L6 ≈ 7,200（官方数）
- Metro L2 ≈ 3,600（估）｜ Cumana ≈ 1,050（估，每20min一班，ET400~350/列）

**待确认的关键假设**（决定崩溃结论）：① 高峰小时系数(现状早高峰 05-09 占 22%) ② **轨道分担率默认 50%**(可做 40/50/60 敏感性) ③ 阈值 V/C>1.0 + LOS 分级

### ⛔ 李兆杰给的需求矩阵（B 的输入，已解析 05-31）—— 🔴 此节已作废,见下方「数据订正」
> **以下 `Tourist_AGGREGATE`/`TOTAL_flow` 及其增幅(+11%/+20.6%/zone1+50%)队友 06-02 确认做错,文件已删。** 现用 `background_od`+`PROJECT`,增幅见「数据订正」节(全区+9.7%/9区赛事日+25%)。保留本节仅作历史推理记录。
- 文件（根目录，Visum `$V` 格式 223×223，含 Italia 聚合区）：
  - `Tourist_AGGREGATE.mtx` = 纯游客增量（5 个游客矩阵之和，无重力模型）
  - `TOTAL_flow.mtx` = 游客 + 背景基流；**背景 = TOTAL − Tourist**
- 解析法：跳过 `* Network object numbers` 后的前 223 个 zone-id token，其余 223×223 即矩阵；**矩阵 index = Zones.csv 的 NO**（列和=到达量）
- **量级**：游客增量 **11,000,000** / 背景 98,849,146 / 合计 109.8M → **全区域 +11.1%**（对上李兆杰说的~10%）。与报告 1.1M 自洽：110万人 × 人均~10 次 = 1100 万次
- **逐区到达增长（进入 7 区）**：zone1 Napoli-11 **+49.7%**(Napoli Centrale门户) ｜ zone3 +25.3% ｜ zone216 +23.5% ｜ zone71 +22.2% ｜ zone10(Bagnoli) +11.7% ｜ zone195 +6.5% ｜ zone73 +4.2%。**7 区平均 +20.6%，游客增量合计 198 万**
- ⚠️ **李兆杰说的"旅游区40%"≈ 峰值区 zone1(50%)，不是 7 区平均(20.6%)** → 增长高度不均
- 🎯 **B 的瓶颈定位**：崩溃风险集中在 **Napoli Centrale 门户(zone1,+50%) + 中心滨海(zone3/216,+24~25%)**；Bagnoli 赛场本身只 +12%(人到了再分流)

### ❓ 用前需向李兆杰确认 2 件事
1. **矩阵单位是"月"吗？**（背景 98.8M ≈ As-is 月度量级；做 V/C 要 月→日→高峰小时，必须先确认）
2. **他说的"40%"具体指哪些区？**（确认是 zone1 峰值，还是另有"核心旅游区"定义）

### 🔴 数据订正（2026-06-02 队友重做矩阵 → Part B 已重建）
**旧的 `Tourist_AGGREGATE` / `TOTAL_flow` 队友确认做错,弃用。** 订正后用:
- `background_od.mtx`(223, as-is 基线 **98.85M**) + `total_new_project_flow_internal_only.mtx`(222, 事件场景 PROJECT **108.45M**)
- **美洲杯净增量 = PROJECT − background = 960万(+9.7%)**（这是唯一可靠的赛事增量口径）
- 验证恒等式: `PROJECT = event + non_event − background`(逐格精确)→ event/non_event 两个日矩阵**各含一份背景**,直接加会重复算背景
- ⚠️ **event/non_event 日拆分矩阵弃用**:其 +91%/日 含 ~80% 本底"忙日/闲日"波动(隐含 4800万≈真实增量5倍),直接用会高估饱和度~5倍
- **分区语义修正**(按 Zones.csv 坐标核对):**火车站=zone 79**(站东,L1+L2),不是 zone1(zone1=Centro Direzionale,+74%);机场=191,火山=212(Ercolano),庞贝=68——191/212/68 在 Alibus/Circumvesuviana 另一张网,不进地铁 V/C(文字提及)

### ⭐ B 分析结果（已重建 06-02）—— 脚本 `5.11 fjy/B_capacity_analysis.py`
需求口径 **best-of-both 按日**:as-is日=背景月/30.4 ｜ 赛事日=as-is日+增量/**20赛事日**（÷60为保守下界）
假设：高峰小时=**8%/日** ｜ 轨道分担=**50%**（敏感性40/50/60）｜ 9区赛事日增幅 **+25%**

**口径2 逐线路**（各区需求按运力比例分摊；含新增 zone79 火车站枢纽）：
- **L1 现状 0.71 → 赛事日 0.91**（几乎满载；60% 分担率破 1.09🔴；走廊级中心全压L1=1.20）← **binding constraint**
- L2 0.70 ｜ L6 0.65 ｜ Cumana 0.51（均有余量）

**🎯 核心结论（答辩主线，不变且更强）**：瓶颈**不在赛场**——Bagnoli/Fuorigrotta 有 3 条线富余(V/C~0.51~0.70)；问题是**运力分布错位**，集中在 **L1 中心主干 + Napoli Centrale 火车站枢纽(zone79)**。即"**distribution 问题，非 capacity 问题**"→ 对策=L1 加密 + L6 分流。
**诚实caveat**：50% 分担率下 L1=0.91(临界、无冗余)、60% 才破1.0。稳健说法="L1 是 binding constraint，已无余量"。

**B 的第二维度 — OSRM 真实路网可达性**（脚本 `B_accessibility_osrm.py`）：
- ⚠️ **用 `distance_real_v2.mtx`（完整 222×222，单位=分钟）**；`distance_real.mtx`(v1) **残缺只算了 22/222 起点，勿用**
- 算各区到最近赛场(zone 3/10)的开车分钟 → 等时圈地图 + 游客来源(=surge行和)叠加
- 发现：**71% 的(Campania内)游客需求在 45 分钟车程内**(加权均 41min)→ 那不勒斯中心集中，印证 L1 走廊压力；**~21% 来自 >60min 远郊**(Salerno/Cilento)，靠长途公路+区域铁路

**全部产出**（`5.11 fjy/`，均已用订正数据重建 06-02）：
- 脚本：`B_capacity_analysis.py`(容量V/C) + `B_accessibility_osrm.py`(可达性) + `B_maps_shapefile.py`(面状图) + `B_map_rail_venues.py`(总览图) + `B_export_metrics.py`(Visum桥梁CSV)
- 图(`output_charts/`，英文可直接进 report,**全部 shapefile 真实地图,无散点**)：`B_chart_VC_by_line.png`(逐线V/C柱状) · `B_chart_sensitivity.png`(40/50/60%敏感性，L1在60%破1.09) · `B_map_venues_rail_schematic.png`(总览主图) · `B_map_saturation_shapefile.png`(饱和面状) · `B_map_accessibility_osrm.png`(可达性面状+游客来源)
- 文字：`B_methodology_results.md`(英文方法论+结论，可直接进report) + `B_答辩话术.md`(答辩Q&A，含教授追问标准答法)
- **可合并文档**：`PartB_section.docx`(带格式+内嵌5图，进 INFRA.docx) + `PartB_slides.pptx`(3页16:9，含演讲备注=话术)
- **面状图(shapefile choropleth，比散点专业，脚本 `B_maps_shapefile.py`)**：
  - **`B_map_venues_rail_schematic.png`**（报告主图：赛场★ + L1/L2/L6/Cumana 示意线 + 各线 Event V/C 标注）
  - `B_map_saturation_shapefile.png`(按**绝对游客到达增量**上色，中心区深红) · 可达性面状图改由 `B_accessibility_osrm.py` 出(`B_map_accessibility_osrm.png`,车程渐变+游客来源叠加；旧的纯车程版 `B_map_accessibility_shapefile.png` 06-02 已删)
  - shapefile 在 `Project_Work.../Shapefile/Campania.shp`(222区,WGS84,**记录顺序=分区NO顺序**,area_id 直接对位)
  - ⚠️ **数据质量发现**：按"增长%"上色会被**低基数农村区**(如 Greci +1031%)污染成假热点 → 改用**绝对增量**才诚实；真正瓶颈=中心高量区(+25~50%)。答辩可主动提这点。
  - **Visum 桥梁**：`B_zone_metrics.csv`(NO/AREA_ID/ZONE_NAME/background_in/tourist_in/project_in/growth_pct/access_min,脚本 `B_export_metrics.py`重生成) → 导入 Visum 按 area_id join 到 zone 层即可上色精修
- **分工边界**：B 只做"诊断"(哪堵/为何堵)；"开方"(增 shuttle bus)是苏艳婷的 Services improvement 部分

## 当前进度

> 📅 **最后更新：2026-06-02**

### ✅ 已完成
- [x] 项目初始化，数据文件整理
- [x] OSRM 真实距离矩阵计算（v1 + v2）
- [x] 基础可视化分析（6 张图表）
- [x] 代码上传至 GitHub：https://github.com/lilfjy/infra-pj-cursor
- [x] 读懂官方 PDF 完整要求 + 确定个人 part = 方向 B
- [x] **方向 B 现状基线已算**：进入 7 个赛事区的月度到达 ≈ **2,016 万**；双峰=早高峰 05-09(444万) + 晚高峰 16-20(404万)；区内 1950万 / 外部 66.5万
- [x] **供给侧运力已查**（L1/L2/L6/Cumana，见上）
- [x] **核验李兆杰选的 7 个目的地区**（用真实场地坐标）
- [x] **拿到并解析李兆杰的需求矩阵**（Tourist_AGGREGATE + TOTAL_flow）→ 验证全区域+11%、7区+20.6%、定位瓶颈在 Napoli Centrale（详见上节）
- [x] **As-is 数据完整盘点**（时段/星期/居住地/国籍/方式/掩码，详见「As-is 数据盘点」节）→ 发现交通方式数据不能直接推公交分担率
- [x] **B 分析跑通**：补入 zone 2/33；走廊级+逐线路两套 V/C；出 2 张图；核心结论=L1 binding constraint（详见「⭐ B 分析结果」节）
- [x] **B Part 完整化（06-01）**：+OSRM 可达性维度(图4)+敏感性图(图3)+英文方法论文档+答辩话术 → Part B 现为 2脚本+4图+2文档
- [x] **QA 修正（06-01）**：LOS 近满载阈值统一为 **0.80**(故 L1 0.84=E 与文档一致)；VC柱状图 L1 改橙色+状态色图例；docx/pptx 换用面状图并重嵌新柱状图；方法论 .md 图引用改面状图+加 growth%噪声说明
- [x] **总览图地理化升级（06-01，commit `a2b0aba`）**：`B_map_venues_rail_schematic.png` 从空白散点底图 → **真实官方 Campania shapefile 分区边界**(浅蓝海湾背景+9个赛事区高亮)，叠赛场★/西部枢纽◆/4条轨道线(按event V/C上色)+V/C标注；标签独立偏移+引线(解决 L1/L6 共端点 14.240,40.836 重叠)；同步重嵌进 docx/pptx/方法论
- [x] **🔴 Part B 重大重建（06-02，commit `f4decb7`）**：队友重做需求矩阵→旧 Tourist/TOTAL 弃用,换 `background_od`+`PROJECT`(净增量960万/+9.7%);确立 best-of-both 按日口径(增量÷20赛事日);弃用被本底污染的 event/non_event 日矩阵;按坐标修正分区语义(火车站=zone79,zone1=Centro Direzionale)并入 V/C。**新结果 L1 0.71→0.91**(60%破1.09,走廊级1.20),L2 0.70/L6 0.65/Cumana 0.51。**全部5脚本+方法论+答辩+docx+pptx 已用订正数据重建,内部一致**（详见「数据订正」+「⭐B分析结果」节）
- [x] **全 shapefile 化 + 清理（06-02）**：所有地图改用真实 Campania shapefile(零散点);删旧 Part A 图 chart1-6 + 冗余/散点图 + 做错的旧矩阵;可达性图最终定为**干净车程面状图**(去掉游客来源圆圈,否则看着像散点)→ docx Fig5/slide2 由用户手动粘新图
- [x] **答辩问答梳理（06-02）**：给用户讲清 OSRM 工作流(纯Python+调OSRM外部引擎)、÷30.4(月→日)、50%(轨道分担率假设+敏感性兜底)、三锚点功能(火车站=入口/RaceVillage=人群/Bagnoli=赛场)、Visum 导入(`B_zone_metrics.csv` 按area_id join,**着色用tourist_in别用growth_pct**)、给李兆杰的增幅回复话术

### 🔍 对李兆杰需求分配的核验结论（B 的输入）
- ✅ 框架合理(重力+POI)、β=0.04 正常、中心滨海(Castel dell'Ovo)+Napoli Centrale+Bagnoli 覆盖到位
- ⚠️ **漏了 Fuorigrotta/Mostra**(NO 2/33)——西部轨道总枢纽(L2+Cumana+L6 交汇)，最易堵的换乘点 → B 里要**主动补这条走廊**(加分点)
- ⚠️ Race Village 滨海精确区其实是 **NO 18**(0.3km)，他用的 zone 3 偏了~2km
- ⚠️ **zone 73(Nocera, 30km外)是离群点** → 待问李兆杰为何选它
- 🔴 他的分配**无分时段** → B 必须自己补高峰小时系数；外部 30万 是纯 POI 权重(无距离)，对走廊负荷指示性弱

### 📌 下一步起点（06-02 收工后）
**Part B 全部完成并已上云**（5脚本 + 5图全shapefile + 方法论 + 答辩 + docx + pptx + zone_metrics.csv,内部全一致）。剩下都是用户侧操作:
1. **发李兆杰增幅** —— 话术已写好(全区+9.7%/9区赛事日+25%,日拆分弃用),用户去发
2. **导入 Visum** —— 用 `B_zone_metrics.csv` 按 area_id join,⚠️ 着色用**绝对量 tourist_in**别用 growth_pct(低基数农村区假高)→ 精细化饱和面状图
3. **用户自己通读 report/slides** 备答辩(答辩问答口径已在「答辩问答梳理」条记录)
4. （可选）把 `PartB_section.docx` 并进小组 `INFRA.docx`
- ✅ **06-02 全部 commit&push 到 GitHub**(重建=`f4decb7`,可达性清理收尾见本次提交)

## 工作习惯

- 每次结束工作，更新本文件的「当前进度」部分
- 然后运行：`git add -A && git commit -m "更新进度" && git push`
- 下次 AI 进来会自动读取本文件，了解项目状态

## 仓库地址

https://github.com/lilfjy/infra-pj-cursor
