import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# ── 路径设置 ──────────────────────────────────────────────
BASE = r"C:\Users\53592\Desktop\infrastructure PW\5.11 fjy"
OUT  = os.path.join(BASE, "output_charts")
os.makedirs(OUT, exist_ok=True)

INTEGRATIVA  = os.path.join(BASE, "OD-3000-zone_202410-matrice-integrativa.csv")
FONDAMENTALE = os.path.join(BASE, "OD-3000-zone-202410-matrice-fondamentale.csv")
LOOKUP_DIR   = os.path.join(BASE, "Lookup")

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi']  = 150

print("Loading data... (may take 30-60 seconds)")

# ── 读取数据 ──────────────────────────────────────────────
df_int  = pd.read_csv(INTEGRATIVA,  sep=';', encoding='utf-8-sig', low_memory=False)
df_fond = pd.read_csv(FONDAMENTALE, sep=';', encoding='utf-8-sig', low_memory=False)

print(f"Integrativa:  {len(df_int):,} rows")
print(f"Fondamentale: {len(df_fond):,} rows")

# ── Lookup tables ─────────────────────────────────────────
def load_lookup(filename, id_col, name_col):
    path = os.path.join(LOOKUP_DIR, filename)
    df = pd.read_csv(path, sep=',', encoding='utf-8-sig')
    return dict(zip(df[id_col], df[name_col]))

giorno_map     = load_lookup('vfa-ferservizi_giorno_settimana_lookup.csv',   'GIORNO_SETTIMANA_ID',   'GIORNO_SETTIMANA')
tipo_giorno_map= load_lookup('vfa-ferservizi_tipo_giorno_lookup.csv',        'TIPO_GIORNO_ID',        'TIPO_GIORNO')
fascia_map     = load_lookup('vfa-ferservizi_fasce_orarie_macro_lookup.csv', 'FASCIA_ORARIA_MACRO_ID','FASCIA_ORARIA_MACRO')
modalita_map   = load_lookup('vfa-ferservizi_modalita_lookup.csv',           'MODALITA_ID',           'MODALITA')
nazionalita_map= load_lookup('vfa-ferservizi_tipo_nazionalita_lookup.csv',   'TIPO_NAZIONALITA_ID',   'TIPO_NAZIONALITA')
sistematicita_map = load_lookup('vfa-ferservizi_sistematicita_lookup.csv',   'SISTEMATICITA_ID',      'SISTEMATICITA')
residenza_map  = load_lookup('vfa-ferservizi_classe_residenza.csv',          'CLASSE_RESIDENZA_ID',   'CLASSE_RESIDENZA')

print("Lookups loaded. Generating charts...")

# ════════════════════════════════════════════════════════════
# CHART 1 — Top 10 destination provinces (integrativa, no Italia origin)
# ════════════════════════════════════════════════════════════
df_camp = df_int[df_int['ORIGIN ZONE'] != 'Italia'].copy()
top_dest = (df_camp.groupby('DESTINATION PROVINCE')['TRIPS']
            .sum().sort_values(ascending=False).head(10))

fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#C0392B' if i == 0 else '#2471A3' for i in range(len(top_dest))]
bars = ax.barh(top_dest.index[::-1], top_dest.values[::-1], color=colors[::-1])
ax.set_xlabel('Total Monthly Trips', fontsize=12)
ax.set_title('Top 10 Destination Provinces\n(Internal Campania flows, Oct 2024)', fontsize=13, fontweight='bold')
for bar, val in zip(bars, top_dest.values[::-1]):
    ax.text(bar.get_width() + top_dest.max()*0.01, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=9)
