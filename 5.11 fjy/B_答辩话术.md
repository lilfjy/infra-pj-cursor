# Part B 答辩话术 —— 容量/崩溃分析 (Capacity & Saturation)

## 一、30 秒电梯陈述（开场就讲这个）

> "I analysed whether the rail network can absorb the America's Cup demand, using a
> volume-to-capacity (V/C) saturation analysis. The key finding is that **this is not a
> total-capacity problem — it's a distribution problem.** The race venue at Bagnoli is
> served by three lines and has plenty of spare capacity, but **Metro Line 1 — the central
> spine through the Napoli Centrale gateway — is the binding constraint**, going from 0.69
> to 0.84 at the peak, and over 1.0 if transit share reaches 60%. So the answer to 'will it
> collapse?' is: the network won't collapse overall, but Line 1 will, unless that specific
> corridor is reinforced."

中文版："我做的是'系统会不会崩溃'的容量饱和分析。核心结论:**这不是总运力不够,而是运力分布错位**——赛场(Bagnoli)有 3 条线、运力富余;真正的瓶颈是 **L1 中心主干 + Napoli Centrale 门户**,高峰 V/C 从 0.69 升到 0.84,分担率到 60% 就破 1.0。所以系统整体不会崩,但 L1 会,除非专门给这条走廊增能。"

## 二、核心数字（背下来）

- 全区域游客增量 **+11%**；中心赛事区 **+23%**；门户峰值区 **+50%**
- 逐线路赛事 V/C（50% 分担率）：**L1 = 0.84** ｜ L6 = 0.62 ｜ L2 = 0.62 ｜ Cumana = 0.50
- L1 在 **60% 分担率破 1.01**
- 运力(高峰单向/h)：L1 12000 ｜ L6 7200 ｜ L2 3600 ｜ Cumana 1050
- 公路可达性：**73% 游客需求在 45 分钟车程内**，加权平均 37 分钟，20% 来自 >60 分钟远郊

## 三、教授可能追问 + 标准答法

**Q: 你的"轨道分担率 50%"哪来的？凭什么？**
A: 这是假设,因为手机信令数据只识别火车/飞机,地铁/Cumana 全归"其他",**无法从数据直接观测城市公交分担率**。所以我做了 **40/50/60% 三档敏感性**(图3)。重点不是绝对值,而是:**只有 L1 会随分担率穿过 1.0,其余线全程安全**——这个结论对假设稳健。

**Q: 高峰小时 8% 怎么定的？**
A: 从 as-is 实测推的——早高峰时段(05–09)占全日 21.8%,4 小时即 ~5.5%/小时,乘峰内峰化系数 ~1.4 得 ~8%。是数据驱动、不是拍脑袋。

**Q: 你为什么把 zone 2/33 加进去？需求模型里没有。**
A: 正因为需求模型漏了。Fuorigrotta/Mostra 是**西部轨道总枢纽**(L2+Cumana+L6 交汇),是去 Bagnoli 赛场最关键的换乘点。漏掉它会低估西部走廊——所以我主动补上,让分析更贴近真实网络。

**Q: 你只算了进入赛事区的流量,线路上还有过境客流，V/C 是不是低估了？**
A: 对,这是诚实的简化——我用"目的赛事区的客流"近似线路负荷,真实负荷还含过境。所以我的 V/C 是**保守下界**;即便如此 L1 已到 0.84,真实只会更紧——**反而强化了"L1 是瓶颈"的结论**。

**Q: 背景基流 98.8M 是怎么来的？**
A: 来自队友的 Visum 模型(基于 as-is 数据,月度量级)。我的分析**内部自洽**——游客增量和背景出自同一套矩阵,V/C 全程在这套体系里算,不依赖外部对齐。

**Q: 那到底崩不崩？**
A: 取决于分担率。50% 时 L1 是 0.84(临界、无冗余);60% 时破 1.0。**稳健说法是:L1 已无余量,是 binding constraint**,而不是"全网崩溃"。这种精确比一句"会崩"更有价值。

**Q: 你的对策是什么？**
A: 我的部分是**诊断**:问题在 L1/中心走廊的分布,不在总量。**对策(增 shuttle bus 等服务增强)在 Services improvement 部分**展开——诊断指明了应该把资源投到 L1 走廊而非赛场。

## 四、OSRM 可达性（第二维度，体现工作量）

> "I also built a real road-network travel-time matrix with OSRM (222×222 zones,
> door-to-door driving minutes) to analyse where the demand comes from. 73% of the
> Campania-origin tourist demand is within a 45-minute drive of the venues — so it's
> Naples-centred, which is exactly why the central Line 1 corridor takes the pressure.
> The remaining ~20% comes from beyond 60 minutes and relies on road approaches and
> regional rail."

## 五、一句话收尾

> "So my contribution answers the headline question with precision: **the bottleneck is
> Line 1 and the Napoli Centrale gateway — a distribution problem — not a network-wide
> capacity shortfall.**"
