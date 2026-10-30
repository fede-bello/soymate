# Spatial datasets: parcels, satellite, soil and climate (Track 3)

Audit done on 29/10/2026. Tags: **[V]** I verified it myself (downloaded, counted, queried the API), **[F]** I read it at the source, **[NV]** not verified (memory or search without confirmation).
Hackathon rule respected: exploration only (download, count, cross, plot). No model was trained or fitted.
Already audited in other files, only referenced here: INRAE bruchid data (`idea3_bruchids.md`), WSU/USDA drone (`idea5_drone.md`), Agreste SAA, SAFRAN/SIM2 and Open-Meteo (`ideas2_4_time_series.md`).

Derived table I left in the repo: `archive/research/datasets/rpg_pulses_dept_year.csv` (8,336 rows: year × department × pulse group, with number of parcels and ha, RPG 2015-2024) [V].

## Summary

| Dataset | Owner | Coverage | Granularity | License | Access | T3 relevance | Main limitation |
|---|---|---|---|---|---|---|---|
| **RPG graphic parcels 2015-2024** | IGN / ASP | France (mainland + DOM, overseas departments) | CAP parcel (polygon), annual | Licence Ouverte 2.0 | WFS without login (`data.geopf.fr/wfs`), GPKG/SHP by region | **10** | No dept/commune column or destination column (human/animal); id_parcel not stable across years |
| **RPG 2025 (v4.0)** | IGN / ASP | France | Parcel, with `precision`, `bio` | LO 2.0 | 7z download only (national 10.9 GB; by region 90 MB to 1.7 GB) | **9** | Not yet in the WFS; large files |
| **RPG Bio 2019-2023** | Agence Bio | France | Organic parcel, with INSEE commune and `precision_culture` | LO 2.0 | data.gouv, GPKG by region/year | **8** | Organic only (80-85% of organic land); 2024 not published there |
| Theia OSO 2016-2023 | CNES/CESBIO (Theia) | Mainland France | 10 m raster, annual | Etalab 2.0 | Recherche Data Gouv (~5 GB/year), Sentinel Hub BYOC | 5 | Class 7 "protéagineux (féverole/pois)" (protein crops: faba bean/pea) but no lentil or chickpea |
| Sentinel-2 L2A | ESA / Copernicus | Global | 10-20 m, every ~5 days | Free | Planetary Computer (STAC + anonymous SAS token), Earth Search (public COGs), CDSE (free search, download with account) | 8 | Clouds; post-2022 reflectance offset on PC |
| PASTIS / PASTIS-R | IGN/ENPC (Sainte Fare Garnot) | 4 S2 tiles in France, 2019 | 128×128 px patch, labels per parcel | CC-BY 4.0 | Zenodo 28.8 GB | 3 | 18 classes, **no grain pulses** (only "Leguminous fodder" and soy) |
| EuroCrops | TUM | EU (France 2018 from RPG) | Parcel, HCAT taxonomy | CC-BY [NV] | Zenodo | 4 | France = RPG 2018 recoded: better to go straight to the RPG |
| Sen4AgriNet | NOA | Catalonia + France 2019-2020 | S2 patch + parcels | MIT (code) [F] | HuggingFace / Dropbox | 3 | French coverage and pulse classes not confirmed |
| AI4Boundaries | JRC | 7 EU countries incl. France | Parcel boundaries + monthly S2 | CC-BY [NV] | JRC FTP [NV] | 2 | Boundaries only, no crop type |
| HRL Crop Types (CLMS) | EEA / Copernicus | EEA38, 2017-2021 (2022-24 in production) | 10 m raster | Copernicus free | CLMS [F] | 4 | 17 classes; did not confirm whether there is a pulse class |
| JRC EU Crop Map 2018/2022 | JRC | EU | 10 m | CC-BY [NV] | JRC data catalogue | 3 | "Dry pulses, vegetables and flowers" together [F] |
| Corine Land Cover | EEA | Europe, 2018 | 100 m / MMU 25 ha | Copernicus free | CLMS | 1 | No individual crops |
| **SoilGrids 2.0** | ISRIC | Global | 250 m, 6 depths | CC-BY 4.0 | REST (beta, rate limit) and public VRT/COG | **7** | No carbonate/lime; nulls in urban areas |
| BDAT (soil analyses) | INRAE Infosol / GIS Sol | France, 1990-2014 | Canton, PRA, dept, region | Restricted (access request) | Recherche Data Gouv | 6 | Restricted-access files (HTTP 403) |
| RMQS | GIS Sol / INRAE | France, 16 km grid | ~2,200 sites | Varies | Recherche Data Gouv | 4 | Very sparse for parcel scale |
| ESDB / BDGSF 1:1M, LUCAS topsoil | JRC ESDAC | EU | 1 km / points | Use with registration | ESDAC form [NV] | 4 | Manual registration, delays |
| **GAEZ v4** | FAO / IIASA | Global, historical + scenarios | 5 arcmin (~9 km) | CC-BY-NC-SA 3.0 IGO [NV] | Public COGs on S3 | **6** | Chickpea, dry pea, dry bean yes; **lentil and faba bean not found** |
| DRIAS / Explore2 / TRACC | Météo-France + IPSL/CERFACS | France, 8 km | Daily, 2006-2100 | Free with account [F] | DRIAS portal (NetCDF/CSV) | 6 | Requires account; not on data.gouv as a file |
| Climadiag Agriculture | Météo-France + Solagro | France, 8 km | ~300 agroclimatic indicators | Free [F] | Web (account) | 4 | Indicators for wheat/maize/rapeseed; pulses not confirmed |
| Météo-France base climate data | Météo-France | Stations, France | Daily/hourly | LO 2.0 [V] | data.gouv / meteo.data.gouv.fr | 5 | Point-based; for the grid, SAFRAN already exists (another file) |
| ERA5 / ERA5-Land | ECMWF | Global | 9-31 km, hourly | Copernicus free | CDS (account) | 3 | Redundant with Open-Meteo/SAFRAN |
| Irrigation (RA 2020, BNPE) | Agreste / OFB | Commune / abstraction point | Census / annual | LO 2.0 [NV] | data.gouv | 3 | Grain pulses are barely irrigated |
| ADMIN EXPRESS | IGN | France | Commune/dept polygons | LO 2.0 | WFS (same server as RPG) [V] | support | Needed to join RPG with Agreste |

