import sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from scipy import stats
sys.path.insert(0, sys.argv[2])
from load import load
D, OUT = sys.argv[1], sys.argv[3]
t, c, df = load(D)
REG = {**dict.fromkeys(["18","28","36","41","45"],"Centre-Val de Loire"), **dict.fromkeys(["02","59","60","62","80"],"Hauts-de-France"),
 **dict.fromkeys(["77","78","91","95"],"Île-de-France"), **dict.fromkeys(["11","31","32","81"],"Occitanie"), **dict.fromkeys(["17","79","86"],"Nouvelle-Aquitaine"),
 **dict.fromkeys(["08","10","51","52","54","55","57"],"Grand Est"), **dict.fromkeys(["49","53"],"Pays de la Loire"), **dict.fromkeys(["21","89"],"Bourgogne-Fr.-Comté"),
 **dict.fromkeys(["35","56"],"Bretagne"), **dict.fromkeys(["14","27","76"],"Normandie"), **dict.fromkeys(["63","73"],"Auvergne-Rh.-Alpes"), "84":"PACA"}
# fix known site errors for region assignment: GRIGNON CP 73 is wrong -> 78; GRIGNON_INRAE -> 78 (Thiverval) assumption
df["dep_fix"] = df.dep.where(~df.site_name.isin(["GRIGNON","GRIGNON_INRAE"]), "78")
df["region"] = df.dep_fix.map(REG)
assert df.region.notna().all()
# fix LE_RHEU harvest date
m = df.situation_id.eq("LE_RHEU__Genotype_58__2013__M1")
df.loc[m, "harvest_date"] = pd.Timestamp("2013-07-16"); df.loc[m, "harv_doy"] = 197
P = df[df.protein_content.notna() & df.harvest_year.between(2013, 2024)].copy()
Y = df[df.yield_14.notna() & df.harvest_year.between(2013, 2024)].copy()
YEARS = list(range(2013, 2025))
COL = {"Spring": "#2a78d6", "Winter": "#eb6834"}
sns.set_theme(style="whitegrid", context="notebook", rc={"grid.color": "#e6e6e6", "axes.edgecolor": "#999", "figure.dpi": 100})
def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig); print("saved", name)
R = {}  # results to print

# ---------- 01 / 02 distributions by year x type
for var, name, lab, lines, fn in [("protein_content", "Grain protein", "Protein (% DM, N×6.25)", [23, 24], "01_protein_by_year_type.png"),
                                  ("yield_14", "Yield", "Yield (q/ha, 14% moisture)", [], "02_yield_by_year_type.png")]:
    d = P if var == "protein_content" else Y
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=d, x="harvest_year", y=var, hue="season", palette=COL, hue_order=["Spring", "Winter"], order=YEARS,
                fliersize=2, linewidth=1, width=0.75, ax=ax)
    for l, ls in zip(lines, ["--", ":"]):
        ax.axhline(l, color="#333", ls=ls, lw=1.2, label=f"threshold {l} %")
    ax.set_xlabel("Harvest year"); ax.set_ylabel(lab)
    ax.set_title(f"{name} by year and pea type (trials 2013-2024; each box = genotype×site situations)")
    ax.legend(loc="upper left", ncol=4, frameon=False)
    # annotate n
    for i, yv in enumerate(YEARS):
        n = d[d.harvest_year == yv].groupby("season").size()
        ax.text(i, ax.get_ylim()[0], f"S{n.get('Spring',0)}\nW{n.get('Winter',0)}", ha="center", va="bottom", fontsize=7, color="#555")
    save(fig, fn)
R["prot_year_type"] = P.groupby(["harvest_year", "season"]).protein_content.agg(["size", "mean", lambda s: (s >= 23).mean()]).round(2)
R["yield_year_type"] = Y.groupby(["harvest_year", "season"]).yield_14.agg(["size", "mean"]).round(1)

# ---------- trial-level table
T = df[df.harvest_year.between(2013, 2024)].groupby(["trial", "site_name", "harvest_year", "season", "region"]).agg(
    prot=("protein_content", "mean"), prot_sd=("protein_content", "std"), n_prot=("protein_content", "count"),
    yld=("yield_14", "mean"), yld_sd=("yield_14", "std"), n_yld=("yield_14", "count"),
    flo=("flo_doy", "median"), sow=("sow_doy", "median"), harv=("harv_doy", "median"),
    lon=("longitude", "first"), lat=("latitude", "first")).reset_index()
TP = T[T.n_prot >= 3]
R["n_trials_prot"] = len(TP); R["n_trials_prot_type"] = TP.season.value_counts().to_dict()

