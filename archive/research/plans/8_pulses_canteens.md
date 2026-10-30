# Dossier Idea 8: "French pulses in canteens" (provisional name: **LotLégume**). Track 2, bridge to Track 3

Dossier prepared on 30/10/2026, before the start of the event. Desk research and data exploration only: downloads, counts, joins, API tests, keyword searches and manual inspection of samples. **The LLM pipeline, the optimiser, the demo and the deck were not built.** All of that is done during the event.

Marks: **[V]** verified by me today on the data, the API or the open primary source; **[F]** read in a source (secondary, search engine snippet or primary source not reopened); **[NV]** not verified: my calculation, assumption or hypothesis.

Audit scripts: `scratchpad/plan8/scripts/` (mc.py, mc2.py, d1-d6.py, b1.py, b2.py, ccp.py, crpm.py). Data downloaded to `scratchpad/plan8/data/` and **deleted at the end** (see the end).

---

## 1. Summary in 5 lines + verdict

1. **Problem:** canteens serving more than 200 meals/day are legally required to submit a multi-year protein diversification plan (CRPM art. L230-5-4) [V], but no public data measures whether they do (Ma Cantine asks the question and does not publish the answer) [V], and in public tenders pulses are almost invisible: only ~4% of food purchase notices have a lot naming pulses, and of 84 "épicerie/féculents" lots only 4 mention them [V, BOAMP 2025 sample].
2. **User:** the purchasing manager ("responsable achats / économe") of a **public central kitchen** with its own tender (1,955 central kitchens supply satellites that add up to >200 meals/day) [V, Ma Cantine register].
3. **Solution:** (a) an LLM pipeline that structures the lots of BOAMP notices (eForms) and contracts from DECP for food and shows the buyer how they buy compared with their peers (separate pulse lot or not, organic/SIQO, "approvisionnements directs" criterion, holders, distance); (b) a generator of **lot structure and legal clauses** anchored (RAG) on the CNRC "légumineuses" livret of June 2026 and on the Code de la commande publique, with a verifier that blocks "origine France" (prohibited by R2111-7) [V]; (c) a quantified diversification plan (tonnes of pulses/year, cost, Agribalyse CO2, CIQUAL nutrition) and the map of nearby French supply (RPG, Agence Bio, DECP holders).
4. **Why it is not Ardoise:** Ardoise (1st place 2025) generates weekly **menus** with CP-SAT over 121 own recipes and displays Ma Cantine badges [V, repo]; it does not touch purchasing, lots, clauses or origin/agricultural supply. Here the object is the **public procurement** and the bridge to the French supply chain.
5. **Business:** SaaS for central kitchens (price anchors of catering software paid by local authorities in DECP: ~6-10 k€/year [V]) and, above all, financing from the sector/territory (Départements, PAT, Terres Univia/SNPV) that want to channel public demand towards French pulses.

**Verdict: NO-GO as the main idea; good plan B for Track 2.** Estimated score **6.2/10** vs 6.4 for idea 1 (section 12). Strengths: it fits literally the context the jury already knows ("few digital tools to help them develop this plan"), first-class open data, realistic demo. Weaknesses: (i) the data that would make the LLM shine (line-level pulse purchase detail, BPU/DQE) is not in open data, only in each buyer's DCE; (ii) the CNRC already published clause templates for pulses in June 2026, which lowers the novelty of the "clauses" part; (iii) same user family as the 2025 winner, the jury will compare; (iv) the payer is weak (small budgets, free public tools).

---

## 2. Problem, concrete user and decision

### The legal framework (verified in the text of the CRPM and the Code de la commande publique)

| Obligation | Text | Since | Status |
|---|---|---|---|
| ≥50% by value of "durable and quality" products, of which ≥20% organic | CRPM L230-5-1 I [V, text via the Légifrance HF dataset, version in force since 25/08/2021] | 1/1/2022 (public); 1/1/2024 private [V, Ma Cantine key-measures.json] | [V] |
| Eligible categories include 1° environmental externalities (life cycle) and **1° bis "performances en matière de protection de l'environnement et de développement des approvisionnements directs"** (environmental performance and development of direct supply), organic, SIQO (Label Rouge, AOP/AOC, IGP, STG), HVE (certification level 2 only until 31/12/2026), fair trade, RUP, fishery ecolabel | L230-5-1 I [V] | | [V] |
| ≥60% durable and quality in meat and fish (100% in State catering) | CNRC livret légumineuses 2026 and EGalim bilan 2025 [V] | 1/1/2024 [V event guide; F bilan] | [V] |
| **Multi-year protein diversification plan** "incluant des alternatives à base de protéines végétales" (including alternatives based on plant proteins), submitted to the governing body | CRPM L230-5-4: "Les gestionnaires des restaurants collectifs servant plus de deux cents couverts par jour en moyenne sur l'année sont tenus de présenter à leurs structures dirigeantes un plan pluriannuel..." [V] | 30/10/2018; company catering 1/1/2024 [V, Ma Cantine] | **No minimum content, no sanction, no publication** [V, text] |
| Weekly vegetarian menu in school catering (public and private) | CRPM L230-5-6 I [V] | 1/11/2019 [V, Ma Cantine] | 96.7% comply among 11,730 schools that responded [V, bilan 2025] |
| Daily vegetarian option in State catering with choix multiple | Loi Climat et résilience n° 2021-1104 of 22/08/2021 [V] | 1/1/2023 [V] | 65.8% comply among 680 respondents [V] |
| No control or sanction of supply obligations | "La loi ne prévoit pas de contrôle ou sanction concernant les obligations d'approvisionnement" (the law does not provide for any control or sanction concerning supply obligations) [V, EGalim bilan 2025 p. 6] | | [V] |

**Can "French origin" be required in a public tender? No.** Code de la commande publique R2111-7: "Les spécifications techniques ne peuvent pas faire mention ... d'une provenance ou origine déterminée ... lorsqu'une telle mention ... est susceptible de favoriser ou d'éliminer certains opérateurs" (technical specifications may not mention a determined provenance or origin where such a mention is likely to favour or exclude certain operators) (unless justified by the subject matter, with "ou équivalent") [V]. The CNRC guide to direct management purchasing (update January 2024) says it explicitly: "la préférence géographique (« localisme ») est interdite dans les achats publics" (geographic preference ("localism") is prohibited in public purchasing), with the risk of the favouritism offence (art. 432-14 penal code) [V, p. 14].

