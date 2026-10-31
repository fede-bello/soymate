#!/bin/bash
# EC2 first-boot script (runs as root via cloud-init). Log: /var/log/cloud-init-output.log
set -euxo pipefail
dnf install -y git tmux htop unzip rsync gcc gcc-c++ make
# uv for ec2-user (Python itself is managed by uv, see scripts/aws/bootstrap.sh)
sudo -u ec2-user bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
touch /var/lib/cloud/instance/soymate-userdata-done
