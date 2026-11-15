# Handing a subtask to another model

The main agent keeps the plan and the decisions. Another model gets one subtask with a full
brief and returns a file. The main agent checks the file before using it.

## When to hand off

| Situation | Hand to | Why |
| --- | --- | --- |
| A hard plan or proof where a wrong step costs rework | the strongest reasoning model you have, high or max effort | planning quality decides the rest (aider architect result, [PRACTICE.md](PRACTICE.md) §3) |
| Many small, well-specified edits after the plan is fixed | a cheaper fast model | the plan already carries the reasoning |
| Reading a long document set (papers, logs, a whole repo) | a 1M-context model | both Gemini and DeepSeek V4 list 1M context |
| Review of a draft | a model from a different family than the writer | self-preference bias ([PRACTICE.md](PRACTICE.md) §6) |
| Final prose polish | one fixed polisher model | stable voice across documents |

Do not hand off: decisions that need the owner, anything that deletes or publishes, and safety
refusals. The main agent handles those itself.

## The two endpoints used here

Both accept the OpenAI Chat Completions format, so one small client covers both
([`scripts/ask_model.py`](../scripts/ask_model.py)).

DeepSeek (checked 2026-11-15 on the [API docs](https://api-docs.deepseek.com/) and
[pricing page](https://api-docs.deepseek.com/quick_start/pricing)):

- base URL `https://api.deepseek.com`, also an Anthropic-format URL `https://api.deepseek.com/anthropic`
- models `deepseek-v4-pro` and `deepseek-flash` (served by DeepSeek-V4.1-Flash), 1M context
- thinking mode on by default; effort `low`, `high` or `max`
  ([thinking mode guide](https://api-docs.deepseek.com/guides/thinking_mode)); V4-Pro GA notes:
  [2026-08-13](https://api-docs.deepseek.com/news/news260813)
- peak and off-peak prices; off-peak is half price

Gemini (checked 2026-11-15 on [OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai)):

- base URL `https://generativelanguage.googleapis.com/v1beta/openai/`
- `reasoning_effort` maps to Gemini `thinking_level`; reasoning cannot be turned off on Gemini 3 and 4 models
- example model name in the docs: `gemini-4-hydrogen`
- headless CLI: `gemini -p "..." --output-format json`

Model names and prices change. Check the two pages above before a long run and write the
model string into the log.

## Recipes

### A. Plan high, do cheap

1. Main agent writes `brief.md`: goal, files in scope, what must not change, acceptance check.
2. `deepseek-v4-pro` at `--effort max` (or the strongest Gemini) writes `plan.md` only.
3. Main agent reads `plan.md`, fixes it, and freezes it (sha256 in the log).
4. A fast model (`deepseek-flash`, or a Gemini Flash model) applies one plan step at a time.
5. Tests or checks run after each step.

### B. Cross-family review

1. Writer model A produces the draft.
2. Reviewer model B (other family) gets the draft, the brief, and the review format in
   [REVIEW_LOOP.md](REVIEW_LOOP.md). It writes findings only, no edits.
3. If two reviewers are used, give each the drafts in a different order.
4. The main agent decides each finding and sends fixes back to writer A.

### C. Long-context reader

Give a 1M-context model the whole folder and ask for a map: which file says what, with line
numbers. The main agent then reads only the cited lines.

### D. Polish only

The polisher gets finished text and a list of what must stay byte-identical (numbers,
commands, paths, names). Diff the result against the input and reject any change to a protected
item.

## Calling from a script

```bash
python3 scripts/ask_model.py --provider deepseek --model deepseek-v4-pro --effort max \
  --prompt brief.md --out plan_v1.md
python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
  --prompt review_request.md --out review_v1.md
python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
  --prompt review_request.md --out review_v1.md --dry-run   # no network
```

The script refuses to write over an existing file and saves a `.meta.json` next to each answer
with the prompt and answer sha256 and the token usage.