---

## 1. RPG, graphic parcels 2015-2024 (core dataset)

- **URL**: WFS `https://data.geopf.fr/wfs/ows`, layers `RPG.2015:parcelles_graphiques` … `RPG.2024:parcelles_graphiques`, plus `RPG.LATEST`, `RPG.20xx:codes_cultures` (2022-2024) and `ilots_anonymes` (2024) [V]. Bulk download: `https://data.geopf.fr/telechargement/resource/RPG` (349 packages, v1 2007-2014 by region; v2.0 2015-2022, v2.2 2023, v4.0 2024-2025) [V].
- **Owner**: ASP (CAP declarations), published by IGN. **License**: Licence Ouverte 2.0 [F].
- **Columns** [V]: `id_parcel`, `surf_parc` (ha), `code_cultu` (3-letter CAP code), `code_group`, `culture_d1`, `culture_d2` (secondary/double crops), and from 2024 `cat_cult_p` (TA/PP/...). Geometry `geom`, except **2022, which is called `the_geom`** (a CQL filter with `geom` in 2022 returns HTTP 400) [V].
- **CRS**: the WFS returns EPSG:4326; the packages come in Lambert 93 (EPSG:2154) [V]. Heads up: in the CQL `BBOX(geom, lat_min, lon_min, lat_max, lon_max)`, the order is lat/lon [V].
- **Fine pulse codes: kept, not grouped** [V]. LEC (non-forage lentil), PCH (chickpea), FVL/FVP/FVT (forage faba bean "féverole"), FEV (faba bean), PHI/PPR/PPT (winter/spring protein pea, "pois protéagineux"), LDH/LDP/LDT (sweet lupin), HAR (dry bean/flageolet, up to 2022), PPO (petits pois, garden peas, up to 2022), MPC/MPP/MPT/MLS (mixtures), GES (gesse, vetch/grass pea), FNU (fenugreek), PAG, LEF (forage lentil), SOJ.
- **Nomenclature change in 2023** [V]: HAR, PPO, LEF, MPP, MLS disappear, and **PHS "Pois et haricot secs (alimentation humaine)"** (dry pea and bean, human food) and **PHF "Pois et haricot frais (alimentation humaine)"** (fresh pea and bean, human food) appear, plus FVP (spring féverole). The 2015-2022 vs 2023-2024 series for dry beans and fresh peas are not directly comparable.
- **There is no department or commune column** [V]. A spatial join is needed. I did it with the representative point (centroid) of each parcel against department polygons: 0.01% of parcels without a department (47 ha over 10 years, coast/border cases) [V]. The resulting codes (`01`…`95`, `2A`/`2B`) are the same ones Agreste uses, so it joins directly with SAA [V].
- **id_parcel cannot be used to follow a parcel over time**: in the two rotation extracts, only 62-63% of parcels have the same `id_parcel` as the parcel at the same point in the previous year [V]. For successions, geometries have to be overlaid.
- **Size/access**: the WFS pages in batches of 5,000 features (~10 s and ~5 MB per page with geometry) [V]. `RESULTTYPE=hits` gives instant counts without downloading anything [V]. I downloaded all pulse parcels in France 2015-2024 (910,005 parcels) in ~50 min, keeping only the centroid.

