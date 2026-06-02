# -*- coding: utf-8 -*-
"""
方向 B 第二维度 —— OSRM 真实路网可达性分析
用 distance_real_v2.mtx (222x222, 单位=分钟, OSRM door-to-door driving) 评估:
  各区开车到赛事场地的真实路网时间 -> 等时圈地图 + 游客来源叠加
回答: 赛事公路可达性如何? 游客需求从多远的地方来? 公路走廊压力在哪?
"""
import os, sys
import numpy as np
import pandas as pd
import shapefile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly
from matplotlib.collections import PatchCollection
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
OUT  = os.path.join(HERE, "output_charts")
DIST = os.path.join(HERE, "distance_real_v2.mtx")   # 完整版(v1残缺,勿用); 单位=分钟
BACKGROUND = os.path.join(ROOT, "background_od.mtx")                       # as-is 基线 (223)
PROJECT    = os.path.join(ROOT, "total_new_project_flow_internal_only.mtx") # 事件场景 (222)
ZONES = os.path.join(HERE, "Zones.csv")
SHP = os.path.join(ROOT, "Project_Work_FSxPOLIMI_March2026 (1)",
                   "Project_Work_FSxPOLIMI_March2026", "Shapefile", "Campania.shp")

VENUE = [3, 10]   # 赛事场地参考区: 3=中心Race Village, 10=Bagnoli技术区; 取到最近场地的时间
BANDS = [15, 30, 45, 60]   # 等时圈分钟

def parse_v(path):
    """稳健 $V 解析: 兼容有/无 'Network object numbers' 行 + 尾部名块"""
    n=None;nxt=False;st=False;toks=[]
    for line in open(path,encoding="utf-8",errors="ignore"):
        s=line.strip()
        if s.startswith("* Number of network objects"): nxt=True;continue
        if nxt and s and not s.startswith("*"): n=int(s.split()[0]);nxt=False;st=True;continue
        if not st: continue
        if s.startswith(("*","$")) or s in ("-",""): continue
        for tok in s.split():
            try: toks.append(float(tok))
            except ValueError: pass
    return np.array(toks[n:n*n+n]).reshape(n,n),n

D, nD = parse_v(DIST)                       # 222 (Campania)
BG = parse_v(BACKGROUND)[0][:222, :222]     # 222 内部块
PROJ = parse_v(PROJECT)[0]                  # 222
SURGE = np.maximum(PROJ - BG, 0.0)          # 美洲杯净增量
z = pd.read_csv(ZONES)
name = dict(zip(z["NO"], z["ZONE_NAME"].fillna("?")))

# 每区到"最近场地"的开车分钟 (索引: NO-1)
acc = np.minimum.reduce([D[:, v-1] for v in VENUE])   # len 222
# 自身=场地的设为 0
for v in VENUE: acc[v-1] = 0.0

# 每区作为"游客出发地"的量 = 美洲杯增量行和 (Campania 内 222 区)
tour_origin = SURGE.sum(axis=1)   # len 222

# 有效区: 有坐标 + 有可达性(>0 或本身是场地)
zc = z[z["NO"].between(1, 222)].copy().dropna(subset=["LAT", "LON"])
zc["acc"] = zc["NO"].map(lambda no: acc[no-1])
zc["tour"] = zc["NO"].map(lambda no: tour_origin[no-1])
zc = zc[(zc["acc"] > 0) | (zc["NO"].isin(VENUE))]   # 去掉未连通(islands等acc=0且非场地)

print("="*70)
print("方向 B 第二维度 — OSRM 真实路网可达性 (到赛事场地的开车分钟)")
print(f"场地参考: zone {VENUE} | 数据: distance_real_v2.mtx (分钟)")
print("="*70)

# 按等时圈统计 游客出发地 占比
tot_tour_camp = zc["tour"].sum()
print(f"\nCampania 内游客出发量(行和): {tot_tour_camp:,.0f}")
print("\n各等时圈内的'游客出发量'占比(衡量需求离场地多远):")
edges = [0]+BANDS+[9999]
labels = ["≤15min","15-30","30-45","45-60",">60min"]
cum=0
for lo,hi,lab in zip(edges[:-1],edges[1:],labels):
    m = zc[(zc["acc"]>lo)&(zc["acc"]<=hi)] if lo>0 else zc[(zc["acc"]>=0)&(zc["acc"]<=hi)]
    v=m["tour"].sum(); cum+=v
    print(f"  {lab:8s}: {v:>12,.0f}  {v/tot_tour_camp*100:5.1f}%   (累计 {cum/tot_tour_camp*100:5.1f}%)")

wmean = (zc["acc"]*zc["tour"]).sum()/tot_tour_camp
print(f"\n游客需求加权平均车程: {wmean:.0f} 分钟")
within45 = zc[zc["acc"]<=45]["tour"].sum()/tot_tour_camp*100
print(f"45分钟车程内的游客需求占比: {within45:.0f}%")

# ── 可达性地图 (真实 shapefile 面状底图 + 游客来源比例符号) ─────────────
def rings(shape):
    pts = shape.points; parts = list(shape.parts) + [len(pts)]
    return [pts[parts[k]:parts[k+1]] for k in range(len(parts)-1)]

reader = shapefile.Reader(SHP)
shapes = reader.shapes()              # 222, 记录顺序=NO

fig, ax = plt.subplots(figsize=(9.5, 8.5))
ax.set_facecolor("#D6EAF8")           # 海面 = 浅蓝
# 面状: 各区按到最近场地车程上色
patches, vals = [], []
for i, sh in enumerate(shapes):
    for ring in rings(sh):
        patches.append(MplPoly(ring, closed=True)); vals.append(acc[i])
pc = PatchCollection(patches, cmap="RdYlGn_r", edgecolor="white", linewidths=0.3, zorder=1)
pc.set_array(np.array(vals)); pc.set_clim(0, 75)
ax.add_collection(pc)
cb = plt.colorbar(pc, ax=ax, shrink=0.8)
cb.set_label("Driving time to nearest venue (min, OSRM real road network)")
# 场地星标
for v in VENUE:
    g = z[z["NO"] == v].iloc[0]
    ax.plot(g["LON"], g["LAT"], marker="*", ms=22, c="#1A5276",
            mec="white", mew=1.3, zorder=6)
ax.annotate("Bagnoli venue", (z[z.NO==10].iloc[0]["LON"], z[z.NO==10].iloc[0]["LAT"]),
            xytext=(6,6), textcoords="offset points", fontsize=9, fontweight="bold", zorder=7)
ax.annotate("Race Village", (z[z.NO==3].iloc[0]["LON"], z[z.NO==3].iloc[0]["LAT"]),
            xytext=(6,-12), textcoords="offset points", fontsize=9, fontweight="bold", zorder=7)
b = reader.bbox; ax.set_xlim(b[0], b[2]); ax.set_ylim(b[1], b[3])
ax.set_aspect(1/np.cos(np.radians(40.8)))
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.set_title("Road accessibility to America's Cup venues (OSRM, real road network)\n"
             "Choropleth on real zone boundaries — drive time to nearest venue (green = near, red = far)",
             fontweight="bold")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_map_accessibility_osrm.png"), dpi=150, bbox_inches="tight")
plt.close()
print(f"\n  ✓ 图4 saved: output_charts/B_map_accessibility_osrm.png (shapefile 面状版)")
print("\n注: 仅含 Campania 内出发的游客; 外部(意大利其余/国际)经长途铁路/高速/航空抵达, 不在此路网矩阵内。")
