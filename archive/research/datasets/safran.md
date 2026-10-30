# SAFRAN / SIM2 daily (Météo-France): reuse note

Audit of 30/10/2026 (agent plan_ia). I downloaded and opened the 2016 file, the `latest`, the grid, the `.prj` and the two documentation PDFs; I went through the entire 2026 file. I aggregated 2016 to départements, weighting with RPG parcels of pea, faba bean and lentil. The data was deleted at the end; the scripts remain in `scratchpad/plan_ia/scripts/` (`sim_inspect.py`, `grid_check.py`, `weights.py`, `aggregate.py`, `wstab.py`, `rpg_peafaba.py`).

Tags: **[V]** verified by me on the file or API, **[F]** read at the source, **[NV]** not verified.

## 1. What it is and where it is

- **Dataset**: "Données changement climatique - SIM quotidienne" (climate change data, daily SIM), Météo-France, on data.gouv: https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne (id `6569b27598256cc583c917a7`) [V].
- **License**: Licence Ouverte v2 (`lov2` in the API), so commercial use is allowed [V].
- **Model**: SAFRAN is an atmospheric analysis (observations + background field (ébauche) from a forecast model, optimal interpolation by "massifs" (mountain zones) and altitude bands of 300 m) projected onto a regular 8 km grid. ISBA computes the soil water and energy balance [F, presentation PDF].
- **Coverage**: one file per year, from 1958 to 2026, plus `QUOT_SIM2_latest.csv.gz` [V].
- **Freshness**:
  - `latest` covers 31/08/2026 to 29/10/2026, i.e. the last ~60 days with a 1-day lag [V].
  - The 2026 file (updated 27/10) reaches 26/10/2026 [V]. When read in streaming, gzip reported "unexpected end of file", so it is worth re-downloading before trusting the last date.
  - The 2009-2022 files have a modification date of 31/07/2026, and the 2023-2026 ones 27/10/2026. That suggests Météo-France reprocesses recent years [V on the dates; the reason is NV]. **For backtests, fix the download date in the README.**

## 2. Exact URLs (stable pattern)

```
https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_{AAAA}.csv.gz      # 1958..2026
https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_latest.csv.gz
https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/coordonnees_grille_safran_lambert-2-etendu.csv
https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/Shapefile/SIM2.prj           # (+ .shp/.shx/.sbn/.sbx, SHP_SIM_FRANCE.*)
https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260331-150448/sim-quotidienne-parametres-20260331.pdf
https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260602-150234/climatologie-presentation-modele-sim-20260602.pdf
```

To list the resources via the API (in case the names change):
`curl -s https://www.data.gouv.fr/api/1/datasets/donnees-changement-climatique-sim-quotidienne/ | jq -r '.resources[]|.title+" "+.url'`

## 3. Sizes and timings (measured from Paris, 30/10/2026) [V]

| Item | Value |
|---|---|
| Annual file (csv.gz) | 135 to 142 MB (2016: 137.3 MB). 2026 partial: 112.5 MB. `latest`: 19.9 MB |
| Total 2009-2025 | **2.34 GB** compressed. With 2026 and `latest`: 2.48 GB |
| Download, 1 thread | 2016 in 104 s (~1.3 MB/s) |
| Download, 4 in parallel | 160 MB in 42 s (~3.8 MB/s total). **2009-2026 complete in ~11-12 min** with 4 threads; ~35 min sequential |
| Reading with polars (`read_csv` on the .gz, 29 columns) | 3.8 s/year, 3,620,472 rows, ~840 MB RAM. With 11 columns: 3.2 s |
| Weighted aggregation to dept × crop × day (join + group_by) | 2 to 9 s/year |
| **Total per year (read + aggregate)** | **~6-13 s**. 17 years: <4 min on a laptop |

RAM recommendation: read only the columns you need and process year by year, without concatenating the raw files.

## 4. Format [V]

