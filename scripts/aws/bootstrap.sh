#!/bin/bash
# Run on the EC2 box as ec2-user (via SSM). Idempotent: safe to re-run.
# Pulls the project code from S3, installs Python deps with uv, caches the DINOv2 weights.
set -euxo pipefail
export PATH="$HOME/.local/bin:$PATH"
export AWS_DEFAULT_REGION=us-east-1
BUCKET="${BUCKET:-fb-soymate-team4-258601136235}"
PROJ="$HOME/soymate"

mkdir -p "$PROJ" "$PROJ/data"
aws s3 sync "s3://$BUCKET/code/" "$PROJ/" --exclude "data/*" --only-show-errors

cd "$PROJ"
uv python install 3.14
uv sync --locked              # creates $PROJ/.venv from pyproject.toml

# Cache DINOv2 weights (small, base) so first use does not stall on a download.
uv run python - <<'PY'
from transformers import AutoModel, AutoImageProcessor
for name in ("facebook/dinov2-small", "facebook/dinov2-base"):
    AutoImageProcessor.from_pretrained(name)
    AutoModel.from_pretrained(name)
    print("cached", name)
PY

uv run python -c "import torch, cv2, sklearn, streamlit; print('torch', torch.__version__, 'threads', torch.get_num_threads())"
echo "BOOTSTRAP DONE"