### 1.1 National figures (RPG, declared ha) [V]

| Group (codes) | 2015 | 2017 | 2019 | 2020 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| Lentil (LEC) | 17,179 | 33,762 | 37,529 | 35,528 | 29,056 | 28,671 | **34,226** |
| Chickpea (PCH) | 8,870 | 19,543 | 36,703 | 23,437 | 16,057 | 24,006 | **27,491** |
| Pois et haricot secs AH (PHS; dry pea and bean, human food) | | | | | | 11,715 | **12,379** |
| Protein pea (PHI+PPR+PPT) | 157,917 | 190,392 | 148,572 | 201,057 | 132,917 | 149,986 | **123,773** |
| Féverole, faba bean (FVL+FVP+FVT) | 84,697 | 75,295 | 62,442 | 75,810 | 67,558 | 80,915 | **83,081** |
| Sweet lupin (LD*) | 6,543 | 5,351 | 2,908 | 5,880 | 5,205 | 4,928 | **4,724** |
| Protein crop + cereal mixture (MPC) | 20,949 | 40,452 | 39,672 | 40,856 | 50,760 | 53,312 | **40,595** |
| Soybean (SOJ, count only) | 30,674 parcels | 35,583 | 39,063 | 44,388 | 43,694 | 37,504 | 35,891 parcels |

2024 parcels: lentil 8,077, chickpea 6,373, PHS 2,765, protein pea 24,543, féverole 21,881. Median size: lentil 2.6 ha, chickpea 2.7 ha, pea 4.0 ha (maximum 135 ha in PHF) [V].
Consistency: the ~34,000 ha of lentil in 2024 is in line with the order of magnitude given by the filière (supply chain) (~35-40 kha) [NV, still to cross-check with the SAA in the other file].

### 1.2 Departments (ha, RPG) [V]

**Lentil**: the centre of gravity moves from Puy/Berry to Champagne-Bourgogne.

| Dept | 2015 | 2017 | 2019 | 2021 | 2024 | Parcels 2024 |
|---|---|---|---|---|---|---|
| 10 Aube | 1,340 | 2,256 | 2,652 | 3,329 | **3,838** | 623 |
| 43 Haute-Loire (AOP Puy) | **4,113** | 3,846 | 3,416 | 2,555 | 2,680 | 1,902 |
| 51 Marne | 398 | 1,508 | 1,979 | 2,587 | 2,596 | 358 |
| 89 Yonne | 1,150 | 2,370 | 2,877 | 2,711 | 2,495 | 402 |
| 36 Indre (Label Rouge Berry) | 2,928 | **5,461** | 3,987 | 2,534 | 1,839 | 182 |
| 85 Vendée | 652 | 1,098 | 1,466 | 1,515 | 1,551 | 233 |
| 32 Gers | 771 | 1,770 | 2,824 | 2,650 | 1,101 | (peak 3,203 in 2020) |

- Haute-Loire: -35% area and -39% parcels (3,101 to 1,902) between 2015 and 2024; small parcels (~1.4 ha on average). Indre: -66% since the 2017 peak. Gers: -66% since the 2020 peak [V]. Hypotheses to validate with mentors: bruchids, 2021 yields (see `ideas2_4_time_series.md`) and contract exits [NV].
- Departments with ≥100 ha of lentil: 23 (2015), 41 (2019), 49 (2024). The top 5 goes from 60% to 39% of the area: lentil has become less concentrated [V].

**Chickpea**: it settled in and moved northwest.