- CSV with `;` separator, decimal point, no quotes and **no nulls** in 2016 or in `latest`.
- One row per cell × day. 2016 has 9,892 cells × 366 days, all complete.
- Columns, in order: `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;SSWI_10J;DRAINC;RUNC;RESR_NEIGE;RESR_NEIGE6;HTEURNEIGE;HTEURNEIGE6;HTEURNEIGEX;SNOW_FRAC;ECOULEMENT;WG_RACINE;WGI_RACINE;TINF_H;TSUP_H`.
- `DATE` is an integer in `YYYYMMDD` format.

Useful variables for crops (definitions and units taken from the parameters PDF [F]; 2016 ranges measured [V]):

| Variable | Definition | Unit | Window | 2016 range |
|---|---|---|---|---|
| PRELIQ / PRENEI | Liquid / solid precipitation | mm | ]06UTC-06UTC] | 0 to 335.9 / 0 to 228.4 |
| T | Daily mean temperature | °C | ]00-00UTC] | -20.6 to 30.2 |
| TINF_H | Minimum of the 24 hourly temperatures | °C | ]18UTC-18UTC] | -22.0 to 26.5 |
| TSUP_H | Maximum of the 24 hourly temperatures | °C | ]06UTC-06UTC] | -19.4 to 38.4 |
| ETP | Potential evapotranspiration, Penman-Monteith FAO-56 | mm | | 0 to 10.6 |
| EVAP | Actual evapotranspiration | mm | ]06-06UTC] | |
| PE | Effective rain | mm | | |
| SWI | Soil wetness index | **the PDF says %, but the file contains a fraction** | mean ]06-06] | **-0.045 to 1.81** |
| SSWI_10J | Soil drought index, integrated over 10 days | unitless | | -2.1 to 2.2 |
| WG_RACINE | Liquid water in the root zone at 06 UTC | m³/m³ | | 0.084 to 0.429 |
| SSI / DLI | Visible / atmospheric radiation | J/cm² | daily | |
| HU, Q, FF | Relative humidity, specific humidity, wind | %, g/kg, m/s | | |

**Gotchas**

- SWI comes as a fraction (1 = field capacity) and can come out **<0 or >1**. Do not clip it without thinking: excess water (>1) is precisely the signal of a waterlogged spring like 2016's.
- TINF_H and TSUP_H use different windows (18-18 and 06-06 UTC), and rain runs from 06 to 06 UTC. To count "days with Tmax>25 °C" this is enough; do not mix dates for hourly analyses.
- The modification dates show that recent years are reprocessed: you have to version the download.

## 5. Grid and coordinates [V]

- `coordonnees_grille_safran_lambert-2-etendu.csv`:
  - Columns `LAMBX (hm);LAMBY (hm);LAT_DG;LON_DG`, with a **decimal comma** in lat/lon.
  - Contains 9,892 cells, the same as the daily files.
- Projection: **NTF Lambert II étendu (Nouvelle Triangulation Française, the former French datum) = EPSG:27572**, with LAMBX/LAMBY in **hectometres** (multiply by 100 to get metres). With `pyproj` (27572 to 4326, `always_xy`) the difference with the file's LAT/LON is ≤0.001° [V].
- The grid is regular: `LAMBX = 40 + 80·i` and `LAMBY = 10 + 80·j` (in hm, 8 km step). The coordinates are the cell **centre** [F].
- To go from a lon/lat point to its cell:

```python
from pyproj import Transformer
tr = Transformer.from_crs(4326, 27572, always_xy=True)
x, y = tr.transform(lon, lat)                       # metres
LAMBX = (np.round((x/100 - 40)/80)*80 + 40).astype(int)
LAMBY = (np.round((y/100 - 10)/80)*80 + 10).astype(int)
```

  With this formula, 99.98% of the 2016 RPG centroids and 99.99% of the 2023 ones fall in an existing cell.
- Cell to department: with the simplified departments GeoJSON (`gregoiredavid/france-geojson`, `departements-version-simplifiee.geojson`), **1,310 of 9,892 cells do not fall in any polygon** (coast, borders, simplified polygon). Median: 93 cells per dept. For unweighted averages it is better to use `sjoin_nearest` or the full IGN ADMIN EXPRESS.

