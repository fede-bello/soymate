# Idea 4: early estimate of departmental pulse yield (pea and faba bean; lentil experimental)

Full dossier for Hack the Fork Paris 2026, Track 3. Written on 30/10/2026 (plan_ia agent).

Tags: **[V]** I verified it myself on the file, the API or the primary source. **[F]** I read it in a source (secondary, or primary via a subagent that opened it). **[NV]** not verified, hypothesis or own calculation.

No model was fitted and no backtest was run. Everything numerical in this document is counts, descriptions or published figures. Inspection scripts: `/private/tmp/claude-501/-Users-fede-bello-develop-hack-the-fork/9fe23a79-8d36-4ec5-81a7-19ddb7a4cabc/scratchpad/plan_ia/scripts/`.

Reuse note on climate: `archive/research/datasets/safran.md`.

---

## 1. Summary in 5 lines and verdict

1. **What it is.** A tool that, for each département and for a cut-off date (1/5, 1/6, 15/6 or 1/7), estimates the yield of protein peas (pois protéagineux) and faba beans for the current season. It uses SAFRAN climate weighted by where that crop's RPG parcels are, returns an uncertainty interval, and explains the estimate with agronomic drivers and analogue seasons.
2. **For whom.** The grain collection or protein crop supply-chain manager of a grain storage body (organisme stockeur, OS). In 2024/25 there were 477 pulse collectors: 117 cooperatives and 360 négociants (grain traders) [V, FranceAgriMer]. That person builds their collection forecast (prévision de collecte) and their commitments with industrial buyers (Roquette, Intact, canners) before the July harvest.
3. **Data.** Verified and open:
   - Agreste SAA 2010-2025: 38 usable départements for pea and 28 for faba bean.
   - SAFRAN/SIM2 daily at 8 km, updated with a 1-day lag.
   - RPG by parcel.
   - Everything downloads in ~15 min and is processed in minutes.
4. **The gap is narrower than thought.** Agreste **does publish departmental yield estimates** for pea and faba bean during the season, but only **from 1 July** (published in mid-July), made "à dire d'experts" (by expert judgement) and without an interval. Its departmental error for pea was 2.8 q/ha MAE in 2023 and 5.6 q/ha in 2025 [V, see §2.4]. Our value is estimating in May and June, with calibrated uncertainty and explanation, in the tonnes of the OS's basin. 42% of the pea year-to-year variation is specific to each département [V, descriptive], so the national figure (or MARS) is not enough.
5. **Verdict: viable and defensible, but of medium impact. Estimated weighted score: 5.9/10.** Technical risk is low. The real risks are two:
   - **Eligibility.** Pea and faba bean have a lot of animal feed and export destinations, and "animal feed" is excluded from the contest. It has to be framed within the human food chain and validated with the organisers on Friday.
   - **Beating the baselines.** With 15 seasons, the model may not beat a strong baseline. There is a stopping rule.

---

## 2. Problem, concrete user and decision

### 2.1 User

**Role:** grain collection manager or "responsable filière protéagineux / productions spécialisées" (protein crop supply-chain / specialty productions manager) of a cooperative or négociant that collects pea and faba bean.

- Examples of actors with protein crop supply chains for human food:
  - Axéréal + Intact in Loiret (yellow pea and faba bean, 30 kt planned for the 2024 season, 100 producers, sourcing within a 150 km radius) [F, Réussir].
  - Roquette in Vic-sur-Aisne, which has had a pea supply chain since 2017 with a quality premium [F, Réussir].
  - Euralis + Bonduelle (dry pulses, ~1,000 ha and 115 producers in 2023; technicians visit each parcel every 15 days) [F, Euralis PDF].
  - The winners of the 2025 "filières légumineuses" call for projects (AAP) (Berry Graines, Axéréal+Intact, Terrena, Vivescia, Trescartes) [F, `track3_context.md`].
- **Size of the universe:** 477 pulse collectors in 2024/25 (117 cooperatives + 360 négociants) and ~12,400 producers delivering [V, FranceAgriMer protein crop supply-chain sheet, 2026]. On average over 2020/21-2024/25, 502 kt of pea and faba bean were collected, 64% of production [V, same sheet].

### 2.2 Decision

| Decision | When | Information used today | Cost of getting it wrong |
|---|---|---|---|
| **Collection forecast**: how many tonnes will come in, by silo and by week. Defines logistics, storage, cleaning and sorting (bruchid) | May-June, before the pea harvest (late June to July) | Areas contracted or declared by members; technician visits; the cooperative's historical or "olympic" average; from mid-July, Agreste's departmental estimate as of 1/7 (expert opinion); DRAAF regional notes | Undersized silos, poorly planned transport and drying [NV, not quantified] |
| **Sales commitments** with the industrial buyer (Roquette, Intact, casserie (split-pea processing), export) | Before and during harvest | The same plus prices | Shortfall: buy outside to comply, or renegotiate. Surplus: sell spot, typically to the animal feed market, which pays less [NV] |
| **Contracting the next season** (how many ha to offer and at what premium) | Autumn-winter | Yields of the season that is ending | Badly calibrated contracts that discourage the producer (the "fear of income loss" in the brief) |

FranceAgriMer requires collectors to declare each month, via VISIOGrains, the flows, stocks and uses **already carried out**, before the 10th of the following month [F, decision MEP/D2017-06, read by a subagent]. That is realised collection, not forecasting. **The forecast before harvest is what is missing.**

Testimonies of the cost of error:

- Vivescia, 2026 harvest: a market manager ("cheffe marché") says yield estimation is "particulièrement délicate" because of heterogeneity [F, search snippet; I did not open the page].
- **Lentil 2021**: 8 q/ha in Aube, Marne and Yonne against a 3-year average of 27.3; 6 vs 15 in the Centre. Most of it was under contract, and the dry pulse federation (FNLS) warned about "importations massives" (massive imports) [F, Terre-net and Pleinchamp].
- **Pea**: the national yield went from 28.3 q/ha (2024) to 35.6 (2025) [V, SAA] and to 29.9 in the July 2026 estimate [F, Agreste Infos rapides n°88, read by a subagent]. Swings of ±20% in the national figure alone.
- **Departmental (pea)**: the absolute deviation from the département mean has a median of 5.1 q/ha and a p90 of 11.5 q/ha. The worst years: Aube 2016 (-21 q/ha), Essonne 2024 (-21), Seine-et-Marne 2024 (-20) [V, SAA, 38 départements without Oise].

### 2.3 Do they already have the information? (the most likely jury objection)

- **Partly, yes.** The cooperative has technicians who walk parcels. But those estimates are subjective, parcel by parcel and heterogeneous between technicians, and they are not compared with 15 years of history.
- **The value is not in "knowing before anyone else".** It is in:
  1. an objective and reproducible estimate, with explicit uncertainty, for all its collection départements;
  2. available from May, before technicians can count pods;
  3. alerting when the season "looks like 2016" or "like 2024".
- To validate with a mentor [NV]: do OSs document their collection forecast and its historical error?

### 2.4 What already exists (competing sources)

**Key finding that contradicts the prior research:** Agreste already publishes each month a **departmental** yield estimate for protein pea (pure and mixed) and faba bean during the season. The competing source is stronger than assumed.

**1. Agreste "Infos rapides Grandes cultures"** (monthly, April to November).

