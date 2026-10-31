#!/bin/bash
# Run a shell command on the SoyMate box as ec2-user through SSM send-command and print its output.
# Non-interactive alternative to connect.sh (for agents and scripts). Needs AWS credentials (e.g. AWS_PROFILE).
# Usage: scripts/aws/run_remote.sh 'cd ~/soymate && ls data/raw'   [timeout seconds, default 600]
set -euo pipefail
export AWS_DEFAULT_REGION=us-east-1
INSTANCE_ID="${SOYMATE_INSTANCE_ID:-i-0bcbb68b41caea868}"
CMD="${1:?usage: run_remote.sh '<command>' [timeout]}"
TIMEOUT="${2:-600}"
# Ship the command base64-encoded so no layer (SSM, sh, sudo -i) re-parses it; run it as ec2-user with uv on PATH.
B64=$(printf 'export PATH=$HOME/.local/bin:$PATH\n%s\n' "$CMD" | base64 | tr -d '\n')
WRAPPED="echo $B64 | base64 -d | sudo -iu ec2-user bash"
PARAMS=$(python3 -c 'import json,sys; print(json.dumps({"commands":[sys.argv[1]],"executionTimeout":[sys.argv[2]]}))' "$WRAPPED" "$TIMEOUT")
ID=$(aws ssm send-command --instance-ids "$INSTANCE_ID" --document-name AWS-RunShellScript \
  --parameters "$PARAMS" --timeout-seconds 60 --query Command.CommandId --output text)
while :; do
  STATUS=$(aws ssm get-command-invocation --command-id "$ID" --instance-id "$INSTANCE_ID" \
    --query Status --output text 2>/dev/null || echo Pending)
  case "$STATUS" in Pending|InProgress|Delayed) sleep 2 ;; *) break ;; esac
done
aws ssm get-command-invocation --command-id "$ID" --instance-id "$INSTANCE_ID" --query StandardOutputContent --output text
ERR=$(aws ssm get-command-invocation --command-id "$ID" --instance-id "$INSTANCE_ID" --query StandardErrorContent --output text)
[ -n "$ERR" ] && [ "$ERR" != "None" ] && echo "--- stderr ---" >&2 && echo "$ERR" >&2
[ "$STATUS" = "Success" ]
