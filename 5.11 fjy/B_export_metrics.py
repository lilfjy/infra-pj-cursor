# -*- coding: utf-8 -*-
"""导出 B_zone_metrics.csv —— Visum 桥梁表 (按 area_id join 到 zone 层上色)。
列: NO, AREA_ID, ZONE_NAME, background_in, tourist_in(surge), project_in,
    growth_pct, access_min   ⚠️ Visum 着色用绝对量 tourist_in, 不用 growth_pct"""
import os, sys
import numpy as np
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\53592\Desktop\infrastructure PW"
HERE = os.path.join(ROOT, "5.11 fjy")
BACKGROUND = os.path.join(ROOT, "background_od.mtx")
PROJECT    = os.path.join(ROOT, "total_new_project_flow_internal_only.mtx")
DIST = os.path.join(HERE, "distance_real_v2.mtx")
ZONES = os.path.join(HERE, "Zones.csv")
VENUE = [3, 10]


def parse_v(path):
    n = None; nxt = False; st = False; toks = []
    for line in open(path, encoding="utf-8", errors="ignore"):
        s = line.strip()
        if s.startswith("* Number of network objects"): nxt = True; continue
        if nxt and s and not s.startswith("*"): n = int(s.split()[0]); nxt = False; st = True; continue
        if not st: continue
        if s.startswith(("*", "$")) or s in ("-", ""): continue
        for tok in s.split():
            try: toks.append(float(tok))
            except ValueError: pass
    return np.array(toks[n:n * n + n]).reshape(n, n)


BG = parse_v(BACKGROUND)[:222, :222]
PROJ = parse_v(PROJECT)
SURGE = np.maximum(PROJ - BG, 0.0)
D = parse_v(DIST)
acc = np.minimum(D[:, VENUE[0] - 1], D[:, VENUE[1] - 1])
for v in VENUE: acc[v - 1] = 0.0

bg_in = BG.sum(axis=0); tour_in = SURGE.sum(axis=0); proj_in = PROJ.sum(axis=0)
z = pd.read_csv(ZONES)
z = z[z["NO"].between(1, 222)].copy()
z["background_in"] = z["NO"].map(lambda no: bg_in[no - 1])
z["tourist_in"] = z["NO"].map(lambda no: tour_in[no - 1])
z["project_in"] = z["NO"].map(lambda no: proj_in[no - 1])
z["growth_pct"] = z["NO"].map(lambda no: tour_in[no - 1] / bg_in[no - 1] * 100 if bg_in[no - 1] > 0 else 0.0)
z["access_min"] = z["NO"].map(lambda no: acc[no - 1])
out = z[["NO", "AREA_ID", "ZONE_NAME", "background_in", "tourist_in", "project_in", "growth_pct", "access_min"]]
out.to_csv(os.path.join(HERE, "B_zone_metrics.csv"), index=False)
print(f"✓ B_zone_metrics.csv ({len(out)} zones) | region surge={tour_in.sum():,.0f} (+{tour_in.sum()/bg_in.sum()*100:.1f}%)")
