# Part B — Network Capacity & Saturation Analysis
### Can the existing rail system absorb the America's Cup demand, or will it collapse?

*(Report section — Infrastructure PW, FS × POLIMI. Diagnosis only; service-enhancement measures (shuttle bus) are covered in the Services-improvement section.)*

---

## 1. Objective

The brief's headline question is whether Naples' transport system can absorb the
extraordinary America's Cup demand. We answer it quantitatively with a **volume-to-capacity
(V/C) saturation analysis** of the rail lines serving the event area, comparing the
*as-is* baseline against the *event-day* scenario, and we complement it with a **real
road-network accessibility analysis** (OSRM) of where that demand originates.

## 2. Study area — event zones

The demand model concentrates arrivals in the central-Naples and venue zones. Zone
identities are taken from the official zone coordinates (`Zones.csv`). Two corridors are
analysed, plus the rail gateway:

- **West corridor (venue):** zones 10 (Bagnoli race & tech zone), 2 and 33
  (Fuorigrotta / Mostra d'Oltremare — the western interchange of Cumana + Line 2 + Line 6
  feeding the course).
- **Central corridor (waterfront + gateway):** zones 3 (Race Village waterfront), 1
  (Centro Direzionale), 71, 195, 216, and **zone 79 — the Napoli Centrale rail hub
  (Lines 1 + 2)**.

> *Note on zone identity:* Napoli Centrale station straddles the boundary of zones 1 and 79
> (both ≈0.8 km from the platforms). The **station hub proper is zone 79**; zone 1 is the
> adjacent Centro Direzionale district. The airport (zone 191) and the Pompeii/Vesuvius
> tourist zones (68, 212) sit on separate networks (Alibus / Circumvesuviana–EAV regional
> rail) and are discussed qualitatively, not modelled in the metro V/C.

## 3. Data

| Side | Source |
|------|--------|
| Demand — event scenario | `total_new_project_flow_internal_only.mtx` (PROJECT = background + tourist surge, 108.4 M trips/month, Campania-internal) |
| Demand — as-is baseline | `background_od.mtx` (98.8 M trips/month) |
| Demand — tourist surge | PROJECT − background = **9.6 M trips** (gravity model, β = 0.04) |
| Supply — line capacity | Published figures (Wikipedia): peak-hour, per-direction |
| Road impedance | `distance_real_v2.mtx` — 222×222 OSRM door-to-door driving **time (min)** |

Region-wide the event adds **+9.7 %** of trips. Concentrated on the **20-day event window**,
this raises **event-day** arrivals into the 9 analysed zones by **+25 %** on average
(per zone: Bagnoli +30 %, Race Village +45 %, Centro Direzionale +74 %, Napoli Centrale
hub +16 %) — within the 10–25 % range expected by the demand-modelling team.

**Rail peak-hour, per-direction capacity** (trains/h × passengers/train):
Metro L1 ≈ 12 000 · Metro L6 ≈ 7 200 · Metro L2 ≈ 3 600 · Cumana ≈ 1 050.

> *Data note — corrected inputs.* An earlier tourist/total pair (`Tourist_AGGREGATE` /
> `TOTAL_flow`) was superseded by the team's corrected matrices above. A separate
> event-day / non-event-day split was **not** used directly: its event-vs-non-event gap
> (+91 %/day) implies ≈48 M extra event-period trips — about **5× the actual regatta surge
> (9.6 M)** — i.e. it is dominated by ordinary busy-vs-quiet-day variation, not the event,
> and would overstate saturation roughly fivefold. We therefore attribute to the event only
> the audited surge (PROJECT − background).

## 4. Method

**Demand chain (per zone):**

```
as-is daily arrivals  = background monthly column-sum ÷ 30.4 days
event-day arrivals    = as-is daily + (PROJECT − background) column-sum ÷ 20 event days
   × 8 % peak-hour share  → peak-hour arrivals (one direction, toward the zone)
   × 50 % transit share   → peak-hour rail demand
```

The surge is spread over the **20 event days** (the days the visitors are actually present),
which is the relevant load for a peak-day test. Spreading it over the full 60-day window
(÷60) is a conservative lower bound and is reported alongside. The **8 % peak-hour share**
is derived from the *as-is* data: the morning peak slot (05:00–08:59) carries 21.8 % of
daily trips over 4 h (≈5.5 %/h), scaled by a within-peak peaking factor (~1.4) → ≈8 %.
Transit mode share is an assumption (the mobile-phone data only labels train/air, so urban
metro is not observable) and is tested at 40/50/60 %.

