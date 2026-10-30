---
name: aws-iam-instance-profile
description: Give an EC2 instance permissions (S3, Bedrock, Session Manager) in the Hack the Fork sandbox through an IAM role and instance profile, without putting credentials on the box. Use whenever the user hits "Unable to locate credentials" or AccessDenied on EC2, wants the instance to read or write S3 or call Bedrock, cannot connect with Session Manager, needs an iam-instance-profile for run-instances, gets denied on iam:CreateRole or iam:PassRole, or asks how credentials should reach EC2.
---

# IAM role and instance profile for EC2

Sandbox rules are in `aws-hackathon-sandbox`. The point of this skill: the instance gets temporary credentials from its role automatically, so nothing secret is ever copied onto it or committed. The event's temporary CLI credentials expire and must not be baked into user-data, AMIs or git.

## Key concept (verified in the IAM docs)

A role reaches an EC2 instance through an **instance profile**. In the console, creating an EC2 role also creates a profile with the same name. With the CLI, the role and the profile are **separate actions**, and you must create the profile and add the role to it yourself.

## Step 0: look for what already exists

The sandbox template may ship a ready-made role or profile, and may block creating new ones. Check before creating:

```bash
aws iam list-instance-profiles --query 'InstanceProfiles[].[InstanceProfileName,Roles[0].RoleName]' --output table
aws iam list-roles --query 'Roles[?contains(RoleName, `ec2`) || contains(RoleName, `EC2`) || contains(RoleName, `SSM`)].RoleName' --output text
```

If a profile with S3 and SSM permissions exists, pass its name to `run-instances --iam-instance-profile Name=<name>` and stop here.

## Step 1: create it (if allowed)

```bash
cat > trust.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
JSON

aws iam create-role --role-name peasure-ec2-role --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name peasure-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam create-instance-profile --instance-profile-name peasure-ec2-profile
aws iam add-role-to-instance-profile --instance-profile-name peasure-ec2-profile --role-name peasure-ec2-role
```

`AmazonSSMManagedInstanceCore` is what lets Session Manager reach the instance. For the bucket, prefer an inline policy limited to your bucket over a broad managed policy:

```bash
aws iam put-role-policy --role-name peasure-ec2-role --policy-name s3-team-bucket --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": "arn:aws:s3:::BUCKET"},
    {"Effect": "Allow", "Action": ["s3:GetObject","s3:PutObject"], "Resource": "arn:aws:s3:::BUCKET/*"}
  ]
}'
```

To call Bedrock from the instance add `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` (the Converse API is authorized by these two actions). Scope `Resource` to `*` if inference profiles make ARNs awkward; this is a throwaway sandbox.

IAM is eventually consistent: wait 10 to 20 seconds after creating the profile before `run-instances`, or the launch can fail with "Invalid IAM Instance Profile name".

Attach to a running instance that was launched without one:

```bash
aws ec2 associate-iam-instance-profile --region us-east-1 --instance-id i-xxxx \
  --iam-instance-profile Name=peasure-ec2-profile
```

## Step 2: verify from the instance

```bash
aws sts get-caller-identity          # should show the assumed role, no keys configured
aws s3 ls s3://BUCKET
```

No `aws configure` needed. If it says "Unable to locate credentials", the profile is not attached yet.

## If role creation is denied

The sandbox policy may block `iam:CreateRole` or `iam:PassRole`. Then, in this order:
1. Look for a pre-created profile (Step 0, or the IAM console, or the event outputs page).
2. Use CloudShell or Kiro: they run with the account's console permissions and need no keys. Process data there or push it to S3 from there.
3. Ask the organizers early (WhatsApp contact in `aws-hackathon-sandbox`); do not work around it by pasting the event's temporary keys into the instance or into git.
4. Last resort for a short job only: export the temporary keys as environment variables in your own SSH or SSM session (not in files, not in user-data) and expect them to expire.

## Security habits

- Least privilege on the inline policy (one bucket, only the actions you use).
- No keys in code, notebooks, prompts or `.env` files committed to git.
- Delete nothing the template created.
