# Climate and pulses

**Two time series ideas for Track 3 · 30 October to 1 November 2026**

## Executive summary

Two approaches share one database: estimating the departmental yield of a pulse before harvest, and recovering historical seasons with similar weather. Both can support the planning of a cooperative that works with pulses for human food.

**Recommendation:** build one minimal workflow with Agreste (the statistics service of the French Ministry of Agriculture) and climate data. Start with historical analogs or a simple model, depending on the data and on what a mentor confirms. Add the second method and Sentinel-2 only if the core works.

### The question guiding the project

With the climate known up to a given date in the season, can we offer a useful estimate or historical comparison of a crop's yield in a French department? The user, the decision and the timeline are hypotheses that must be validated with a cooperative or a mentor.

### What still needs to be checked

- Open the departmental file and count years, departments and valid values for the chosen crop. The specific file has not been inspected for this report.
- Confirm that the crop and the user relate to human food: aggregate statistics do not automatically identify the destination of each harvest.
- Check that the information would arrive in time for a real decision. Yield per hectare is not the same as available production, income or margin.

### MVP scope

One pulse, a few departments and one cutoff date; real data; a retrospective evaluation by year; a baseline; a simple interface and traceable sources. The results are departmental, not predictions per plot.

## 1 | Yield estimation

*An early prediction, evaluated against later statistics.*

### The idea

A cooperative selects a crop, a department and a cutoff date. The system uses the climate up to that date and historical yields to estimate the departmental yield. In a retrospective demo, the prediction is compared with the figure published afterwards.

### Data needed

- **Agreste / SAA** (SAA = Annual Agricultural Statistics, *Statistique Agricole Annuelle*): annual area, production and yield by crop and territory. The departmental yield is the statistical label; check completeness and units. 2025 appears as provisional in the publication consulted.
- **Open-Meteo / ERA5-Land**: temperature and precipitation series estimated on a grid of approximately 0.1°. These are modeled meteorological inputs, not exact measurements for each plot.
- **Optional, RPG** (*Registre Parcellaire Graphique*, the French graphic parcel register): geometries and declared crops, used to locate cultivated areas and improve the spatial aggregation of climate data. It does not provide yield per plot.
- **Optional, Sentinel-2**: repeated multispectral images that allow vegetation indices to be extracted. They do not directly label yield or pests.

### Model and evaluation

Start with the department's historical mean as the baseline; then try a Ridge regression and, if there is enough data, a tree-based model. Compare the mean absolute error (MAE) in yield units and show errors by year.

Reserve complete later years for testing. Compute normalization, historical means and variable selection exclusively with training information. The input climate must end at the cutoff date; the revised statistical figures may differ from those available in real time.

### Minimal demo

A selector for crop, department and historical season; a yield chart; the model's estimate, the baseline and the later observed statistical value; the number of cases evaluated and the limits. The cutoff date must be useful to the user and consistent with the crop calendar.

### Main risk

Few years, missing values and a climatically unrepresentative point can limit reliability. Do not confuse many departments with many independent years. If the model does not beat the baseline, report it and reconsider its usefulness.

## 2 | Similar seasons

*Find climatic precedents and show their results.*

### The idea

For a given season and cutoff date, retrieve earlier years with similar temperature and rainfall profiles, and show the departmental yield observed in those years. An exploration tool for putting a season in context, subject to validation with users.

### Data needed

- **Open-Meteo / ERA5-Land**: historical temperature and rainfall series for the area. Use the same source and comparable time windows across years.
- **Agreste / SAA**: observed annual yield by crop and department, to display and evaluate the analogs.
- **Optional, RPG and Sentinel-2**: the RPG provides the location of declared plots; Sentinel-2 provides multispectral images for vegetation curves. Incorporate them only if time allows.

### Method

1. Aggregate the climate by week or month up to the cutoff date.
2. Normalize using only the earlier years available.
3. Find the *k* closest historical neighbors.
4. Show their curves and yields.

Start with simple distances. DTW or other representations are extensions, not requirements.

### Is there ground truth?

There is no label saying which analog is the "correct" one. There are yield statistics that allow evaluating whether the neighbors are useful for a task: average their yields and compare that estimate with the published yield for the reserved year and with the historical mean.

### Minimal demo

Choose a historical year, a department and a crop; show the climate series up to the cutoff date, three similar earlier seasons, their yields and the baseline. For the evaluated year, reveal the observed statistical yield at the end.

### Limits and decisions

Similar climate does not guarantee a similar harvest: varieties, soil, practices and other factors change. If the backtest uses revised data, or data that were not available on the simulated date, state it. Selecting a neighbor does not prove a causal relationship.

**Pending product decision:** ask the cooperative whether these analogs would help plan storage, commercial conversations or another concrete task, and on what date it would need the information.

## 3 | Work plan

*Team of three · approximately 20 hours of work per person*

### Friday: decide and check

- Talk to a mentor about the crop, region, user, decision, timing and tools that already exist. Declare the track before 23:00.
- Once the event has started, open SAA and count the useful records by crop, department and year; check units, missing values and provisional status. Try a small climate query.
- Decision: continue if there is a relevant crop and enough data for a temporal test; if not, change the crop or region and reduce the scope.

### Saturday morning: build the foundation

- **Person 1:** clean Agreste, document categories and units; validate the use case with a mentor.
- **Person 2:** obtain climate data, choose representative coordinates and build variables up to the cutoff date.
- **Person 3:** prepare the interface and the baseline; agree on a common data format with the team.

**Milestone:** a table with department, year, crop, climate variables and yield.

### Saturday afternoon: evaluate and demonstrate

- Build the analogs or a simple regression; reserve complete years; compare with the historical average and compute the MAE.
- Connect a real example to the interface. Show failures, scale and the number of cases evaluated.
- If the core works, add the second method. Leave the satellite images for last.

### Saturday night and Sunday

Prepare the presentation PDF and the fact sheet; document resources and licenses; back up code and data outside AWS; rehearse the four-minute pitch. On Sunday, test the links and submit before 9:30.

### Questions for the mentor

Who decides what, and when? Does this regional yield really help? Which pulse is aimed at human food? Which existing tools do they use? What accuracy and what economic data would they need?

## Sources and checks

*Main links for the team · consulted for the report*

- **Agreste / SAA, departmental files:** statistics on area, production and yield by product and territory.
- **SAA Occitanie 2010-2025:** example of a regional file and explanation of series revisions.
- **SAA 2024, national report:** categories and national statistics on pulses; does not guarantee departmental completeness.
- **Open-Meteo, historical API:** variables, coverage, models, resolution and access.
- **RPG, data.gouv.fr:** geometries of plots and declared crops.
- **Sentinel-2, Copernicus:** multispectral images, resolution and access.
- **Observatoire OléoProtéines:** context on production, markets and human food consumption.
- **Terres Inovia, tools:** existing tools to contrast the problem and the proposal.

The attached participant guide was also used for rules, schedules, deliverables and preparation constraints.

### Communication rules

Distinguish measured results, estimates, assumptions and synthetic data. Agreste statistics are aggregated; they do not prove the food destination or the income per plot. The commercial and environmental impact is a hypothesis to validate.
