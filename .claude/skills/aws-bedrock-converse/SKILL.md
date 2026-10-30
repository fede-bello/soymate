---
name: aws-bedrock-converse
description: Call Amazon Bedrock models (Claude, Nova, others) from Python with boto3 in the Hack the Fork sandbox using the Converse API. Use whenever the user wants an LLM on AWS, text generation or explanations from a Bedrock model, structured output, rate limits, model IDs or inference profiles, ThrottlingException, a model access or data retention error, or asks which Bedrock model to use. Also use to find the exact model ID of an allowed model.
---

# Bedrock from Python (Converse API)

Model allowlist and rate guidance are in `aws-hackathon-sandbox`. Remember the limits: us-east-1, about 1 request per second per person, only allowlisted models.

## Do not guess model IDs

Bedrock model IDs change per generation, and newer Claude models are often invoked through a cross-Region **inference profile** ID (for example a `us.` prefix) instead of the bare model ID. The AWS page that used to list IDs has moved ("models at a glance"), so discover the ID live from the account instead of from memory:

```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')].[modelId,modelName]" --output table
aws bedrock list-inference-profiles --region us-east-1 \
  --query "inferenceProfileSummaries[].[inferenceProfileId,inferenceProfileName]" --output table
```

Use whichever ID the account returns for the model you want. If invoking a bare model ID fails with an on-demand throughput error, use the inference profile ID instead (a system-defined profile accepts its ID or ARN in `modelId`). Put the chosen ID in an env var (`BEDROCK_MODEL_ID`), not hard-coded across files.

For the first call with GPT-5.x or Claude Fable 5, set data retention to Default via the Playground (see sandbox skill).

## Minimal call (pattern from the AWS Converse docs)

```python
import os, time
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = os.environ["BEDROCK_MODEL_ID"]

def ask(prompt: str, system: str = "", max_tokens: int = 600, temperature: float = 0.2) -> str:
    kwargs = dict(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    if system:
        kwargs["system"] = [{"text": system}]
    resp = bedrock.converse(**kwargs)
    return resp["output"]["message"]["content"][0]["text"]
```

`resp["usage"]` has token counts and `resp["stopReason"]` says why it stopped. Converse takes the same request shape for every provider, so swapping models is a one-line change. Model-specific parameters go in `additionalModelRequestFields`. For streaming use `converse_stream`.

## Rate limits and caching

Stay under about 1 request per second per person. Cache by input hash so identical inputs never call the model twice:

```python
import hashlib, json, pathlib
CACHE = pathlib.Path("data/llm_cache"); CACHE.mkdir(parents=True, exist_ok=True)

def ask_cached(prompt, **kw):
    key = CACHE / (hashlib.sha256(json.dumps([MODEL_ID, prompt, kw]).encode()).hexdigest() + ".txt")
    if key.exists():
        return key.read_text()
    out = ask(prompt, **kw)
    key.write_text(out)
    time.sleep(1)
    return out
```

On `ThrottlingException`, back off (sleep 2, 4, 8 seconds) and retry. boto3 also supports `Config(retries={"mode": "adaptive", "max_attempts": 8})`.

## Using it in a project like PeaSure

The LLM should explain numbers the model already produced (for example a per-department paragraph from the forecast table), never invent them. Pass the figures in the prompt, ask for a short plain-language summary in the user's language, and label it as generated text in the UI. Generate texts offline and cache them, so the live demo never waits on, or fails because of, a model call. Start with a cheap fast model (Haiku 4.5 or Nova Lite) and only switch for the final demo if quality needs it.

## Errors

| Error | Likely cause |
|---|---|
| `AccessDeniedException` | Model not on the allowlist, wrong region, or expired credentials |
| `ValidationException` about on-demand throughput | Need the inference profile ID, not the bare model ID |
| Data retention error | Set Default in the Playground (GPT-5.x, Fable 5) |
| `ThrottlingException` | Too many requests; sleep, cache, retry with backoff |
