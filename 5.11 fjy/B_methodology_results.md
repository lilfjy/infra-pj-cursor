# Part B — Network Capacity & Saturation Analysis
### Can the existing rail system absorb the America's Cup demand, or will it collapse?

*(Report section — Infrastructure PW, FS × POLIMI. Diagnosis only; service-enhancement measures (shuttle bus) are covered in the Services-improvement section.)*

---

## 1. Objective

The brief's headline question is whether Naples' transport system can absorb the
extraordinary America's Cup demand. We answer it quantitatively with a **volume-to-capacity
(V/C) saturation analysis** of the rail lines serving the event area, comparing the
*as-is* baseline against the *event* scenario, and we complement it with a **real
road-network accessibility analysis** (OSRM) of where that demand originates.

## 2. Study area — event zones

The demand model concentrates arrivals in 9 traffic zones. Seven were taken from the
demand-forecast destinations; **we additionally include zones 2 and 33 (Fuorigrotta /
Mostra d'Oltremare)**, because that area is the western rail interchange (Cumana + Line 2 +
Line 6) feeding the Bagnoli race course and is otherwise omitted. Two corridors:

- **West corridor (venue):** zones 2, 10, 33 — Bagnoli / Fuorigrotta race & tech zone.
- **Central corridor (gateway + race village):** zones 1, 3, 71, 195, 216 — central
  waterfront and the Napoli Centrale rail gateway.
- Zone 73 (Nocera Superiore, ~30 km SE) is an accommodation outlier on the regional rail
  and is reported separately.

## 3. Data

| Side | Source |
|------|--------|
| Demand — tourist increment | `Tourist_AGGREGATE.mtx` (pure tourist O-D, 11.0 M trips/month region-wide) |
| Demand — background | `TOTAL_flow.mtx` − tourist = 98.8 M trips/month (As-is baseline) |
| Supply — line capacity | Published figures (Wikipedia): peak-hour, per-direction |
| Road impedance | `distance_real_v2.mtx` — 222×222 OSRM door-to-door driving **time (min)** |

Region-wide the event adds **+11 %** of trips; in the central event zones the increment
reaches **+23 %**, peaking at **+50 %** in the Napoli Centrale gateway zone.

**Rail peak-hour, per-direction capacity** (trains/h × passengers/train):
Metro L1 ≈ 12 000 · Metro L6 ≈ 7 200 · Metro L2 ≈ 3 600 · Cumana ≈ 1 050.

## 4. Method

**Demand chain (per zone, per series):**

```
monthly arrivals (matrix column-sum)
   ÷ 30.4 days            → average daily arrivals
   × 8 % peak-hour share  → peak-hour arrivals  (one direction, toward the zone)
   × 50 % transit share   → peak-hour rail demand
```

The peak-hour share is derived from the *as-is* data: the morning peak slot (05:00–08:59)
carries 21.8 % of daily trips over 4 h (≈5.5 %/h), scaled by a within-peak peaking factor
(~1.4) → ≈8 %. Transit mode share is an assumption (the mobile-phone data only labels
train/air, so urban metro is not observable) and is tested at 40/50/60 %.

**Saturation:** `V/C = peak-hour rail demand / line capacity`, classified with a
level-of-service scale (A–C < 0.60 free; D 0.60–0.80 busy; E 0.80–1.0 near-capacity;
**F > 1.0 oversaturated / "collapse"**). We treat 0.80 as the practical near-capacity
threshold for peak rail loading (beyond ~80% load factor, crowding and reliability degrade
and there is no recovery margin).

Two calibers are reported: (1) **corridor-level**, and (2) **per-line**, in which each
zone's demand is split across its serving lines in proportion to capacity (avoids
arbitrarily assigning shared lines to one corridor).

## 5. Results

**Spatial overview — venues & rail lines** — *Fig. `B_map_venues_rail_schematic.png`*:
schematic map of the Gulf of Naples with the three event anchors (Bagnoli venue, Race
Village, Napoli Centrale gateway), the western interchange (Fuorigrotta/Mostra), and the
four analysed rail corridors (Metro L1, L6, L2, Cumana) colour-coded by **event V/C**
(peak hour, 50 % transit share). Line geometry follows major stations (illustrative, not
official track GIS).

**Per-line V/C (transit share 50 %)** — *Fig. `B_chart_VC_by_line.png`*

| Line | Baseline V/C | Event V/C | LOS |
|------|:---:|:---:|:---|
| **Metro L1** | 0.69 | **0.84** | E — near-capacity |
| Metro L6 | 0.54 | 0.62 | D |
| Metro L2 | 0.54 | 0.62 | D |
| Cumana | 0.46 | 0.50 | A–C |

**Sensitivity** — *Fig. `B_chart_sensitivity.png`*: at 40 % transit share L1 sits at 0.67;
at 50 % it reaches 0.84; **at 60 % it crosses 1.01 (oversaturated)**. All other lines stay
below 0.75 across the full range. L1 is the only line at risk.

**Spatial pattern** — *Fig. `B_map_saturation_shapefile.png`* (choropleth on real zone
boundaries): the added demand is highly uneven — it concentrates on central Naples and the
Napoli Centrale gateway, while the race venue (Bagnoli/Fuorigrotta) absorbs a much smaller
absolute increment, consistent with the line-level finding that L1 is the binding constraint.
*(We map the absolute increment, not growth-%: low-baseline rural zones produce extreme
percentages off tiny volumes and would be misleading hotspots.)*

**Road accessibility (OSRM)** — *Fig. `B_map_accessibility_shapefile.png`*: of the tourist
demand originating within Campania, **73 % is within a 45-minute drive** of the venues
(weighted-mean 37 min), confirming a Naples-centred concentration; but **~20 % originates
beyond 60 minutes** (Salerno/Avellino/Cilento), which depends on long road approaches and
regional rail rather than the urban metro.

## 6. Conclusion

The system does **not** face an aggregate capacity shortfall — total regatta-area rail
capacity (~24 000 pax/h/dir) exceeds total event demand. **The problem is the *distribution*
of that capacity, not its quantity.** Specifically:

- **Metro Line 1 is the binding constraint** — the central spine serving the race village
  and the Napoli Centrale gateway. The event pushes it from 0.69 to **0.84**, leaving no
  reserve, and it tips into oversaturation (>1.0) under a 60 % transit share. The
  steepest demand growth (+50 %) lands exactly on this corridor.
- **The race venue (Bagnoli/Fuorigrotta) is over-served** — three lines (Cumana, L2, L6)
  carry only V/C ≈ 0.35–0.62, i.e. ample spare capacity.

The implication is **targeted relief of the L1 / Napoli Centrale corridor** (e.g. peak
frequency increase, and diversion via Line 6 Municipio↔Mostra), rather than network-wide
expansion. The concrete service-enhancement design (shuttle-bus provision) is developed in
the Services-improvement section.