- **Files**: each note comes with a departmental xlsx.
  - Pattern: `https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/<ID>/<AAAA>_<NN>donnees_grandescultures_departements.xlsx` (2024+). In 2022-23 it is called `..._donneesdeptgrandescultures.xlsx` and in 2020-21 it is `.xls` [F, subagent].
  - I opened 3 files [V]:
    - `IraGcu2688/2026_88donnees_grandescultures_departements.xlsx` (1/7/2026): sheet `grandes_cultures`, 5,482 rows. The row "Pois protéagineux purs" has a 2026 yield in **87 départements** (42 with ≥500 ha), and faba bean in 90.
    - `IraGcu2591/2025_91...` (1/7/2025).
    - `IraGcu2379/2023_79donneesdeptgrandescultures.xlsx` (1/7/2023).
  - The URL pattern did not work for ID 2482 (2024).
- **Method, according to the xlsx note itself** [V]: "Les estimations de surfaces et de rendements [...] sont établies à **dire d'experts** ou à partir des résultats des enquêtes Terres labourables [...] Pour les estimations de rendements, les résultats des enquêtes sont intégrés à partir de **septembre ou octobre**". Before September, yield is expert opinion.
  - Many values are round integers (Essonne and Val-d'Oise at 40, Eure-et-Loir and Loiret at 30) [V].
  - The subagent saw départements with the regional value copied: all Île-de-France départements with 39.0 in faba bean as of 1/8/2025 [F].
- **First yield estimate: that of 1 July**, published in mid-July. The notes of 1/6/2025 and 1/6/2026 only carry areas [F, subagent].
- **Departmental error of the 1/7 estimate against the SAA**, which I calculated (descriptive comparison of published figures) [V]. Départements with ≥500 ha, without Oise:

| Season | Crop | n départements | MAE (q/ha) | MAPE | Median abs. | Max. | Bias | % integer values |
|---|---|---|---|---|---|---|---|---|
| 2023 | Pea | 43 | 2.8 | 9% | 2.0 | 13.0 | -0.5 | 51% |
| 2023 | Faba bean | 47 | 2.9 | 9% | 2.0 | 12.0 | -2.0 | 49% |
| 2025 (SAA prov.) | Pea | 39 | **5.6** | **17%** | 5.0 | 22.4 | -0.9 | 51% |
| 2025 (SAA prov.) | Faba bean | 47 | 2.2 | 9% | 1.0 | 11.5 | +0.7 | 38% |

  Note: the final SAA is partly built from the same surveys and regional services, so this error may **understate** the real uncertainty [NV].

- **National error** (estimate minus final, q/ha, pure pea), with the figures from each xlsx collected by the subagent [F]:

| Year | 1 July | 1 August | Final |
|---|---|---|---|
| 2020 | 33.1 (+20%) | 30.8 | 27.6 |
| 2021 | n/a | 36.2 (**+28%**) | 28.4 |
| 2023 | 32.7 (+2%) | 32.3 | 32.0 |
| 2024 | 29.9 (+6%) | 28.8 | 28.3 |
| 2025 | 33.2 (-7%) | 34.5 | 35.6 |
| 2026 | **29.9** | 31.1 | no figure yet |

  I verified the 29.9 of 1/7/2026 (95 kha, 285 kt) myself in the PDF of Infos rapides n°88 [V].
  - For faba bean, the 1/7 error ranges from -12% (2024) to +27% (2020).
  - The 2016-2019 notes are not on the current platform [NV].

**2. DRAAF**: the regional notes (Pays de la Loire, July 2026; Centre-Val de Loire, September 2025) are **regional** and repackage Agreste's figures [F, subagent].

**3. JRC MARS Bulletin**: the country tables **do include** Field peas and Field beans for France [F]. The subagent read it in bulletin Vol. 33 n°8 of September 2025, from a mirror (oilworld.ru), because publications.jrc.ec.europa.eu rejects bots. Forecast for France in September 2025:
   - Field peas: 3.50 t/ha, against a 5-year average of 2.91; the final was 35.6 q/ha, an error of -2%.
   - Field beans: 2.68 t/ha; the final was 25.4, an error of +5%.
   - It is national, not departmental. From which year it includes pulses: [NV].

**4. Terres Inovia / Terres Univia / FOP**:
   - Statement of 31/7/2025: pea at "40-45 q/ha"; the final was 35.6, a large overestimate [F].
   - The November 2025 faba bean balance (26.8) matches Agreste's figure of 1/9, so it is not independent [F].
   - Joint harvest balance from FranceAgriMer, Arvalis and Terres Inovia at end of August [F].

**Consequences for the project:**

- **The gap is no longer "nobody estimates by département".** It is that:
  1. **before 1 July** there is no official yield estimate (the 1/7 one comes out in mid-July, with winter pea harvest already under way);
  2. the official estimate is expert opinion, with no interval or explanation, and its departmental error varies a lot between years (MAE from 2.8 to 5.6 q/ha for pea);
  3. it is not in the format of the OS's decision (tonnes of its basin).
- **Baseline B3 redefined**: Agreste's departmental estimate of 1/7 (available for 2020, 2023, 2025 and 2026; 2024 to be confirmed). The honest evaluation question is: **"is our 15/6 estimate as good as Agreste's 1/7 estimate, two to four weeks earlier?"** With 2-4 comparable years, this is weak evidence, and that has to be said.
- **Live 2026 control**: compare our 15/6/2026 estimates with Agreste's departmental estimates of 1/7, 1/8 and 1/9/2026 (IDs 2688, 2698 and 26114). It is not the final truth, but it is a real out-of-sample control.

---

## 3. Hypotheses

| # | Type | Hypothesis | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | Data | The SAA departmental yield of pea is a usable label: enough départements and years, few gaps | **[V]** | 38 départements with ≥500 ha, ≥7/9 training years (2010-18) and 6/6 test years (2019-24); 34 in statut 1 and 4 in statut 2. 28 with ≥1,000 ha all 16 years. No "s" for secret, gaps are NaN | Move to regional level or restrict to 28 départements with ≥1,000 ha |
| H2 | Data | The faba bean label is usable | **[V] with reservations** | 28 départements (24 statut 1, 4 statut 2), but in 44% of dept-years with ≥100 ha the yield is identical to another département's in the same region that same year (for pea it is 23.5%) | Faba bean only as a demo, evaluated by region |
| H3 | Data | Lentil works as a departmental label | **False [V]** | 4 usable départements; 52% of values duplicated between départements of the same region. The regional file has 8 regions with ≥1,000 ha at some point, with suspicious series (Grand Est 24.39/24.38/24.35 in 2014-2016) | "Experimental" mode at regional level, without strong metrics |
| H4 | Data | The 2010-2019 series is comparable with 2020-2025 | **Doubtful [V]** | For pea, departmental yields are integers in 48-60% of cases in 2010-2019 and in 84-94% since 2020: there is a regime change (back-calculation to RA 2020, as Agreste says). Oise: 9-16 q/ha in 2010-19 and 30-43 in 2020-25 (ratio 2.78); Hérault 2.38 and Tarn 1.72 | Model anomalies against the département trend, exclude Oise (and review Hérault and Tarn), add a post-2020 dummy and report it as a limit |
| H5 | Data | 2025 is provisional and can be used with a warning | **[V]** | The file says "Données arrêtées au 30/03/2026. Données 2025 provisoires". Pea 2025: 35 of the 38 départements still have ≥500 ha | Use 2025 only as a "provisional" test, without training on it |
| H6 | Data | SAFRAN can be downloaded and processed within the hackathon time | **[V]** | 2.34 GB for 2009-2025; ~11-12 min with 4 parallel downloads; 3-4 s to read and 2-9 s to aggregate per year | Open-Meteo `era5_seamless`, one point per département (tested; same order of magnitude) |
| H7 | Data | Weighting climate by RPG parcels changes the variables | **[V] partially** | April-June 2016 rain: median difference of 2.4% against the simple average, p90 13%, maximum 45% (Hérault). It matters in the south and east | If there is no time, use the simple average (you lose little in the Paris basin) |
| H8 | Data | One year of RPG is enough as a mask | **[V]** | Weights 2016 vs 2023: April-June rain changes by 0.6% in the median (p90 2%) | n/a |
| H9 | Agronomic | Year-to-year variation in pea yield depends on spring climate (heat >25 °C and water stress at flowering, which runs to mid or late June; waterlogging; frost on winter pea) | **[F]** | Terres Inovia 2025 pea growing guide (germineo.com): spring pea "doit être bien alimenté en eau jusqu'à mi-juin, voire fin juin"; "le stress hydrique arrête prématurément la floraison et diminue ainsi le nombre de graines". Terre-net/Terres Inovia 2022: "Tout stress hydrique ou thermique (> 25°C) survenant à cette période peut lourdement impacter le nombre de grains par m²". Counter-evidence: the LEGITIMES project (INRAE) found no relationship between heat and yield in 6 Burgundy parcels [F, search snippet] | The model does not beat the baseline: pivot to a "risk radar" with analogues (stopping rule, §7) |
| H10 | Agronomic | Diseases (aphanomyces, bacteriosis 2016), bruchid and pests are not in the climate and are noise | **[F]** | 2016: "historiquement bas", with winter pea at 0-30 q/ha due to bacteriosis [F, FranceAgriMer snippet]. Bacteriosis is linked to wet and cold climate, so it is partly capturable | State it as a limit; the waterlogging variable (SWI>1) partly captures it |
| H11 | Agronomic | The share of winter vs spring pea by département changes the risk | **[V] that it can be measured** | The RPG separates PHI (winter) from PPR (spring): 11,231 vs 24,715 parcels in 2016 and 10,732 vs 19,211 in 2023. The SAA does not separate them | Ignore it |
| H12 | User | The OS decides between May and July and values a departmental estimate with an interval | **[NV]** | Indications: the declaration obligation (realised), the Vivescia quote and Axéréal's "18 months of preparation" [F, snippets] | **Validate with a mentor on Friday.** If it decides by basin and not by département, show the area-weighted aggregate for its zone |
| H13 | User | Departmental scale is useful (not only national) | **[V] partially** | 58% of the year-to-year variation within each département is shared by all of France that year (pea); 42% is département-specific. Faba bean: 35% shared and 65% specific. Part of the 42% is noise or imputation | If almost all were common, the national Agreste figure would suffice and the idea loses meaning |
| H14 | Market | Pea and faba bean fall under "human food" for Track 3 | **Risk [V]** | Domestic uses 2024/25: 146 kt for human food against 62 kt for animal feed (pea + faba bean) [V, FranceAgriMer]. But on average 200 kt of pea and 61 kt of faba bean are exported, and 72% of exported faba bean goes to Norway (fish farming) [V], and the guide excludes "animal feed" [V] | Framing: "supply of the plant protein chain for human food (Roquette, Intact, casserie)" + experimental lentil. **Ask the organisers on Friday before 23:00** |
| H15 | Market | OSs would pay a subscription | **[NV]** | No public prices for B2B forecasting tools. Producer references: Mes Sat'images €9/ha and Mes Parcelles €367 excl. VAT/year [F, Chambres d'agriculture] | Common-good model funded by the interprofession (Terres Univia) or by FranceAgriMer |
| H16 | Technical | With 15 seasons, a pooled model on anomalies beats the département mean and trend | **[NV]** | Cannot be verified without modelling (rule). Literature: regional ML in Europe beats the operational system in 18 of 35 cases 60 days before harvest (Paudel et al.) [F, `ideas2_4_time_series.md`] | Saturday 14:00 stopping rule (§7) |
| H17 | Technical | Climate information is available at the cut-off date | **[V]** | SIM2 `latest` runs up to yesterday (29/10/2026); recent years are reprocessed (modification date 27/10) | For the backtest use the reanalysed climate; say so |
| H19 | Competition | Before 1/7 there is no official departmental yield estimate | **[V] partially** | The notes of 1/6/2025 and 1/6/2026 carry no pulse yield [F, subagent]; that of 1/7/2026 does, for 87 départements [V] | If Agreste brought its estimate forward to June, the value would be left only in uncertainty, explanation and basin |
| H18 | Technical | The RPG for year N is not available in June of N | **[V]** | The RPG 2025 files are dated 11/09/2026 [F, `geo_soil_climate.md`] | Use the mask for year N-1 or a fixed one; the OS knows year N area from its contracts |