ax.set_xlim(0, top_dest.max() * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart1_top_destinations.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 1: Top destination provinces")

# ════════════════════════════════════════════════════════════
# CHART 2 — Trips by day of week (fondamentale)
# ════════════════════════════════════════════════════════════
df_day = df_fond[df_fond['GIORNO_SETTIMANA_ID'] != -1].copy()
df_day['Day'] = df_day['GIORNO_SETTIMANA_ID'].map(giorno_map)
day_trips = df_day.groupby('Day')['TRIPS'].sum()

day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
day_order_it = ['Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato','Domenica']
# try Italian first, then English
for order in [day_order_it, day_order]:
    available = [d for d in order if d in day_trips.index]
    if available:
        day_trips = day_trips.reindex(available)
        break

fig, ax = plt.subplots(figsize=(10, 5))
palette = ['#2471A3' if i < 5 else '#E67E22' for i in range(len(day_trips))]
ax.bar(range(len(day_trips)), day_trips.values, color=palette)
ax.set_xticks(range(len(day_trips)))
ax.set_xticklabels(day_trips.index, rotation=30, ha='right')
ax.set_ylabel('Total Monthly Trips', fontsize=12)
ax.set_title('Mobility by Day of Week\n(Campania region, Oct 2024)', fontsize=13, fontweight='bold')
weekday_patch = mpatches.Patch(color='#2471A3', label='Weekday')
weekend_patch = mpatches.Patch(color='#E67E22', label='Weekend')
ax.legend(handles=[weekday_patch, weekend_patch])
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart2_day_of_week.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 2: Trips by day of week")

# ════════════════════════════════════════════════════════════
# CHART 3 — Trips by time slot (fondamentale)
# ════════════════════════════════════════════════════════════
df_fascia = df_fond[df_fond['FASCIA_ORARIA_MACRO_ID'] != -1].copy()
df_fascia['TimeSlot'] = df_fascia['FASCIA_ORARIA_MACRO_ID'].map(fascia_map)
fascia_trips = df_fascia.groupby('TimeSlot')['TRIPS'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(range(len(fascia_trips)), fascia_trips.values, color='#1A5276')
ax.set_xticks(range(len(fascia_trips)))
ax.set_xticklabels(fascia_trips.index, rotation=20, ha='right')
ax.set_ylabel('Total Monthly Trips', fontsize=12)
ax.set_title('Mobility by Time Slot\n(Campania region, Oct 2024)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart3_time_slots.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 3: Trips by time slot")

# ════════════════════════════════════════════════════════════
# CHART 4 — Transport mode split (integrativa)
# ════════════════════════════════════════════════════════════
df_mode = df_int[df_int['MODALITA_ID'] != -1].copy()
df_mode['Mode'] = df_mode['MODALITA_ID'].map(modalita_map)
mode_trips = df_mode.groupby('Mode')['TRIPS'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(7, 5))
colors_pie = ['#2E86C1', '#E74C3C', '#27AE60', '#F39C12', '#8E44AD']
wedges, texts, autotexts = ax.pie(
    mode_trips.values,
    labels=mode_trips.index,
    autopct='%1.1f%%',
    colors=colors_pie[:len(mode_trips)],
    startangle=140,
    pctdistance=0.75
)
for at in autotexts:
    at.set_fontsize(10)
ax.set_title('Transport Mode Split\n(Campania region, Oct 2024)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart4_transport_mode.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 4: Transport mode split")

# ════════════════════════════════════════════════════════════
# CHART 5 — Nationality split: domestic vs international (fondamentale)
# ════════════════════════════════════════════════════════════
df_naz = df_fond[df_fond['TIPO_NAZIONALITA_ID'] != -1].copy()
df_naz['Nationality'] = df_naz['TIPO_NAZIONALITA_ID'].map(nazionalita_map)
naz_trips = df_naz.groupby('Nationality')['TRIPS'].sum()

fig, ax = plt.subplots(figsize=(7, 5))
colors_naz = ['#2E86C1', '#E74C3C', '#27AE60']
wedges, texts, autotexts = ax.pie(
    naz_trips.values,
    labels=naz_trips.index,
    autopct='%1.1f%%',
    colors=colors_naz[:len(naz_trips)],
    startangle=90,
    pctdistance=0.75
)
for at in autotexts:
    at.set_fontsize(10)
ax.set_title('Traveller Nationality Split\n(Campania region, Oct 2024)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart5_nationality.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 5: Nationality split")

# ════════════════════════════════════════════════════════════
# CHART 6 — External Italy → Campania: top origin provinces
# ════════════════════════════════════════════════════════════
df_ext = df_fond[df_fond['ORIGIN ZONE'] == 'Italia'].copy()
top_ext_dest = (df_ext.groupby('DESTINATION PROVINCE')['TRIPS']
                .sum().sort_values(ascending=False).head(8))

fig, ax = plt.subplots(figsize=(10, 5))
colors6 = ['#C0392B' if i == 0 else '#2471A3' for i in range(len(top_ext_dest))]
bars = ax.barh(top_ext_dest.index[::-1], top_ext_dest.values[::-1], color=colors6[::-1])
ax.set_xlabel('Total Monthly Trips from Rest of Italy', fontsize=11)
ax.set_title('Inbound Flows: Rest of Italy → Campania Provinces\n(Oct 2024)', fontsize=13, fontweight='bold')
for bar, val in zip(bars, top_ext_dest.values[::-1]):
    ax.text(bar.get_width() + top_ext_dest.max()*0.01, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f}', va='center', fontsize=9)
ax.set_xlim(0, top_ext_dest.max() * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'chart6_inbound_italy.png'), bbox_inches='tight')
plt.close()
print("  ✓ Chart 6: Inbound flows from Italy")

# ════════════════════════════════════════════════════════════
# SUMMARY STATS
# ════════════════════════════════════════════════════════════
total_int  = df_int['TRIPS'].sum()
total_fond = df_fond['TRIPS'].sum()
ext_trips  = df_fond[df_fond['ORIGIN ZONE'] == 'Italia']['TRIPS'].sum()
int_trips  = df_fond[df_fond['ORIGIN ZONE'] != 'Italia']['TRIPS'].sum()

print("\n" + "="*50)
print("SUMMARY STATISTICS (October 2024)")
print("="*50)
print(f"Total trips (integrativa matrix): {total_int:,.0f}")
print(f"Total trips (fondamentale matrix): {total_fond:,.0f}")
print(f"  → Internal Campania trips: {int_trips:,.0f}")
print(f"  → Inbound from rest of Italy: {ext_trips:,.0f}")
print(f"  → Inbound share: {ext_trips/(ext_trips+int_trips)*100:.1f}%")
print("="*50)
print(f"\n✅ All charts saved to: {OUT}")
