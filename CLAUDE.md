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

`5.11 fjy/output_charts/` 包含以下分析图：
1. `chart1_top_destinations.png` — 热门目的地 Top N
2. `chart2_day_of_week.png` — 按星期几分布
3. `chart3_time_slots.png` — 按时间段分布
4. `chart4_transport_mode.png` — 交通方式分布
5. `chart5_nationality.png` — 国籍分布
6. `chart6_inbound_italy.png` — 入境意大利流量

## 当前进度

> 📅 **最后更新：2026-05-27**

### ✅ 已完成
- [ ] 项目初始化，数据文件整理
- [ ] OSRM 真实距离矩阵计算（v1 + v2）
- [ ] 基础可视化分析（6 张图表）
- [ ] 代码上传至 GitHub：https://github.com/lilfjy/infra-pj-cursor

### 🔄 进行中
- （在这里填写你目前正在做的事）

### 📌 下一步
- （在这里填写下次要做的事）

## 工作习惯

- 每次结束工作，更新本文件的「当前进度」部分
- 然后运行：`git add -A && git commit -m "更新进度" && git push`
- 下次 AI 进来会自动读取本文件，了解项目状态

## 仓库地址

https://github.com/lilfjy/infra-pj-cursor
