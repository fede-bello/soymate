#!/bin/bash
# Open a shell on the SoyMate EC2 box through Session Manager (no SSH key, no open port).
# Needs fresh temporary AWS credentials exported in this terminal (see docs/aws_setup.md).
# Usage:
#   scripts/aws/connect.sh                # interactive shell (as ssm-user; run `sudo -iu ec2-user`)
#   scripts/aws/connect.sh forward 8501   # forward a remote port to localhost (Streamlit 8501, Jupyter 8888)
set -euo pipefail
export AWS_DEFAULT_REGION=us-east-1
INSTANCE_ID="${SOYMATE_INSTANCE_ID:-i-0bcbb68b41caea868}"

if [ "${1:-}" = "forward" ]; then
  PORT="${2:?usage: connect.sh forward <port>}"
  exec aws ssm start-session --target "$INSTANCE_ID" \
    --document-name AWS-StartPortForwardingSession \
    --parameters "{\"portNumber\":[\"$PORT\"],\"localPortNumber\":[\"$PORT\"]}"
fi
exec aws ssm start-session --target "$INSTANCE_ID"