---

## 4. Datasets (verified audit)

### 4.1 Agreste SAA long series 2010-2025 (label) [V]

| Field | Value |
|---|---|
| URL | https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip (the page `.../disaron/SAA-SeriesLongues/detail/` returns 0 bytes to curl, because it is built with JS; the ZIP downloads directly) |
| Licence | Licence Ouverte (Agreste) [F, `datasets.md`] |
| Access | Tested on 30/10/2026: HTTP 200, 7.08 MB, no login |
| Content | `SAA_2010-2025_provisoires_donnees_departementales.xlsx` (11 MB) and `..._regionales.xlsx` (3.6 MB), both dated 10/07/2026. It is the same version the previous round audited |
| Sheet | `COP`, header in row 6 (`header=5`): `LIB_REG2, LIB_DEP, LIB_SAA, STATUT_QUALITE, SURF_2010..2025, REND_2010..2025, PROD_2010..2025`. 4,500 rows = 45 products × 100 départements (95 metropolitan + 5 overseas) |
| Units | ha, quintals and q/ha (stated in the sheet itself). Yield "au stade arrivée ferme"; pea at 14% moisture [F, SAA methodology] |
| Products | `41 - Pois protéagineux` (without mixes, which are in `42 - Mélange de pois`), `38 - Féveroles et fèves`, `40 - Lentilles (y compris semences)` |
| `LIB_DEP` | Format `"077 - Seine-et-Marne"`. To join with the RPG or INSEE codes: `LIB_DEP.str[:3].str.lstrip('0')`, taking care to keep `2A`/`2B` (they come as `02A`, `02B`). `STATUT_QUALITE` is read as a string |
| Pea counts | See table. National yield (sum of départements): 43.0 (2010), 23.4 (2016), 38.7 (2019), 27.6 (2020), 28.4 (2021), 30.0 (2022), 32.0 (2023), 28.3 (2024), 35.6 (2025 prov.) q/ha. Area from 210 kha (2010) to 98 kha (2025) |
| Faba bean counts | National: 45.1 (2012) as maximum, 19.3 (2020) as minimum, 25.2 (2025 prov.). 112 kha in 2025 |
| Gotchas | (1) **Oise**, pea: 9.1-16.3 q/ha in 2010-19 and 30-43 in 2020-25, with normal area (5-13 kha). It is an artefact: exclude it or treat 2010-19 as missing. (2) **Regime break in 2020**: see H4. (3) Duplicates between départements of the same region. (4) 2025 provisional. (5) Revised data, not what was known in real time |

