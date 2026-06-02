# -*- coding: utf-8 -*-
"""
方向 B —— 分区面状图 (choropleth) 用真实 shapefile 边界
比散点更专业、可拿去 Visum 精修。两张图:
  1) 各区赛事需求增长% (游客增量/背景)  -> 饱和压力空间分布
  2) 各区到赛场的真实路网车程(min, OSRM) -> 可达性
shapefile 记录顺序 == 分区 NO 顺序 == 矩阵索引 (record i <-> NO i+1 <-> idx i)
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
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
OUT  = os.path.join(HERE, "output_charts")
SHP  = os.path.join(ROOT, "Project_Work_FSxPOLIMI_March2026 (1)",
                    "Project_Work_FSxPOLIMI_March2026", "Shapefile", "Campania.shp")
BACKGROUND = os.path.join(ROOT, "background_od.mtx")                       # as-is 基线 (223)
PROJECT    = os.path.join(ROOT, "total_new_project_flow_internal_only.mtx") # 事件场景 (222)
DIST = os.path.join(HERE, "distance_real_v2.mtx")
VENUE = [3, 10]   # NO; 3=中心RaceVillage 10=Bagnoli

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
    return np.array(toks[n:n*n+n]).reshape(n,n)

BG=parse_v(BACKGROUND)[:222,:222]; PROJ=parse_v(PROJECT); D=parse_v(DIST)   # BG,PROJ:222  D:222
SURGE=np.maximum(PROJ-BG,0.0)   # 美洲杯净增量

# 各区(NO i+1, idx i, i=0..221) 指标
tour_in=SURGE.sum(axis=0)               # 进入各Campania区的游客增量(列和; = PROJECT-background)
bg_in  =BG.sum(axis=0)
growth =np.where(bg_in>0, tour_in/bg_in*100, 0.0)      # 增长%
acc=np.minimum(D[:, VENUE[0]-1], D[:, VENUE[1]-1])     # 到最近场地车程(min)
for v in VENUE: acc[v-1]=0.0

# 读 shapefile 几何
r=shapefile.Reader(SHP)
shapes=r.shapes()                       # 222, 顺序=NO

def rings(shape):
    pts=shape.points; parts=list(shape.parts)+[len(pts)]
    return [pts[parts[k]:parts[k+1]] for k in range(len(parts)-1)]

zc=pd.read_csv(os.path.join(HERE,"Zones.csv"))
def lalo(no):
    g=zc[zc.NO==no].iloc[0]; return g["LON"],g["LAT"]

def choropleth(values, cmap, vmin, vmax, title, clabel, fname, annots, zoom=None):
    fig,ax=plt.subplots(figsize=(10,9))
    patches=[]; vals=[]
    for i,sh in enumerate(shapes):
        for ring in rings(sh):
            patches.append(MplPoly(ring, closed=True)); vals.append(values[i])
    pc=PatchCollection(patches, cmap=cmap, edgecolor="white", linewidths=0.25)
    pc.set_array(np.array(vals)); pc.set_clim(vmin,vmax)
    ax.add_collection(pc)
    cb=plt.colorbar(pc, ax=ax, shrink=0.75); cb.set_label(clabel, fontsize=11)
    # 场地星标
    for v in VENUE:
        lo,la=lalo(v); ax.plot(lo,la,marker="*",ms=22,c="#1A5276",
                               mec="white",mew=1.3,zorder=6)
    for no,txt,dy in annots:
        lo,la=lalo(no); ax.annotate(txt,(lo,la),xytext=(7,dy),textcoords="offset points",
                                    fontsize=9,fontweight="bold",zorder=7,
                                    bbox=dict(boxstyle="round,pad=0.2",fc="white",ec="none",alpha=0.7))
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    if zoom: ax.set_xlim(zoom[0],zoom[1]); ax.set_ylim(zoom[2],zoom[3])
    else:
        b=r.bbox; ax.set_xlim(b[0],b[2]); ax.set_ylim(b[1],b[3])
    ax.set_aspect(1/np.cos(np.radians(40.8)))   # 经纬比例校正
    plt.tight_layout(); plt.savefig(os.path.join(OUT,fname),dpi=150,bbox_inches="tight")
    plt.close(); print(f"  ✓ {fname}")

# 图A: 绝对游客到达增量 (需求真正落在哪; 避开低基数百分比噪声) — 放大那不勒斯
vmaxA=float(np.percentile(tour_in,97))
choropleth(np.clip(tour_in,0,vmaxA), "YlOrRd", 0, vmaxA,
           "America's Cup added demand — where the surge lands\n(tourist-arrival increment per zone, trips/month; red = highest absolute load)",
           "Tourist arrivals increment (trips/month)", "B_map_saturation_shapefile.png",
           [(79,"Napoli Centrale\n(rail hub)",6),(1,"Centro Direzionale",-14),(10,"Bagnoli venue",-14),(3,"Race Village",6)],
           zoom=(14.05,14.45,40.75,40.95))
# 注: 可达性面状图改由 B_accessibility_osrm.py 生成(含游客来源叠加, 更丰富),此处不再重复出图
print("Done. 饱和面状图已生成 (可导入 Visum 精修)。")
