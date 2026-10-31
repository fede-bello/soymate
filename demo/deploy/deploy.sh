#!/bin/bash
# Build the SoyMate web app, ship it with the demo backend files to the box through S3, install nginx and the
# systemd unit, regenerate gallery thumbnails, restart soymate-api and reload nginx. Safe to re-run.
# Usage (repo root, AWS credentials for the team account):
#   AWS_PROFILE=soymate demo/deploy/deploy.sh               # build + deploy
#   AWS_PROFILE=soymate demo/deploy/deploy.sh --skip-build  # deploy the existing demo/web/dist
# Does not touch security groups or any network exposure (see demo/deploy/README.md).
set -euo pipefail
export AWS_DEFAULT_REGION=us-east-1
cd "$(dirname "$0")/../.."  # repo root

BUCKET="s3://fb-soymate-team4-258601136235/code"
REL="$(date -u +%Y%m%dT%H%M%SZ)"
APP_DIR="soymate-next"  # code dir under /home/ec2-user on the box; must match demo/deploy/soymate-api.service
BACKEND_FILES=(demo/api/main.py demo/api/make_thumbs.py demo/API.md)

if [ "${1:-}" != "--skip-build" ]; then
  (cd demo/web && npm ci && npm run build)
fi
[ -f demo/web/dist/index.html ] || { echo "demo/web/dist/index.html missing: build first" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
COPYFILE_DISABLE=1 tar --no-xattrs -C demo/web/dist -czf "$TMP/web.tgz" .  # no macOS xattr headers
aws s3 cp --only-show-errors "$TMP/web.tgz" "$BUCKET/deploy/releases/web-$REL.tgz"
aws s3 cp --only-show-errors demo/deploy/nginx_soymate.conf "$BUCKET/deploy/nginx_soymate.conf"
aws s3 cp --only-show-errors demo/deploy/soymate-api.service "$BUCKET/deploy/soymate-api.service"
for f in "${BACKEND_FILES[@]}"; do aws s3 cp --only-show-errors "$f" "$BUCKET/$f"; done
echo "uploaded release $REL"

scripts/aws/run_remote.sh "$(cat <<REMOTE
set -euo pipefail
B=$BUCKET; REL=$REL
cd ~/$APP_DIR
for f in ${BACKEND_FILES[*]}; do aws s3 cp --only-show-errors "\$B/\$f" "\$f"; done

# Web release: /var/www/soymate/releases/<ts>, served through the 'current' symlink; keep the last 5.
sudo mkdir -p /var/www/soymate/releases/\$REL
aws s3 cp --only-show-errors "\$B/deploy/releases/web-\$REL.tgz" /tmp/web-\$REL.tgz
sudo tar -C /var/www/soymate/releases/\$REL -xzf /tmp/web-\$REL.tgz && rm -f /tmp/web-\$REL.tgz
sudo chmod -R a+rX /var/www/soymate
sudo ln -sfn releases/\$REL /var/www/soymate/current
ls -1d /var/www/soymate/releases/* | head -n -5 | xargs -r sudo rm -rf

# Gallery thumbnails (originals untouched), then install the unit, restart the API and wait for it.
.venv/bin/python demo/api/make_thumbs.py
aws s3 cp --only-show-errors "\$B/deploy/soymate-api.service" /tmp/soymate-api.service
sudo install -m 644 /tmp/soymate-api.service /etc/systemd/system/soymate-api.service && rm -f /tmp/soymate-api.service
sudo systemctl daemon-reload
sudo systemctl enable soymate-api
sudo systemctl restart soymate-api
for i in \$(seq 1 60); do curl -sf 127.0.0.1:8000/api/health >/dev/null && break; sleep 2; done

# nginx
rpm -q nginx >/dev/null || sudo dnf install -y -q nginx
aws s3 cp --only-show-errors "\$B/deploy/nginx_soymate.conf" /tmp/soymate.conf
sudo install -m 644 /tmp/soymate.conf /etc/nginx/conf.d/soymate.conf && rm -f /tmp/soymate.conf
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx

echo "enabled: \$(systemctl is-enabled nginx soymate-api | tr '\n' ' ')"
echo "active:  \$(systemctl is-active nginx soymate-api | tr '\n' ' ')"
echo "current: \$(readlink /var/www/soymate/current)"
curl -sf http://127.0.0.1/api/health && echo
curl -s -o /dev/null -w "index.html via nginx: %{http_code}\n" http://127.0.0.1/
REMOTE
)" 600
