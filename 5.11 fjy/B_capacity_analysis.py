# -*- coding: utf-8 -*-
"""
方向 B —— 容量/崩溃分析 (V/C saturation)   America's Cup 2027, Naples
Infrastructure PW (lilfjy)

需求侧 (订正数据, 2026-06 队友重做后):
  - background_od.mtx                          = as-is 背景基线 (223, 用 222 内部块)
  - total_new_project_flow_internal_only.mtx   = 事件场景总量 PROJECT (222)
  - 美洲杯净增量 surge = PROJECT - background  (≈ 960万)
  ⚠️ 旧的 Tourist_AGGREGATE / TOTAL_flow 队友确认做错, 已弃用
  ⚠️ event/non_event 日拆分矩阵: 赛事增量被本底"忙日波动"污染(+91%含~80%噪声), 弃用

需求口径 (best-of-both, 按日):
  as-is 日到达   = background 月到达 / 30.4
  赛事日到达     = background月到达/30.4 + surge / 20 (游客增量摊到20个赛事日)
  -> 高峰小时 -> 轨道分担 -> V/C
供给侧: 服务赛事区的轨道线高峰单向运力 (Wikipedia, 见 CLAUDE.md)
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── 路径 ──────────────────────────────────────────────
ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
OUT  = os.path.join(HERE, "output_charts")
os.makedirs(OUT, exist_ok=True)
BACKGROUND = os.path.join(ROOT, "background_od.mtx")
PROJECT    = os.path.join(ROOT, "total_new_project_flow_internal_only.mtx")
ZONES      = os.path.join(HERE, "Zones.csv")

# ── 假设（答辩时在这里改）──────────────────────────────
DAYS_PER_MONTH = 30.4
N_EVENT_DAYS   = 20      # 赛事持续天数(李兆杰); 游客增量按此摊到每个赛事日
PEAK_HOUR_FRAC = 0.08    # 高峰小时占全日; As-is 早高峰 21.8%/4h≈5.5% × 峰内系数~1.4
TRANSIT_SHARE  = 0.50    # 轨道分担率(默认); 敏感性 40/50/60
SENS_SHARES    = [0.40, 0.50, 0.60]

CAP = {"L1": 12000, "L2": 3600, "L6": 7200, "Cumana": 1050}   # pax/h/dir

# 赛事相关区(NO) -> 服务的轨道线路 (按真实坐标核对, 见 Zones.csv)
ZONE_LINES = {
    79:  ["L1", "L2"],            # Napoli-73  Napoli Centrale 火车站枢纽 (站东, 0.8km)
    1:   ["L1", "L2"],            # Napoli-11  Centro Direzionale/Garibaldi (站西南, 0.8km)
    3:   ["L1", "L6"],            # Napoli-39  中心 Race Village/Municipio
    71:  ["L1"],                  # Napoli-7   中心北
    195: ["L1"],                  # Napoli-55  Vomero
    216: ["L1", "L6"],            # Napoli-71  中心/Municipio
    2:   ["L2", "L6", "Cumana"],  # Napoli-42  Fuorigrotta (西部换乘枢纽)
    10:  ["L2", "Cumana"],        # Napoli-68  Bagnoli (赛场技术区)
    33:  ["L2", "L6", "Cumana"],  # Napoli-40  Fuorigrotta/Mostra
}
# 走廊分组(走廊级口径 + 地图配色)
WEST    = [2, 10, 33]                 # 赛场/Fuorigrotta
CENTRAL = [79, 1, 3, 71, 195, 216]    # 中心滨海 + 火车站枢纽

# ── 解析 Visum $V 矩阵 (稳健版: 兼容有/无 "Network object numbers" 行 + 尾部名块) ──
def parse_v(path):
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
                pass   # 跳过尾部分区名块的 "" 等非数字
    return np.array(toks[n:n + n * n]).reshape(n, n)

BG_full = parse_v(BACKGROUND)          # 223
BG = BG_full[:222, :222]               # 内部 222 块
PROJ = parse_v(PROJECT)                # 222
SURGE = np.maximum(PROJ - BG, 0.0)     # 美洲杯净增量(逐格, 截断负值)

z = pd.read_csv(ZONES)
name = dict(zip(z["NO"], z["ZONE_NAME"].fillna("?")))

def bg_in(no):      # 进入某区的月到达量(背景, 列和)
    return BG[:, no - 1].sum()

def surge_in(no):   # 进入某区的美洲杯净增量(列和)
    return SURGE[:, no - 1].sum()

def asis_day(no):   # as-is 日到达
    return bg_in(no) / DAYS_PER_MONTH

def event_day(no):  # 赛事日到达 = as-is 日 + 增量/20
    return bg_in(no) / DAYS_PER_MONTH + surge_in(no) / N_EVENT_DAYS

def peak_rail(daily):   # 日到达 -> 高峰小时单向轨道需求
    return daily * PEAK_HOUR_FRAC * TRANSIT_SHARE

def los(vc):
    return ("A-C ok" if vc < .60 else "D busy" if vc < .80
            else "E near-cap" if vc < 1 else "F OVERSATURATED")

# ══════════════════════════════════════════════════════
print("=" * 78)
print("方向 B — V/C 容量饱和分析  (America's Cup 2027, Naples)  [订正数据版]")
print(f"数据: background_od + PROJECT | 净增量 surge={SURGE.sum():,.0f} (+{SURGE.sum()/BG.sum()*100:.1f}%)")
print(f"假设: 高峰小时={PEAK_HOUR_FRAC:.0%}/日 · 轨道分担={TRANSIT_SHARE:.0%} · 赛事增量摊到{N_EVENT_DAYS}天 · {DAYS_PER_MONTH}天/月")
print("=" * 78)

# ── 赛事区增幅一览 ──
print("\n【赛事区 赛事日 vs as-is 增幅】")
print(f"  {'NO':>4} {'zone':>12} {'as-is/日':>10} {'赛事/日':>10} {'增幅':>7}  线路")
tot_a = tot_e = 0.0
for no in ZONE_LINES:
    a, e = asis_day(no), event_day(no)
    tot_a += a; tot_e += e
    print(f"  {no:>4} {name.get(no,'?'):>12} {a:>10,.0f} {e:>10,.0f} {(e/a-1)*100:>6.0f}%  {'+'.join(ZONE_LINES[no])}")
print(f"  {'合计':>4} {'':>12} {tot_a:>10,.0f} {tot_e:>10,.0f} {(tot_e/tot_a-1)*100:>6.0f}%")

# ══════════════════════════════════════════════════════
# 口径 1 —— 走廊级
# ══════════════════════════════════════════════════════
print("\n【口径1: 走廊级】")
CORR = {"West (Bagnoli/Fuorigrotta 赛场)": (WEST, ["Cumana", "L2", "L6"]),
        "Central (滨海+火车站枢纽)":        (CENTRAL, ["L1"])}
for cn, (zs, lines) in CORR.items():
    da = sum(asis_day(n) for n in zs); de = sum(event_day(n) for n in zs)
    cap = sum(CAP[l] for l in lines)
    vb, ve = peak_rail(da) / cap, peak_rail(de) / cap
    flag = "🔴崩溃" if ve > 1 else "🟠临界" if ve > .80 else "🟢可承接"
    print(f"  {cn}: 线路 {'+'.join(lines)} 运力={cap:,}/h")
    print(f"    日到达 as-is {da:,.0f} -> 赛事 {de:,.0f} (+{(de/da-1)*100:.0f}%) | V/C {vb:.2f} -> {ve:.2f}  {flag}")

# ══════════════════════════════════════════════════════
# 口径 2 —— 逐条线路 (各区需求按服务线路运力比例分摊)
# ══════════════════════════════════════════════════════
print("\n【口径2: 逐条线路】(各区需求按运力比例分摊到服务线路)")
load_bg = {l: 0.0 for l in CAP}
load_ev = {l: 0.0 for l in CAP}
for no, lines in ZONE_LINES.items():
    capsum = sum(CAP[l] for l in lines)
    for l in lines:
        w = CAP[l] / capsum
        load_bg[l] += peak_rail(asis_day(no)) * w
        load_ev[l] += peak_rail(event_day(no)) * w

line_rows = []
print(f"  {'线路':6} {'运力/h':>8} {'现状V/C':>8} {'赛事V/C':>8}  判定")
for l in ["L1", "L6", "L2", "Cumana"]:
    vb, ve = load_bg[l] / CAP[l], load_ev[l] / CAP[l]
    flag = "🔴" if ve > 1 else "🟠" if ve > .80 else "🟢"
    print(f"  {l:6} {CAP[l]:>8,} {vb:>8.2f} {ve:>8.2f}  {flag} {los(ve)}")
    line_rows.append((l, vb, ve))

# 敏感性
print("\n敏感性 — 逐线路 赛事 V/C @ 分担率:")
print("  线路    " + "".join(f"{int(s*100)}%".rjust(9) for s in SENS_SHARES))
sens = {l: [] for l in CAP}
for l in ["L1", "L6", "L2", "Cumana"]:
    cells = ""
    for s in SENS_SHARES:
        lo = 0.0
        for no, lines in ZONE_LINES.items():
            if l in lines:
                capsum = sum(CAP[k] for k in lines)
                lo += event_day(no) * PEAK_HOUR_FRAC * s * (CAP[l] / capsum)
        vc = lo / CAP[l]
        sens[l].append(vc)
        cells += (f"{vc:.2f}" + ("🔴" if vc > 1 else "🟠" if vc > .80 else "🟢")).rjust(9)
    print(f"  {l:6}{cells}")

# ══════════════════════════════════════════════════════
# 图 1 —— 逐线路 V/C 柱状图
# ══════════════════════════════════════════════════════
lines = [r[0] for r in line_rows]
vb = [r[1] for r in line_rows]; ve = [r[2] for r in line_rows]
x = np.arange(len(lines)); w = 0.38
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.bar(x - w/2, vb, w, color="#7FB3D5")
ax.bar(x + w/2, ve, w,
       color=["#C0392B" if v > 1 else "#E67E22" if v > .80 else "#27AE60" for v in ve])
ax.axhline(1.0, color="#C0392B", ls="--", lw=1.5)
ax.text(len(lines)-0.5, 1.02, "V/C = 1.0  collapse", color="#C0392B", fontsize=9, ha="right")
for i, v in enumerate(ve):
    ax.text(i + w/2, v + 0.02, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([f"Metro {l}" if l.startswith("L") else l for l in lines])
ax.set_ylabel("V/C ratio (peak hour, per direction)")
ax.set_title("Peak-hour saturation by rail line — Naples\n"
             "America's Cup event day vs as-is (transit share 50%)", fontweight="bold")
ax.legend(handles=[
    mpatches.Patch(color="#7FB3D5", label="As-is day"),
    mpatches.Patch(color="#27AE60", label="Event day — within capacity (<0.80)"),
    mpatches.Patch(color="#E67E22", label="Event day — near capacity (0.80–1.0)"),
    mpatches.Patch(color="#C0392B", label="Event day — oversaturated (>1.0)"),
], fontsize=9)
ax.set_ylim(0, max(ve) * 1.3)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_chart_VC_by_line.png"), dpi=150, bbox_inches="tight")
plt.close(); print(f"\n  ✓ 图1 saved: output_charts/B_chart_VC_by_line.png")

# ══════════════════════════════════════════════════════
# 图 3 —— 敏感性: 逐线路 赛事 V/C vs 轨道分担率
# ══════════════════════════════════════════════════════
shares = np.array(SENS_SHARES)
fig, ax = plt.subplots(figsize=(9, 5.5))
colors = {"L1": "#C0392B", "L6": "#2980B9", "L2": "#27AE60", "Cumana": "#8E44AD"}
for l in ["L1", "L6", "L2", "Cumana"]:
    ys = sens[l]
    ax.plot(shares * 100, ys, "o-", color=colors[l], lw=2, markersize=7,
            label=f"Metro {l}" if l.startswith("L") else l)
    ax.annotate(f"{ys[-1]:.2f}", (shares[-1]*100, ys[-1]), xytext=(6, 0),
                textcoords="offset points", fontsize=9, color=colors[l], va="center")
ax.axhline(1.0, color="#C0392B", ls="--", lw=1.5)
ax.text(40, 1.02, "V/C = 1.0  collapse threshold", color="#C0392B", fontsize=9)
ax.set_xlabel("Assumed public-transit mode share (%)")
ax.set_ylabel("Event-day V/C ratio (peak hour, per direction)")
ax.set_title("Sensitivity of saturation to transit mode share\nAmerica's Cup 2027, Naples — rail lines",
             fontweight="bold")
ax.set_xticks([40, 50, 60]); ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_chart_sensitivity.png"), dpi=150, bbox_inches="tight")
plt.close(); print(f"  ✓ 图3 saved: output_charts/B_chart_sensitivity.png")

print("\n注: 🟢可承接 🟠临界(>.80) 🔴崩溃(>1.0) · V/C绝对值依赖分担率/高峰假设,相对增量稳健")
print("    数据底=订正后 background_od + PROJECT; 增量按20赛事日摊算(÷60保守下界见方法论)")