**Legal levers that do exist** [V unless stated]:
1. **Allotissement** (lotting, L2113-10: markets must be split into separate lots unless indivisible; the buyer sets the number, size and object of the lots) [V]. A small lot "légumineuses sèches et appertisées" (dry and canned pulses) lets in cooperatives and légumeries (vegetable processing plants).
2. **SIQO** (quality signs): AOP Lentille verte du Puy, IGP Lentilles vertes du Berry, IGP Haricot tarbais, Label Rouge lentilles vertes, etc. [V, INAO référentiel, prior research]. SIQO is legal even though it de facto implies an area, because it is a quality sign, not a geographic criterion. Note: Label Rouge is open to any origin [V, CNRC guide p. 17].
3. **Category 1° bis "approvisionnements directs"** (direct supply): the **CNRC "légumineuses" livret (June 2026, version for buyers subject to the CCP)** proposes weighted criteria: price 20%, environmental performance 30% (no mineral fertilisation, no desiccants, rotation, IAE, plastic reduction...), direct supply 25% (0 or 1 intermediary between producer and buyer; link with a PAT; chain within the same production basin), technical 25%, and a **bonus of ≤10%** for fair remuneration of the producer (bi/tripartite contracts) [V, PDF]. The definition of direct supply is "achat ... directement auprès du premier metteur en marché de ce produit, ou auprès du premier acheteur" (purchase ... directly from the first placer on the market of this product, or from the first buyer) [V].
4. **Prior sourcing** with suppliers of any origin, respecting equal treatment [V, CNRC guide II.3].
5. **Lots reserved** for ESAT/entreprises adaptées (sheltered-employment bodies) (they appear in DECP as "lot réservé EA et ESAT") [V].
6. **Free access to the DCE**: the tender documents are made freely available to operators (R2132-2) [V, text in the 09/2025 dataset version; the 40 k€ threshold may have changed with decree 2025-1386, see below].
7. **Thresholds:** the advertising and competition exemption for supplies rises from 40 k€ to **60 k€ excl. VAT from 1/4/2026** (decree 2025-1386 of 29/12/2025) [F, several legal sources via search engine]. DECP mandatory for markets ≥40 k€ excl. VAT (R2196-1) [V, text of 09/2025; check whether it was updated to 60 k€].

### User

