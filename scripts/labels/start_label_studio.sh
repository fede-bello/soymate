#!/bin/bash
# Start Label Studio locally (laptop) for the seed point labelling. Data stays on this machine.
# 1. Fetch the images:  AWS_PROFILE=soymate aws s3 sync s3://fb-soymate-team4-258601136235/labels/ data/labels/
# 2. Run this script, open http://localhost:8080, sign up locally (any email, stays on this laptop).
# 3. Create project "soymate-seeds", Settings > Labeling Interface > Code: paste scripts/labels/label_config.xml.
# 4. Import: drag the 3 files from data/labels/images/. Label (keys 1-7, click the seed centre).
# 5. Export as JSON to data/labels/export.json, then: uv run python scripts/labels/convert_export.py
set -euo pipefail
cd "$(dirname "$0")/../.."
export LABEL_STUDIO_BASE_DATA_DIR="$PWD/data/labels/label_studio"
exec uvx --python 3.12 label-studio start --port 8080 --no-browser
