import pandas as pd
import requests
import numpy as np
import time
import os
from datetime import date

# ── 路径设置 ──────────────────────────────────────────────
BASE = r"C:\Users\53592\Desktop\infrastructure PW\5.11 fjy"
ZONES_FILE = os.path.join(BASE, "Zones.csv")
OUTPUT_MTX = os.path.join(BASE, "distance_real_v2.mtx")

OSRM_URL = "http://router.project-osrm.org/table/v1/driving"

# ── 读取区域 ──────────────────────────────────────────────
print("Reading zones...")
df = pd.read_csv(ZONES_FILE)
df = df[['NO', 'ZONE_NAME', 'LAT', 'LON']].dropna().reset_index(drop=True)
n = len(df)
print(f"  {n} zones loaded")

# OSRM格式坐标: lon,lat
coords_list = [f"{row.LON:.6f},{row.LAT:.6f}" for _, row in df.iterrows()]

# ── 结果矩阵 ──────────────────────────────────────────────
matrix = np.zeros((n, n), dtype=int)

# ── OSRM只能一次处理~100个坐标，分批查询 ──────────────────
# 策略：每次取25个出发区，目的地是全部223个区
# 这样每次请求坐标数 = 25 + 223 = 248，在限制内
SRC_BATCH = 25

print(f"\nQuerying OSRM ({n}x{n} matrix, batch size={SRC_BATCH})...")
print(f"Total batches: {int(np.ceil(n/SRC_BATCH))}\n")

for batch_start in range(0, n, SRC_BATCH):
    batch_end = min(batch_start + SRC_BATCH, n)
    src_indices = list(range(batch_start, batch_end))
    
    # 把源区域坐标放前面，目的地坐标放后面
    src_coords = [coords_list[i] for i in src_indices]
    dst_coords = coords_list  # 全部223个
    
    all_coords = src_coords + dst_coords
    coord_str = ";".join(all_coords)
    
    # sources = 0 到 len(src)-1
    # destinations = len(src) 到 len(src)+n-1
    src_str = ";".join(str(i) for i in range(len(src_indices)))
    dst_str = ";".join(str(i) for i in range(len(src_indices), len(src_indices) + n))
    
    url = f"{OSRM_URL}/{coord_str}?sources={src_str}&destinations={dst_str}&annotations=duration"
    
    try:
        resp = requests.get(url, timeout=60)
        data = resp.json()
        
        if data.get('code') == 'Ok':
            durations = data['durations']
            for local_i, global_i in enumerate(src_indices):
                for j in range(n):
                    val = durations[local_i][j]
                    matrix[global_i][j] = round(val / 60) if val is not None else 0
            
            batch_num = batch_start // SRC_BATCH + 1
            total_batches = int(np.ceil(n / SRC_BATCH))
            print(f"  Batch {batch_num}/{total_batches}: zones {batch_start+1}-{batch_end} OK")
        else:
            print(f"  Batch error: {data.get('code')} - {data.get('message','')}")
            
    except Exception as e:
        print(f"  Batch {batch_start+1}-{batch_end} failed: {e}")
    
    time.sleep(0.5)

# ── 检查结果 ──────────────────────────────────────────────
flat = matrix[matrix > 0]
zero_count = np.sum(matrix == 0) - n  # 减去对角线
print(f"\nMatrix check:")
print(f"  Non-zero values: {len(flat)}")
print(f"  Unexpected zeros (off-diagonal): {zero_count}")
if len(flat) > 0:
    print(f"  Min: {flat.min()} min | Max: {flat.max()} min | Avg: {flat.mean():.1f} min")

# ── 写 .mtx 文件 ──────────────────────────────────────────
print(f"\nWriting .mtx file...")
today = date.today().strftime("%m/%d/%y")

with open(OUTPUT_MTX, 'w') as f:
    f.write("$V;D3\n")
    f.write("* From To\n- -\n")
    f.write("* Factor\n1.00\n*\n")
    f.write(f"* {today}\n")
    f.write("* Number of network objects\n")
    f.write(f"{n}\n")
    f.write("* Network object numbers\n")
    
    for i, row in df.iterrows():
        f.write(f"{int(row.NO):8d}")
        if (i + 1) % 10 == 0:
            f.write("\n")
    if n % 10 != 0:
        f.write("\n")
    
    for i in range(n):
        for j in range(n):
            f.write(f"{int(matrix[i][j]):8d}")
            if (j + 1) % 10 == 0:
                f.write("\n")
        if n % 10 != 0:
            f.write("\n")

print(f"\n✅ Done!")
print(f"   File: {OUTPUT_MTX}")
print(f"   Zones: {n}")
