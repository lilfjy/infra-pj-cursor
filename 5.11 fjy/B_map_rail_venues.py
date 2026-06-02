# -*- coding: utf-8 -*-
"""
方向 B —— 报告用总览图：真实 Campania 分区边界(shapefile) + 那不勒斯湾
         + 赛场 + 四条轨道线 + 赛事 V/C
底图为官方 shapefile 真实分区边界(海湾=浅蓝背景, 9个赛事区高亮)；
轨道线走向基于公开站点坐标(示意线位, 非官方轨道 GIS)，用于空间叙事与答辩。
"""
import os, sys
import numpy as np
import pandas as pd
import shapefile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPoly
from matplotlib.collections import PatchCollection

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
OUT = os.path.join(HERE, "output_charts")
BACKGROUND = os.path.join(ROOT, "background_od.mtx")                       # as-is 基线 (223)
PROJECT = os.path.join(ROOT, "total_new_project_flow_internal_only.mtx")   # 事件场景 (222)
ZONES = os.path.join(HERE, "Zones.csv")
SHP = os.path.join(ROOT, "Project_Work_FSxPOLIMI_March2026 (1)",
                   "Project_Work_FSxPOLIMI_March2026", "Shapefile", "Campania.shp")

DAYS_PER_MONTH = 30.4
N_EVENT_DAYS = 20
PEAK_HOUR_FRAC = 0.08
TRANSIT_SHARE = 0.50
CAP = {"L1": 12000, "L2": 3600, "L6": 7200, "Cumana": 1050}
ZONE_LINES = {
    79: ["L1", "L2"],   # Napoli Centrale 火车站枢纽
    1: ["L1", "L2"], 3: ["L1", "L6"], 71: ["L1"], 195: ["L1"], 216: ["L1", "L6"],
    2: ["L2", "L6", "Cumana"], 10: ["L2", "Cumana"], 33: ["L2", "L6", "Cumana"],
}

# 示意线路折线 (lon, lat) — 主要换乘站/端点，非精确线位
RAIL_ROUTES = {
    "L1": [
        (14.272, 40.853), (14.258, 40.848), (14.250, 40.843), (14.240, 40.836),
        (14.232, 40.832), (14.225, 40.848), (14.218, 40.852),
    ],
    "L6": [(14.193, 40.823), (14.210, 40.828), (14.228, 40.833), (14.240, 40.836)],
    "L2": [(14.195, 40.828), (14.182, 40.824), (14.168, 40.820), (14.158, 40.812)],
    "Cumana": [
        (14.238, 40.848), (14.220, 40.838), (14.193, 40.823), (14.175, 40.818), (14.158, 40.808),
    ],
}
RAIL_COLORS = {"L1": "#C0392B", "L6": "#2980B9", "L2": "#27AE60", "Cumana": "#8E44AD"}
# (no, label, lon, lat, (dx,dy) label offset in points)
# 注: zone 1 是 Centro Direzionale(站西南), 火车站本体在 zone 79(站东); 星标放真实站点坐标
VENUES = [
    (10, "Bagnoli\n(venue & tech zone)", 14.171, 40.826, (-6, 26)),
    (3, "Race Village\n(central waterfront)", 14.237, 40.837, (14, 30)),
    (79, "Napoli Centrale\n(L1+L2 rail hub)", 14.272, 40.853, (12, 14)),
]
HUB = (2, "Fuorigrotta / Mostra\n(western interchange)", 14.199, 40.825, (24, -42))


def parse_v(path):
    """稳健 $V 解析: 读 n, 收集全部数字 token, 切片 [n:n+n*n]。"""
    n = None; nxt = False; started = False; toks = []
    for line in open(path, encoding="utf-8", errors="ignore"):
        s = line.strip()
        if s.startswith("* Number of network objects"):
            nxt = True; continue
        if nxt and s and not s.startswith("*"):
            n = int(s.split()[0]); nxt = False; started = True; continue
        if not started:
            continue
        if s.startswith(("*", "$")) or s in ("-", ""):
            continue
        for tok in s.split():
            try:
                toks.append(float(tok))
            except ValueError:
                pass
    return np.array(toks[n:n + n * n]).reshape(n, n)


def event_day(no, BG, SURGE):
    """赛事日到达 = as-is 日(背景月/30.4) + 增量/20"""
    return BG[:, no - 1].sum() / DAYS_PER_MONTH + SURGE[:, no - 1].sum() / N_EVENT_DAYS


def event_vc_by_line(BG, SURGE):
    load_ev = {l: 0.0 for l in CAP}
    for no, lines in ZONE_LINES.items():
        capsum = sum(CAP[l] for l in lines)
        d_ev = event_day(no, BG, SURGE) * PEAK_HOUR_FRAC * TRANSIT_SHARE
        for l in lines:
            load_ev[l] += d_ev * (CAP[l] / capsum)
    return {l: load_ev[l] / CAP[l] for l in CAP}


def vc_style(vc):
    if vc > 1.0:
        return "#C0392B", 5.5, "OVERSATURATED"
    if vc > 0.80:
        return "#E67E22", 4.5, "near capacity"
    if vc > 0.60:
        return "#F39C12", 3.5, "busy"
    return "#27AE60", 3.0, "headroom"


BG = parse_v(BACKGROUND)[:222, :222]
PROJ = parse_v(PROJECT)
SURGE = np.maximum(PROJ - BG, 0.0)
vc = event_vc_by_line(BG, SURGE)