# ---------- 03 trial mean protein vs yield
TPY = TP[TP.n_yld >= 3]
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
cmap = plt.get_cmap("cividis"); norm = matplotlib.colors.Normalize(2013, 2024)
for ax, tp in zip(axes, ["Spring", "Winter"]):
    d = TPY[TPY.season == tp]
    sc = ax.scatter(d.yld, d.prot, c=d.harvest_year, cmap=cmap, norm=norm, s=40, edgecolor="white", lw=0.8)
    r, p = stats.spearmanr(d.yld, d.prot)
    ax.axhline(23, color="#333", ls="--", lw=1)
    ax.set_title(f"{tp}: {len(d)} trials, Spearman ρ = {r:.2f}")
    ax.set_xlabel("Mean trial yield (q/ha)")
    R[f"rho_trial_{tp}"] = (round(r, 2), round(p, 4), len(d))
    for _, row in d[(d.prot > 27.5) | (d.prot < 18.5)].iterrows():
        ax.annotate(f"{row.site_name[:14]} {row.harvest_year}", (row.yld, row.prot), fontsize=7, xytext=(4, 2), textcoords="offset points", color="#333")
axes[0].set_ylabel("Mean trial protein (% DM)")
fig.colorbar(sc, ax=axes, label="Harvest year", fraction=0.025)
fig.suptitle("Between trials (site-year×type): mean protein vs mean yield", y=1.0)
save(fig, "03_trial_protein_vs_yield.png")

# ---------- 04 within-trial genotype relation
PY = P[P.yield_14.notna()].copy()
PY["dp"] = PY.protein_content - PY.groupby("trial").protein_content.transform("mean")
PY["dy"] = PY.yield_14 - PY.groupby("trial").yield_14.transform("mean")
rhos = []
for tr, g in PY.groupby("trial"):
    if len(g) >= 8 and g.protein_content.std() > 0: rhos.append((tr, g.season.iloc[0], stats.spearmanr(g.yield_14, g.protein_content)[0]))
rh = pd.DataFrame(rhos, columns=["trial", "season", "rho"])
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
for tp in ["Spring", "Winter"]:
    d = PY[PY.season == tp]; ax.scatter(d.dy, d.dp, s=6, alpha=0.35, color=COL[tp], label=tp)
r_w = stats.spearmanr(PY.dy, PY.dp)[0]
ax.set_xlabel("Yield deviation from trial mean (q/ha)"); ax.set_ylabel("Protein deviation from trial mean (% DM points)")
ax.set_title(f"Within trial, genotypes centered (n={len(PY)}, global ρ={r_w:.2f})"); ax.legend(frameon=False, markerscale=3)
ax.axhline(0, color="#999", lw=0.8); ax.axvline(0, color="#999", lw=0.8)
ax = axes[1]
sns.histplot(data=rh, x="rho", hue="season", palette=COL, bins=np.linspace(-1, 1, 21), multiple="layer", element="step", ax=ax, hue_order=["Spring", "Winter"])
ax.axvline(rh.rho.median(), color="#333", ls="--", lw=1)
ax.set_xlabel("Spearman ρ yield-protein within each trial (≥8 genotypes)"); ax.set_ylabel("No. of trials")
ax.set_title(f"Distribution of ρ per trial (n={len(rh)}, median {rh.rho.median():.2f}, {(rh.rho<0).mean():.0%} negative)")
save(fig, "04_within_trial_genotype_protein_vs_yield.png")
R["within_rho_global"] = round(r_w, 3); R["within_rho_median"] = rh.groupby("season").rho.median().round(2).to_dict(); R["within_rho_neg_share"] = round((rh.rho < 0).mean(), 2)

