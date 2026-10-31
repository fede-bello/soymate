# AWS dev box for SoyMate

A big CPU machine in the team's hackathon AWS account, set up on 2026-10-31 so nobody has to train or process data on a laptop battery. Everything here is CPU only (the sandbox blocks GPUs, see `.claude/skills/aws-hackathon-sandbox/SKILL.md`).

**The account is deleted when the event window closes (up to 72 h after start). Nothing in it is recoverable.** Back up as described at the end.

## What exists

| Thing | Value |
|---|---|
| Account | Team 4, `258601136235`, region **us-east-1 only** |
| Instance | `i-0bcbb68b41caea868`, name `soymate-dev`, **c7i.4xlarge** (16 vCPU, 32 GiB RAM), Amazon Linux 2023, 200 GiB gp3 disk |
| Why not bigger | 8xlarge and up are explicitly denied by the sandbox policy (checked with a dry run). 4xlarge is the largest we can launch |
| Network | Default VPC, security group `soymate-sg` (`sg-0cba683a99bc47999`) with no SSH rule: shell access is only through AWS Session Manager (no SSH key). Port 80 is open for the live demo (http://18.206.176.19, see `demo/deploy/README.md`) |
| IAM | Role `soymate-ec2-role` via instance profile `soymate-ec2-profile`: Session Manager, read/write on the team bucket, Bedrock invoke. The box has no stored keys; it gets temporary credentials from the role |
| Bucket | `s3://fb-soymate-team4-258601136235` (private). `code/` holds the repo copy used to bootstrap the box |
| Other boxes in the account | Two 8xlarge instances created by the event template (Kiro and VS Code Server). Not ours, do not touch |

## Connect

You need fresh temporary credentials from the Workshop Studio event page (they expire; copy them again when a command says `ExpiredToken`). Paste the `export AWS_...` block into your terminal, then:

```bash
aws sts get-caller-identity          # must print account 258601136235
scripts/aws/connect.sh               # shell on the box (Session Manager)
sudo -iu ec2-user                    # become the user that owns everything
cd ~/soymate-next                    # current repo layout (the demo runs from here)
```

Requirements on your laptop: AWS CLI v2 and the Session Manager plugin (`brew install --cask session-manager-plugin`; already installed on Fede's Mac). If your terminal has an old SSO profile, run `unset AWS_PROFILE` first.

Open the web apps running on the box from your laptop (port forwarding, nothing is exposed publicly):

```bash
scripts/aws/connect.sh forward 8001   # a test API started on port 8001 -> http://localhost:8001
scripts/aws/connect.sh forward 8888   # JupyterLab -> http://localhost:8888
```

On the box:

```bash
cd ~/soymate-next
uv run jupyter lab --no-browser --ip 127.0.0.1 --port 8888     # prints a token URL
```

Use `tmux` (installed) so jobs survive a dropped connection: `tmux new -s work`, detach with `Ctrl-b d`, return with `tmux attach -t work`.

The public demo (nginx on port 80, API service `soymate-api`) is documented in `demo/deploy/README.md`.

## What is inside the box

Everything lives under `/home/ec2-user/`:

```
~/soymate-next/             copy of this repo in the current layout (NOT a git clone); the demo API runs from here
  pyproject.toml            dependency list, resolved into ~/soymate-next/.venv by uv (Python 3.12)
  .venv/                    Python environment (use `uv run ...`, or `source .venv/bin/activate`)
  pipeline/ experiments/    data pipeline and experiments (see the top-level README)
  demo/                     demo API and web app; systemd unit soymate-api runs demo.api.main from here
  data -> ~/soymate/data    symlink to the original copy's data
~/soymate/                  original copy in the pre-restructure layout (app/, eval/, scripts/data/); keep it, it holds data/
  data/raw/                 downloaded datasets (git-ignored), plus MANIFEST.json
  data/{splits,crops,features,models}/   pipeline outputs and the demo model
~/logs/                     bootstrap.log, download.log
~/.local/bin/uv             uv (Python and package manager)
~/.cache/huggingface/       cached DINOv2 weights (facebook/dinov2-small and dinov2-base)
```

`pyproject.toml` allows Python 3.12 to 3.14; the box venv is 3.12, laptops may use 3.14. OpenCV is the headless build (the box has no libGL). Dependencies (see `pyproject.toml`) include numpy, pandas, pyarrow, scipy, scikit-learn, statsmodels, scikit-image, pillow, **torch and torchvision (CPU build on Linux)**, transformers, huggingface_hub, matplotlib, plotly, streamlit, jupyterlab, boto3, requests. System tools: git, tmux, htop, unzip, rsync, gcc. Optional extra not installed: `uv sync --extra seg` adds cellpose for touching-grain separation.

The box is a copy, not a git checkout. To push code to GitHub from the box, `git init`/clone there and use a fine-grained token limited to the team repo (never store it in a file in the repo). The simplest flow is to edit on your laptop, then re-sync:

```bash
# laptop (credentials exported)
aws s3 sync . s3://fb-soymate-team4-258601136235/code/ --exclude ".git/*" --exclude "archive/*" --exclude "data/*" --exclude ".claude/*" --exclude "*.pdf" --exclude ".DS_Store"
# box
cd ~/soymate-next && aws s3 sync s3://fb-soymate-team4-258601136235/code/ . --exclude "data/*" && uv sync
```

## Datasets (in `~/soymate/data/raw/`)

Downloaded by `pipeline/download_datasets.py` (re-runnable, skips what is complete). Sizes, licences and source URLs are in `data/raw/MANIFEST.json`; the licences and the "declare as prior resource" list are in `CONTEXT.md` sections 6 and 14.

| Folder | What | Licence |
|---|---|---|
| `soybean_v1/` | (2,693 images) Mendeley d97rjyk2tz v1: `Train.zip`, `Validation.zip`, `Test.zip` and their extracted folders. **Keeps the original file names needed to group by original photo** | CC BY 4.0 |
| `soybean_v2/` | (2,726 images) Same dataset v2: `Soybean_Seed_Dataset.zip` and extracted | CC BY 4.0 |
| `soybean_seeds_5classes/` | (5,518 images in 6 folders: 1,201 / 1,127 / 1,125 / 1,058 / 1,002 / 5) Mendeley v6vzvfszj6 (Lin et al.), loose JPEG crops. **Subfolders are Mendeley folder ids, not class names** (the API does not give names). Map them to intact / spotted / immature / broken / skin-damaged by looking at a few images and the dataset page, then rename | CC BY 4.0 |
| `grainset_tiny/` | (13,160 images; wheat/maize/sorghum/rice under `GrainSet-tiny/tiny_data/`) GrainSet tiny (figshare 22989029) | CC BY 4.0 |
| `grainset_raw/` | GrainSet raw (figshare 24137472), 3.4 GB zip | CC BY 4.0 |
| `pea_zenodo/` | (5 images) Zenodo 21110940, pea segmentation demo subset (5 photos, LabelMe polygons) | CC BY 4.0 |
| `faba_zenodo/` | (78 images) Zenodo 18226381, faba bean photos on blue background | CC BY 4.0 |
| `corn1000/` | Hugging Face `SmartFarmingLab/corn1000`, about 9 GB, phone photos with counts | CC BY-NC 4.0 |
| `radio_lentille/` | **Not downloaded.** `JeanEudesH/Radio_lentille` is gated: log in to Hugging Face, accept the terms on the dataset page, create a read token, then on the box `HF_TOKEN=hf_... uv run python pipeline/download_datasets.py radio_lentille` (type the token in your own session only, never in a file) | MIT |

The leak-free split is **not** a download: it is `research/soybean_bruchid/resplit_by_original.csv` in this repo (and on the box under `~/soymate/research/`). It must be declared as a prior resource.

Re-run or fetch one dataset: `cd ~/soymate-next && uv run python pipeline/download_datasets.py grainset_raw`.

## Compute notes

- Measured on this box (2026-10-31, batch of 64 images at 224 px, while a download was running): **dinov2-small about 32 images/s, dinov2-base about 11 images/s**. So GrainSet tiny (13,160 images) takes roughly 7 min with small and 20 min with base; soybean (about 2,700 images) takes 1.5 to 4 min. These are single-run numbers, not a benchmark.
- DINOv2 feature extraction is the heavy step. PyTorch uses 8 threads on this box (physical cores). Batch the images, use `torch.inference_mode()`, and start with `dinov2-small` to time it, then `dinov2-base`. Save features to parquet or `.npy` under `data/` (and copy to S3), so the classifier and the transfer curve never recompute them.
- The linear classifier and the 5/10/25/50-grain curve are cheap; run them anywhere.
- Cost is not a concern (the account is free), but stop the instance when you are not using it if you want to keep it quiet: `aws ec2 stop-instances --instance-ids i-0bcbb68b41caea868` (disk and files stay; `start-instances` brings it back, services and tmux sessions do not survive a stop).

## Back up (the account will be erased)

1. Code and results: push to the team GitHub repo from your laptop, at least hourly.
2. Features, models, figures, own photos: `aws s3 sync ~/soymate/data/derived s3://fb-soymate-team4-258601136235/derived/` from the box (create the folder you use), and from the laptop `aws s3 sync s3://fb-soymate-team4-258601136235 ./backup --exclude "code/*"`.
3. Public datasets do not need backing up (the URLs are in the manifest). Our own photos and anything labelled by hand do.
4. Record the demo video and screenshots while the app still runs. Sunday 12:00 is the deadline in the plan; do the final export 3 hours before the end.
5. The temporary credentials in your terminal are secrets: never put them in a file, in git or in a chat shared outside the team.

## Rebuild from zero (if the box is lost)

```bash
# laptop, credentials exported; the role, profile, SG and bucket already exist
AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
aws ec2 run-instances --image-id "$AMI" --instance-type c7i.4xlarge \
  --security-group-ids sg-0cba683a99bc47999 --subnet-id subnet-012f52529fb1e3c4e \
  --iam-instance-profile Name=soymate-ec2-profile \
  --metadata-options HttpTokens=required,HttpEndpoint=enabled \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=200,VolumeType=gp3,DeleteOnTermination=true}' \
  --user-data file://scripts/aws/user_data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=soymate-dev}]'
# then, once it shows in `aws ssm describe-instance-information`, connect and run:
aws s3 cp s3://fb-soymate-team4-258601136235/code/scripts/aws/bootstrap.sh ~/ && bash ~/bootstrap.sh
cd ~/soymate-next && uv run python pipeline/download_datasets.py
```

Update `INSTANCE_ID` in `scripts/aws/connect.sh` (or export `SOYMATE_INSTANCE_ID`) for the new instance.
