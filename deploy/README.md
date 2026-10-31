# Deploying the SoyMate demo

Box: `i-0bcbb68b41caea868` (Amazon Linux 2023, us-east-1). nginx on port 80 serves the React build
(`app/web/dist`) at `/` and proxies `/api/` to the FastAPI service `soymate-api` (uvicorn on 127.0.0.1:8000).
Config: `deploy/nginx_soymate.conf`, installed as `/etc/nginx/conf.d/soymate.conf`.

The port is **not public**: the security group `sg-0cba683a99bc47999` has no rule for port 80. Test through
a Session Manager tunnel (below) until the team decides to open it.

## Redeploy

```bash
AWS_PROFILE=soymate deploy/deploy.sh               # npm ci + build, upload, install, restart
AWS_PROFILE=soymate deploy/deploy.sh --skip-build  # reuse the existing app/web/dist
```

What it does (safe to re-run):
1. Builds `app/web` and uploads `dist` as `s3://fb-soymate-team4-258601136235/code/deploy/releases/web-<UTC ts>.tgz`,
   plus `deploy/nginx_soymate.conf` and the demo backend files (`app/api/main.py`, `app/api/make_thumbs.py`, `app/API.md`).
2. On the box: copies the backend files into `~/soymate`, unpacks the web release into
   `/var/www/soymate/releases/<ts>` and points the symlink `/var/www/soymate/current` at it (keeps the last 5).
3. Runs `app/api/make_thumbs.py` (480 px gallery thumbnails `<id>.thumb.jpg`; originals untouched), restarts
   `soymate-api` and waits for `/api/health`.
4. Installs nginx if needed, installs the config, `nginx -t`, enables and reloads nginx, prints
   `systemctl is-enabled nginx soymate-api` and a health check through nginx.

Model or other backend code changes still go to `~/soymate` through `s3://.../code/` as before; the script
only ships the files listed in `BACKEND_FILES`.

## Rollback

Frontend (instant, no restart):

```bash
scripts/aws/run_remote.sh 'ls -1 /var/www/soymate/releases; readlink /var/www/soymate/current'
scripts/aws/run_remote.sh 'sudo ln -sfn releases/<previous ts> /var/www/soymate/current'
```

Backend files: check out the previous version locally (`git checkout <rev> -- app/api/main.py`) and run
`deploy/deploy.sh --skip-build`, or copy the file back and `sudo systemctl restart soymate-api`.

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