**Saturation:** `V/C = peak-hour rail demand / line capacity`, classified with a
level-of-service scale (A–C < 0.60 free; D 0.60–0.80 busy; E 0.80–1.0 near-capacity;
**F > 1.0 oversaturated / "collapse"**). We treat 0.80 as the practical near-capacity
threshold for peak rail loading (beyond ~80 % load factor, crowding and reliability degrade
and there is no recovery margin).

Two calibers are reported: (1) **corridor-level**, and (2) **per-line**, in which each
zone's demand is split across its serving lines in proportion to capacity (avoids
arbitrarily assigning shared lines to one corridor).

## 5. Results

**Spatial overview — venues & rail lines** — *Fig. `B_map_venues_rail_schematic.png`*:
map on real Campania zone boundaries with the event anchors (Bagnoli venue, Race Village,
Napoli Centrale rail hub), the western interchange (Fuorigrotta/Mostra), and the four
analysed rail corridors (Metro L1, L6, L2, Cumana) colour-coded by **event-day V/C**
(peak hour, 50 % transit share). Line geometry follows major stations (illustrative, not
official track GIS).

**Per-line V/C (transit share 50 %)** — *Fig. `B_chart_VC_by_line.png`*

| Line | As-is V/C | Event-day V/C | LOS |
|------|:---:|:---:|:---|
| **Metro L1** | 0.71 | **0.91** | E — near-capacity |
| Metro L2 | 0.57 | 0.70 | D |
| Metro L6 | 0.53 | 0.65 | D |
| Cumana | 0.44 | 0.51 | A–C |

**Sensitivity** — *Fig. `B_chart_sensitivity.png`*: at 40 % transit share L1 sits at 0.73;
at 50 % it reaches 0.91; **at 60 % it crosses 1.09 (oversaturated)**. The corridor-level
caliber (all central demand on L1) gives event-day **V/C = 1.20**. All other lines stay at
or below 0.84 across the full range. **L1 is the only line at risk.**

**Spatial pattern** — *Fig. `B_map_saturation_shapefile.png`* (choropleth on real zone
boundaries): the added demand is highly uneven — it concentrates on central Naples and the
Napoli Centrale corridor, while the race venue (Bagnoli/Fuorigrotta) absorbs a much smaller
absolute increment, consistent with the line-level finding that L1 is the binding constraint.
*(We map the absolute increment, not growth-%: low-baseline rural zones produce extreme
percentages off tiny volumes and would be misleading hotspots.)*

**Road accessibility (OSRM)** — *Fig. `B_map_accessibility_osrm.png`*: of the tourist
demand originating within Campania, **71 % is within a 45-minute drive** of the venues
(weighted-mean 41 min), confirming a Naples-centred concentration; but **~21 % originates
beyond 60 minutes** (Salerno/Avellino/Cilento), which depends on long road approaches and
regional rail rather than the urban metro.

## 6. Conclusion

The system does **not** face an aggregate capacity shortfall — total regatta-area rail
capacity (~24 000 pax/h/dir) exceeds total event demand. **The problem is the *distribution*
of that capacity, not its quantity.** Specifically:

- **Metro Line 1 is the binding constraint** — the central spine serving the race village,
  Centro Direzionale and the Napoli Centrale gateway. The event pushes it from 0.71 to
  **0.91 on an event day**, leaving essentially no reserve, and it tips into oversaturation
  (>1.0) under a 60 % transit share or under the corridor-concentration caliber (1.20). The
  steepest demand growth lands exactly on this corridor.
- **The race venue (Bagnoli/Fuorigrotta) is over-served** — three lines (Cumana, L2, L6)
  carry only V/C ≈ 0.51–0.70, i.e. ample spare capacity.

The implication is **targeted relief of the L1 / Napoli Centrale corridor** (e.g. peak
frequency increase, and diversion via Line 6 Municipio↔Mostra), rather than network-wide
expansion. The concrete service-enhancement design (shuttle-bus provision) is developed in
the Services-improvement section.
