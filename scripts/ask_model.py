#!/usr/bin/env python3
"""Send one prompt file to an OpenAI-compatible chat endpoint and save the answer.

Works with Gemini and DeepSeek because both accept the OpenAI Chat Completions
format. Standard library only.

Examples:
  python3 scripts/ask_model.py --provider deepseek --model deepseek-v4-pro \
      --effort high --prompt task.md --out answer.md
  python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
      --prompt review.md --out review_gemini.md --dry-run

The output file must not exist yet; the script never overwrites.
API keys are read from the environment (DEEPSEEK_API_KEY, GEMINI_API_KEY).
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

PROVIDERS = {
    # base URLs from the providers' own docs (see docs/OUTSOURCING.md)
    "deepseek": {
        "url": "https://api.deepseek.com/chat/completions",
        "key_env": "DEEPSEEK_API_KEY",
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key_env": "GEMINI_API_KEY",
    },
}


def build_request(provider, model, prompt, system=None, effort=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": model, "messages": messages}
    if effort:
        body["reasoning_effort"] = effort
    if provider == "deepseek" and effort:
        # DeepSeek thinking mode is on by default; state it so the log is explicit.
        body["thinking"] = {"type": "enabled"}
    return {"url": PROVIDERS[provider]["url"], "body": body}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    p.add_argument("--model", required=True)
    p.add_argument("--prompt", required=True, help="path to a text/markdown prompt file")
    p.add_argument("--system", help="path to a system prompt file")
    p.add_argument("--effort", choices=["low", "medium", "high", "max"],
                   help="reasoning effort; DeepSeek uses low/high/max, Gemini maps it to thinking_level")
    p.add_argument("--out", required=True, help="answer file; must not exist")
    p.add_argument("--dry-run", action="store_true", help="print the request and exit, no network")
    p.add_argument("--timeout", type=int, default=600)
    a = p.parse_args(argv)

    if os.path.exists(a.out):
        p.error(f"{a.out} exists; pick a new name (this script never overwrites)")
    with open(a.prompt, encoding="utf-8") as f:
        prompt = f.read()
    system = None
    if a.system:
        with open(a.system, encoding="utf-8") as f:
            system = f.read()

    req = build_request(a.provider, a.model, prompt, system, a.effort)
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    if a.dry_run:
        print(json.dumps({"url": req["url"], "body": req["body"], "prompt_sha256": prompt_sha},
                         ensure_ascii=False, indent=2))
        return 0

    key = os.environ.get(PROVIDERS[a.provider]["key_env"])
    if not key:
        p.error(f"set {PROVIDERS[a.provider]['key_env']} first")
    data = json.dumps(req["body"]).encode("utf-8")
    http = urllib.request.Request(req["url"], data=data, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    })
    with urllib.request.urlopen(http, timeout=a.timeout) as r:
        resp = json.load(r)
    msg = resp["choices"][0]["message"]
    answer = msg.get("content") or ""
    with open(a.out, "x", encoding="utf-8") as f:
        f.write(answer)
    meta = {
        "provider": a.provider,
        "model": resp.get("model", a.model),
        "effort": a.effort,
        "prompt": a.prompt,
        "prompt_sha256": prompt_sha,
        "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
        "usage": resp.get("usage"),
    }
    with open(a.out + ".meta.json", "x", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