# ---------- 05 variance decomposition (descriptive, sequential group means)
def decomp(d, var):
    d = d.copy(); x = d[var]; gm = x.mean(); SST = ((x - gm) ** 2).sum()
    d["m_y"] = d.groupby("harvest_year")[var].transform("mean")
    d["m_yt"] = d.groupby(["harvest_year", "season"])[var].transform("mean")
    d["m_tr"] = d.groupby("trial")[var].transform("mean")
    # site main effect: mean over trials of (trial mean - year×type mean), per site
    tr = d.groupby(["trial", "site_name"]).agg(mt=("m_tr", "first"), myt=("m_yt", "first"), n=(var, "size")).reset_index()
    tr["dev"] = tr.mt - tr.myt
    ns = tr.groupby("site_name").trial.nunique()
    site_eff = tr.groupby("site_name").dev.mean().where(ns >= 2, 0.0)  # only identifiable for sites with >=2 trials
    d["s_eff"] = d.site_name.map(site_eff)
    d["res_tr"] = x - d.m_tr
    d["g_eff"] = d.groupby("genotype").res_tr.transform("mean")
    ss = {"Year": ((d.m_y - gm) ** 2).sum(), "Type (within year)": ((d.m_yt - d.m_y) ** 2).sum(),
          "Site (sites with ≥2 trials)": (d.s_eff ** 2).sum()}
    ss["Site×year (rest of trial)"] = ((d.m_tr - d.m_yt) ** 2).sum() - ss["Site (sites with ≥2 trials)"]
    ss["Genotype (within trial)"] = (d.g_eff ** 2).sum()
    ss["Residual (G×E + error)"] = ((d.res_tr - d.g_eff) ** 2).sum()
    s = pd.Series(ss) / SST
    return s
dec = pd.DataFrame({"Protein": decomp(P, "protein_content"), "Yield": decomp(Y, "yield_14")})
R["decomp"] = dec.round(3)
fig, ax = plt.subplots(figsize=(11, 4.2))
pal = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#eda100", "#bdbdbd"]
left = np.zeros(2)
for i, comp in enumerate(dec.index):
    vals = dec.loc[comp].values
    ax.barh(dec.columns, vals, left=left, color=pal[i], edgecolor="white", lw=2, label=comp)
    for j, v in enumerate(vals):
        if v > 0.04: ax.text(left[j] + v / 2, j, f"{v:.0%}", ha="center", va="center", color="black" if pal[i] in ("#eda100", "#bdbdbd", "#1baf7a") else "white", fontsize=10, fontweight="bold")
    left += vals
ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.invert_yaxis()
ax.set_xlabel("Share of total sum of squares (sequential group-mean decomposition, descriptive)")
ax.set_title("Where does the variation come from? Protein and yield, situations 2013-2024")
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
save(fig, "05_variance_decomposition.png")

# ---------- 06 GxE heatmap: top genotypes protein deviation from trial mean, by year
P["dp"] = P.protein_content - P.groupby("trial").protein_content.transform("mean")
top = P.groupby("genotype").size().sort_values(ascending=False).head(20).index
H = P[P.genotype.isin(top)].pivot_table(index="genotype", columns="harvest_year", values="dp", aggfunc="mean")
Hn = P[P.genotype.isin(top)].pivot_table(index="genotype", columns="harvest_year", values="dp", aggfunc="size")
gtype = P.groupby("genotype").season.first()
gclass = P.groupby("genotype").seed_prot.first().fillna("NA")
H = H.loc[H.mean(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(12, 8))
cm = matplotlib.colors.LinearSegmentedColormap.from_list("div", ["#c2410c", "#f4f4f2", "#1d5fb8"])
sns.heatmap(H, cmap=cm, center=0, vmin=-2.5, vmax=2.5, annot=H.round(1), fmt="", annot_kws={"fontsize": 7},
            cbar_kws={"label": "Protein deviation from trial mean (% DM points)"}, linewidths=1, linecolor="white", ax=ax)
ax.set_yticklabels([f"{g.replace('Genotype_', 'G')} ({gtype[g][0]}, {gclass[g]})" for g in H.index], rotation=0, fontsize=8)
ax.set_xlabel("Harvest year"); ax.set_ylabel("Genotype (S=spring, W=winter; breeder protein class)")
ax.set_title("Genotype × environment: the 20 most tested genotypes, mean protein deviation by year\n(blue = more protein than their trial neighbors; empty cells = not tested)")
save(fig, "06_GxE_heatmap_genotypes.png")
# sign consistency
Gall = P.groupby(["genotype", "trial"]).dp.mean().reset_index()
gs = Gall.groupby("genotype").dp.agg(["mean", "std", "size", lambda s: max((s > 0).mean(), (s < 0).mean())])
gs.columns = ["mean", "sd", "ntr", "sign_cons"]
R["geno_sign_consistency_ntr>=10"] = gs[gs.ntr >= 10].sign_cons.describe().round(2).to_dict()
R["geno_mean_dev_range_ntr>=10"] = (gs[gs.ntr >= 10]["mean"].min().round(2), gs[gs.ntr >= 10]["mean"].max().round(2), int((gs.ntr >= 10).sum()))
R["geno_sd_within_median"] = round(gs[gs.ntr >= 10].sd.median(), 2)

# ---------- 07 rank stability
pairs = []
trials = {tr: g.groupby("genotype").protein_content.mean() for tr, g in P.groupby("trial")}
tl = list(trials)
yrs = P.groupby("trial").harvest_year.first(); tps = P.groupby("trial").season.first()
for i in range(len(tl)):
    for j in range(i + 1, len(tl)):
        a, b = trials[tl[i]], trials[tl[j]]
        if tps[tl[i]] != tps[tl[j]]: continue
        com = a.index.intersection(b.index)
        if len(com) >= 6:
            pairs.append((stats.spearmanr(a[com], b[com])[0], yrs[tl[i]] == yrs[tl[j]], tps[tl[i]], len(com)))
pr = pd.DataFrame(pairs, columns=["rho", "same_year", "season", "n"]).dropna()
pr["Trial pair"] = np.where(pr.same_year, "same year", "different year")
gsel = gs[gs.ntr >= 10].sort_values("mean")
fig, axes = plt.subplots(1, 2, figsize=(15, 13), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 0.45})
ax = axes[0]
sns.boxplot(data=pr, x="season", y="rho", hue="Trial pair", palette=["#1baf7a", "#6250d6"], ax=ax, fliersize=1.5, order=["Spring", "Winter"])
ax.axhline(0, color="#999", lw=0.8)
ax.set_xlabel(""); ax.set_ylabel("Spearman ρ of the protein ranking between two trials\n(shared genotypes ≥6)")
ax.set_title(f"Ranking stability: {len(pr)} trial pairs")
ax = axes[1]
yy = np.arange(len(gsel))
ax.errorbar(gsel["mean"], yy, xerr=gsel["sd"], fmt="none", color="#333", ecolor="#bbb", ms=4, capsize=0)
for k, (g, row) in enumerate(gsel.iterrows()):
    ax.plot(row["mean"], k, "o", color=COL[gtype[g]], ms=5)
