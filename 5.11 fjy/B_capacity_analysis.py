# -*- coding: utf-8 -*-
"""
方向 B —— 容量/崩溃分析 (V/C saturation)   America's Cup 2027, Naples
Infrastructure PW (lilfjy)

需求侧: 李兆杰 Tourist_AGGREGATE.mtx (游客增量) + 背景 = TOTAL_flow - Tourist
供给侧: 服务赛事区的轨道线路高峰单向运力 (Wikipedia, 见 CLAUDE.md)
链路:   进入赛事区到达量(列和,月) -> 日 -> 高峰小时 -> 轨道分担 -> V/C
两套口径: (1) 走廊级  (2) 逐条线路级(按运力比例分摊各区需求)
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── 路径 ──────────────────────────────────────────────
ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
OUT  = os.path.join(HERE, "output_charts")
os.makedirs(OUT, exist_ok=True)
TOURIST = os.path.join(ROOT, "Tourist_AGGREGATE.mtx")
TOTAL   = os.path.join(ROOT, "TOTAL_flow.mtx")
ZONES   = os.path.join(HERE, "Zones.csv")

# ── 假设（答辩时在这里改）──────────────────────────────
DAYS_PER_MONTH = 30.4
PEAK_HOUR_FRAC = 0.08    # 高峰小时占全日; 来源 As-is 早高峰 21.8%/4h≈5.5% × 峰内系数~1.4
TRANSIT_SHARE  = 0.50    # 轨道分担率(默认); 敏感性 40/50/60
SENS_SHARES    = [0.40, 0.50, 0.60]

CAP = {"L1": 12000, "L2": 3600, "L6": 7200, "Cumana": 1050}   # pax/h/dir

# 赛事区(NO) -> 服务的轨道线路 (按地理位置)
ZONE_LINES = {
    1:   ["L1", "L2"],            # Napoli-11  Garibaldi/Napoli Centrale 门户
    3:   ["L1", "L6"],            # Napoli-39  中心/Municipio
    71:  ["L1"],                  # Napoli-7   中心北
    195: ["L1"],                  # Napoli-55  Vomero
    216: ["L1", "L6"],            # Napoli-71  中心/Municipio
    2:   ["L2", "L6", "Cumana"],  # Napoli-42  Fuorigrotta
    10:  ["L2", "Cumana"],        # Napoli-68  Bagnoli (赛场技术区)
    33:  ["L2", "L6", "Cumana"],  # Napoli-40  Fuorigrotta/Mostra
}
# 走廊分组(用于走廊级口径 + 地图配色)
WEST    = [2, 10, 33]
CENTRAL = [1, 3, 71, 195, 216]
OUTLIER = [73]   # Nocera Superiore, 区域铁路, 单列

# ── 解析 Visum $V 矩阵 ─────────────────────────────────
def parse_v(path, n=223):
    toks, collect = [], False
    for line in open(path, encoding="utf-8", errors="ignore"):
        s = line.strip()
        if s.startswith("* Network object numbers"):
            collect = True; continue
        if not collect: continue
        if s.startswith(("*", "$")) or s in ("-", ""):
            continue
        toks += s.split()
    nums = [float(x) for x in toks][n:]
    return np.array(nums[:n * n]).reshape(n, n)

T = parse_v(TOURIST)
F = parse_v(TOTAL)
B = F - T
z = pd.read_csv(ZONES)
name = dict(zip(z["NO"], z["ZONE_NAME"].fillna("?")))

def inbound(mat, no):           # 进入某区的月到达量 = 列和
    return mat[:, no - 1].sum()

def peak_transit(monthly):      # 月 -> 高峰小时单向轨道需求
    return monthly / DAYS_PER_MONTH * PEAK_HOUR_FRAC * TRANSIT_SHARE

def los(vc):
    return ("A-C ok" if vc < .60 else "D busy" if vc < .80
            else "E near-cap" if vc < 1 else "F OVERSATURATED")

# ══════════════════════════════════════════════════════
# 口径 1 —— 走廊级
# ══════════════════════════════════════════════════════
print("=" * 74)
print("方向 B — V/C 容量饱和分析  (America's Cup 2027, Naples)")
print(f"假设: 高峰小时={PEAK_HOUR_FRAC:.0%}/日 · 轨道分担={TRANSIT_SHARE:.0%} · {DAYS_PER_MONTH}天/月")
print("=" * 74)
print("\n【口径1: 走廊级】")
CORR = {"West (Bagnoli/Fuorigrotta 赛场)": (WEST, ["Cumana", "L2", "L6"]),
        "Central (滨海+Napoli Centrale)":   (CENTRAL, ["L1"])}
for cn, (zs, lines) in CORR.items():
    bg = sum(inbound(B, n) for n in zs); tr = sum(inbound(T, n) for n in zs)
    cap = sum(CAP[l] for l in lines)
    vb, ve = peak_transit(bg) / cap, peak_transit(bg + tr) / cap
    flag = "🔴崩溃" if ve > 1 else "🟠临界" if ve > .80 else "🟢可承接"
    print(f"  {cn}")
    print(f"    线路 {'+'.join(lines)} 运力={cap:,}/h | 月到达 背景{bg:,.0f}+游客{tr:,.0f}(+{tr/bg*100:.0f}%)")
    print(f"    V/C 现状 {vb:.2f} -> 赛事 {ve:.2f}  {flag}")

# ══════════════════════════════════════════════════════
# 口径 2 —— 逐条线路 (各区需求按服务线路运力比例分摊)
# ══════════════════════════════════════════════════════
print("\n【口径2: 逐条线路】(各区需求按运力比例分摊到服务线路)")
load_bg = {l: 0.0 for l in CAP}
load_ev = {l: 0.0 for l in CAP}
for no, lines in ZONE_LINES.items():
    capsum = sum(CAP[l] for l in lines)
    d_bg = peak_transit(inbound(B, no))
    d_ev = peak_transit(inbound(B, no) + inbound(T, no))
    for l in lines:
        w = CAP[l] / capsum
        load_bg[l] += d_bg * w
        load_ev[l] += d_ev * w

line_rows = []
print(f"  {'线路':6} {'运力/h':>8} {'现状负荷':>9} {'赛事负荷':>9} {'现状V/C':>8} {'赛事V/C':>8}  判定")
for l in ["L1", "L6", "L2", "Cumana"]:
    vb, ve = load_bg[l] / CAP[l], load_ev[l] / CAP[l]
    flag = "🔴" if ve > 1 else "🟠" if ve > .80 else "🟢"
    print(f"  {l:6} {CAP[l]:>8,} {load_bg[l]:>9,.0f} {load_ev[l]:>9,.0f} {vb:>8.2f} {ve:>8.2f}  {flag} {los(ve)}")
    line_rows.append((l, vb, ve))

print(f"\n  Outlier zone73 Nocera: 背景{inbound(B,73):,.0f}+游客{inbound(T,73):,.0f}(+{inbound(T,73)/inbound(B,73)*100:.0f}%) 区域铁路,压力小")

# 敏感性
print("\n敏感性 — 逐线路 赛事 V/C @ 分担率:")
print("  线路    " + "".join(f"{int(s*100)}%".rjust(9) for s in SENS_SHARES))
for l in ["L1", "L6", "L2", "Cumana"]:
    cells = ""
    for s in SENS_SHARES:
        lo = 0.0
        for no, lines in ZONE_LINES.items():
            if l in lines:
                capsum = sum(CAP[k] for k in lines)
                m = inbound(B, no) + inbound(T, no)
                lo += m / DAYS_PER_MONTH * PEAK_HOUR_FRAC * s * (CAP[l] / capsum)
        vc = lo / CAP[l]
        cells += (f"{vc:.2f}" + ("🔴" if vc > 1 else "🟠" if vc > .80 else "🟢")).rjust(9)
    print(f"  {l:6}{cells}")

# ══════════════════════════════════════════════════════
# 图 1 —— 逐线路 V/C 柱状图
# ══════════════════════════════════════════════════════
lines = [r[0] for r in line_rows]
vb = [r[1] for r in line_rows]; ve = [r[2] for r in line_rows]
x = np.arange(len(lines)); w = 0.38
import matplotlib.patches as mpatches
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
ax.set_title("Peak-hour saturation by rail line — Naples\nAmerica's Cup 2027 (transit share 50%)",
             fontweight="bold")
ax.legend(handles=[
    mpatches.Patch(color="#7FB3D5", label="Baseline (As-is)"),
    mpatches.Patch(color="#27AE60", label="Event — within capacity (<0.80)"),
    mpatches.Patch(color="#E67E22", label="Event — near capacity (0.80–1.0)"),
    mpatches.Patch(color="#C0392B", label="Event — oversaturated (>1.0)"),
], fontsize=9)
ax.set_ylim(0, max(ve) * 1.25)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_chart_VC_by_line.png"), dpi=150, bbox_inches="tight")
plt.close(); print(f"\n  ✓ 图1 saved: output_charts/B_chart_VC_by_line.png")

# ══════════════════════════════════════════════════════
# 图 2 —— 饱和度地图
# ══════════════════════════════════════════════════════
zc = z.dropna(subset=["LAT", "LON"])
fig, ax = plt.subplots(figsize=(9, 8))
# 背景: 所有 Campania 区 faint
ax.scatter(zc["LON"], zc["LAT"], s=6, c="#D5D8DC", alpha=0.6, zorder=1)
# 赛事区: 西部=绿(富余) 中心=红(饱和), size ∝ 游客增量
def gz(no): return z[z["NO"] == no].iloc[0]
for grp, col, lab in [(WEST, "#27AE60", "West venue (headroom V/C~0.4)"),
                      (CENTRAL, "#C0392B", "Central spine L1 (saturated V/C>1)")]:
    lons = [gz(n)["LON"] for n in grp]; lats = [gz(n)["LAT"] for n in grp]
    sz = [max(60, inbound(T, n) / 800) for n in grp]
    ax.scatter(lons, lats, s=sz, c=col, alpha=0.8, edgecolors="k", linewidths=0.6, zorder=3, label=lab)
# 标注关键点
for n, txt in [(1, "Napoli Centrale\n(gateway +50%)"), (10, "Bagnoli\n(venue)"), (2, "Fuorigrotta/Mostra")]:
    g = gz(n); ax.annotate(txt, (g["LON"], g["LAT"]), fontsize=8, xytext=(6, 6),
                           textcoords="offset points", fontweight="bold")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.set_title("America's Cup 2027 — transit saturation hotspots\n"
             "Bubble size ∝ tourist increment | red = oversaturated, green = headroom", fontweight="bold")
ax.legend(loc="lower right", fontsize=9)
ax.set_xlim(14.0, 14.45); ax.set_ylim(40.75, 40.95)   # zoom Naples
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_map_saturation.png"), dpi=150, bbox_inches="tight")
plt.close(); print(f"  ✓ 图2 saved: output_charts/B_map_saturation.png")

# ══════════════════════════════════════════════════════
# 图 3 —— 敏感性: 逐线路 赛事 V/C vs 轨道分担率
# ══════════════════════════════════════════════════════
shares = np.array(SENS_SHARES)
fig, ax = plt.subplots(figsize=(9, 5.5))
colors = {"L1": "#C0392B", "L6": "#2980B9", "L2": "#27AE60", "Cumana": "#8E44AD"}
for l in ["L1", "L6", "L2", "Cumana"]:
    ys = []
    for s in shares:
        lo = sum((inbound(B, no) + inbound(T, no)) / DAYS_PER_MONTH * PEAK_HOUR_FRAC * s
                 * (CAP[l] / sum(CAP[k] for k in ln))
                 for no, ln in ZONE_LINES.items() if l in ln)
        ys.append(lo / CAP[l])
    ax.plot(shares * 100, ys, "o-", color=colors[l], lw=2, markersize=7,
            label=f"Metro {l}" if l.startswith("L") else l)
    ax.annotate(f"{ys[-1]:.2f}", (shares[-1]*100, ys[-1]), xytext=(6, 0),
                textcoords="offset points", fontsize=9, color=colors[l], va="center")
ax.axhline(1.0, color="#C0392B", ls="--", lw=1.5)
ax.text(40, 1.02, "V/C = 1.0  collapse threshold", color="#C0392B", fontsize=9)
ax.set_xlabel("Assumed public-transit mode share (%)")
ax.set_ylabel("Event V/C ratio (peak hour, per direction)")
ax.set_title("Sensitivity of saturation to transit mode share\nAmerica's Cup 2027, Naples — rail lines",
             fontweight="bold")
ax.set_xticks([40, 50, 60]); ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "B_chart_sensitivity.png"), dpi=150, bbox_inches="tight")
plt.close(); print(f"  ✓ 图3 saved: output_charts/B_chart_sensitivity.png")

print("\n注: 🟢可承接 🟠临界(>.80) 🔴崩溃(>1.0) · V/C绝对值依赖分担率假设,相对增量稳健 · 图为英文(report用)")
