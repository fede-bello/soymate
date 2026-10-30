import sys, json, numpy as np, pandas as pd
from matplotlib.path import Path
sys.path.insert(0, sys.argv[2])
from load import load
D = sys.argv[1]
t, c, df = load(D)
print("irrig", df.irrig.sum(), df[df.irrig].groupby("harvest_year").size().to_dict())
print(df[df.irrig].groupby(["site_year"]).irrig.size())
# sites with both irrigated and non irrigated
g = df.groupby("site_year").irrig.agg(["sum","size"]); print(g[(g["sum"]>0)&(g["sum"]<g["size"])])
# coordinate check
gj = json.load(open(f"{D}/deps.geojson"))
polys = []
for f in gj["features"]:
    geom = f["geometry"]; code = f["properties"]["code"]
    rings = [geom["coordinates"]] if geom["type"]=="Polygon" else geom["coordinates"]
    for r in rings: polys.append((code, Path(np.array(r[0]))))
sites = df.groupby("site_name").agg(lon=("longitude","first"), lat=("latitude","first"), dep=("dep","first"), n=("situation_id","size"))
def which(lon, lat):
    for code, p in polys:
        if p.contains_point((lon, lat)): return code
    return None
sites["dep_coord"] = [which(a,b) for a,b in zip(sites.lon, sites.lat)]
bad = sites[sites.dep != sites.dep_coord]; print(bad)
print(df[df.harv_doy>400][["situation_id","sowing_date","harvest_date"]])
print(df.harvest_year.value_counts().sort_index().to_dict())
print(sorted(df.dep.unique()))