| Crop | Usable départements (≥500 ha, ≥7/9 train, 6/6 test) | Statut 1 / 2 among usable | With ≥1,000 ha all 16 years | Usable with 2025 ≥500 ha | % dept-year duplicated in the region |
|---|---|---|---|---|---|
| Pea | **38** (37 without Oise) | 34 / 4 | 28 | 35 | 23.5% |
| Faba bean | **28** | 24 / 4 | 3 | 28 | 44.2% |
| Lentil | **4** | 3 / 1 | 3 | 4 | 52.1% |
| Soft wheat (ref.) | 87 | 85 / 2 | 83 | 87 | n/a |

Usable pea départements (code): 077 078 091 095 018 028 036 037 041 045 021 058 089 014 027 061 076 002 060(Oise) 062 080 008 010 051 052 054 055 057 049 072 085 016 017 079 086 011 031 026 [V].

Download on Friday:
```bash
curl -s -o saa.zip "https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip" && unzip saa.zip
```

### 4.2 SAFRAN / SIM2 (climate) [V]

The full audit is in `archive/research/datasets/safran.md`. The essentials:

- **Files**: `https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/QUOT_SIM2_{1958..2026}.csv.gz` plus `QUOT_SIM2_latest.csv.gz`, which covers the last 60 days up to yesterday. Licence Ouverte v2.
- **Size**: 135-142 MB per year; **2.34 GB for 2009-2025** and 2.48 GB with 2026 and `latest`.
- **Format**: `;`-separated CSV, 29 columns, 9,892 cells × 365/366 days and **0 nulls** (2016: 3,620,472 rows). Useful columns: `PRELIQ, PRENEI, T, TINF_H, TSUP_H, ETP, SWI, SSWI_10J, WG_RACINE`.
  - SWI comes as a fraction, from -0.05 to 1.81, although the PDF says %.
- **Grid**: Lambert II étendu (EPSG:27572) in hectometres. `LAMBX = 40 + 80i` and `LAMBY = 10 + 80j`. The pyproj conversion differs by ≤0.001° from LAT/LON in the file of the grid, which uses decimal commas.
- **Timings**: download in ~11-12 min with 4 threads (35 min with one). Reading with polars 3-4 s/year and aggregation 2-9 s/year.
- **RPG join to cell**: 99.98% of centroids fall in an existing cell.
- **Cell to département join** (simplified GeoJSON): 1,310 cells end up without a département. Use `sjoin_nearest`.

### 4.3 RPG (spatial crop mask) [V]

- **WFS**: `https://data.geopf.fr/wfs/ows`, layer `RPG.{AAAA}:parcelles_graphiques`, filter `CQL_FILTER=code_cultu IN ('PHI','PPR','PPT','FVL','FVP','FVT','FEV','LEC')`, 5,000 features per page.
  - Tested: 2016 gives 59,363 parcels in 95 s; 2023 gives 60,791 in 96 s (3 threads).
  - The geometry is called `the_geom` in 2022 [F, `geo_soil_climate.md`].
  - Licence Ouverte 2.0.
- **Codes and counts**:
  - Pea: `PHI` (winter), `PPR` (spring), `PPT`.
  - Faba bean: `FVL`, `FVP` (since 2023), `FVT`, `FEV`.
  - Lentil: `LEC`.
  - By year: 2016 PPR 24,715, FVL 17,058, PHI 11,231, LEC 6,137, FEV 222. 2023 PPR 19,211, FVL 17,845, PHI 10,732, LEC 7,596, FVP 5,117, FEV 290.
- **Reconciliation with the SAA** (ha, RPG vs SAA): pea 190.9 vs 188.0 (2016) and 150.0 vs 151.6 (2023); faba bean 75.6 vs 77.8 and 81.4 vs 80.2; lentil 20.9 vs 19.5 and 28.7 vs 27.7.
- **Existing table**: `archive/research/datasets/rpg_pulses_dept_year.csv` (year × département × group, ha and parcels, 2015-2024). It serves for area and the winter-pea share of pea, **but not for weighting cells**: for that the centroids are needed (script `rpg_peafaba.py`).
- **Gotcha**: the RPG for year N is published in September of N+1. Do not use it as a variable for year N.

### 4.4 Open-Meteo (fallback) [V]

- Endpoint: `https://archive-api.open-meteo.com/v1/archive?latitude=..,..&longitude=..,..&daily=temperature_2m_max,precipitation_sum,et0_fao_evapotranspiration&models=era5_seamless`.
- Tested today with 2 points in a single request: HTTP 200, 91 days, no nulls.
- April-June 2016 rain: 295 mm in Oise vs 301 from weighted SAFRAN; 347 mm in Aube vs 329.
- Limits: non-commercial free tier and a daily call limit [F, `ideas2_4_time_series.md`].

### 4.5 Auxiliaries

| Dataset | Use | Status |
|---|---|---|
| FranceAgriMer, protein crop supply-chain sheet 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf | Users (477 collectors), 502 kt collected, 146 kt for human use vs 62 kt for animal feed, exports | [V], opened with curl |
| Agreste Infos rapides grandes cultures (monthly national estimates) | Competing source and 2026 control | See §2.4 |
| Terres Inovia pea growing guide 2025 (germineo.com mirror) | Agronomic drivers, no N, -20 to -60 kg N/ha in the following crop | [V] |
| Départements GeoJSON (`gregoiredavid/france-geojson`, simplified) | Map and joins | [V] 569 kB |
| Pea_dataset INRAE (doi 10.57745/FW78RE) | Optional: flowering dates by site to calibrate the windows | [F, `datasets.md`] |

### 4.6 Tested joins [V]

- SAA ↔ RPG: département code (`LIB_DEP[:3]` without leading zeros ↔ `code` in the GeoJSON). Areas close to ±5%.
- RPG ↔ SAFRAN: centroid → EPSG:27572 → snapped cell. 99.98% coverage.
- SAFRAN ↔ département: via RPG weights (preferred) or point-in-polygon with `nearest`.
- Tested result: 2016 gives a département × crop × day table of 94,794 rows (pea, faba bean and lentil).

---

## 5. AI method

### 5.1 Objective and unit

- **Main target**: pea `REND` (q/ha) by dept-year, 37 départements (without Oise), 2010-2024 for training and validation and 2025 as provisional test.
- **Secondary target**: faba bean, 28 départements.
- **Lentil**: regional yield, demo mode only.
- **Transformation**: anomaly `y - dept_trend(t)`, with the trend estimated only with training years. The final prediction is trend + predicted anomaly.

### 5.2 Decision dates and variables

