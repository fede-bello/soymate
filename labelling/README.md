# labelling/

Hand-labelling of real multi-seed photos for lot-level ground truth (critique C2): one point per seed with its
class, in Label Studio. Points, not our segmentation, so the reference count does not depend on our pipeline.

| File | What |
|---|---|
| `prepare_labelling.py` | Picks the photos or regions to label; writes `data/labels/images/*.jpg`, `tasks.json` (Label Studio import) and `regions.csv` (maps regions back to the source photo) |
| `label_config.xml` | Label Studio interface: point labels, keys 1-7 for the classes |
| `start_label_studio.sh` | Starts Label Studio locally on the laptop (data stays local), with the steps in its header |
| `convert_export.py` | Label Studio JSON export to `data/labels/points.csv` (one row per point) and per-region counts with Wilson 95 % CIs |

```bash
cd ~/soymate-next && uv run python labelling/prepare_labelling.py            # box
AWS_PROFILE=soymate aws s3 sync s3://fb-soymate-team4-258601136235/labels/ data/labels/   # laptop
labelling/start_label_studio.sh                                              # laptop, http://localhost:8080
uv run python labelling/convert_export.py data/labels/export.json            # after exporting
```

Status: the lot-level comparison on these labels is still pending (`results/provenance.md`).
