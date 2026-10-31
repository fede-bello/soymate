# Deploying the SoyMate demo

Box: `i-0bcbb68b41caea868` (Amazon Linux 2023, us-east-1). nginx on port 80 serves the React build
(`demo/web/dist`) at `/` and proxies `/api/` to the FastAPI service `soymate-api` (uvicorn on 127.0.0.1:8000).
Config: `demo/deploy/nginx_soymate.conf`, installed as `/etc/nginx/conf.d/soymate.conf`.

Port 80 is open: the live demo is http://18.206.176.19 (public IPv4, changes if the instance is stopped and
started). The Session Manager tunnel below still works for private testing.

The API runs from `~/soymate-rel2` on the box (release 2, with the experimental bulk mode; repo layout with
`pipeline/`, `experiments/`, `demo/`; Python 3.12 venv in `~/soymate-rel2/.venv`, built with
`uv sync --locked --group baseline`; needs `mesa-libGL` for Ultralytics' opencv). The previous release
`~/soymate-next` and its venv are left untouched for rollback. Its `data/` is a symlink to `~/soymate/data`, the original copy that holds the
datasets, crops, features and `data/models/soymate-pooled-v1.joblib`. Unit: `demo/deploy/soymate-api.service`,
installed as `/etc/systemd/system/soymate-api.service`.

| File | What |
|---|---|
| `deploy.sh` | build, upload through S3, install nginx config and unit, restart, health check |
| `nginx_soymate.conf` | nginx site: static build at `/`, `/api/` proxied to 127.0.0.1:8000 |
| `soymate-api.service` | systemd unit: uvicorn `demo.api.main:app` from `~/soymate-next` |

## New release dir (how `~/soymate-rel2` was built)

Never modify the live code dir or its venv in place. Build a new one, test it on port 8001, then switch:

```bash
# box: repo copy (tarball through s3://.../code/rel2/), data symlink, own venv, examples, test instance
mkdir ~/soymate-rel2 && cd ~/soymate-rel2 && tar -xzf /tmp/repo.tgz && ln -sfn ~/soymate/data data
sudo dnf install -y mesa-libGL && uv sync --locked --group baseline
.venv/bin/python demo/api/build_examples.py && .venv/bin/python demo/api/make_thumbs.py
.venv/bin/uvicorn demo.api.main:app --host 127.0.0.1 --port 8001   # test, then stop it
# laptop: switch the unit and web build to the new dir
APP_DIR=soymate-rel2 AWS_PROFILE=soymate demo/deploy/deploy.sh
```

## Redeploy

```bash
AWS_PROFILE=soymate demo/deploy/deploy.sh               # npm ci + build, upload, install, restart
AWS_PROFILE=soymate demo/deploy/deploy.sh --skip-build  # reuse the existing demo/web/dist
```

What it does (safe to re-run):
1. Builds `demo/web` and uploads `dist` as `s3://fb-soymate-team4-258601136235/code/deploy/releases/web-<UTC ts>.tgz`,
   plus `demo/deploy/nginx_soymate.conf`, `demo/deploy/soymate-api.service` and the demo backend files (`demo/api/main.py`, `demo/api/make_thumbs.py`, `demo/API.md`).
2. On the box: copies the backend files into `~/soymate-next` (`APP_DIR` in the script), unpacks the web release into
   `/var/www/soymate/releases/<ts>` and points the symlink `/var/www/soymate/current` at it (keeps the last 5).
3. Runs `demo/api/make_thumbs.py` (480 px gallery thumbnails `<id>.thumb.jpg`; originals untouched), installs
   the systemd unit, `daemon-reload`, restarts `soymate-api` and waits for `/api/health`.
4. Installs nginx if needed, installs the config, `nginx -t`, enables and reloads nginx, prints
   `systemctl is-enabled nginx soymate-api` and a health check through nginx.

Model or other backend code changes (for example `demo/api/pipeline.py`) go to `~/soymate-next` through `s3://.../code/`; the script
only ships the files listed in `BACKEND_FILES`.

## Rollback

**One command** (restores the unit and web release that were live before the last `deploy.sh` run; the script is
written on the box by `deploy.sh` just before it switches):

```bash
AWS_PROFILE=soymate scripts/aws/run_remote.sh 'bash ~/rollback-soymate.sh'
```

After the release-2 switch this points the service back to `~/soymate-next` and the previous web build.

Frontend only (instant, no restart):

```bash
scripts/aws/run_remote.sh 'ls -1 /var/www/soymate/releases; readlink /var/www/soymate/current'
scripts/aws/run_remote.sh 'sudo ln -sfn releases/<previous ts> /var/www/soymate/current'
```

Backend files: check out the previous version locally (`git checkout <rev> -- demo/api/main.py`) and run
`demo/deploy/deploy.sh --skip-build`, or copy the file back and `sudo systemctl restart soymate-api`.

Back to the pre-restructure code dir (`~/soymate`, old layout, still intact): edit the unit to
`WorkingDirectory=/home/ec2-user/soymate` and `ExecStart=/home/ec2-user/soymate/.venv/bin/uvicorn app.api.main:app ...`,
then `sudo systemctl daemon-reload && sudo systemctl restart soymate-api`.

Remove nginx entirely: `sudo systemctl disable --now nginx && sudo rm /etc/nginx/conf.d/soymate.conf`.

## Test privately (Session Manager tunnel)

```bash
AWS_PROFILE=soymate aws ssm start-session --region us-east-1 --target i-0bcbb68b41caea868 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["80"],"localPortNumber":["8080"]}'
# then open http://localhost:8080 ; Ctrl+C closes the tunnel
```

## Opening public access later (documented only, not run)

Decide first with the team. Prefer a single IP (`/32`) over the whole internet. Find your current IP with
`curl -s https://checkip.amazonaws.com`.

Single IP:

```bash
AWS_PROFILE=soymate aws ec2 authorize-security-group-ingress --region us-east-1 \
  --group-id sg-0cba683a99bc47999 --protocol tcp --port 80 --cidr 203.0.113.7/32
```

Everyone (public demo):

```bash
AWS_PROFILE=soymate aws ec2 authorize-security-group-ingress --region us-east-1 \
  --group-id sg-0cba683a99bc47999 --protocol tcp --port 80 --cidr 0.0.0.0/0
```

Then the demo is at `http://<public DNS or IP>/`:

```bash
AWS_PROFILE=soymate aws ec2 describe-instances --region us-east-1 --instance-ids i-0bcbb68b41caea868 \
  --query 'Reservations[0].Instances[0].[PublicDnsName,PublicIpAddress]' --output text
```

Revoke (same CIDR you opened):

```bash
AWS_PROFILE=soymate aws ec2 revoke-security-group-ingress --region us-east-1 \
  --group-id sg-0cba683a99bc47999 --protocol tcp --port 80 --cidr 0.0.0.0/0      # or 203.0.113.7/32
```

Check what is open: `aws ec2 describe-security-groups --region us-east-1 --group-ids sg-0cba683a99bc47999
--query 'SecurityGroups[0].IpPermissions'`.