| Cut-off | What it is for | Variables (all from SAFRAN weighted by the crop's RPG) |
|---|---|---|
| 1/5 | First signal, before spring pea flowering | Winter (Nov-Feb): days with TINF_H < -5 °C and < -10 °C (winter pea); rain and SWI of Mar-Apr; accumulated ETP-P; waterlogging (days with SWI > 1) |
| 1/6 | Start of flowering | The above + May: days with TSUP_H ≥ 25 °C, rain, ETP-P and mean and minimum SWI |
| **15/6 (main)** | Full flowering of spring pea; water matters "jusqu'à mi-juin, voire fin juin" | The above + 1-15 June. Fixed windows by date (not by phenological stage, which is not observed) |
| 1/7 | Before harvest; comparable with Agreste's July note | The above + 15-30 June |

Non-climate variables:

- Share of winter pea in the département (RPG of year N-1).
- Département trend (with the training set).
- Yield of N-1 (optional).
- Post-2020 dummy (for the regime break in H4).

About 12-20 variables in total. No raw daily curves: with 15 years it is not enough.

### 5.3 List of information leaks

1. **Normalisation, trends and département means** computed with test years. Compute them within each fold.
2. **Random CV by dept-year**: the same year appears in train and test, and the climate is shared. **Always block by year.**
3. **Regional duplicates** (yield copies between départements): they aggravate point 2. Also report the error at regional level.
4. **RPG for year N** as a variable (it is published in September of N+1).
5. **Climate after the cut-off date**, including 10-day variables such as `SSWI_10J` that integrate earlier days (those are fine), and windows that cross the cut-off.
6. **Revised and back-calculated SAA**: the 2010-2019 values are not what was known in real time. State it.
7. **Choosing windows, thresholds (25 °C) or variables by looking at the test**. Fix them beforehand, on agronomic grounds (H9), and freeze them on Saturday at 10:00.
8. **Excluding Oise** was decided after looking at the full data. Document it as a prior decision, based on an obvious artefact.
9. **SIM2 reprocessed** versus the real-time operational one: declared limitation.

### 5.4 Baselines

| Baseline | Description | Why |
|---|---|---|
| B0 | Département mean in the training set | The simplest |
| B1 | Linear département trend | Captures the drift |
| B2 | 5-year "olympic average" (without the maximum or minimum) | **What agricultural practice uses** [NV, ask the mentor] |
| B3 | **Official competitor**: Agreste's departmental estimate of 1/7 (xlsx from Infos rapides; years 2020, 2023, 2025 and 2026, 2024 to be confirmed). Before 1/7 it does not exist | What the OS has for free from mid-July. Compare our 15/6 (and 1/6) against its 1/7 in the available years (n = 2-4, weak evidence) |

### 5.5 Model family (justified by n)

- **n**: ~37 départements × 15 years ≈ 555 dept-years for pea, but **only 15 independent seasons** (58% of the variance is common to the year).
- **Main model**: pooled Ridge on anomalies, with the same ~15 variables for all départements, standardised on the training set. It is stable with small n and interpretable (coefficients with the expected agronomic sign).
- **Comparator**: LightGBM or shallow sklearn HistGradientBoosting (depth 2, ≤200 trees, monotonic constraints on heat and water deficit). Only if it beats Ridge in the locked validation.
- **Explanatory layer (idea 2 integrated)**: kNN of analogue seasons on the same standardised variable vector, with candidates only from earlier years. Shows "this season looks like 2016 and 2021" with their yields.
- **Ruled out**: deep learning on daily series or an LLM in the core. No data justify it. An LLM (Bedrock) only to draft the bulletin from the outputs, and it is on the cut list.

### 5.6 Uncertainty

- **Year-blocked conformal**: leave-one-year-out residuals in the training set give the 10% and 90% quantiles of the absolute error, by cut-off date. Intervals widen at early dates.
- Report the empirical coverage on the test (should be around 80%).
- Alternative: quantile regression with LightGBM. Not needed.

### 5.7 Validation design

1. **Selection and tuning**: leave-one-year-out within 2010-2018.
2. **Temporal test** with an expanding window:
   - For each year t between 2019 and 2024: train on 2010…t-1 and predict t.
   - There are 6 test years, including 2020 and 2024 (bad) and 2019 (good).
3. **"Provisional" test**: 2025, training on 2010-2024. Labelled as provisional data.
4. **Out-of-sample 2026 control**: there is no SAA for 2026. Aggregate the 2026 departmental predictions (weighted by year N-1 area) to a national yield and compare it with Agreste's 2026 national estimate (§2.4). It is data published after our cut-off date, but it must be made clear that it is an estimate, not the final figure.

### 5.8 Metrics

- MAE in q/ha and MAPE by test year and by cut-off date. **Show the 6 years separately and the effective n = 6.**
- Skill = 1 - MAE_model / MAE_best_baseline.
- Tonnage error for an example basin: Σ(area × error).
- Bad-year detection: recall and precision of "yield < 85% of trend" at the 15/6 cut-off.
- 80% interval coverage.
- Error aggregated to region, because of the duplicates.

### 5.9 What the AI adds (jury test)

- **Without AI**, the OS has the historical mean and a national note, with 4 limitations:
  - it does not adapt to the spring under way;
  - it is not departmental;
  - it has no uncertainty;
  - it does not say why.
- **With AI**, each département has an estimate that is updated with climate up to yesterday, with a calibrated interval, explained drivers and analogue seasons.
- If the model does not beat B0-B3, the AI adds no predictive value, and that has to be said and the project pivoted (§7).
- **Scoring risk**: the jury may read "Ridge = regression". The answer: the problem has 15 seasons, and a more complex method would be less rigorous. The value is in the spatial agro-climatic variable engineering (RPG × SAFRAN), honest validation and calibrated uncertainty.

### 5.10 Explainability

- Contribution per variable (coefficient × standardised value) for each département and date. Example: "-4 q/ha per 9 days >25 °C at flowering".
- The 3 analogue years with their climate and yield.
- Risk flags: heat at flowering, water deficit, waterlogging and winter frost.

---

## 6. MVP and demo

### 6.1 Screens (Streamlit)

1. **Map of France** (choropleth by département) for the chosen crop, year and cut-off date. Colour = estimated anomaly against trend (%), with interval in the tooltip.
2. **Département card**:
   - SAA yield series 2010-2025;
   - estimated point with interval for the chosen year;
   - baselines B0-B3;
   - "reveal the actual" button;
   - evolution of the estimate between 1/5, 1/6, 15/6 and 1/7.
3. **Drivers and analogues**:
   - contribution bars per variable;
   - accumulated rain and days >25 °C curves for the year against the 3 analogues;
   - table with those years' yields.
4. **Validation**: table and chart of MAE by test year (2019-2024) for the model and the baselines, interval coverage, effective n and limits. This screen earns rigour points.
5. **"My collection basin"**: the user picks départements and contracted areas, and the tool gives expected tonnes with an interval. It translates q/ha into the user's decision.
6. **2026 live**: 15/6/2026 estimates by département against Agreste's departmental estimates of 1/7, 1/8 and 1/9/2026 (published after our cut-off date), and the national aggregate against 29.9 q/ha (1/7) and 31.1 (1/8).
7. (Experimental) Lentil at regional level, with the imputation warning.

### 6.2 Exact demo script (≈90 s within the 4 min)

1. (10 s) "We are the grain collection manager of a cooperative in Seine-et-Marne and Loiret. It is 15 June 2024." Open the map on pea / 2024 / 15-6.
2. (20 s) Show that Seine-et-Marne and Essonne come out in red, with estimate and interval. The "historical average" baseline says X (real values on Sunday).
3. (20 s) Click "why": drivers (spring rain and waterlogging, heat) and analogues ("looks like 2016").
4. (15 s) "Reveal the actual": 2024 Seine-et-Marne, with -20 q/ha against its mean according to the SAA. Where it falls within the interval. Remind that the first official departmental figure only came out in mid-July.
5. (15 s) "My basin" screen: 8,000 contracted ha mean Y kt expected against Z kt of the baseline: "that is N lorries or N days of silo".
6. (10 s) Validation screen: "over 6 test years, the mean error is A against B for the baseline, and it fails in C" (figures measured on Saturday).

**Demo backup plan**: a video recorded Saturday night plus screenshots in the deck. All pre-computed artefacts in parquet, so the app does not depend on the network.

### 6.3 Stack

- **ETL**: Python 3.12, `polars`, `geopandas`, `pyproj`, `pandas` + `openpyxl` (SAA).
- **ML**: `scikit-learn` (Ridge, KNN, HistGradientBoosting), `numpy`. Conformal done by hand (20 lines) or `mapie`.
- **App**: Streamlit + `plotly` (choropleth with the départements GeoJSON). Deploy on Streamlit Community Cloud (public repo) or on AWS (EC2 or App Runner) with the event credits.
- **AWS**: S3 for the raw SIM2 files (downloading them from an EC2 instance is probably faster than wifi [NV]); EC2 t3.large for the ETL. Optional: everything runs on a laptop.
- **Optional**: Bedrock (Claude) to draft a "weekly bulletin" from the structured outputs. Not core.

### 6.4 Repo structure

```
hackthefork-legumes-yield/
  README.md                 # problem, data with version and download date, how to reproduce, declared prior resources
  data/README.md            # exact URLs, licences, what is measured, source, assumption or synthetic
  etl/
    01_download.sh          # SAA zip + SIM2 2009-2026 (xargs -P4) + grid + GeoJSON
    02_saa_clean.py         # COP → tidy (dep, year, crop, surf, rend, prod, statut), exclusions (Oise)
    03_rpg_weights.py       # WFS → centroids → weights per cell (dep, crop)
    04_sim2_aggregate.py    # year by year → clim_dep_crop_day.parquet
    05_features.py          # variables per cut-off date → features.parquet
  model/
    baselines.py            # B0-B3
    train_eval.py           # LOYO + expanding window, conformal, metrics → results/*.parquet
    analogs.py
  app/
    app.py                  # Streamlit
  results/                  # frozen metrics cited in the deck
  deck/
```

---

## 7. Hour-by-hour work plan

Roles: **A** = data and evaluation, **B** = modelling (ML/CV student), **C** = product, business and pitch.

| When | A (data/eval) | B (modelling) | C (product/business/pitch) |
|---|---|---|---|
| **Fri 17:45-20:45** | Welcome. Locate mentors from Terres Inovia / cooperatives | Same | Same. **Ask the organisers whether pea/faba bean "for the human protein chain" is eligible** |
| **Fri 20:45-21:30** | Launch the downloads (SAA, SIM2 2009-2026 with 4 threads, grid, GeoJSON) on EC2 or laptop. `02_saa_clean.py` | `03_rpg_weights.py` (2 years of WFS, ~3 min) | Mentor: validate user, decision and date (questions in §11). Create the repo and the prior resources README |
| **Fri 21:30-23:00** | SAA tidy table + exclusions + counts (should give 38/28) | `04_sim2_aggregate.py` over all years | Streamlit skeleton with the map and the département card using the SAA. **Declare Track 3 before 23:00** |
| **Checkpoint 1 (23:00)** | **GO** if `clim_dep_crop_day.parquet` exists for 2009-2025 and the SAA tidy. **NO-GO**: switch to Open-Meteo with 1 point per département (the RPG centroid) | | |
| Friday night (off campus, optional, ≤1 h) | Freeze the windows and thresholds of §5.2 in writing (anti-leakage) | `05_features.py` | Collect Agreste's estimates (dates and values) for B3 and the 2026 control |
| **Sat 9:30-10:15** | Workshop (C goes; A and B carry on) | | Workshop "AI at the heart of innovation" |
| **Sat 10:15-13:00** | Evaluation harness: LOYO and expanding window, B0-B3, metrics by year | Pooled Ridge + kNN analogues + conformal | Drivers, validation and "my basin" screens. First draft of the deck (problem and user) |
| **Checkpoint 2 (13:00)** | MAE table by year for the baselines and Ridge at the 15/6 cut-off | | |
| **Sat 14:00 (stopping rule)** | **If Ridge does not improve the MAE of the best baseline by ≥10% in at least 4 of 6 years** → stop iterating the model and pivot the story to "risk radar + analogues", reporting the negative result honestly. If it improves → continue | | |
| **Sat 14:00-18:00** | Faba bean with the same pipeline; error analysis (2020, 2024); regional error; coverage | GBM comparator (only if time allows); 1/5, 1/6, 1/7 cuts; 2026 prediction | Integrate the real results into the app; business (pricing, market); write the online project sheet |
| **Checkpoint 3 (17:30)** | **End-to-end demo on a laptop with frozen artefacts.** Push to GitHub. If it fails: freeze the scope to pea / 15-6 | | |
| Sat 18:00-23:00 (off campus) | Check every number in the deck against `results/` | Experimental regional lentil (optional) | Full deck, demo video as backup, 3 timed rehearsals |
| **Sun 8:30-9:15** | Final check of links, PDF exported from the official template | Backup of the repo and the artefacts | **Upload the PDF and the sheet by 9:15** (15-min margin) |
| **Sun 10:15-12:00** | Pitch: C presents, B answers the technical questions, A answers data and limits | | |
| **Sun 12:00** | Download everything from AWS (S3, EC2) before accounts close | | |

**Cut list** (from first to last to be cut):

1. Bedrock / LLM bulletin.
2. Regional lentil.
3. GBM.
4. The 1/5 and 1/7 cuts (keep only 15/6).
5. Faba bean.
6. "My basin" screen.
7. RPG weighting (use the simple average).

**Never cut**: year-by-year validation against the baselines, the limits screen and a working demo.

---

## 8. Business

- **Value proposition**: "From May, an objective and updated estimate of how many tonnes of pea and faba bean will come into your collection area, with its margin of error and the reason, to adjust logistics and commitments with your industrial clients in time."
- **Who pays**:
  1. The OS (cooperative or négociant): annual subscription.
  2. The interprofession (Terres Univia) or FranceAgriMer, as a common good of the supply chain; it is consistent with the Plan protéines (protein plan).
  3. The industrial buyer (Roquette, Intact), to see its supply.
- **Price references** (there are no public prices for B2B forecasting):
  - Mes Sat'images (Chambre d'agriculture): €9/ha [F].
  - Mes Parcelles: €367 excl. VAT/year in Isère [F].
  - Farmstar: ~€8-10/ha [F].
  - EarthDaily/Geosys, Kayrros and Hummingbird: "contact sales" [F].
