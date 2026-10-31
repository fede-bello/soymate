#!/bin/bash
# Build the SoyMate web app, ship it with the demo backend files to the box through S3, install nginx,
# regenerate gallery thumbnails, restart soymate-api and reload nginx. Safe to re-run.
# Usage (repo root, AWS credentials for the team account):
#   AWS_PROFILE=soymate deploy/deploy.sh               # build + deploy
#   AWS_PROFILE=soymate deploy/deploy.sh --skip-build  # deploy the existing app/web/dist
# Does not touch security groups or any network exposure (see deploy/README.md).
set -euo pipefail
export AWS_DEFAULT_REGION=us-east-1
cd "$(dirname "$0")/.."

BUCKET="s3://fb-soymate-team4-258601136235/code"
REL="$(date -u +%Y%m%dT%H%M%SZ)"
BACKEND_FILES=(app/api/main.py app/api/make_thumbs.py app/API.md)

if [ "${1:-}" != "--skip-build" ]; then
  (cd app/web && npm ci && npm run build)
fi
[ -f app/web/dist/index.html ] || { echo "app/web/dist/index.html missing: build first" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
COPYFILE_DISABLE=1 tar --no-xattrs -C app/web/dist -czf "$TMP/web.tgz" .  # no macOS xattr headers
aws s3 cp --only-show-errors "$TMP/web.tgz" "$BUCKET/deploy/releases/web-$REL.tgz"
aws s3 cp --only-show-errors deploy/nginx_soymate.conf "$BUCKET/deploy/nginx_soymate.conf"
for f in "${BACKEND_FILES[@]}"; do aws s3 cp --only-show-errors "$f" "$BUCKET/$f"; done
echo "uploaded release $REL"

scripts/aws/run_remote.sh "$(cat <<REMOTE
set -euo pipefail
B=$BUCKET; REL=$REL
cd ~/soymate
for f in ${BACKEND_FILES[*]}; do aws s3 cp --only-show-errors "\$B/\$f" "\$f"; done

# Web release: /var/www/soymate/releases/<ts>, served through the 'current' symlink; keep the last 5.
sudo mkdir -p /var/www/soymate/releases/\$REL
aws s3 cp --only-show-errors "\$B/deploy/releases/web-\$REL.tgz" /tmp/web-\$REL.tgz
sudo tar -C /var/www/soymate/releases/\$REL -xzf /tmp/web-\$REL.tgz && rm -f /tmp/web-\$REL.tgz
sudo chmod -R a+rX /var/www/soymate
sudo ln -sfn releases/\$REL /var/www/soymate/current
ls -1d /var/www/soymate/releases/* | head -n -5 | xargs -r sudo rm -rf

# Gallery thumbnails (originals untouched), then restart the API and wait for it.
.venv/bin/python app/api/make_thumbs.py
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
