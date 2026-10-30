import pandas as pd, numpy as np, sys
D = sys.argv[1] if len(sys.argv) > 1 else None
def load(D):
    t = pd.read_csv(f"{D}/trials_data.csv", encoding="utf-8-sig")
    c = pd.read_csv(f"{D}/crop_traits_data.csv", encoding="utf-8-sig", low_memory=False)
    # one row per situation for yield/protein/flowering etc
    single = c[c.variable.isin(["yield_14","protein_content","start_flo_date","end_flo_date","tsw_14"])]
    w = single.pivot_table(index="situation_id", columns="variable", values="value", aggfunc="first")
    hv = c.groupby("situation_id").harvest_date.first()
    df = t.merge(w, left_on="situation_id", right_index=True, how="left").merge(hv, left_on="situation_id", right_index=True, how="left")
    for v in ["yield_14","protein_content","tsw_14"]:
        df[v] = pd.to_numeric(df[v], errors="coerce")
    for v in ["sowing_date","start_flo_date","end_flo_date","harvest_date"]:
        df[v] = pd.to_datetime(df[v], errors="coerce")
    df["dep"] = df.postal_code.astype(str).str.zfill(5).str[:2]
    df["season"] = df.pea_type.map({"SPRING":"Spring","WINTER":"Winter"})
    df["site_year"] = df.site_name + "_" + df.harvest_year.astype(str)
    df["trial"] = df.site_year + "_" + df.pea_type
    # julian day of year relative to Jan 1 of harvest year (sowing in autumn -> negative)
    base = pd.to_datetime(df.harvest_year.astype(str) + "-01-01")
    df["flo_doy"] = (df.start_flo_date - base).dt.days + 1
    df["sow_doy"] = (df.sowing_date - base).dt.days + 1
    df["harv_doy"] = (df.harvest_date - base).dt.days + 1
    df["irrig"] = df.irrigation_event_1.astype(str).str.lower().str.startswith("date")
    return t, c, df
if __name__ == "__main__":
    t, c, df = load(D)
    print(df.shape); print(df.dtypes.to_string())
    print(df[["yield_14","protein_content","flo_doy","sow_doy","harv_doy"]].describe().T)
    print(df.irrig.sum(), df.irrigation_event_1.value_counts().head())
    print(df.seed_prot.value_counts(dropna=False))
    print(df.management.value_counts().head(20))