ax.set_yticks(yy); ax.set_yticklabels([f"{g.replace('Genotype_', 'G')} ({gclass[g] if gclass[g] != 'NA' else 'no class'}, n={int(gsel.ntr[g])})" for g in gsel.index], fontsize=7.5)
ax.set_ylim(-1, len(gsel))
ax.axvline(0, color="#999", lw=0.8)
ax.set_xlabel("Mean protein deviation from trial mean (% DM points) ± 1 SD across trials")
ax.set_title(f"{len(gsel)} genotypes with ≥10 trials (blue spring, orange winter)")
save(fig, "07_ranking_stability_genotypes.png")
R["rank_pairs"] = pr.groupby(["season", "Trial pair"]).rho.agg(["size", "median"]).round(2)

# ---------- 08 seed_prot class vs measured
order = ["low", "medium", "medium/high", "high", "very high"]
Q = P[P.seed_prot.isin(order)].copy()
fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1, 1.4]})
ax = axes[0]
sns.boxplot(data=Q, x="seed_prot", y="dp", order=order, hue="season", palette=COL, hue_order=["Spring", "Winter"], ax=ax, fliersize=1.5)
ax.axhline(0, color="#999", lw=0.8)
ax.set_xlabel("Breeder-declared protein class (seed_prot)"); ax.set_ylabel("Deviation from trial mean (% DM points)")
ax.set_title("Breeder class vs measured protein (centered by trial)")
ax.legend(frameon=False)
ax = axes[1]
cy = Q.groupby(["harvest_year", "seed_prot"]).dp.agg(["mean", "size"]).reset_index()
cy = cy[cy["size"] >= 10]
seq = ["#c6dbef", "#9ecae1", "#6baed6", "#2171b5", "#08306b"]
for o, col in zip(order, seq):
    if o == "medium/high": continue
    d = cy[cy.seed_prot == o]
    ax.plot(d.harvest_year, d["mean"], "-o", color=col, label=o, lw=2, ms=5)
ax.axhline(0, color="#999", lw=0.8)
ax.set_xlabel("Harvest year"); ax.set_ylabel("Mean deviation from trial mean (% DM points)")
ax.set_title("Is the class ordering stable across years? (cells with ≥10 situations)")
ax.legend(title="Breeder class", frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.15)); ax.set_xticks(YEARS)
save(fig, "08_breeder_class_vs_protein.png")
R["class_dev"] = Q.groupby("seed_prot").dp.agg(["size", "mean"]).loc[order].round(2)
R["class_raw"] = Q.groupby("seed_prot").protein_content.mean().loc[order].round(2)
R["class_na_share_prot"] = round(P.seed_prot.isna().mean(), 3)

