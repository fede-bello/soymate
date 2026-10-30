---
name: aws-ec2-compute
description: Launch and use EC2 instances in the Hack the Fork sandbox (us-east-1, CPU only, below 6xlarge) for heavy data processing, CPU model training (LightGBM, scikit-learn, statsmodels) and hosting a Streamlit demo with a public URL. Use whenever the user wants to download or process large files (e.g. SAFRAN climate data), train a model on AWS, run a long job, host a Streamlit/web app, connect to an instance, or asks about instance types, AMIs, security groups, Session Manager or user-data. Also use for SageMaker notebook questions, since EC2 is the preferred path here.
---

# EC2 in the hackathon sandbox

Read `aws-hackathon-sandbox` first for the account limits. Summary: us-east-1 only, no GPU, nothing 6xlarge or larger, no Marketplace AMIs, no domain purchase, account deleted after the event.

## Choosing the instance

CPU work (pandas, pyarrow, LightGBM, sklearn, mixed models) does not need a GPU. Pick by memory:

| Need | Start with |
|---|---|
| Streamlit demo, light scripts | `t3.medium` (2 vCPU, 4 GiB) or `t3.large` |
| Data wrangling on a few GB | `m6i.xlarge` / `m7i.xlarge` (16 GiB) |
| Larger joins, many parallel folds | `m6i.4xlarge` (64 GiB) or `c6i.4xlarge` |

Stay at `4xlarge` or below. Stop (do not terminate) instances you are not using; the 72 h clock keeps running either way. Check the types the account actually allows with `aws ec2 describe-instance-type-offerings --region us-east-1` if a launch is denied.

## Get the AMI

Use the public SSM parameter so you always get the current Amazon Linux 2023 image (verified in the AWS docs; `kernel-default` is the current path, with `-x86_64` or `-arm64`):

```bash
AMI=$(aws ssm get-parameter --region us-east-1 \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' --output text)
```

Pair an x86_64 AMI with x86 types (`t3`, `m6i`, `c6i`). Graviton types (`t4g`, `m7g`) need the arm64 parameter. Ubuntu is fine too if the team prefers it; avoid Marketplace listings.

## Launch (CLI sketch)

Keep these commands in a script in the repo (`scripts/ec2_launch.sh`) so the setup is reproducible.

```bash
aws ec2 create-security-group --region us-east-1 --group-name peasure-sg \
  --description "peasure demo" --vpc-id <default-vpc-id>
# Streamlit demo on 8501. Open to the world only because it is a throwaway public demo.
aws ec2 authorize-security-group-ingress --region us-east-1 --group-id <sg-id> \
  --protocol tcp --port 8501 --cidr 0.0.0.0/0

aws ec2 run-instances --region us-east-1 \
  --image-id "$AMI" --instance-type m6i.xlarge \
  --security-group-ids <sg-id> \
  --iam-instance-profile Name=<profile-with-AmazonSSMManagedInstanceCore-and-S3-access> \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=100,VolumeType=gp3}' \
  --user-data file://scripts/ec2_bootstrap.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=peasure-work}]'
```

Notes:
- Default root volume is small (8 GiB). Size it for the data (SAFRAN is about 4.9 GB compressed, give it 100 GiB).
- Prefix resource names with a feature or person name; the whole team shares the account.
- IAM role creation may be restricted in the sandbox. If `create-role` is denied, look in the IAM console for a pre-created instance profile, or ask the organizers. Without an instance profile you can still use `aws configure` style env vars with the temporary credentials, but never bake credentials into the AMI, user-data or git.

## Connect

Preferred: Session Manager (no SSH key, no open port 22). Needs the instance profile with `AmazonSSMManagedInstanceCore` and the Session Manager plugin on your laptop:

```bash
aws ssm start-session --region us-east-1 --target i-xxxxxxxxxxxx
```

Fallback: a key pair (`aws ec2 create-key-pair`, save the `.pem` outside git) and `ssh -i key.pem ec2-user@<public-dns>`; this needs port 22 in the security group.

## Bootstrap script

`scripts/ec2_bootstrap.sh` (user-data runs as root on first boot; log goes to `/var/log/cloud-init-output.log`):

```bash
#!/bin/bash
set -euxo pipefail
dnf install -y git python3.12 python3.12-pip
sudo -u ec2-user bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
```

Then as `ec2-user`: `git clone` the repo (public repo or a fine-grained token entered interactively, never stored in git), `uv sync`, run the job. If `python3.12` is not available in the AL2023 repos at the time, use `uv python install 3.12` instead, which does not depend on dnf.

## Long jobs

Run inside `tmux` or with `nohup ... &` so a dropped session does not kill them. Write intermediate outputs (parquet) to S3 as they finish (`aws s3 cp`), not only to the instance disk, so a stopped or lost instance costs nothing. See `aws-s3-data`.

## Hosting the Streamlit demo

```bash
uv run streamlit run app/streamlit_app.py \
  --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

Public URL: `http://<instance-public-dns>:8501`. Keep it alive with `tmux`, or a systemd unit. The address changes if the instance is stopped and started (no Elastic IP planning needed for 72 h, but re-read the DNS after a restart). The URL disappears with the account, so record a demo video and screenshots before the end.

If the team prefers a managed front door: ECS on Fargate or Amplify are on the allowlist; App Runner is not.

## SageMaker notebooks (alternative)

CPU instances only. Useful if the team likes JupyterLab, but an EC2 box plus `uv` is simpler to script and to back up. If used, export each `.ipynb` (File, Download) and copy data to S3.
