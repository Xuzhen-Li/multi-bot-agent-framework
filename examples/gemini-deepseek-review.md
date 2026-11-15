# Example: DeepSeek plans, Gemini reviews, Primary decides

Task: add a methods section to a repo README.

```text
You are Primary. Decide and finish. Do not create a bot.

Project: vitis-te README methods section
Outcome: one PR that adds docs/METHODS.md; no other file changes.

Step 1, plan (outside model): send brief.md to deepseek-v4-pro, effort max.
  python3 scripts/ask_model.py --provider deepseek --model deepseek-v4-pro --effort max \
    --prompt brief.md --out plan_v1.md
  Read plan_v1.md. Fix it. Record its sha256 in the plan file.

Step 2, write: the executor bot writes docs/METHODS.md from plan_v1.md and seals round v1.

Step 3, review (other family): send the sealed file and REVIEW_LOOP.md to gemini-4-hydrogen.
  python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
    --prompt review_request_v1.md --out review_gemini_v1.md
  The subject reviewer bot also reviews round v1. Both must PASS.

Step 4, polish: the polisher bot rewrites prose only. Diff numbers, commands and paths
against round v1; reject any change to them.

Step 5: open the PR. Report the PR link and status only.
```