# ---------- 09 map
gj = json.load(open(f"{D}/deps.geojson"))
S = df[df.harvest_year.between(2013, 2024)].groupby("site_name").agg(lon=("longitude", "first"), lat=("latitude", "first"),
        ntr=("trial", "nunique"), prot=("protein_content", "mean"), nyr=("harvest_year", "nunique")).reset_index()
BAD = ["AVANCON", "DIOU", "GRIGNON", "GRIGNON_INRAE"]
fig, ax = plt.subplots(figsize=(10, 10))
for f in gj["features"]:
    geom = f["geometry"]; rings = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for r in rings:
        a = np.array(r[0]); ax.fill(a[:, 0], a[:, 1], facecolor="#f4f4f2", edgecolor="#bbbbbb", lw=0.5)
Sp = S[S.prot.notna()]; Sn = S[S.prot.isna()]
ax.scatter(Sn.lon, Sn.lat, s=Sn.ntr * 25, facecolor="none", edgecolor="#777", lw=1, label="protein not measured")
sc = ax.scatter(Sp.lon, Sp.lat, s=Sp.ntr * 25, c=Sp.prot, cmap="viridis", vmin=20.5, vmax=25.5, edgecolor="white", lw=0.6, alpha=0.9)
for _, r in S[S.site_name.isin(BAD)].iterrows():
    ax.scatter(r.lon, r.lat, marker="x", color="#e34948", s=80, lw=2)
    ax.annotate(r.site_name + " (coord. vs CP)", (r.lon, r.lat), xytext=(6, -10), textcoords="offset points", fontsize=8, color="#b91c1c")
for _, r in S.sort_values("nyr", ascending=False).head(6).iterrows():
    ax.annotate(f"{r.site_name} ({r.nyr} years)", (r.lon, r.lat), xytext=(6, 6), textcoords="offset points", fontsize=7.5)
ax.set_xlim(-5.2, 8.3); ax.set_ylim(42.2, 51.2); ax.set_aspect(1 / np.cos(np.radians(46.5)))
ax.set_xlabel("Longitude (°)"); ax.set_ylabel("Latitude (°)")
fig.colorbar(sc, ax=ax, fraction=0.035, label="Mean site protein 2013-2024 (% DM)")
for n in [1, 3, 6]: ax.scatter([], [], s=n * 25, facecolor="#ccc", edgecolor="#777", label=f"{n} trial(s)")
ax.legend(loc="lower left", frameon=True, title="Size = no. of site-year×type trials")
ax.set_title(f"Trial sites 2013-2024 ({len(S)} sites; red x = coordinates and postal code do not match)")
save(fig, "09_map_sites_protein.png")
R["sites_n"] = len(S); R["sites_by_nyr"] = S.nyr.value_counts().sort_index().to_dict()

# ---------- 10 flowering vs protein / yield (trial means)
fig, axes = plt.subplots(2, 2, figsize=(13, 10), gridspec_kw={"hspace": 0.4})
for i, (var, lab) in enumerate([("prot", "Mean trial protein (% DM)"), ("yld", "Mean trial yield (q/ha)")]):
    for j, tp in enumerate(["Spring", "Winter"]):
        ax = axes[i, j]; d = TP[TP.season == tp] if var == "prot" else T[(T.season == tp) & (T.n_yld >= 3)]
        sc10 = ax.scatter(d.flo, d[var], c=d.harvest_year, cmap=cmap, norm=norm, s=30, edgecolor="white", lw=0.6)
        r = stats.spearmanr(d.flo, d[var])[0]; R[f"rho_flo_{var}_{tp}"] = (round(r, 2), len(d))
        ax.set_title(f"{tp}: ρ = {r:.2f} (n={len(d)} trials)")
        ax.set_xlabel("Start of flowering (Julian day, trial median)"); ax.set_ylabel(lab)
        if var == "prot": ax.axhline(23, color="#333", ls="--", lw=1)
fig.colorbar(sc10, ax=axes, fraction=0.025, label="Harvest year")
fig.suptitle("Flowering date vs protein and yield (trial means, site-year×type)", y=0.95)
save(fig, "10_flowering_vs_protein_yield.png")
# within trial: flowering deviation vs protein deviation
P["dflo"] = P.flo_doy - P.groupby("trial").flo_doy.transform("mean")
R["within_rho_flo_prot"] = {tp: round(stats.spearmanr(g.dflo, g.dp)[0], 2) for tp, g in P.groupby("season")}