- **Primary:** purchasing manager of a **public central kitchen under direct management** (commune, intercommunal syndicate, caisse des écoles, département for colleges, région for lycées, hospital). Examples already tendering pulses in their own lot: Ville de Nantes (lots "légumes secs bio", "légumes secs bio surgelés", "produits élaborés à base de légumes secs bio réfrigérés", BOAMP 2025) [V]; Cuisine centrale des lycées de Toulouse ("céréales / légumineuses bio") [V]; Département de l'Hérault (lot 23 "légumineuses précuites, blanchies bio", €1.55-1.64M, holder Agriviva 6 km away) [V, DECP].
- **Segment size [V, Ma Cantine register 30/10/2026]:** 66,353 restaurants; 16,616 with >200 meals/day; 38,258 satellites depend on 3,849 central-kitchen SIRETs, of which **1,955 add up to >200 meals/day**, 734 >1,000 and 148 >5,000. In the 2024 télédéclaration campaign 1,540 central kitchens declared [V].
- **Secondary:** (i) the **filière** (supply chain): cooperatives and légumeries that win pulse lots (Cavac, Unisvert, Norabio, Coopérative Bio d'Île-de-France, Manger Bio Sud-Ouest / Pays de la Loire, Agriviva) [V, DECP]; (ii) the **territory**: PAT (local food projects), Départements (Agrilocal), Terres Univia (co-chaired the CNRC "légumineuses" working group) [V].

### Decision they make

| When | Decision | Information used today | Cost of getting it wrong |
|---|---|---|---|
| Renewal of the framework agreement for foodstuffs (typically every 1 to 4 years; DECP: dureeMois) | **How to lot** (separate pulse lot or inside épicerie?), which criteria and weightings, which SIQO to ask for | Previous specification copied, CNRC guides in PDF, informal sourcing | Single "épicerie" lot → won by a national wholesaler (Pomona Episaveurs, Pro à Pro, Transgourmet win most pulse contracts [V]) and the origin stays invisible for 3-4 years; "origine France" clause → annulment and criminal risk |
| Each year (Ma Cantine télédéclaration, January-March) | What to declare in the diversification section; update the multi-year plan | Nothing structured | "Paper" plan with no quantified trajectory |
| Design of the food plan | How many dishes based on pulses, which forms (dry, canned, 5th range) | CNRC recipe books, PNNS (pulses ≥2 times/week [F, Réussir 2021 citing PNNS]) | Diner rejection, extra cost, waste |

---

## 3. Hypotheses

| # | Hypothesis | Type | Status | Evidence | If false |
|---|---|---|---|---|---|
| H1 | The diversification plan obligation exists, applies to >200 covers/day and has no content or sanction | Legal | **[V]** | Text of L230-5-4 in force since 1/1/2024; bilan 2025: no control or sanction | n/a |
| H2 | There is no public data on who has a diversification plan | Data | **[V]** | The Ma Cantine model has `has_diversification_plan`, `diversification_plan_actions`, `vegetarian_menu_bases` (GRAIN = "céréales et/ou légumes secs") [V code], but the télédéclaration open data only has `ratio_bio` and `ratio_egalim_hors_bio` [V schema]; the 2025 bilan gives no figure on plans [V grep]; the statistics API has no vegetarian field [V] | If it is published, better: it gets integrated |
| H3 | French origin cannot be required in a tender | Legal | **[V]** | R2111-7 + CNRC guide 2024 | n/a |
| H4 | Pulses are invisible at notice/contract level because they sit inside "épicerie" | Data | **[V]** | DECP food (CPV 03/15): 46,966 contracts, 241 with explicit pulses (0.5%), 2,689 with "épicerie"; BOAMP 2025 sample of 300: 4% of notices have a lot naming pulses; of 84 épicerie/féculents/produits secs lots only 4 name pulses | Already assumed: the detail is in the BPU/DQE of the DCE, not in open data |
| H5 | DCEs can be downloaded without an account | Data | **[V] partial** | R2132-2 (free); e-marchespublics offers "accéder au dossier de manière anonyme" (anonymous access to the file) [V on one page]; other profiles (marches-publics.info) require login [V URL `dematEnt.login`] | For the demo: 3-5 DCEs downloaded by hand on Friday; real product: the buyer uploads its own DCE |
| H6 | There is an upward trend in pulse lots | Market | **[V] weak** | DECP contracts with explicit pulses by notification year: 7 (2019), 20, 28, 22, 25, 46 (2024), 51 (2025), 37 (2026 to Oct.) [V] | Count as a signal, not as proof (DECP coverage changes by year) |
| H7 | Central kitchens that tender are identifiable in DECP | Data | **[V]** | Join by SIREN: 447 of 1,540 central kitchens TD 2024 appear as DECP buyers; 381 with 03/15 contracts; 206 with "épicerie"; 51 with explicit pulse lot | Benchmark only on that subset (~25%) and say so |
| H8 | Pulses in collective catering are few and mostly canned | Market | **[V]** | OléoProtéines 2025 (GIRA, panel of 7 distributors covering ≥50% of RHD value): dry 4,900 t (76% collective), canned 18 kt (82% collective), frozen 1,500 t (63% collective), 2024 | n/a |
| H9 | Most pulses in canteens are not French | Market | **[NV]** | I found no origin study in collective catering [V search]. Proxy: lentil imports ~40 kt/year, bean canning 30-36 kt/year [V, prior research Comext] | If they already were French, the value shifts to "trace and declare" (Ma Cantine's 2026 campaign adds a focus on origin [F]) |
| H10 | A buyer would pay for this | Business | **[NV]** | They spend on catering software: Grand Cubzaguais €25.8k/48 months; Cherbourg €41k/48 months; Région Hauts-de-France €1.31M/36 months for Easilys for lycées [V, DECP] | Pivot: payer = Département/PAT/filière (territorial licence) |
| H11 | The LLM beats keyword search at structuring lots | AI | **[NV], test Friday** | Keyword finds explicit pulses well; the LLM must add product family, form, criteria, SIQO, reservation, normalisation | If it does not beat it: present the LLM only for RAG clauses and keep regex for detection |
| H12 | The CNRC livret 2026 is a sufficient base to generate clauses | AI/legal | **[V]** exists, 34 p., with tables of criteria, tests and weightings | If the jury says "it already exists": our value is applying it to the buyer's case (lots, volumes, nearby supply), not the text |
| H13 | There is French supply near most buyers | Track 3 | **[V] partial** | RPG 2024: lentil 34,226 ha, chickpea 27,491 ha, pois/haricots secs AH 12,379 ha; 49 depts with ≥100 ha of lentil [V, prior research]; Agence Bio API: 126 organic operators matching "lentilles" in dept 43 [V] | Show real distance; some territories have no supply |
| H14 | Meat savings finance quality (60% meat EGalim) | Economics | **[NV]**, calculate on Friday with RHD prices | RHD 2024 prices for dry lentil €2.93/kg conv, €4.23 organic; canned €1.24 / €2.76 [V OléoProtéines] | If it does not close, show honest net cost |

---

## 4. Datasets (verified audit)

### 4.1 Ma Cantine: national canteen register
- **URL:** https://www.data.gouv.fr/datasets/registre-national-des-cantines/ (id 6482def590d4cf8cea3aa33e). Direct CSV: `https://cellar-c2.services.clever-cloud.com/ma-cantine-egalim-prod/media/open_data/registre_cantines.csv` (7.99 MB, updated 30/10/2026 01:01) [V].
- **Licence:** Licence Ouverte 2.0 [V, prior research].
- **Size/columns [V]:** 66,353 rows, 63,526 distinct SIRETs; 33 columns: `id, name, siret, siren_unite_legale, city, city_insee_code, postal_code, epci, epci_lib, pat_list, pat_lib_list, department, region, economic_model, management_type, production_type, central_producer_siret, groupe_id, daily_meal_count, yearly_meal_count, sector_list, line_ministry, declaration_donnees_2021..2025, active_on_ma_cantine, creation_date, modification_date`.
- **Counts [V]:** production_type: `site_cooked_elsewhere` 38,258 (satellites), `site` 26,211, empty 1,884. **Central kitchens no longer appear as their own rows**: they are rebuilt by grouping satellites by `central_producer_siret` (3,849 SIRETs; 1,955 with >200 meals/day summed; median 210). Declared meals/year: 2,522 million (4,286 rows with 0 or empty); with >200/day: 16,616 sites and 1,707 M meals/year; public 1,721 M, private 764 M.
- **Gotchas:** declarative figures, not cleaned; the sum of daily satellite meals does not prove the central kitchen is the buyer (the commune may be the buyer); `groupe_id` is new and not documented in the changelog [V].
- **Friday command:** `curl -L -o data/registre.csv "https://cellar-c2.services.clever-cloud.com/ma-cantine-egalim-prod/media/open_data/registre_cantines.csv"`

### 4.2 Ma Cantine: télédéclarations
- **URL:** https://www.data.gouv.fr/datasets/resultats-de-campagnes-de-teledeclaration-des-cantines/ (id 6482ed2ee3f9ec5215b41828); `campagne_td_2024.csv` (last updated 22/02/2026). There is no 2025 data file [V].
- **Columns [V, JSON schema]:** 28, includes `teledeclaration_mode` (SITE / CENTRAL_ALL / CENTRAL_APPRO), `canteen_siret`, `canteen_satellite_canteens_count`, `teledeclaration_ratio_bio`, `teledeclaration_ratio_egalim_hors_bio`. **No diversification or vegetarian field.**
- **Counts 2024 [V]:** 21,592 declarations, 1,540 central kitchens; median organic 12.8%, EGalim excluding organic 18.0%.
- **Command:** `curl -L -o data/td2024.csv "https://cellar-c2.services.clever-cloud.com/ma-cantine-egalim-prod/media/open_data/campagne_td_2024.csv"`

### 4.3 Ma Cantine: source code and texts (RAG corpus)
- **Repo:** https://github.com/betagouv/ma-cantine [V]. Useful: `frontend/src/data/key-measures.json` (obligations, dates, who), `frontend/src/data/quality-labels.json` (EGalim labels), `data/models/diagnostic_volet_diversification.py` (diversification fields, plan action options: PRODUCTS, PRESENTATION, MENU, PROMOTION, TRAINING) [V].
- **Command:** `gh api repos/betagouv/ma-cantine/contents/frontend/src/data/key-measures.json --jq .content | base64 -d > data/key-measures.json`

### 4.4 DECP consolidated (contracts)
- **URL:** https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/ (id 608c055b35eb4e6ee20eb325), `decp.parquet` 255 MB, 29/10/2026; licence `lov2` [V].
- **Size [V]:** 3,358,206 rows, 1,880,261 `uid`; `donneesActuelles` True 2,153,886 / False 1,175,535 / null 28,785. 66 columns (buyer SIRET, category, coordinates; holder SIRET, NAF, distance; `objet`, `codeCPV`, `montant`, `montant_rationalise`, `dureeMois`, `considerationsEnvironnementales`, `origineFrance`, `idAccordCadre`...).
- **Food (CPV 03/15, latest version per uid) [V]:** 46,966 contracts, 3,188 buyers. `origineFrance` empty 76%; `considerationsEnvironnementales` empty 48% and "Sans objet" (not applicable) in 37% of those reported. Length of `objet`: median 70 characters (p10 25, p90 195).
- **Pulses [V]:** object with légumineuse/légumes secs/lentille (outside CPV 3x)/pois chiche or CPV 032122*: **241 contracts, 131 buyers, 105 holders**; buyers: communes 127, no category 55, intercommunales 21, départements 17, hospitals 14, régions 6. Median holder-buyer distance **43 km** (p25 15, p75 115). Top holders: Pomona Episaveurs 26, Pro à Pro 12+8+5, Soboriz (Réunion) 10, Royal Bourbon 10, Coop Bio IDF 7, Agriviva 7.
- **Amounts:** these are maximum framework-agreement values; `montant_rationalise` still has outliers (44 thousand M€ of "food" in 2026 is not credible) [V]. **Do not use sums of amounts as spending.** Real spending: use the EGalim bilan (section 8).
- **Join tested:** DECP buyer SIREN ↔ `canteen_siret` TD 2024 central kitchens: 447/1,540 [V].
- **Command:** `curl -L -o data/decp.parquet "https://static.data.gouv.fr/resources/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/20261029-052718/decp.parquet"` (the path changes with each publication: take it from `https://www.data.gouv.fr/api/1/datasets/608c055b35eb4e6ee20eb325/`). Takes ~2 min.

### 4.5 BOAMP (notices with lots, eForms) **[new, key]**
- **API:** `https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records` (opendatasoft; **you have to use `curl --compressed`**, otherwise it returns binary gzip) [V]. 1,722,243 notices [V]. Licence: [NV, check on the DILA sheet; assumed Licence Ouverte].
- **Fields [V]:** `idweb, dateparution, nomacheteur, objet, nature_libelle, type_marche, descripteur_libelle, criteres, titulaire, url_avis, donnees` (complete JSON string of the notice: eForms, FNSimple, MAPA, DSP).
- **Counts [V]:** notices with "denrées alimentaires" (foodstuffs): 2,075 (2022), 2,214 (2023), 1,990 (2024), 2,113 (2025), 1,579 (2026 to Oct.). Of these, with "légumes secs" 188-248/year, "légumineuses" 37-64/year, "épicerie" 444-619/year. Since 2025: 3,692 food notices, 2,541 market notices, 1,096 results; **527 (14%) mention "approvisionnements directs"**; "lentille verte du Puy" in 9 notices total; "légumes secs" + "label rouge" 153.
- **Sample inspected (300 market notices 2025) [V]:** 210 eForms with 1,214 lots (median 2, mean 5.8 per notice), 72 FNSimple, 14 MAPA, 4 DSP. Lots with pulses: 12 notices. Examples of lots: "céréales / légumineuses bio" (Toulouse lycées), "lot 8 - produits à base de protéines végétales" (Lycée La Pérouse), "légumes secs bio surgelés" (Nantes), "lentilles cuisinées" (FranceAgriMer). Words in the full notice: bio 85, ESAT/EA 40, circuit court (short supply chain) 23, origine 16, végétarien 8, label rouge 6, AOP 5, protéines végétales 4, IGP 2.
- **Key gotcha:** the lot description in eForms is extracted from `cac:ProcurementProjectLot > cac:ProcurementProject > cbc:Name/cbc:Description`; in FNSimple the structure is different (45 of 72 have something lot-like). The DCEs are linked (`cac:CallForTendersDocumentReference`, 207/300) on heterogeneous profiles.
- **Friday command (2,000-4,000 notices, <200 MB):**
  `curl -s --compressed -G "$B" --data-urlencode 'where=search("denrées alimentaires") and dateparution>="2024-01-01"' --data-urlencode limit=100 --data-urlencode offset=$OFF --data-urlencode order_by=idweb > boamp_$OFF.json` in a loop (max offset+limit 10,000 in the ODS API [NV]; if needed, use the `/exports/json` endpoint).

### 4.6 CNRC: guides and légumineuses livret (RAG corpus)
- **Methodological livret légumineuses, CCP buyers (34 p.)** and **non-CCP (26 p.)**, June 2026: `https://ma-cantine.agriculture.gouv.fr/static/documents/20260618_livret_methodologique_legumineuses_CCP.pdf` and `..._non_CCP.pdf` [V downloaded]. Content: definition of the family (dry pulses; raw and minimally processed products, canned, 4th/5th range), example of a tender regulation and CCTP, tables of environmental criteria and direct supply with scoring and proof elements, bonus ≤10%. **The PDF text has gaps when extracted with pdftotext** (fonts/vectors): for RAG the tables need OCR or manual review.
- **Practical guide to direct management purchasing (CNRC, update January 2024, 74 p.):** `https://ma-cantine.agriculture.gouv.fr/static/documents/Guide_Pratique_MP_Gestion_directe.pdf` [V]. Guide for service provision (Nov. 2021) [F].
- **Framework for the multi-year diversification plan (CNRC, 8/6/2021):** 5 categories of actions + example plan [F, Réussir 09/06/2021].
- Licence: public administration documents [NV on the exact licence]; use them as cited sources, do not redistribute.

### 4.7 Code de la commande publique and CRPM (legal text, RAG corpus)
- HuggingFace `louisbrulenaudet/code-commande-publique` (parquet 1.2 MB, lastModified 21/09/2025) and `louisbrulenaudet/code-rural-peche-maritime` (9.3 MB, 11/07/2025): Légifrance text per article with `num`, `texte`, `dateDebut` [V]. Note: 2025 snapshot, does not include decree 2025-1386; for the pitch cite Légifrance (which blocks automatic fetch: 404 to the bot) [V].
- **Command:** `curl -sL -o data/ccp.parquet https://huggingface.co/api/datasets/louisbrulenaudet/code-commande-publique/parquet/default/train/0.parquet`

### 4.8 EGalim statistical bilan 2025 and OléoProtéines 2025
- **EGalim bilan 2025 (2024 data, 95 p., 22/12/2025):** https://ma-cantine.agriculture.gouv.fr/static/documents/rapport-bilan-statistique-EGALIM_2025.pdf [V]. Table 1 (EY 2021 / GIRA 2018): 80,851 restaurants, 3,984 M meals/year (2,470 M public, 1,514 M private); school catering 1,422 M. Declared purchases 2024: €4,256M (organic 11.8%, EGalim 29.5-30.1%), total estimated purchases **€9.5 billion** (extrapolation of €7 billion in 2018 with inflation, "à considérer avec précaution" (to be treated with caution)) [V].
- **OléoProtéines 2025 (Terres Univia, 30 p.):** https://www.terresunivia.fr/fichiers/publications/oleoproteines-edition-2025.pdf [V]. RHD 2024 (GIRA, panel of 7 distributors, ≥50% of value, possible underestimate): dry 4,900 t / €14M (lentil 61% of volume; 76% collective; organic ~10%); canned 18 kt / €24M (82% collective; bean 51%, chickpea 26%, lentil 23%); frozen 1,500 t / €5.7M (63% collective). Wholesale prices 2024 (€/kg): dry lentil 2.93 conv / 4.23 organic; dry chickpea 2.97 / 3.97; dry bean 2.86 / 4.02; split pea 1.61 / 3.27; canned: bean 1.30 / 3.15, lentil 1.24 / 2.76, chickpea 1.39 / 3.33 [V].

### 4.9 CIQUAL 2025 and Agribalyse 3.2
- Audited in prior research [V there]; I re-verified Agribalyse today via `https://data.ademe.fr/data-fair/api/v1/datasets/agribalyse-31-synthese/lines?q=...` [V]: kg CO2e/kg: dry lentil 0.581 (green, brown, red identical: a single proxy, **no distinction France vs imported**), cooked lentil 0.466, drained canned lentil 1.13, dry chickpea 0.899, canned chickpea 2.2, dry white bean 0.448; raw beef steak mince 35.7, "haché à base de bœuf 15%" (minced, 15% beef) 17.5, raw pork tenderloin 6.58, frozen hake 7.85 [V].
- CIQUAL: protein of dry green lentil 25.1 g/100 g, chickpea 20.5 [V prior].

### 4.10 French supply
- **RPG by dept (2015-2024):** `archive/research/datasets/rpg_pulses_dept_year.csv` (8,336 rows: year, dept, group, plots, ha; groups `lentille, pois_chiche, haricot_flageolet, pois_haricot_secs_AH, feve, feverole, lupin...`) [V]. **Prior resource to declare** (aggregate built before the event).
- **Agence Bio API:** `https://opendata.agencebio.org/api/gouv/operateurs/?q=lentilles&departements=43&nb=50` → 126 operators [V]. Returns SIRET, activities, products, commune. **Privacy:** many are sole traders with a person's name: show only aggregates or the company name of cooperatives.
- **INAO SIQO** (data.gouv, 5,246 lines) [V prior].
- **DECP holders** that have already won pulse lots (with NAF and distance) [V].

### 4.11 What does NOT exist in open data [V]
- Pulse purchases per canteen, pulse origin in canteens, diversification plans per canteen, BPU/DQE of tenders (only in the DCE per buyer).

---

## 5. AI method

### 5.1 What each component does
1. **Lot extractor (LLM, Bedrock Claude or similar [NV availability: check on Friday in the AWS console]):** input = name + description of the lot (BOAMP eForms) or `objet` (DECP); output is JSON validated against a schema: `familia` (épicerie, F&L, meats, dairy, pulses, cooked dishes, mixed), `menciona_legumbres`, `tipos` (lentil, chickpea, bean, split pea, faba bean, processed plant protein), `forma` (dry, canned, frozen, 4th/5th range, processed), `bio`, `siqo` (list), `approvisionnement_direct`, `circuit_court`, `reservado_esat`, `criterios_ambientales`, `evidencia` (literal substring justifying each field). **Anti-hallucination rule:** each positive field must cite a substring present in the text; otherwise it is forced to false/unknown (deterministic check).
2. **Peer benchmark:** for the chosen buyer, compare with kitchens of its size class (Ma Cantine) and region: % that have a separate pulse lot, % that use the 1° bis category, % organic in pulses, median holder distance.
3. **Lot structure and clause generator (RAG):** retrieves passages from the CNRC légumineuses livret, CNRC 2024 guide and CCP/CRPM articles; proposes lot(s), criteria and weightings (starting point: CNRC table 20/30/25/25 + bonus ≤10%), each clause with a citation to the passage. **Deterministic legal lint** before display: regex over "origine France", "local", "département", "km", "région de production" in technical specifications → blocks it and proposes the alternative (SIQO, 1° bis, fine lot).
4. **Quantified diversification plan (LP optimiser, not an LLM):** variables = number of main pulse-based dishes per 20 meals per year (3 years), mix of types and forms; constraints: protein per dish (CIQUAL), PNNS frequency (≥2/week as a target [F]), budget (RHD prices OléoProtéines), acceptance (cap on annual increase, editable assumption); objective: CO2 (Agribalyse) or cost. Output: tonnes of pulses/year by type and form, € and CO2. **Difference with Ardoise:** we work at the level of annual purchase volume and lot, not the daily menu.
5. **Supply map:** RPG (ha by dept and type) + Agence Bio operators + DECP holders, distance to the buyer.

### 5.2 Evaluation (gold set labelled by hand on Friday/Saturday)
- **Gold set:** 200 BOAMP lots 2024-2025 + 100 DECP `objet`, stratified: 60 with pulse words, 60 épicerie/féculents, 80 other foods, 100 DECP at random in CPV 03/15. Two people label 50 in common to measure agreement (Cohen's kappa) and resolve disagreements.
- **Baselines:** B0 = keyword regex (the one I used in this audit); B1 = contract CPV (032122*, 1533*).
- **Metrics:** precision/recall/F1 per field (`menciona_legumbres`, `familia`, `forma`, `bio`, `siqo`), accuracy of `familia`; "invalid evidence" rate (hallucination detected by the substring check); cost and latency per 1,000 lots.
- **Honest expectation:** on `menciona_legumbres` the regex will be close to the LLM (the text is either explicit or absent). The LLM should win on `familia`, `forma`, criteria and SIQO, and on normalising multi-family lots ("céréales et légumineuses, biscuits, épicerie..."). If it does not win, say so.
- **Clauses:** qualitative evaluation with an 8-point checklist derived from the livret (≥3 environmental dimensions, upstream >50% of the environmental weight, verifiable proofs, bonus ≤10%, no geographic criterion...) applied to 5 outputs; ideally review by a mentor who is a lawyer.
- **Plan:** no "accuracy"; validate unit consistency (dry vs cooked portion, canned factor) and sensitivity to prices.

### 5.3 What the AI adds (jury test)
Without the LLM: the buyer sees 241 contracts with the word "légumineuse" and a pile of PDFs. With the LLM: the lot structure of thousands of notices normalised for comparison with peers, and a draft lot and clauses specific to their case and cited. **Risk:** the "clauses" part can be seen as "chat over a PDF". Mitigation: deterministic legal lint + quantitative benchmark + quantified plan with sources.

### 5.4 Explainability and limits to declare
Each field with its literal evidence; each clause with its source passage; the plan with its editable assumptions. Limits: we do not see the purchase detail (BPU); DECP covers only ≥40 k€ (or 60 k€ depending on date) and has duplicates; Agribalyse does not distinguish origin; RHD volumes come from a partial panel.

---

## 6. MVP and demo

### 6.1 Screens (Streamlit or Next.js; Streamlit for speed)
1. **"My central kitchen":** search by name/SIRET → Ma Cantine profile (meals/day, satellites, sectors, PAT) + timeline of DECP/BOAMP food contracts with the lot table structured by the LLM.
2. **"How my peers buy":** benchmark by size class and region (bars: separate pulse lot, 1° bis, organic, holder distance) with clickable real examples (Nantes, Toulouse lycées, Hérault).
3. **"My plan 2027-2029":** sliders (target frequency, budget, % organic) → tonnes/year by type and form, € and t CO2e, protein per dish.
4. **"My next tender":** proposed lot + weighted criteria + clauses with citation; live demo of the lint: type "lentilles d'origine France" → blocked with R2111-7 and alternative.
5. **"Who grows nearby":** map of depts (RPG 2024 ha of lentil/chickpea/bean) + organic operators + holders that have already won pulse lots, with distance.

### 6.2 Live demo script (~90 s within the pitch)
1. (15 s) We choose a real central kitchen with >1,000 meals/day and an "épicerie" lot without explicit pulses.
2. (20 s) Screen 2: "among central kitchens tendering food in DECP, 51 of 381 (13%) already have a lot with explicit pulses; the holders of those lots are at a median of 43 km".
3. (20 s) Screen 3: the plan gives X t/year of pulses, −Y t CO2e, cost-neutral if Z% of meat spend is reallocated (figures calculated at the event).
4. (25 s) Screen 4: generate lot + clauses; we type "origine France" live and the lint blocks it citing R2111-7; the CNRC alternative appears (direct supply 25%, SIQO Lentille verte du Puy).
5. (10 s) Screen 5: hectares of lentil within a 150 km radius.

### 6.3 Stack
Python 3.12 + uv, duckdb (DECP/Ma Cantine/BOAMP locally in parquet), pydantic for the schema, boto3 Bedrock (or alternative API if Bedrock does not have the model), small embeddings index (Bedrock Titan or local sentence-transformers) over ~150 passages, PuLP/OR-Tools LP for the plan, Streamlit + pydeck/folium for the map. Cache all LLM outputs to disk so the demo does not depend on the network (AWS closes after the event).

### 6.4 Repo
```
lotlegume/
  data_raw/ (gitignored)   data/ (small derived parquets)
  etl/ macantine.py decp.py boamp.py rpg.py agribalyse.py
  llm/ schema.py extract_lots.py rag_index.py clauses.py lint.py
  eval/ gold_lots.csv label_guide.md eval_extract.py
  plan/ optimizer.py prices.yaml (sources) factors.yaml
  app/ streamlit_app.py
  docs/ SOURCES.md DATA_STATUS.md (measured/sourced/assumed/synthetic)
```

---

## 7. Hour-by-hour plan (3 roles)

Roles: **A = ML/CV** (LLM extraction, gold set, evaluation, RAG); **B = data/backend** (ETL, joins, optimiser, map); **C = product/pitch** (user, legal, business, mentors, UI, deck).

### Friday 30/10
| Time | A | B | C |
|---|---|---|---|
| 20:45-21:30 | Test Bedrock access (models, quotas); JSON schema | Download DECP, register, TD 2024, BOAMP 2024-26 (section 4) | Talk to 2 mentors: is a central-kitchen user valid? Difference with Ardoise? |
| 21:30-22:30 | Labelling guide + label 60 lots | ETL BOAMP eForms → lot table; SIREN join | Choose 3 demo kitchens; download 2-3 DCEs with BPU by hand (anonymous access) |
| 22:30-23:00 | **Go/no-go 1:** LLM extraction runs on 20 lots with valid JSON | `lots.parquet` table with ≥1,000 lots | **Declare track before 23:00** (Track 2) |

### Saturday 31/10
| Time | A | B | C |
|---|---|---|---|
| 9:30-10:15 | Workshop | Workshop | Workshop |
| 10:15-13:00 | Complete gold set (300) + agreement; run full extraction | Peer benchmark; prices and factors (YAML with source) | UI screens 1-2; 2 mentors (public procurement and filière) |
| 13:00 | **Go/no-go 2:** F1 LLM vs regex measured | Benchmark works for 3 kitchens | Script v1 |
| 14:00-16:00 | RAG over livret + CCP; legal lint | LP optimiser for the plan | Screens 3-4 |
| 16:00-18:00 | Clause evaluation (checklist); cache | Supply map | Deck v1 (official template), impact figures |
| Night (off-campus) | Polish errors; metrics table | End-to-end tests, frozen data | Timed rehearsal ×3 |

### Sunday 1/11
| 8:30-9:15 | Freeze repo, README, SOURCES, DATA_STATUS | Demo backup video | Deck PDF + online profile |
| **9:30** | **Submission** (PDF with link to code/demo + profile) | | |

### Fallback and cuts
- If Bedrock does not work: alternative API or small local model for extraction; if nothing: regex + rules and the LLM only for clauses (lowers "essential AI").
- Cuts in order: (1) Agence Bio map (keep RPG); (2) optimiser → fixed scenario calculation; (3) DECP (keep BOAMP); (4) multi-document RAG → CNRC livret only.

---

## 8. Business

**Value proposition:** "Your next food tender, with a pulse lot a French cooperative can win, legal, compared with your peers and with your quantified diversification plan for the télédéclaration."

**Who pays (in order of probability):**
1. **Territory/filière (B2G2B):** Départements (colleges), Régions (lycées), PAT and Terres Univia/SNPV fund licences for all their kitchens: they align public demand with local supply without breaking R2111-7. Precedent: Agrilocal, a platform of départements to connect public buyers and local producers (created 2013; 34-38 départements joined according to the source) [F].
2. **Large central kitchen** (>1,000 meals/day: 734 [V]): subscription. Price anchors of software paid by local authorities [V, DECP]: Grand Cubzaguais €25.8k/48 months (~€6.5k/year), Cherbourg €41k/48 months (~€10k/year), Granville €51-62k, Saint-Maur €160k/48 months, Région Hauts-de-France €1.31M/36 months (Easilys, lycées). Ardoise was aiming at €25/month per canteen [V repo].
3. **Suppliers (cooperatives, légumeries):** tender radar with pulse lots. A generic tender-watch market already exists [NV].

**Size [V unless stated]:** 1,955 central kitchens >200 meals/day + 10,300 autonomous sites >200/day; collective catering food purchases ~€9.5 billion/year (official estimate, to be treated with caution). Software TAM (assumption €4k/year × 1,955 central kitchens) ≈ €7.8M/year [NV]; realistic SAM for the first 3 years: 50-100 kitchens or 5-10 territories [NV]. **It is a small market**: the strong economic thesis is the filière one (value of pulses channelled), not the SaaS.

**Competitors and substitutes:**
| Actor | What it does | Difference |
|---|---|---|
| Ardoise (1st HtF 2025) | Vegetarian menus CP-SAT, map of Ma Cantine badges, OCR of invoices with Gemini; last commit 14/12/2025 [V repo] | No public purchasing, no lots, no clauses, no agricultural supply |
| Ma Cantine (MASA) | Télédéclaration, guides, badges; free [V] | No tender benchmark and no quantified plan; we complement it |
| CNRC guides (livret légumineuses 2026) | Templates in PDF [V] | We operationalise them for a specific buyer |
| Easilys (Mapal), Salamandre, Ianord, Ideolys | Production management, technical sheets, stock [V DECP; F Easilys >4,000 establishments] | No public-market or filière analysis; potential channel/integration |
| Agrilocal | Simplified enquiries to local producers [F] | Transactional, no plan or benchmark |
| Sodexo Menu AI, AI menu generators | Menus [F, search engine] | Menu side, not purchasing |

**Adoption:** the public buyer purchases by tender; start with an experimentation agreement with a Département/PAT (active examples: Toulouse Métropole "Léguminons !", Strasbourg "Fabuleuses légumineuses", Lot, Pays de la Loire LAG 72 [F, search engine]).

---

## 9. Quantified impact (everything derived is [NV] and labelled as an estimate)

**Baseline [V]:** collective catering buys (GIRA panel, floor) ~3.7 kt of dry pulses, ~14.8 kt canned and ~0.9 kt frozen per year. With canned→dry factor 0.4 (assumption) ≈ **10 kt dry-equivalent** in the panel; if the panel covers half the market, up to ~20 kt [NV]. Over ~4,000 M meals: 2.5-5 g of dry pulse per meal [NV].

**Scenario (explicit assumptions):** in the sites >200 meals/day (1,707 M meals/year [V]), one main pulse-based dish per 20 meals, replacing a meat dish; portion 60 g dry (assumption, verify GEMRCN); meat replaced 80 g raw with a mix of 50% poultry / 30% beef preparation / 20% pork.
- Additional pulses: 1,707 M / 20 × 0.06 kg ≈ **5.1 kt/year** dry-equivalent (+25-50% on the baseline) [NV].
- Area if it were French: at 1.5 t/ha ≈ **3,400 ha** (≈10% of RPG 2024 lentil, 34,226 ha [V]) [NV].
- Farm income: 5.1 kt × ~€850/t (French lentil producer price per FranceAgriMer €806-873/t, 2023-2026 seasons [V, prior research]) ≈ **€4.3M/year** of sales to producers [NV].
- CO2: blended meat factor ≈ 0.5×5.58 (chicken, prior research) + 0.3×17.5 + 0.2×6.58 ≈ 9.4 kg CO2e/kg [NV mix; factors V]; per dish 0.75 kg vs pulse 0.06×0.581 = 0.035 kg → ~0.71 kg avoided × 85 M dishes ≈ **60 kt CO2e/year** [NV]. We do not claim CO2 for "French origin" because Agribalyse uses a single proxy [V].
- Canteen economics: dry lentil €2.93/kg RHD → ~€0.18 per pulse portion [V price, NV calculation]; meat savings fund compliance with the 60% meat EGalim (calculation to close on Friday with meat prices from a cited source).

---

## 10. Pitch

### 4-minute script
- **0:00-0:40 Problem.** "Since 2018 the law requires 16,616 canteens to have a plan to diversify proteins. Nobody knows how many have one: the data is not published. And when they buy, pulses disappear into an 'épicerie' lot: only 4% of food notices have a lot that says pulses. So public demand, 4 billion meals a year, does not reach the French fields the country wants to double by 2030."
- **0:40-1:10 User and decision.** The buyer of a central kitchen serving 3,000 meals, the month before renewing its framework agreement.
- **1:10-2:40 Live demo** (section 6.2).
- **2:40-3:20 AI and rigour.** Gold set of 300 lots, F1 vs regex, literal evidence per field, cited RAG, legal lint. What is measured, sourced, assumed.
- **3:20-4:00 Scale and impact.** One Département with its colleges; scenario 5 kt of pulses, 3,400 ha, 60 kt CO2e (estimates); territorial business model.

### Slides (official template)
1 Problem with 3 figures; 2 User/decision; 3 Demo (backup screenshot); 4 How the AI works + metrics; 5 Data (measured/sourced/assumed/synthetic table); 6 Impact and business; 7 Limits + team + prior resources.

### Likely questions
- **"How is this different from Ardoise?"** Ardoise optimises the week's menu; we optimise the purchasing specification for the next 3 years. Ardoise does not look at tenders, lots, clauses or where pulses come from; we connect the public buyer with French hectares, legally. They are complementary: the plan we generate can feed a menu generator.
- **"Can't you simply require French origin?"** No: R2111-7, and the CNRC guide talks about the favouritism offence. That is why we use lots, SIQO and the "approvisionnements directs" category.
- **"Didn't the CNRC already publish this?"** Yes, the June 2026 livret is our source; we apply it to the buyer's case with its volumes, its peers and nearby supply.
- **"How do you know which pulses they buy?"** We don't at line level: the BPU is in the DCE. We show that honestly; the buyer uploads its own DCE.
- **"Who pays?"** Territory and filière first; the large kitchen after; price anchors in DECP.
- **"What is the LLM's error margin?"** F1 per field on the gold set, with a baseline.

---

## 11. Risks, mentors, prior resources, checklist

### Risks
| Risk | Prob. | Mitigation |
|---|---|---|
| Jury sees it as "Ardoise 2" | High | Open with tenders and filière, not menus; prepared answer |
| LLM does not beat regex on detection | Medium-high | Measure other fields; be explicit |
| Line-level data (BPU) not available in open data | Certain | Manual DCEs for the demo, declared |
| Clauses with legal error | Medium | Lint + citation + mentor validation; disclaimer |
| Bedrock without a suitable model | Medium | Check Friday 20:45 |
| DECP amounts misread | Medium | Do not sum amounts; use bilan |
| Privacy (Agence Bio with personal names, DECP "[ND]") | Low | Only aggregates and legal entities |

### Questions for mentors
1. Would a central kitchen pay, or is the natural payer the Département/PAT?
2. What does a real food BPU look like and where do pulses appear?
3. Is the "approvisionnement direct" criterion being used for pulses? Risk of appeal?
4. What part of the diversification plan do governing bodies actually ask for?
5. What does Terres Univia think of channelling public demand?

### Prior resources to declare
- This desk research (dossier and audits in `research/`).
- `archive/research/datasets/rpg_pulses_dept_year.csv` (RPG aggregate built before the event).
- Exploratory counts (DECP, BOAMP, Ma Cantine) done on 30/10 in the morning; exploration scripts, not solution.

### Deliverables checklist (Sunday 9:30)
- [ ] Deck PDF in the template, with link to the repo and the demo
- [ ] Online project profile
- [ ] README with instructions, SOURCES.md, DATA_STATUS.md
- [ ] Gold set + evaluation script + metrics table
- [ ] LLM output cache and backup video
- [ ] No unverified citation on slides

---

## 12. Rubric (self-assessment)

| Criterion | Weight | Idea 8 score | Idea 1 score | Justification (idea 8) |
|---|---|---|---|---|
| Impact and sustainability | 30% | 7 | 6 | Fits squarely the official context of Track 2 and bridges to the filière; impact quantifiable but through scenarios, no current origin data |
| Scientific and technical rigour | 20% | 6 | 7.5 | Legal texts and data verified, gold set feasible; but the central problem (which pulses are bought) is not measurable in open data |
| Essential AI | 20% | 6 | 6.5 | Structured extraction + cited RAG + lint; risk of "chat over PDF" and of regex being enough for detection |
| Economic viability | 20% | 5 | 5.5 | Diffuse payer, small budgets, free public substitutes; best route is territorial |
| Execution and pitch | 10% | 7 | 7 | Demo with real data and "live lint" moment; a lot of product surface |
| **Weighted total** | | **6.2** | **6.4** | 0.3×7 + 0.2×6 + 0.2×6 + 0.2×5 + 0.1×7 = 6.20 |

**Does not beat idea 1** (6.2 vs 6.4), although it wins on impact. It would be the best option if the team decides to go to Track 2.

---

## 13. Sources (open today unless stated)

Legal and official
- CRPM L230-5-1, L230-5-3, L230-5-4, L230-5-6 and CCP R2111-7, L2113-10, R2132-2, R2152-10, R2196-1: texts via https://huggingface.co/datasets/louisbrulenaudet/code-rural-peche-maritime and https://huggingface.co/datasets/louisbrulenaudet/code-commande-publique (Légifrance mirrors, 2025) [V]
- EGalim statistical bilan 2025: https://ma-cantine.agriculture.gouv.fr/static/documents/rapport-bilan-statistique-EGALIM_2025.pdf [V]
- CNRC, Practical guide to public procurement in direct management (January 2024): https://ma-cantine.agriculture.gouv.fr/static/documents/Guide_Pratique_MP_Gestion_directe.pdf [V]
- CNRC, Methodological livrets légumineuses (June 2026): https://ma-cantine.agriculture.gouv.fr/static/documents/20260618_livret_methodologique_legumineuses_CCP.pdf and ..._non_CCP.pdf [V]
- Ma Cantine code: https://github.com/betagouv/ma-cantine (key-measures.json, quality-labels.json, diagnostic_volet_diversification.py, schema_teledeclarations.json, CHANGELOG_CANTINES.MD) [V]
- Réussir, "Le CNRC guide la restauration collective dans sa diversification des sources de protéines", 09/06/2021: https://www.reussir.fr/lesmarches/le-cnrc-guide-la-restauration-collective-dans-sa-diversification-des-sources-de-proteines [V]
- Decree 2025-1386 (60 k€ threshold): e.g. https://blog.landot-avocats.net/2025/12/30/rehaussement-des-seuils-de-dispense-de-publicite-et-de-mise-en-concurrence-decryptage-du-decret-n-2025-1386-du-29-decembre-2025-modifiant-certains-seuils-relatifs-aux-marches-publics/ [F, not opened]

Data
- Ma Cantine register: https://www.data.gouv.fr/datasets/registre-national-des-cantines/ [V]
- Télédéclarations: https://www.data.gouv.fr/datasets/resultats-de-campagnes-de-teledeclaration-des-cantines/ [V]
- DECP: https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/ [V]
- BOAMP API: https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records [V]
- Agribalyse 3.2: https://data.ademe.fr/datasets/agribalyse-31-synthese [V]
- Agence Bio API: https://opendata.agencebio.org/api/gouv/operateurs/ [V]
- Terres Univia, OléoProtéines 2025: https://www.terresunivia.fr/fichiers/publications/oleoproteines-edition-2025.pdf [V]
- Terres Univia, press kit on légumineuses in RHD 2022 (INRAE survey Fernandez-Inigo & Magrini 2020: 59% of school canteens serve pulses less than 2 times/week): https://www.terresunivia.fr/fichiers/cp/2022-06-15-DP-rh-campagne-legumineuses.pdf [V]
- Prior research in the repo: `archive/research/datasets/food_quality.md`, `economics_markets.md`, `geo_soil_climate.md` [V there]

Hack the Fork and competitors
- Ardoise repo: https://github.com/FelixMo42/HackTheFork2025 [V] (contains an exposed API key in `ocr_supplier.py`: do not copy or spread it)
- Savoir Animal, 15/04/2026: https://savoir-animal.fr/hack-the-fork-futur-proteines-alternatives-hackathon/ [V]
- SIAL Paris, Hack the Fork 2025 (Ardoise 1st, €3,000): https://www.sialparis.com/en/trends/News/sial-paris-hack-the-fork-2025-foodtech [F, snippet]
- HtF 2025 report (https://hackthefork.org/reports/HtF%202025%20-%20report.pdf): **not accessible** on 30/10/2026, hackthefork.org and hackthefork.com return 404 "Application not found" and Wayback was offline [V]
- Agrilocal: https://www.banquedesterritoires.fr/agrilocal-plateforme-de-mise-en-relation-entre-les-acheteurs-publics-de-la-restauration-collective [F]
- Easilys/Mapal: https://www.reussir.fr/lesmarches/easilys-rejoint-le-groupe-espagnol-mapal [F]
- Local initiatives: https://metropole.toulouse.fr/leguminons, https://www.strasbourg.eu/fabuleuses-legumineuses [F]

---

## Process note
- Data downloaded to `scratchpad/plan8/data/` (DECP 255 MB, register, TD 2024, 300 BOAMP notices, PDFs, HF parquets): **deleted at the end** (see confirmation in the summary).
- No model output or solution result; only counts, joins and manual inspection.