- **Proposed pricing [NV, hypothesis]**: €2,000 to 10,000/year per OS depending on tonnage collected, of the order of €0.1-0.5 per tonne of pea and faba bean collected.
- **Market size** (labelled estimates):
  - **Initial**: 477 protein crop collectors [V] × €5,000 = €2.4m/year if all adopted [NV, theoretical ceiling]. With a realistic 10% adoption: ~€0.24m/year. **It is small.**
  - **The scale comes from the pipeline, not the pulse**: the same SAFRAN × RPG × SAA serves rapeseed, sunflower, wheat and barley for the same clients. Lentil, chickpea and bean come in when their data improve (the RPG's PHS since 2023).
- **Adoption**:
  1. Free pilot with an OS in a food-grade pea supply chain (Axéréal/Intact or a Roquette supplier) in the 2027 season.
  2. Compare with its internal forecast at the close of collection (July 2027).
  3. Agreement with Terres Univia or Terres Inovia to disseminate it.
- **Competitors and differentiation**:
  - Agreste: official, free and **departmental from 1/7**, but expert opinion, no interval and nothing before July. The DRAAFs: regional and repackage Agreste.
  - JRC MARS: EU and country (see §2.4).
  - Terres Inovia: harvest balances in July and August; its satellite yield work with INRAE is on sunflower, not pulses [F].
  - Private satellite services: expensive, opaque and oriented to commodities.
  - **Difference**: département or basin scale, pulses, in May-June, with calibrated interval, open and explainable.

---

## 9. Impact and sustainability

| Element | Figure | Status |
|---|---|---|
| Volume affected | 502 kt/year of pea and faba bean collected by OSs (5-season average) | [V] FranceAgriMer |
| Domestic human use | 146 kt in 2024/25 (155 kt on average) against 62 kt for animal feed | [V] FranceAgriMer |
| Value of collection | 502 kt × €200-260/t ≈ **€100-130m/year** | [NV] own calculation with the CRIT Grand Est 2025 price reference [F] |
| Current uncertainty by département | Median deviation of 5.1 q/ha (~15% of yield) against the département mean; p90 of 11.5 q/ha | [V] SAA, descriptive |
| Basin example | 10,000 ha × 1 q/ha less error = 1,000 t better planned ≈ €200-260k of volume | [NV] arithmetic; **the real improvement (q/ha) is measured on Saturday and cannot be claimed before** |
| Agronomic sustainability | Pea receives no nitrogen fertiliser and reduces N needs by 20-60 kg N/ha in the following crop; it brings a yield gain (and protein gain) to the next wheat | [V] Terres Inovia 2025 pea growing guide |
| Impact mechanism | Less collection risk → more reliable contracts → more pulse area for the human chain | [NV] this is the project's thesis; pea area is falling (123 → 98 → 95 kha, 2024-2026) [F], and the brake, according to the Track 3 brief, is the producer's fear of losing income |

**Communication rule:** the tonnage impact is presented as "for each q/ha of error reduced", with the real error measured in the backtest. Never promise reductions that were not measured.

---

## 10. Pitch

### 10.1 4-minute script

| Time | Block | Content |
|---|---|---|
| 0:00-0:40 | Problem | "July 2024: Seine-et-Marne peas yield 20 q/ha less than normal. The collection manager finds out from the combine harvesters. France wants to double pulses, and every bad surprise hits the contracts that have to convince producers." Figures: 477 collectors, 502 kt/year and ±20% national swing |
| 0:40-1:20 | Solution | A departmental estimate from May, with SAFRAN climate where the parcels are, calibrated interval and the reason. Diagram: SAA + SAFRAN + RPG → model → map |
| 1:20-2:50 | Live demo | Script of §6.2 |
| 2:50-3:20 | Rigour | MAE by year against the 4 baselines, effective n = 6, interval coverage, limits (2010-19 back-calculation, Oise, imputed lentil) |
| 3:20-4:00 | Scale | Pilot with one OS of the pea protein supply chain → Terres Univia → other crops with the same pipeline. Close: "fewer surprises, more pulse contracts" |

### 10.2 Deck slides (official template)

1. Title + one sentence + link to the repo and the demo.
2. User and decision (OS persona, season calendar).
3. Quantified problem (swings, 2016, 2024, lentil 2021).
4. What exists today (national Agreste, MARS, technicians) and the gap.
5. Solution and data architecture (measured / source / assumption).
6. Method: agronomic variables, year-by-year validation, conformal.
7. Results: MAE by year against the baselines (measured).
8. Demo screenshot (backup if the live demo fails).
9. Limits and effective n.
10. Business: who pays, price (assumption), adoption.
11. Impact (source and estimate kept separate).
12. Team, declared prior resources and sources.

### 10.3 Likely jury questions

| Question | Prepared answer |
|---|---|
| "Isn't it animal feed?" | "In France, the domestic use of pea and faba bean is mostly human: 146 kt against 62 kt for feed in 2024/25 (FranceAgriMer). We target the protein pea supply chains (Roquette, Intact). Lentil goes in experimental mode because its departmental data are imputed." |
| "Is it just a regression?" | "Yes, on purpose: there are 15 seasons. A more complex model would overfit. The AI is in the spatial construction of agro-climatic variables (RPG × SAFRAN), the year-blocked validation and the calibrated uncertainty." |
| "Does it beat Agreste?" | "Agreste publishes its first departmental estimate on 1 July, à dire d'experts and without a margin of error; for pea it was off by 2.8 q/ha per département in 2023 and 5.6 in 2025. We arrive 2 to 6 weeks earlier and with an interval." Show the measured comparison for the available years, even if few |
| "How many independent data points do you have?" | "6 test years and 15 of history. We say so on the limits slide." |
| "Doesn't the cooperative already know from its technicians?" | "The technicians see parcels from late June. We give an objective reference from May, comparable year to year. We complement, we do not replace." (Validate with the mentor) |
| "Why not use satellite?" | "It is the next step (Sentinel-2 from June). In 20 h we prioritise what can be validated." |
| "Who pays?" | The OS, or the interprofession as a common good. Reference price: €9/ha for a satellite service from the Chambres; ours, per tonne collected (assumption). |
| "What about the 2010-2019 data?" | "Agreste back-calculated them. We detect it (integer yields in 48-60% of cases before 2020 and in 84-94% after), we model anomalies and exclude Oise." |

---

## 11. Risks, mentors, prior resources and deliverables

### 11.1 Risks and mitigations

| Risk | Prob. | Impact | Mitigation |
|---|---|---|---|
| Ineligibility ("animal feed") | Medium | Fatal | Ask on Friday. Frame as human protein. Fallback: the same pipeline on lentil and chickpea at regional level (idea 2: analogues) |
| The model does not beat the baselines | Medium | High on rigour and AI | Saturday 14:00 stopping rule; honest pivot to "risk radar + analogues"; report the negative result |
| SIM2 ETL slow over wifi | Low | Medium | EC2 + S3; fallback to Open-Meteo; parallel downloads |
| Temporal leakage | Medium | High on rigour | List in §5.3; freeze variables on Saturday at 10:00; cross-review by A of B's code |
| The user does not decide by département | Medium | Medium on economics | "My basin" screen, which aggregates départements with areas |
| The jury sees little AI | Medium | Medium | Explain the complexity of the data problem, the analogues and the uncertainty; do not inflate with an LLM |
| Deck figures without traceability | Low | High | Every figure in the deck comes from `results/` or a listed source |

### 11.2 Questions for mentors (Friday)

1. Are pea and faba bean "for the protein human chain" eligible? (Organisers)
2. Who builds the collection forecast in an OS, on what dates and with what historical error?
3. Do they use the département or do they need the "collection zone"? What silo granularity?
4. Do they use the "olympic average" as a reference? What penalties or costs does falling short against an industrial buyer carry?
5. Do Terres Inovia or Arvalis have an internal departmental pea forecast?
6. Which cut-off date would change decisions: 1/6 or 15/6?
7. What share of pea collection in their area goes to human protein or casserie?

### 11.3 Prior resources to declare

- The desk research in `research/` (this file, `safran.md`, `datasets.md`, `ideas2_4_time_series.md`, `track3_context.md`): counts and readings of public data, not solution code or a model.
- The derived table `rpg_pulses_dept_year.csv` (RPG counts by département) and the scratchpad inspection scripts (download and counting). **Recommendation: rewrite the ETL during the event** and declare that the prior exploration existed.
- Generic libraries: polars, geopandas, scikit-learn, Streamlit.
- Open data: Agreste SAA, SIM2, RPG, Open-Meteo, FranceAgriMer and the départements GeoJSON.

### 11.4 Deliverables checklist

- [ ] Track declared before Friday 23:00.
- [ ] Public repo with README (data, versions, download date, measured / source / assumption / synthetic, prior resources).
- [ ] Demo working (URL + local run + backup video).
- [ ] Deck PDF in the official template, with the link to the code and the demo.
- [ ] Online project sheet (non-confidential summary: problem, solution, business model).
- [ ] Both uploaded to the Drive before Sunday 9:30 (target: 9:15).
- [ ] Pitch rehearsal in ≤3:50.
- [ ] Sunday 12:00: backup of S3 and EC2, close resources.

---

## 12. Rubric (own estimate, before measuring results)

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Impact and sustainability | 30% | **5.5** | Plausible mechanism (more reliable contracts → more pulses) and real volumes (502 kt), but indirect. Doubt about the share of human consumption in pea and faba bean weighs on it |
| Scientific and technical rigour | 20% | **7.5** | Audited data (imputations, 2020 break, Oise), year-blocked validation, strong baselines, calibrated uncertainty, declared limits |
| Appropriate and essential AI | 20% | **5.5** | Prediction with classical ML, well justified by n, but the jury may see it as "a regression". The analogues and the uncertainty help |
| Economic viability | 20% | **4.5** | Concrete user and real OS obligations, but pricing is an assumption, the initial market is small, nobody has confirmed willingness to pay and **there is a free official substitute since 1/7** |
| Execution and pitch | 10% | **7.5** | The pipeline is simple and tested (download and aggregation measured); the demo is visual and there is a backup plan |
| **Weighted total** | | **5.9** | 0.3×5.5 + 0.2×7.5 + 0.2×5.5 + 0.2×4.5 + 0.1×7.5 = 1.65 + 1.5 + 1.1 + 0.9 + 0.75 = **5.9** |

What would raise the score: (a) the organisers confirm eligibility and an OS mentor confirms the decision and date (+1 on economics and impact); (b) a measured skill ≥15% against the best of B0-B2 in 4 or more of 6 years, and an error at the 15/6 cut-off comparable with Agreste's 1/7 (+1 on AI and economics).

---

## 13. Sources (opened in this session or by the subagents)

Opened by me:

- Data.gouv API, SIM quotidienne: https://www.data.gouv.fr/api/1/datasets/donnees-changement-climatique-sim-quotidienne/
- SIM2 2016 and latest, grid, `.prj`: https://meteofrance.s3.sbg.io.cloud.ovh.net/data/REF_CC/SIM/
- SIM parameters PDF: https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260331-150448/sim-quotidienne-parametres-20260331.pdf
- SIM model presentation PDF: https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260602-150234/climatologie-presentation-modele-sim-20260602.pdf
- Agreste SAA long series (ZIP): https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/SAA-SeriesLongues/SAA-SeriesLongues-2010-2025_DonneesProvisoires-DepartementalesRegionales.zip
- RPG WFS: https://data.geopf.fr/wfs/ows
- Open-Meteo archive API: https://archive-api.open-meteo.com/v1/archive
- Départements GeoJSON: https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson
- FranceAgriMer, protein crop supply-chain sheet 2026: https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf
- Terres Inovia pea growing guide 2025 (mirror; terresinovia.fr returns Cloudflare HTML): https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf
- Terre-net / Terres Inovia, "Semer précocement pour sécuriser le potentiel des protéagineux de printemps" (15/02/2022): https://www.terre-net.fr/pois-proteagineux/article/205909/semer-precocement-pour-securiser-le-potentiel-des-proteagineux-de-printemps
- Participant guide (local): `event/participant_guide.txt`

Opened by the subagents (per their reports):

- Agreste Infos rapides, departmental xlsx of 1/7 (2023, 2025, 2026), opened by me: https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/IraGcu2688/2026_88donnees_grandescultures_departements.xlsx ; https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/IraGcu2591/2025_91donnees_grandescultures_departements.xlsx ; https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/IraGcu2379/2023_79donneesdeptgrandescultures.xlsx
- The other Infos rapides notes (IDs 2074, 2093, 20107, 21101, 22111, 2393, 23107, 2496, 24113, 25115, 2599, 2698, 26114; detail page https://agreste.agriculture.gouv.fr/agreste-web/disaron/<ID>/detail/), opened by the subagent
- JRC MARS Bulletin, September 2025 (mirror): https://www.oilworld.ru/data/postfiles/362652/JRC_MARS_0925.pdf
- DRAAF Pays de la Loire, July 2026: https://draaf.pays-de-la-loire.agriculture.gouv.fr/IMG/pdf/2026_07_plaquette_etat_des_cultures_previsisons_de_collecte_recolte_2026.pdf
- DRAAF Centre-Val de Loire n°11, September 2025: https://draaf.centre-val-de-loire.agriculture.gouv.fr/IMG/pdf/no11_bimestrielle_septembre_2025.pdf
- Agreste Bilan conjoncturel 2025: https://agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/BilanConj2025/Bilan_conjoncturel_2025.pdf
- Agreste Infos rapides grandes cultures n°88 (July 2026): https://www.agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/IraGcu2688/2026_88inforapgdescultures.pdf
- FranceAgriMer decision MEP/D2017-06: https://info.agriculture.gouv.fr/boagri/document_administratif-006efff4-ebf0-408d-9779-b9aa56f593ef/telechargement
- Euralis/Bonduelle 2023: https://www.euralis.fr/wp-content/uploads/2023/06/1er-anniversaire-partenariat-Bonduelle-legumes-secs-juin-2023.pdf
- Axéréal-Intact: https://www.reussir.fr/ladepeche/intact-regenerative-et-axereal-lancent-une-filiere-proteine-vegetale-dans-le-loiret
- Roquette, pea supply chain: https://www.reussir.fr/grandes-cultures/roquette-developpe-une-filiere-pois-pour-le-marche-des-proteines-vegetales
- Penalties for failing to deliver the agreed supply (Cour de cassation): https://www.reussir.fr/vigne/quelles-sanctions-pour-un-exploitant-agricole-qui-ne-tient-pas-son-engagement-vis-vis-de-sa
- Lentil 2021 harvest balance: https://www.terre-net.fr/observatoire-technique-culturale/strategie-technique-culturale/article/bilan-de-recolte-lentille-video-itk-217-203084.html
- Pea harvest 2025 (La Dépêche): https://www.reussir.fr/ladepeche/moisson-2025-rebond-des-rendements-en-pois-proteagineux
- Protein crops harvest 2025 (Pleinchamp): https://www.pleinchamp.com/actualite/moisson-2025-les-proteagineux-retrouvent-des-couleurs
- CRIT Grand Est 2025 price reference: https://draaf.grand-est.agriculture.gouv.fr/IMG/pdf/crit_16_avril_2025___annexe_2___referentiel_des_prix_crit_2025.pdf
- Mes Parcelles, Isère: https://isere.chambres-agriculture.fr/etre-accompagne/notre-offre-pour-les-agriculteurs/detail-de-la-prestation-38/gerez-et-suivez-vos-cultures-avec-mes-parcelles
- Mes Sat'images, Ain: https://ain.chambres-agriculture.fr/etre-accompagne-1/notre-offre-pour-les-agriculteurs/detail-de-la-prestation-01/piloter-lazote-mes-satimages
- Faba bean and Egypt (Réussir): https://www.reussir.fr/ladepeche/terres-inovia-le-salut-de-la-feverole-passe-par-les-os
- Press kit, Stratégie protéines 2020: https://agriculture.gouv.fr/telecharger/122401