# ---------- 11 crop calendar + sowing vs protein
fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
ax = axes[0]
cal = T[T.n_prot >= 0].copy()
for k, tp in enumerate(["Spring", "Winter"]):
    d = cal[cal.season == tp]
    for m, (col, nm) in enumerate([("sow", "sowing"), ("flo", "flowering"), ("harv", "harvest")]):
        v = d[col].dropna(); pos = k * 4 + m
        bp = ax.boxplot(v, positions=[pos], vert=False, widths=0.6, patch_artist=True, showfliers=False)
        bp["boxes"][0].set_facecolor(COL[tp]); bp["medians"][0].set_color("black")
        ax.text(v.quantile(0.05), pos + 0.5, f"{nm}: median {pd.Timestamp('2023-01-01') + pd.Timedelta(days=int(v.median()) - 1):%d %b}", va="bottom", fontsize=8)
        R[f"cal_{tp}_{nm}"] = (int(v.quantile(0.05)), int(v.median()), int(v.quantile(0.95)))
ax.set_yticks([1, 5]); ax.set_yticklabels(["Spring", "Winter"]); ax.set_ylim(-1, 7)
ax.axvline(1, color="#999", lw=0.8); ax.text(3, -0.6, "1 Jan", fontsize=8, color="#555")
ax.set_xlabel("Day relative to 1 Jan of the harvest year (negative = previous autumn)"); ax.set_xlim(-90, 290)
ax.set_title("Trial calendar (per-trial medians, p5-p95)")
ax = axes[1]
for tp in ["Spring", "Winter"]:
    d = TP[TP.season == tp]; ax.scatter(d.sow, d.prot, s=28, color=COL[tp], edgecolor="white", lw=0.5, label=tp)
    R[f"rho_sow_prot_{tp}"] = round(stats.spearmanr(d.sow, d.prot)[0], 2)
ax.axhline(23, color="#333", ls="--", lw=1)
ax.set_xlabel("Sowing date (day relative to 1 Jan of the harvest year)"); ax.set_ylabel("Mean trial protein (% DM)")
ax.set_title(f"Sowing vs protein: ρ spring {R['rho_sow_prot_Spring']}, winter {R['rho_sow_prot_Winter']}"); ax.legend(frameon=False)
save(fig, "11_calendar_and_sowing.png")

# ---------- 12 missingness
vars_ = ["yield_14", "protein_content", "start_flo_date", "end_flo_date", "tsw_14", "harvest_date", "previous_crop", "seed_prot", "flow_precocity", "TSW", "cold_tolerance", "Hr_allele"]
tr2 = t.copy(); tr2 = tr2.merge(df[["situation_id", "yield_14", "protein_content", "start_flo_date", "end_flo_date", "tsw_14", "harvest_date"]], on="situation_id")
tr2 = tr2[tr2.harvest_year.between(2013, 2024)]
for v in ["previous_crop", "seed_prot", "flow_precocity", "TSW", "cold_tolerance", "Hr_allele"]:
    tr2[v] = tr2[v].replace({"NA": np.nan, "": np.nan})
M = tr2.groupby("harvest_year")[vars_].apply(lambda g: g.notna().mean()).T
fig, ax = plt.subplots(figsize=(12, 5.5))
sns.heatmap(M, cmap="Blues", vmin=0, vmax=1, annot=(M * 100).round(0).astype(int), fmt="d", annot_kws={"fontsize": 7.5},
            cbar_kws={"label": "% of situations with a value"}, linewidths=1, linecolor="white", ax=ax)
ax.set_xlabel("Harvest year"); ax.set_ylabel("")
ax.set_title("Completeness by year and variable (% of situations with a value; cold_tolerance and Hr exist only for winter)")
save(fig, "12_missingness_year_variable.png")
R["missing_prot_by_siteyear"] = None
sy = df[df.harvest_year.between(2013, 2024)].groupby("site_year").protein_content.apply(lambda s: s.notna().mean())
R["siteyear_prot_full_none_partial"] = (int((sy == 1).sum()), int((sy == 0).sum()), int(((sy > 0) & (sy < 1)).sum()))

# ---------- 13 share of trials >= 23 by year/type and region
TP2 = TP.copy(); TP2["ok23"] = TP2.prot >= 23
fig, axes = plt.subplots(1, 2, figsize=(16, 5.8), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.35})
ax = axes[0]
sh = TP2.groupby(["harvest_year", "season"]).ok23.agg(["mean", "size"]).reset_index()
w = 0.38
for k, tp in enumerate(["Spring", "Winter"]):
    d = sh[sh.season == tp].set_index("harvest_year").reindex(YEARS)
    xs = np.arange(len(YEARS)) + (k - 0.5) * w
    ax.bar(xs, d["mean"], width=w - 0.04, color=COL[tp], label=tp)
    for x, (m_, n_) in zip(xs, zip(d["mean"], d["size"])):
        if not np.isnan(n_): ax.text(x, (m_ if not np.isnan(m_) else 0) + 0.02, f"{int(n_)}", ha="center", fontsize=6.5, color="#555")
