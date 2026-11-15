# Handing a subtask to another model

The main agent keeps control of the plan and decisions. Another model receives a single subtask with a complete brief and returns a file, which the main agent inspects before using.

## When to hand off

| Situation | Hand to | Why |
| --- | --- | --- |
| A hard plan or proof where a wrong step costs rework | the strongest reasoning model you have, high or max effort | planning quality decides the rest (aider architect result, [PRACTICE.md](PRACTICE.md) §3) |
| Many small, well-specified edits after the plan is fixed | a cheaper fast model | the plan already carries the reasoning |
| Reading a long document set (papers, logs, a whole repo) | a 1M-context model | DeepSeek's pricing page lists 1M context for both V4 models; the PAL MCP README describes Gemini as 1M tokens |
| Review of a draft | a model from a different family than the writer | self-preference bias ([PRACTICE.md](PRACTICE.md) §6) |
| Final prose polish | one fixed polisher model | house rule from this repo's own use, not from a source |

Do not hand off decisions that require the owner, actions that delete or publish, or safety refusals. The main agent handles those directly.

## The two endpoints used here

Both endpoints accept the OpenAI Chat Completions format, so a single small client covers both ([`scripts/ask_model.py`](../scripts/ask_model.py)).

DeepSeek (checked 2026-11-15 on the [API docs](https://api-docs.deepseek.com/) and
[pricing page](https://api-docs.deepseek.com/quick_start/pricing)):

- base URL `https://api.deepseek.com`, plus an Anthropic-format URL `https://api.deepseek.com/anthropic`
- models `deepseek-v4-pro` and `deepseek-flash` (served by DeepSeek-V4.1-Flash), 1M context
- thinking mode on by default; effort `low`, `high`, or `max`
  ([thinking mode guide](https://api-docs.deepseek.com/guides/thinking_mode)); V4-Pro GA notes:
  [2026-08-13](https://api-docs.deepseek.com/news/news260813)
- peak and off-peak prices; off-peak is half price

Gemini (checked 2026-11-15 on [OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai)):

- base URL `https://generativelanguage.googleapis.com/v1beta/openai/`
- `reasoning_effort` maps to Gemini `thinking_level`; reasoning cannot be turned off on Gemini 3 and 4 models
- example model name in the docs: `gemini-4-hydrogen`
- headless CLI: `gemini -p "..." --output-format json`

Model names and prices change over time. Check the two pages above before a long run and record the exact model string in the log.

## Recipes

### A. Plan high, do cheap

1. Main agent writes `brief.md`: goal, files in scope, what must not change, and acceptance check.
2. `deepseek-v4-pro` at `--effort max` (or the strongest Gemini model) writes `plan.md` only.
3. Main agent reads `plan.md`, edits it if needed, and freezes it (recording its sha256 in the log).
4. A fast model (`deepseek-flash`, or a Gemini Flash model) applies one step of the plan at a time.
5. Tests or checks run after each step.

### B. Cross-family review

1. Writer model A produces the draft.
2. Reviewer model B (from a different model family) receives the draft, the brief, and the review format in [REVIEW_LOOP.md](REVIEW_LOOP.md). It outputs findings only, with no edits.
3. If two reviewers are used, give each the drafts in a different order.
4. The main agent evaluates each finding and sends fixes back to writer A.

### C. Long-context reader

Pass the entire folder to a 1M-context model and ask for a map showing which file covers what, with line numbers. The main agent then reads only the cited lines.

### D. Polish only

The polisher receives finished text along with a list of items that must stay byte-identical (numbers, commands, paths, names). Diff the output against the input and reject any change to a protected item.

## Calling from a script

```bash
python3 scripts/ask_model.py --provider deepseek --model deepseek-v4-pro --effort max \
  --prompt brief.md --out plan_v1.md
python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
  --prompt review_request.md --out review_v1.md
python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
  --prompt review_request.md --out review_v1.md --dry-run   # no network
```

The script refuses to overwrite an existing file. It checks for the answer file and its `.meta.json` before making the paid call, then writes `.meta.json` alongside each answer with the prompt and answer sha256 hashes and token usage. If the model returns no answer text, it writes no answer file, saves the full response as `<out>.empty-response.json`, and exits with code 3.
