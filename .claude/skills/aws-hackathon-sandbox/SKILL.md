---
name: aws-hackathon-sandbox
description: Rules and limits of the Hack the Fork AWS sandbox account (Workshop Studio, us-east-1 only, 72 h, Bedrock model allowlist, no GPU, no personal data, backup duty). Use this skill before suggesting or running ANY AWS command, service, instance type or Bedrock model in this project, and whenever the user hits AccessDenied, ThrottlingException, a missing model, a blocked EC2 type, expired credentials, or asks how to log in, save work, or back up before the account is deleted.
---

# Hack the Fork AWS sandbox

Source: the official "AWS Participant Guide" and webinar notes (`~/Downloads/AWS PARTICIPANT GUIDE.pdf`, `AWS Webinar Notes.pdf`). Read them again if a rule here looks stale; the organizers can update the allowlist before the event.

## Hard facts

- One account per team, created by AWS Workshop Studio. Free, no card. **Deleted when the event window closes (up to 72 h), nothing recoverable.**
- **Region: us-east-1 only.** Almost every `AccessDenied` is a wrong region. Always pass `--region us-east-1` or `AWS_DEFAULT_REGION=us-east-1`.
- Login: Workshop Studio sign-in, email one-time password (same email as the application), then the team's 12-character access code. Never share the code outside the team.
- Laptop access: the event page gives temporary CLI credentials. They expire; copy fresh ones. Never commit them. Check with `aws sts get-caller-identity`.
- Kiro (agentic IDE over RDP) is also offered, capped at 1,000 credits per account. Optional.

## Blocked or limited

| Thing | Rule |
|---|---|
| GPU / `g*`, `p*` instances | Blocked. No deep learning training. Classical ML on CPU is fine (LightGBM, sklearn, statsmodels). |
| EC2 size | Below 6xlarge. No bare metal, no high-memory (`u-*`, `x1*`, `x2*`, `z1*`). |
| Marketplace AMIs | Blocked. Use Amazon Linux or Ubuntu. |
| Domains | Cannot buy. Use the public IP/DNS of EC2, or Amplify / CloudFront / API Gateway / Lambda URLs. |
| Quotas | Cannot be raised. |
| Bedrock rate | About 1 request per second per person. Sleep in loops, cache results. |
| Bedrock models | Allowlist only (below). Anything else is denied. |
| Data | **No personal or sensitive data.** Public, anonymized or synthetic only. |
| S3 | Never make a bucket public. Keep Block Public Access on. |
| Secrets | Never put keys or tokens in code, prompts, notebooks or git. |

Available services include EC2, S3, SageMaker (CPU only), Lambda, ECS, EKS, DynamoDB, RDS, Athena, Glue, API Gateway, CloudFront, Amplify, Bedrock (+ Knowledge Bases, Agents, AgentCore), CloudFormation, CodeBuild, Systems Manager, Secrets Manager, Cognito. **App Runner is not on the list**: do not plan on it. Host demos on EC2, ECS on Fargate, or Amplify.

## Bedrock allowlist (from the guide)

Anthropic: Claude Sonnet 5, Opus 5, Fable 5, Opus 4.8 / 4.7 / 4.6 / 4.5, Sonnet 4.6 / 4.5, Haiku 4.5. Amazon: Nova Micro/Lite/Pro, Nova 2 Lite, Titan Embeddings. Also OpenAI GPT-5.x, Llama 3 / 3.1 / 3.3 / 4, Mistral, Cohere Embed/Rerank, DeepSeek-R1, Writer Palmyra.
**Not available:** Opus 5.5, Fable 5.1, Mythos 5, GPT-6, gpt-oss, Llama 3.2, Google, xAI, Qwen and others.
GPT-5.x and Fable 5 need data retention set to Default: Bedrock console, Playground, pick the model, send a test prompt, accept Default. Claude models may ask for a one-time use-case form (one teammate fills it for the team).
Exact model IDs: see the `aws-bedrock-converse` skill (discover them live, do not guess).

## Saving work (do this from hour one)

1. Code lives in a GitHub repo, pushed at least hourly. Code on the laptop, run against the account with temporary credentials.
2. Data and artifacts: `aws s3 sync s3://<bucket> ./backup --region us-east-1`.
3. Describe what you create in a script or CloudFormation template kept in the repo; console clicks cannot be replayed.
4. Record a demo video and screenshots while the demo URL still works. The URL dies with the account.
5. Stop adding features 3 hours before the end, export everything, and check that a teammate can clone and run.

## When something fails

- `AccessDenied`: wrong region first, then a blocked service/model.
- `ThrottlingException` on Bedrock: add `time.sleep(1)` and cache.
- Cannot launch EC2: instance too big, GPU, or Marketplace AMI.
- Teammates cannot see your resources: confirm same access code, same account number, us-east-1.
- Organizer contact for access problems: see the participant guide (kept locally, not in git).