| Dept | 2015 | 2017 | 2019 | 2022 | 2024 |
|---|---|---|---|---|---|
| 32 Gers | 503 | 2,994 | 5,325 (2018) / 5,253 | 2,751 | **4,310** |
| 16 Charente | 107 | 1,687 | 4,282 | 1,758 | **3,469** |
| 17 Charente-Maritime | 145 | 587 | 1,820 | 1,403 | 2,915 |
| 85 Vendée | **6** | 89 | 521 | 362 | **2,324** |
| 79 Deux-Sèvres | 9 | 227 | 931 | 692 | 1,282 |
| 86 Vienne | 0 | 44 | 510 | 200 | 753 |
| 30 Gard | 1,422 | 1,643 | 2,058 | 798 | 816 |

- National: boom 2015-2019 (×4), fall of 56% to 2022, rebound to 27.5 kha in 2024. Vendée went from 6 ha to 2,324 ha: a concrete sign of northward expansion (Poitou-Charentes / Pays de la Loire) [V].

**PHS (dry, for human food, 2023-24)**: Vendée 2,085 ha, Eure-et-Loir 1,773, Côtes-d'Armor 948, Loiret 902, Morbihan 846 (2024) [V]. It is the only RPG code that explicitly says "alimentation humaine" (human food).

**Protein pea**: Charente-Maritime, Oise, Marne, Eure-et-Loir, Aisne lead (5-8 kha each in 2024). Yonne falls from 17,800 ha (2020) to 5,367 (2024) [V]. The national trend is down (201 kha in 2020 to 124 kha in 2024), consistent with "pea area falling".

### 1.3 Rotations (what precedes and follows lentil and chickpea) [V]

Method: for each parcel of the target crop in year t, an interior point of the parcel, and I look for which RPG parcel contains it in t-3…t+3 (point-in-polygon). Two extracts with **all** parcels, 2015/2016-2024:

**A. Le Puy basin (Haute-Loire), bbox 3.75-3.95 E / 44.95-45.10 N**: ~13,000-14,000 parcels/year; lentil from 766 ha (638 parcels) in 2015 to 548 ha (405) in 2024. 5,269 parcel-years of lentil.
- Previous crop: winter soft wheat 30%, winter barley 20%, temporary grassland 14%, silage maize 6%, legume-grass mixture 5%, permanent grassland 4.5%. By group: **cereal 58%, grassland 25%**, maize 6%, pulse 0.5%.
- Following crop: **soft wheat 66%**, winter barley 10%; cereal 85%.
- Return of lentil to the same spot: 0.4% the following year, 7% after 2 years, 13% after 3; 77% with no lentil in the previous 3 years.
- Most frequent sequences (BTH = winter soft wheat, ORH = winter barley, PTR = temporary grassland): BTH > ORH > [LEC] > BTH (421), BTH > BTH > [LEC] > BTH (269), PTR > PTR > [LEC] > BTH (218), LEC > BTH > [LEC] > BTH (147).
- Reading: Puy lentil comes after cereals or after breaking up grassland, and it is almost always followed by wheat. The 2-year return (7%) goes against the usual 5+ year recommendation for Aphanomyces [NV for the agronomic rule].

**B. Charente / Deux-Sèvres (densest chickpea area), bbox -0.2-0.0 E / 45.90-46.05 N**: ~6,600 parcels/year; chickpea from 240 ha (2016) to 956 ha (2019), 381 ha (2022), 933 ha (2024). 1,134 parcel-years.
- Previous: soft wheat 47%, winter barley 25%, durum wheat 6%, spring barley 5%, sunflower 3%. Cereal 87%, pulse 4%.
- Following: soft wheat 64%, durum wheat 11%, sunflower 4%. Cereal 82%.
- Return: 90% with no chickpea in the previous 3 years; 5% at 2 years.
- Sequences: BTH > ORH > [PCH] > BTH (126), TRN > BTH > [PCH] > BTH (117), CZH > BTH > [PCH] > BTH (65).

Rotation gotchas: (1) the RPG only covers parcels declared to the CAP (1-1.5% of points fall outside the RPG the following year); (2) geometry changes between years; (3) double crops in `culture_d1/d2`, which I did not use.

### 1.4 RPG idea seeds
- Map of territorial dynamics by commune/dept (chickpea expansion to the north, collapse of Puy and Berry) for cooperatives and the interprofession.
- Landscape variables for bruchid risk: previous year's lentil area within ≤2 km (the INRAE data paper already calculates them from the RPG, see `idea3_bruchids.md`).
- Labels to map pulses with Sentinel-2 before the RPG comes out (the RPG for year N is published around September of N+1: the 2025 files are dated 11/09/2026) [V].

