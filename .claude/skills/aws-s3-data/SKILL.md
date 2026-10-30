---
name: aws-s3-data
description: Use S3 in the Hack the Fork sandbox to store datasets, intermediate parquet files and backups, to read AWS Open Data anonymously, and to move data between laptop, EC2 and the bucket. Use whenever the user mentions S3, a bucket, aws s3 cp/sync, parquet in S3, pandas or pyarrow reading from S3, the Registry of Open Data, anonymous access, --no-sign-request, presigned URLs, or backing up data before the account is deleted.
---

# S3 for data and backups

Account rules (us-east-1 only, never public buckets, no personal data) are in `aws-hackathon-sandbox`.

## Bucket

Names are globally unique, 3 to 63 characters, lowercase. Use team initials plus a date, e.g. `fb-peasure-20261030`. Create it in us-east-1 and leave Block Public Access on (the default for new buckets):

```bash
aws s3 mb s3://fb-peasure-20261030 --region us-east-1
```

Use prefixes to organize: `raw/`, `interim/`, `processed/`, `models/`, `reports/`. Keep a `data/README` or manifest listing the source and license of every dataset (the jury and the rules ask for attribution).

## Move data (verified against the AWS CLI reference)

```bash
aws s3 cp local.parquet s3://BUCKET/processed/local.parquet
aws s3 sync ./data/processed s3://BUCKET/processed --exclude "*.tmp"
aws s3 sync s3://BUCKET ./backup --region us-east-1        # backup to laptop
aws s3 sync SRC DST --dryrun                                # preview first
```

`--delete` removes files at the destination that no longer exist at the source. Do not use it on a backup target unless that is exactly what you want.

## AWS Open Data (anonymous)

Public buckets are read without credentials. Many live outside us-east-1, so anonymous reads are the most reliable option from the sandbox:

```bash
aws s3 ls --no-sign-request s3://hestia-aggregated-data/
aws s3 cp --no-sign-request s3://<bucket>/<key> ./data/
```

Python:

```python
import boto3
from botocore import UNSIGNED
from botocore.config import Config

s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
# pandas via s3fs; needs `pip install s3fs`
import pandas as pd
df = pd.read_parquet("s3://bucket/path/file.parquet", storage_options={"anon": True})
```

Datasets named in the guide (check each dataset page on registry.opendata.aws for license, region and layout before relying on them): HESTIA `hestia-aggregated-data` (eu-west-2, CC BY 4.0), NASA POWER `nasa-power` (us-west-2), ESA WorldCover `esa-worldcover` (eu-central-1), UniProt, PDB, ESM Atlas, Sentinel-2, NOAA GHCN-D, iSDAsoil. Large datasets: copy only the subset you need into your own bucket in us-east-1.

Non-AWS sources (for example French open data portals) are downloaded with `curl`/`wget` on the EC2 box, then written to your bucket.

## Parquet from Python on EC2

With an instance profile or exported temporary credentials, `pandas`/`pyarrow` read and write `s3://` paths directly:

```python
df.to_parquet("s3://fb-peasure-20261030/processed/features.parquet", index=False)
```

For repeated reads, download once to local disk (`aws s3 cp`) and read locally; it is faster and avoids request overhead.

## Sharing a file without opening the bucket

Generate a time-limited link instead of making anything public:

```bash
aws s3 presign s3://BUCKET/reports/figure.png --expires-in 3600
```

## Backup checklist

- Final `aws s3 sync s3://BUCKET ./backup` to the laptop and a USB drive (the organizers explicitly recommend a USB stick), at least 3 hours before the end.
- Check sizes: GitHub rejects files over 100 MB, so large data goes to USB or a cloud drive, not git.
- Do not store anything personal in the bucket.
