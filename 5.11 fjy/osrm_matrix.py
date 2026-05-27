import pandas as pd
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore')

# ── 路径设置 ──────────────────────────────────────────────
BASE = r"C:\Users\53592\Desktop\infrastructure PW\5.11 fjy"
ZONES_FILE = os.path.join(BASE, "Zones.csv")
OUTPUT_MTX = os.path.join(BASE, "distance_real.mtx")

# OSRM 公开服务器
OSRM_URL = "http://router.project-osrm.org/table/v1/driving"

# ── 读取区域数据 ──────────────────────────────────────────
print("Reading zones...")
df = pd.read_csv(ZONES_FILE)
df = df[['NO', 'ZONE_NAME', 'LAT', 'LON']].dropna()
df = df.reset_index(drop=True)
n = len(df)
print(f"  {n} zones loaded")

# ── 坐标字符串列表（OSRM格式：lon,lat）──────────────────────
coords = [f"{row.LON},{row.LAT}" for _, row in df.iterrows()]

# ── 批量查询（每次最多100个区域，分批处理）────────────────────
BATCH = 100  # OSRM免费服务器每次最多处理约100个坐标

import numpy as np
matrix = np.zeros((n, n))

print(f"\nQuerying OSRM travel times ({n}x{n} matrix)...")
print("This will take a few minutes, please wait...\n")

# 把所有区域分批
batches = [list(range(i, min(i+BATCH, n))) for i in range(0, n, BATCH)]

for bi, src_batch in enumerate(batches):
    src_coords = ";".join([coords[i] for i in src_batch])
    all_coords = ";".join(coords)
    
    # sources=src indices, destinations=all
    src_indices = ";".join([str(i) for i in range(len(src_batch))])
    dst_indices = ";".join([str(i) for i in range(n)])
    
    # Build request with all coords, mark sources
    all_coord_list = [coords[i] for i in src_batch] + coords
    all_coord_str = ";".join(all_coord_list)
    src_idx_str = ";".join([str(i) for i in range(len(src_batch))])
    dst_idx_str = ";".join([str(i) for i in range(len(src_batch), len(src_batch)+n)])
    
    url = f"{OSRM_URL}/{all_coord_str}?sources={src_idx_str}&destinations={dst_idx_str}&annotations=duration"
    
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        
        if data.get('code') == 'Ok':
            durations = data['durations']
            for local_i, global_i in enumerate(src_batch):
                for j in range(n):
                    val = durations[local_i][j]
                    if val is None:
                        val = 0
                    matrix[global_i][j] = round(val / 60)  # seconds → minutes
            print(f"  Batch {bi+1}/{len(batches)} done ({src_batch[0]+1}-{src_batch[-1]+1})")
        else:
            print(f"  Batch {bi+1} error: {data.get('code')} - {data.get('message','')}")
            
    except Exception as e:
        print(f"  Batch {bi+1} failed: {e}")
    
    time.sleep(1)  # 礼貌等待，避免被限速

# ── 写入 .mtx 文件 ────────────────────────────────────────
print(f"\nWriting {OUTPUT_MTX}...")

from datetime import date
today = date.today().strftime("%m/%d/%y")

with open(OUTPUT_MTX, 'w') as f:
    f.write("$V;D3\n")
    f.write("* From To\n- -\n")
    f.write("* Factor\n1.00\n*\n")
    f.write(f"* {today}\n")
    f.write("* Number of network objects\n")
    f.write(f"{n}\n")
    f.write("* Network object numbers\n")
    
    # 写区域编号（每行10个）
    for i, row in df.iterrows():
        f.write(f"{int(row.NO):8d}")
        if (i+1) % 10 == 0:
            f.write("\n")
    if n % 10 != 0:
        f.write("\n")
    
    # 写矩阵数据（每行10个数）
    for i in range(n):
        for j in range(n):
            f.write(f"{int(matrix[i][j]):8d}")
            if (j+1) % 10 == 0:
                f.write("\n")
        if n % 10 != 0:
            f.write("\n")

print(f"\n✅ Done! Real travel time matrix saved to:")
print(f"   {OUTPUT_MTX}")
print(f"\nMatrix stats:")
flat = matrix[matrix > 0]
if len(flat) > 0:
    print(f"  Min travel time: {int(flat.min())} min")
    print(f"  Max travel time: {int(matrix.max())} min")
    print(f"  Average travel time: {flat.mean():.1f} min")