## 2. RPG 2025 (v4.0): new fields `precision` and `bio`

- **Access**: 7z download only. National GPKG = 3 parts (4.29 + 4.29 + 2.35 GB). Regions: Île-de-France 94 MB, Corse 88 MB, Centre-Val de Loire 482 MB, Auvergne-Rhône-Alpes 1.7 GB [V]. I downloaded Île-de-France.
- **Contents** [V]: `RPG_Parcelles.gpkg` (125,212 parcels in IdF, EPSG:2154), `RPG_Ilots.gpkg`, `RPG_SNA.gpkg` (non-agricultural areas), `RPG_ZDH.gpkg` (hedge densification zones [NV]).
- **Columns** [V]: `id_parcel, surf_parc, cat_cult_p, code_cultu, code_group, precision, gcp, pp, bio, iae`. Missing: `precision` 9.6%, `cat_cult_p`/`pp` 4.9%.
- **`bio` (boolean)**: 7.8% of IdF parcels; for pulses it is much higher: lentil 61% organic, chickpea 75%, PHS 57%, winter féverole 40%, spring pea 3% [V]. In other words, IdF lentil and chickpea are mostly organic (human food).
- **`precision`**: crop sub-code. PHS has 001 and 002, PHF 001-003, PHI 001-002 [V]. From the RPG Bio (below) I know that in PHS 001 = dry bean and 002 = **dry pea (pois cassé, split pea)**, and PHI/PPR 001 = "alimentation animale" (animal feed) [V for Bio 2023]. The meaning of `precision` in the general RPG 2025 (and whether PHI 002 = pea for human consumption) is [NV]: the 2025 Telepac notice (instructions) needs to be read.
- Pulses in IdF 2025 [V]: féverole (faba bean) 8,656 ha (FVL+FVP), spring pea 4,064, winter pea 1,933, lentil 1,095 (178 parcels), PHF 935, MPC 460, PHS 206, chickpea 76, soybean 2,308.

## 3. RPG Bio (parcels in organic farming declared to the CAP)

- **URL**: https://www.data.gouv.fr/datasets/parcelles-en-agriculture-biologique-ab-declarees-a-la-pac. Agence Bio, LO 2.0, updated 29/10/2026 [V].
- **Coverage**: 2019-2023 national and by region (GPKG/SHP/GeoJSON). National ~240-490 MB/year [V]. According to the description, 80-85% of organic parcels (not all claim CAP aid) [F].
- **Sample**: Centre-Val de Loire 2023, 34,573 parcels, EPSG:2154 [V].
- **Columns** [V]: `gid, millesime, code_culture, precision_culture, lbl_culture, grp_culture, surface_ha, code_commune_insee, lbl_commune, code_epci, code_departement, code_region, zone_geo`. No missing values except `precision_culture` (7.9%). **It carries INSEE commune and dept**: it joins with Agreste without a spatial join.
- **`lbl_culture` disambiguates the destination** [V]: PHI 001 "Pois protéagineux d'hiver (alimentation animale)" (winter protein pea, animal feed), PPR 001 "(alimentation animale)", PHS 001 "Haricot sec et demi-sec (flageolet, coco, lingot…)" (dry and semi-dry bean: flageolet, coco, lingot), PHS 002 "Pois cassé (pois sec)" (split dry pea), PHF 001-003 green bean / garden pea / snow pea.
- Organic pulses in Centre 2023 [V]: lentil 198 parcels / 1,020 ha, chickpea 40 / 256 ha, féverole 453 / 2,267 ha, MPC 533 / 3,083 ha, PHS 60 / 327 ha (45 dry beans, 15 dry pea).
- **Relevance 8**: it is the only open source with an explicit destination (human vs animal) per parcel, and with commune.

## 4. Theia OSO (Land cover, "Occupation des Sols")

- **Owner**: CNES + CESBIO, iota² chain (Random Forest trained on RPG, BD TOPO, etc.) [F]. License Etalab 2.0 [V on Recherche Data Gouv].
- **Coverage**: mainland France, 10 m, 2016-2023 [V: files OSO_2016…2023 at doi:10.57745/UZ2NJ7, 5.0-5.7 GB each].
- **Nomenclature of 23 classes since 2018** [F, Planet/Sentinel Hub docs]: 5 oilseeds, 6 straw cereals, **7 protéagineux (féverole/pois)** (protein crops: faba bean/pea), 8 soy, 9 sunflower, 10 maize, 11 rice, 12 tubers, 13 grasslands… There is a 30-class version since 2020 with more agricultural classes [F]. 2016-2017 use 17 classes.
- Limitation: it does not separate lentil or chickpea; it is a product of a classifier trained on the RPG, so it adds no new information about declared parcels. Useful as a baseline for "how well protein crops are detected from satellite".