ax.set_xticks(range(len(YEARS))); ax.set_xticklabels(YEARS, rotation=45)
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.set_ylim(0, 1.08)
ax.set_ylabel("% of trials with mean ≥ 23 % DM"); ax.set_xlabel("Harvest year (number above bar = no. of trials)")
ax.set_title("Trials whose mean protein exceeds 23 %"); ax.legend(frameon=False)
ax = axes[1]
RG = TP2.groupby(["region", "harvest_year"]).ok23.mean().unstack().reindex(columns=YEARS)
RGn = TP2.groupby(["region", "harvest_year"]).ok23.size().unstack().reindex(columns=YEARS)
RG = RG.loc[RGn.sum(axis=1).sort_values(ascending=False).index]
RGn = RGn.loc[RG.index]
ann = np.array([[("" if np.isnan(RGn.iloc[i, j]) else f"{RG.iloc[i, j]*100:.0f}\n({int(RGn.iloc[i, j])})") for j in range(RG.shape[1])] for i in range(RG.shape[0])], dtype=object)
sns.heatmap(RG, cmap="viridis", vmin=0, vmax=1, annot=ann, fmt="", annot_kws={"fontsize": 6.5}, linewidths=1, linecolor="white",
            cbar_kws={"label": "% of trials ≥ 23 %"}, ax=ax)
ax.set_xlabel("Harvest year"); ax.set_ylabel("")
ax.set_title("By region and year: % of trials ≥ 23 % (no. of trials)")
save(fig, "13_share_trials_23_year_region.png")
R["share23_region"] = TP2.groupby("region").ok23.agg(["size", "mean"]).sort_values("size", ascending=False).round(2)
R["share23_type"] = TP2.groupby("season").ok23.mean().round(2).to_dict()
R["share23_year"] = TP2.groupby("harvest_year").ok23.mean().round(2).to_dict()
R["share_sit_23_24"] = (round((P.protein_content >= 23).mean(), 3), round((P.protein_content >= 24).mean(), 3))
# year vs region: how much of trial-level variance is year
tm = TP.prot; R["trial_prot_sd"] = round(tm.std(), 2)
R["trial_prot_year_share"] = round(((TP.groupby("harvest_year").prot.transform("mean") - tm.mean()) ** 2).sum() / ((tm - tm.mean()) ** 2).sum(), 3)
R["trial_prot_region_share"] = round(((TP.groupby("region").prot.transform("mean") - tm.mean()) ** 2).sum() / ((tm - tm.mean()) ** 2).sum(), 3)
R["trial_prot_type_share"] = round(((TP.groupby("season").prot.transform("mean") - tm.mean()) ** 2).sum() / ((tm - tm.mean()) ** 2).sum(), 3)
R["within_sd_median"] = round(TP.prot_sd.median(), 2)

# ---------- 14 outliers by trial block + irrigation
fig, axes = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={"wspace": 0.5})
ax = axes[0]
TP["z"] = (TP.prot - TP.groupby("harvest_year").prot.transform("mean")) / TP.groupby("harvest_year").prot.transform("std")
for tp in ["Spring", "Winter"]:
    d = TP[TP.season == tp]; ax.scatter(d.prot, d.prot_sd, s=d.n_prot * 3, color=COL[tp], alpha=0.7, edgecolor="white", lw=0.5, label=tp)