## 6. Aggregation to dept weighted by RPG parcels [V]

Tested method:

1. Download from the IGN WFS the centroids (`representative_point`) of the parcels by crop code. Script `rpg_peafaba.py`, ~95 s per year. Volumes:
   - 2016: 59,363 parcels.
   - 2023: 60,791 parcels (PPR, PHI, FVL, FVP, FEV, LEC).
2. Assign each parcel's dept by point-in-polygon. Left without a dept: 12 parcels in 2016 and 18 in 2023.
3. Assign each parcel to its SAFRAN cell with the formula above.
4. Cell weight = ha of that cell / ha of the dept.
5. Aggregate with a join against the daily file and a group_by, ~2-9 s per year.

Results:

- **RPG vs SAA (area reconciliation)**:
  - Pea: 190.9 kha RPG vs 188.0 kha SAA in 2016; 150.0 vs 151.6 kha in 2023.
  - Faba bean: 75.6 vs 77.8 kha in 2016; 81.4 vs 80.2 kha in 2023.
  - Lentil: 20.9 vs 19.5 kha in 2016; 28.7 vs 27.7 kha in 2023.
  - The two sources reconcile within ±5%.
- **Cells per dept (depts with ≥500 ha of the crop)**:
  - Pea: median ~80 cells; maximum cell weight, median 0.06.
  - Faba bean: ~71-84 cells.
  - Lentil: ~40-49 cells.
- **Does weighting matter?** I compared April-June 2016 rain in depts with ≥500 ha of pea, RPG-weighted vs the simple mean of the dept's cells:
  - Median difference 2.4%, p90 13%, maximum 45% (Hérault: 137 vs 249 mm).
  - Alpes-de-Haute-Provence: 21 vs 5 days with Tmax ≥25 °C.
  - **Conclusion: it matters in depts with relief (south and east), almost nothing in the Paris basin.**
- **Does the RPG year matter?** I measured the overlap of weights between the RPG 2016 and 2023: median 0.70 for pea and 0.52 for faba bean. But April-June 2016 rain computed with the 2016 or the 2023 weights differs by only 0.6% in the median (p90 2%, maximum 14.7%). **One single RPG year (or an average of several) is enough as a fixed mask.** For years before 2015 there is no RPG per parcel: use the 2015-2016 mask.
- **Cross-check with Open-Meteo** (`era5_seamless`, one point, April-June 2016): Oise 295 mm vs 301 mm SAFRAN weighted, Aube 347 vs 329 mm. Same order, so it works as a fallback.

## 7. Quick recipe for Friday

```bash
D=data/sim2; mkdir -p $D
B=https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM
seq 2009 2026 | xargs -P 4 -I{} curl -s -o $D/QUOT_SIM2_{}.csv.gz $B/QUOT_SIM2_{}.csv.gz
curl -s -o $D/latest.csv.gz $B/QUOT_SIM2_latest.csv.gz
curl -s -o $D/grid.csv $B/coordonnees_grille_safran_lambert-2-etendu.csv
```

On AWS it is best to download straight to S3 or EBS from an instance, which is probably faster than the campus wifi [NV].

Minimum columns for crops: `LAMBX,LAMBY,DATE,PRENEI,PRELIQ,T,TINF_H,TSUP_H,ETP,SWI,WG_RACINE`.
Recommended output: `clim_dep_crop_day.parquet` (dept × crop × date), which is ~95,000 rows per year for 3 crops.

## 8. Fallback: Open-Meteo [V]

- `archive-api.open-meteo.com/v1/archive?...&models=era5_seamless` accepts several points per request and returns rain and ET0.
- **Do not use `era5_land`**: the rain comes out null (see `ideas2_4_time_series.md`).
- The free tier is non-commercial and has a daily call limit. It is fine for one point per dept, not for the grid.