## 5. Sentinel-2 (access tested)

- **Microsoft Planetary Computer** [V]: STAC `https://planetarycomputer.microsoft.com/api/stac/v1`, collection `sentinel-2-l2a`, anonymous SAS token (`/api/sas/v1/token/sentinel-2-l2a`), no account. Test: a RPG 2024 lentil parcel of 16.42 ha near Le Puy (44.948 N, 3.893 E), tile 31TEK. With cloud cover <40%, 14 scenes between February and September 2024; 1,637 pixels of 10 m inside the polygon (= 16.37 ha, matches `surf_parc`). COG window reads in seconds.
- **Gotcha** [V]: with raw DNs, the NDVI of this lentil gives 0.01 in March and a maximum of 0.38 at the end of August. It is too low: since baseline 04.00 (January 2022), L2A products carry a +1000 offset that has to be subtracted by hand on PC [F]. The `sentinel-2-c1-l2a` collection on Earth Search is already harmonized [F].
- **Earth Search (Element84)** [V]: STAC `https://earth-search.aws.element84.com/v1`, `sentinel-2-c1-l2a`, public HTTPS assets on S3 us-west-2, no account or token.
- **Copernicus Data Space (CDSE)** [V]: STAC `https://stac.dataspace.copernicus.eu/v1` searches without login, but the assets are `s3://eodata/...` (they need CDSE S3 credentials).
- Sentinel-1 (radar, useful under clouds) is on the same platforms [NV].
- **Relevance 8 as an input**: the labels come from the RPG (≥8,000 lentil parcels per year since 2017).

## 6. Crop classification benchmarks

- **PASTIS / PASTIS-R** [V]: Zenodo record 5012942, `PASTIS.zip` of 28.76 GB, CC-BY 4.0. 2,433 S2 patches from 4 French tiles, labels from the RPG 2019 [NV for these figures]. **18 classes** (verified on the nomenclature image in the repo): grassland, winter soft wheat, maize, winter barley, rapeseed, spring barley, sunflower, grapevine, sugar beet, triticale, durum wheat, fruit/vegetables/flowers, potato, **forage legumes (3,174 parcels)**, **soy (1,212)**, orchards, mixed cereal, sorghum. **There is no pea, féverole, lentil or chickpea**: they fall into "void" or background. Useful as a format model (and for pretrained models), not as a pulse dataset.
- **EuroCrops** [V partial]: lookup table on Zenodo (13951976) with 2,979 rows; it has HCAT classes `lentils`, `chickpeas`, `peas`, `beans`, `sweet_lupins`, and maps French labels ("Cultivated lentil (not fodder)" to lentils, "Faba bean sown before 31 May" to beans) [V]. France is RPG 2018 [F]. Useful only if you want to compare with other countries.
- **Sen4AgriNet** [NV]: Catalonia 2019-2020 and France 2019, FAO ICC nomenclature (~168 classes). I could not confirm the French coverage or the pulse classes.
- **AI4Boundaries** [NV]: parcel boundaries (includes France from the RPG) with monthly S2 composites; no crop type.
- **BreizhCrops** [NV]: Brittany 2017, 9 classes, no grain pulses.
- **HRL Crop Types (Copernicus)** [F]: 17 classes, 10 m, 2017-2021 published in May 2025; whether it has a pulse class [NV]. **JRC EU Crop Map 2018** [F]: "dry pulses, vegetables and flowers" in a single class.

## 7. Soil

### 7.1 SoilGrids 2.0 (ISRIC)
- CC-BY 4.0, 250 m, 6 depths, mean + quantiles. Properties: pH (H2O), clay, sand, silt, SOC, CEC, N, bulk density, coarse fragments [F].
- **Access** [V]: (a) REST `rest.isric.org/soilgrids/v2.0/properties/query` (beta; with 3 consecutive queries it returned an empty response, rate limit [V]); (b) public VRT/COG `files.isric.org/soilgrids/latest/data/<prop>/<prop>_0-5cm_mean.vrt` in Homolosine projection (int16, pH×10), readable with rasterio `/vsicurl/` without an account [V].
- Samples at 0-5 cm [V]: Haute-Loire lentil parcel pH 6.2, clay 20.6%, SOC 50 g/kg; Marne (Champagne crayeuse, chalky Champagne) pH 7.4, clay 25%; Beauce pH 6.6, clay 26.8%. In Auch and Le Puy (urban area) it returns null.
- **CaCO3/carbonate (calcáreo) is missing**, the key variable for lupin (which does not tolerate lime) and one that favours chickpea and lentil. For that: ESDB/BDGSF or BDAT.