ext = TP[(TP.prot < 19) | (TP.prot > 27) | (TP.prot_sd > 2.2)]
for _, r in ext.iterrows():
    ax.annotate(f"{r.site_name[:16]} {r.harvest_year}", (r.prot, r.prot_sd), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.set_xlabel("Mean trial protein (% DM)"); ax.set_ylabel("SD of protein among genotypes within trial (points)")
ax.set_title("Outliers come in blocks: extreme trials (size = no. of genotypes)"); ax.legend(frameon=False)
R["extreme_trials"] = ext[["trial", "prot", "prot_sd", "yld", "n_prot"]].round(1).sort_values("prot")
R["situations_lt18_gt28"] = (int((P.protein_content < 18).sum()), int((P.protein_content > 28).sum()),
    P[P.protein_content < 18].trial.nunique(), P[P.protein_content > 28].trial.nunique())
ax = axes[1]
IR = df[df.site_year.isin(["BRETENIERE_2014", "BRETENIERE_2015", "BRETENIERE_2022", "CHAMBON_2022", "SAINT_GERMAIN_DU_PUY_2013", "SAINT_GERMAIN_DU_PUY_2014"])].copy()
IR["Irrigation"] = np.where(IR.irrig, "irrigated", "rainfed")
rows = []
for (sy_, tp), g in IR.groupby(["site_year", "season"]):
    for var in ["protein_content", "yield_14"]:
        a = g[g.irrig][var].mean(); b = g[~g.irrig][var].mean()
        if not (np.isnan(a) or np.isnan(b)): rows.append((f"{sy_} ({tp[0]})", var, a - b, g[g.irrig][var].count(), g[~g.irrig][var].count()))
ir = pd.DataFrame(rows, columns=["trial", "var", "diff", "n_irr", "n_dry"])
R["irrig"] = ir.round(2)
ip = ir.pivot(index="trial", columns="var", values="diff")
yy = np.arange(len(ip))
ax.barh(yy - 0.2, ip["protein_content"], height=0.38, color="#1baf7a", label="protein (% DM points)")
ax.barh(yy + 0.2, ip["yield_14"] / 10, height=0.38, color="#6250d6", label="yield (÷10, q/ha)")
ax.set_yticks(yy); ax.set_yticklabels(ip.index, fontsize=8); ax.axvline(0, color="#333", lw=0.8)
ax.set_xlabel("Difference irrigated − rainfed within the same site-year"); ax.legend(frameon=False, fontsize=8)
ax.set_title("Irrigation (descriptive): only 6 site-years compare it")
save(fig, "14_outliers_block_and_irrigation.png")

# ---------- 15 year effect: trial means by year type with national-like threshold
fig, ax = plt.subplots(figsize=(12, 5))
for k, tp in enumerate(["Spring", "Winter"]):
    d = TP[TP.season == tp]
    xs = d.harvest_year + (k - 0.5) * 0.3 + np.random.default_rng(1).uniform(-0.08, 0.08, len(d))
    ax.scatter(xs, d.prot, s=18, color=COL[tp], alpha=0.75, edgecolor="white", lw=0.4, label=f"{tp} (trial)")
    mm = d.groupby("harvest_year").prot.mean()
    ax.plot(mm.index + (k - 0.5) * 0.3, mm.values, "_", color="black", ms=18, mew=2)
ax.axhline(23, color="#333", ls="--", lw=1, label="23 %")
ax.set_xticks(YEARS); ax.set_xlabel("Harvest year"); ax.set_ylabel("Mean trial protein (% DM)")
ax.set_title("Mean protein of each site-year×type trial, by year (black dash = year and type mean)\nThe year shifts the block, but the spread between trials of the same year is larger")
ax.legend(frameon=False, ncol=3)
save(fig, "15_trials_by_year.png")
yr_sd = TP.groupby(["harvest_year"]).prot.std()
R["within_year_trial_sd_median"] = round(yr_sd.median(), 2); R["year_means_sd"] = round(TP.groupby("harvest_year").prot.mean().std(), 2)
R["winter_minus_spring_same_siteyear"] = None
both = TP.pivot_table(index=["site_name", "harvest_year"], columns="season", values="prot").dropna()
R["winter_minus_spring_same_siteyear"] = (len(both), round((both.Winter - both.Spring).mean(), 2), round((both.Winter < both.Spring).mean(), 2))
bothy = T[T.n_yld >= 3].pivot_table(index=["site_name", "harvest_year"], columns="season", values="yld").dropna()
R["winter_minus_spring_yield"] = (len(bothy), round((bothy.Winter - bothy.Spring).mean(), 1))

pd.set_option("display.width", 200, "display.max_rows", 200)
R["class_by_type"] = Q.groupby(["season", "seed_prot"]).dp.agg(["size", "mean"]).round(2)
R["class_by_type_raw"] = Q.groupby(["season", "seed_prot"]).protein_content.mean().round(2)
R["yield_trial_sd"] = round(T[T.n_yld >= 3].yld.std(), 1); R["yield_within_sd_median"] = round(T[T.n_yld >= 3].yld_sd.median(), 1)
R["n_geno_prot"] = P.genotype.nunique(); R["n_trials_any_prot"] = P.trial.nunique()
R["yr_means"] = TP.groupby("harvest_year").prot.mean().round(2).to_dict()
for k, v in R.items(): print(f"\n## {k}\n{v}")