# ── 底图：真实 shapefile 分区边界 ──
# shapefile 记录顺序 == 分区 NO 顺序 (record i <-> NO i+1)
EVENT_ZONES = set(ZONE_LINES.keys())   # 9 个赛事区 NO


def rings(shape):
    pts = shape.points
    parts = list(shape.parts) + [len(pts)]
    return [pts[parts[k]:parts[k + 1]] for k in range(len(parts) - 1)]


reader = shapefile.Reader(SHP)
shapes = reader.shapes()                # 222, 顺序=NO

fig, ax = plt.subplots(figsize=(10, 9))
ax.set_facecolor("#D6EAF8")             # 海湾/海面 = 浅蓝背景

# 真实分区面：普通区浅灰，9 个赛事区高亮米黄
patches, facecolors = [], []
for i, sh in enumerate(shapes):
    no = i + 1
    fc = "#FCF3CF" if no in EVENT_ZONES else "#ECF0F1"
    for ring in rings(sh):
        patches.append(MplPoly(ring, closed=True))
        facecolors.append(fc)
pc = PatchCollection(patches, facecolor=facecolors, edgecolor="white",
                     linewidths=0.35, zorder=1)
ax.add_collection(pc)

# ── 轨道示意线 + V/C 标注 ──
for line, route in RAIL_ROUTES.items():
    xs, ys = zip(*route)
    col, lw, status = vc_style(vc[line])
    ax.plot(xs, ys, color=col, lw=lw, solid_capstyle="round", zorder=4)
    mid = len(route) // 2
    lx, ly = route[mid]
    label = f"{'Metro ' if line.startswith('L') else ''}{line}\nEvent V/C={vc[line]:.2f} ({status})"
    off = (72, -40) if line == "L1" else (16, -46) if line == "L6" else (-62, 8) if line == "L2" else (-42, -42)
    ax.annotate(
        label, (lx, ly), xytext=off, textcoords="offset points", fontsize=8.5,
        fontweight="bold", color=col,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=col, alpha=0.92),
        arrowprops=dict(arrowstyle="-", color=col, lw=0.8),
        zorder=6,
    )

# ── 赛场 / 枢纽 ── 带引线，标签向不同象限拉开
for _no, txt, lon, lat, off in VENUES:
    ax.plot(lon, lat, marker="*", ms=22, c="#1A5276", mec="white", mew=1.4, zorder=8)
    ax.annotate(
        txt, (lon, lat), xytext=off, textcoords="offset points", fontsize=9,
        fontweight="bold", color="#1A5276", zorder=8, ha="center",
        bbox=dict(boxstyle="round,pad=0.28", fc="#EBF5FB", ec="#1A5276", alpha=0.95),
        arrowprops=dict(arrowstyle="-", color="#1A5276", lw=0.7),
    )
_no, txt, lon, lat, off = HUB
ax.plot(lon, lat, marker="D", ms=10, c="#D35400", mec="white", mew=1.0, zorder=8)
ax.annotate(
    txt, (lon, lat), xytext=off, textcoords="offset points", fontsize=8.5,
    fontweight="bold", color="#D35400", zorder=8, ha="center",
    bbox=dict(boxstyle="round,pad=0.28", fc="#FEF9E7", ec="#D35400", alpha=0.95),
    arrowprops=dict(arrowstyle="-", color="#D35400", lw=0.7),
)

# 海湾示意（浅蓝背景区 = 海面）
ax.annotate(
    "Gulf of Naples", xy=(14.205, 40.800), fontsize=11, color="#2874A6",
    style="italic", fontweight="bold", ha="center", zorder=2,
)

ax.set_xlim(14.115, 14.315)
ax.set_ylim(40.783, 40.882)
ax.set_aspect(1 / np.cos(np.radians(40.83)))
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(
    "America's Cup 2027 — event venues & serving rail lines\n"
    "Real Campania zone boundaries · line colour/width ∝ event V/C "
    "(peak hour, transit share 50%) · rail routes illustrative",
    fontsize=12,
    fontweight="bold",
)

legend_elems = [
    Line2D([0], [0], color="#C0392B", lw=4, label="Rail line, V/C > 0.80 (near cap / risk)"),
    Line2D([0], [0], color="#27AE60", lw=3, label="Rail line, V/C < 0.80 (headroom)"),
    mpatches.Patch(facecolor="#EBF5FB", edgecolor="#1A5276", label="★ Race venue / gateway"),
    mpatches.Patch(facecolor="#FEF9E7", edgecolor="#D35400", label="◆ Western rail interchange"),
    mpatches.Patch(facecolor="#FCF3CF", edgecolor="#BDC3C7", label="Event zone (served)"),
    mpatches.Patch(facecolor="#ECF0F1", edgecolor="#BDC3C7", label="Other Campania zone"),
]
ax.legend(handles=legend_elems, loc="upper left", fontsize=8.5, framealpha=0.95)
ax.text(
    0.02, 0.02,
    "Basemap: official Campania zone boundaries (shapefile, WGS84).\n"
    "Rail alignments schematic (major stations), not official track GIS.\n"
    "Demand: background_od + PROJECT event scenario; capacity from published headways.",
    transform=ax.transAxes, fontsize=7.5, color="#566573", va="bottom",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#D5D8DC", alpha=0.85),
)

plt.tight_layout()
out_path = os.path.join(OUT, "B_map_venues_rail_schematic.png")
plt.savefig(out_path, dpi=180, bbox_inches="tight")
plt.close()
print(f"✓ Saved: {out_path}")
for l in ["L1", "L6", "L2", "Cumana"]:
    print(f"  {l}: V/C={vc[l]:.2f}")