### 7.2 BDAT (Base de Données d'Analyses de Terre, soil analysis database), GIS Sol / INRAE Infosol
- doi:10.15454/SVDTOU: statistics (n, mean, median, quartiles, deciles) of **water pH, KCl pH, total CaCO3, active lime, clay, silt, sand, C, N, P, K…** by canton (pre-2014; cantons are French administrative units), PRA (petite région agricole, small agricultural region), department and region, periods 1990-94 … 2010-14 [V readme]. ~3.6 million lab analyses [F].
- **Access** [V]: the 24 `.tab` files are **restricted** (HTTP 403, `restricted: true`). Only the readme is open. You have to request access through the Recherche Data Gouv form (uncertain delay). An open summary (doi:10.15454/NFQRRB, 2 `.ods` of ~4.6 KB) is national and not useful for mapping.
- Relevance 6: canton-level lime would be gold for lupin/chickpea suitability, but it is not open. Alternative: GIS Sol viewer (webapps.gissol.fr) [NV].

### 7.3 Others
- **RMQS** (16 km grid network, ~2,200 sites) on Recherche Data Gouv: several publications (microbiology, profiles with management practices doi:10.15454/AIQ9WS) [V list]. Far too sparse for a single parcel.
- **ESDB / BDGSF 1:1M and LUCAS topsoil 2018/2022** (JRC ESDAC): require a registration form [NV]. LUCAS has pH, CaCO3 and texture at ~20,000 EU points.

## 8. Crop suitability: GAEZ v4 (FAO/IIASA)

- **Access** [V]: public COGs at `https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/...` (you cannot list the bucket, you have to guess the name). EPSG:4326, 5 arcmin (~9 km), int16.
- **Crops** (tested with `suHr_<crop>.tif`, historical CRU-TS 1981-2010, high input, rainfed) [V]: `chk` chickpea, `pea` dry pea, `phb` dry bean, `pig`, `cow`, `soy` exist; `len`, `lnt`, `fab`, `fbn` do not. **I did not find lentil or faba bean**. The documentation mentions 51 crops [F].
- Suitability index values (0-10,000) [V]:

| Point | Chickpea | Dry pea | Dry bean | Soybean |
|---|---|---|---|---|
| Haute-Loire | 0 | 10,000 | 8,097 | 3,333 |
| Marne | 0 | 3,307 | 2,948 | 2,503 |
| Beauce | 0 | 7,131 | 7,131 | 3,920 |
| Gers | 7,776 | 7,776 | 7,547 | 5,325 |
| Lauragais | 8,586 | 8,586 | 8,569 | 6,368 |

- Reading: under the 1981-2010 climate, GAEZ says chickpea is not suitable north of the Loire. But the RPG shows chickpea in 80 departments in 2024, Vendée with 2,324 ha and Vienne with 753 [V]. There are versions with RCP scenarios for the 2020s-2080s [F] (exact paths [NV]). It is a good hook for a story about "climate migration of chickpea".
- License: CC BY-NC-SA 3.0 IGO [NV]. Watch out for commercial use.

## 9. Future and observed climate

- **DRIAS** (Météo-France, IPSL, CERFACS): DRIAS-2020 and EXPLORE2 (and TRACC-2023, 17 projections) at 8 km, daily, up to 2100 [F]. **Free but requires an account** (accept the terms); simplified access (full NetCDF) or personalized (cropping, CSV) [F]. On data.gouv there is only a record with a link (fr-lo) [V]. I did not download it (requires an account).
- **Climadiag Agriculture** (Météo-France + Solagro): ~300 agroclimatic indicators at 8 km for +2.0 °C (2030), +2.7 °C (2050), +4 °C (2100) [F]. Public examples are wheat, maize, rapeseed, sunflower, grapevine, potato; pulses [NV, not confirmed]. New indicators can be requested by email [F].
- **Météo-France base climate data** [V]: on data.gouv, daily (628 resources) and complementary stations (266), LO 2.0, updated 29/10/2026.
- **ERA5 / ERA5-Land** (CDS, account): redundant with Open-Meteo and SAFRAN, already audited in `ideas2_4_time_series.md`.

## 10. Irrigation and others

- **Irrigation** [NV]: RA 2020 (Recensement agricole 2020, agricultural census: irrigable/irrigated area by commune, with statistical secrecy) and BNPE (Banque nationale des prélèvements en eau, national water abstraction database: withdrawals by point). Low relevance: lentil, chickpea and pea are rainfed in France, except dry bean (haricot) [NV].
- **Corine Land Cover 2018** [NV]: class 211 (non-irrigated arable land) with no crop detail. Relevance 1.
- **ADMIN EXPRESS** (IGN) [V]: in the same WFS (`ADMINEXPRESS-COG.20xx:commune|departement`), to go from RPG to commune/dept. I used a departments GeoJSON (france-geojson) for the centroid join.

---

## Idea seeds

1. **Early map of human-food pulses from Sentinel-2 ("early RPG")** (high relevance, essential AI). The RPG arrives ~15 months after sowing (the 2025 one came out in September 2026). With RPG parcels 2017-2024 as labels (≥8,000 lentil and ≥5,000 chickpea per year) and S2 from Planetary Computer or Earth Search, one can estimate in June where and how much lentil/chickpea there is. **User**: cooperative / organisme stockeur (grain storage body) / Terres Univia. **Decision**: size collection, sorting (bruchids) and contracts before harvest. It chains with the yield forecast in `ideas2_4_time_series.md` (area × yield = supply). **Risk**: PASTIS shows that pulses are almost absent from benchmarks, so there is no pretrained model (an opportunity and also a risk).
2. **"Where to add pulses?": parcel/commune recommender for contracts** (high relevance). Combines the parcel rotation history (RPG: cereal before, return ≥5 years), soil (SoilGrids pH/clay, lime if BDAT is obtained), suitability (GAEZ) and future climate (DRIAS). **User**: cooperative technician who has to go from 1.6% to 8-10%. **Decision**: which producers to offer a lentil/chickpea contract to, and on which parcel. The AI contributes the learning of "which similar parcels already grew pulses" (positive-unlabeled on RPG).
3. **Radar of chickpea migration and lentil decline** (medium-high relevance, very demonstrable). Verified facts: chickpea in Vendée from 6 to 2,324 ha (2015-2024); historical GAEZ says "not suitable" north of the Loire; Puy lentil -35% and Berry -66% since 2017. **User**: Region / DRAAF / interprofession. **Decision**: where to invest in the supply chain (silos, sorting, processing). The AI part is weaker: it needs a predictive component (where chickpea will appear next year).
4. **Bruchid risk at landscape scale** (complements `idea3_bruchids.md`). Density of previous year's lentil/faba bean within a 2 km radius, computed from the RPG for each parcel in France, plus climate. **User**: collector. **Decision**: which lots to prioritize for sorting or for human vs animal destination. Limitation: the bruchid dataset has no fine coordinates (see that file).
5. **Tracing the "alimentation humaine" destination per parcel** (enabler). The RPG 2023+ (PHS), the RPG 2025 (`precision`, `bio`) and the RPG Bio (`lbl_culture`) make it possible to separate dry pea for humans from forage pea and to measure the organic share (61% of IdF lentil in 2025). It serves as a project impact metric ("ha of human-food pulses by dept").

## Cross-cutting gotchas

- The RPG 2022 geometry is called `the_geom`; the other years, `geom`. In the CQL BBOX, use lat/lon.
- Codes that appear and disappear (HAR/PPO up to 2022, PHS/PHF/FVP from 2023): normalize by groups before building series.
- `surf_parc` has values of 0 and 0.01 (tiny parcels or fragments): filter them before computing means.
- The RPG only covers what is declared to the CAP: it does not include producers who do not claim aid (relevant for horticulture and some organic land).
- Sentinel-2 on Planetary Computer: subtract the 1000 offset from 2022 onward before computing indices.
- SoilGrids REST has a rate limit: for many parcels, use the VRT/COG files.

## Cleanup

Downloaded data was kept in the scratchpad (`.../scratchpad/ds_geo/data/`) and deleted at the end. Exploration scripts are in `.../scratchpad/ds_geo/scripts/` (`rpg_pulses.py`, `rpg_dept.py`, `rpg_bbox.py`, `rotation.py`, `s2test.py`, `soilgrids.py`, `gaez.py`).
