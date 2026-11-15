# multi-bot-agent-framework

English | [中文说明](docs/zh/practice.md)

Rules and a small script for splitting work across several AI agents and models: who plans,
who writes, who reviews, and when to hand a subtask to Gemini or DeepSeek.

It started as a Cursor skill for writing Grok Bot prompts with a shared pool of role bots
([`SKILL.md`](SKILL.md)). The docs below add what public write-ups and papers say about
multi-agent work, with links.

## Files

| Path | What it is |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Cursor skill: writes a paste-ready Primary prompt with role bots |
| [`.cursor/rules/primary-worker.mdc`](.cursor/rules/primary-worker.mdc) | Primary/worker rule (English); Chinese in [`docs/zh/primary-worker.md`](docs/zh/primary-worker.md) |
| [`docs/PRACTICE.md`](docs/PRACTICE.md) | Published practice: when to split, costs, failure modes, review bias |
| [`docs/OUTSOURCING.md`](docs/OUTSOURCING.md) | When and how to hand a subtask to another model (Gemini, DeepSeek V4) |
| [`docs/REVIEW_LOOP.md`](docs/REVIEW_LOOP.md) | Sealed rounds, ①/② findings, PASS/FAIL, three-strike stop |
| [`docs/ROLES.md`](docs/ROLES.md) | Role table: Primary, owner, executor, reviewer, polisher, look-only planner |
| [`scripts/ask_model.py`](scripts/ask_model.py) | Sends one prompt file to an OpenAI-compatible endpoint, saves the answer, never overwrites |
| [`SOURCES_READ.tsv`](SOURCES_READ.tsv) | Every outside page read for these docs, what was read, and the date |
| [`examples/`](examples/) | A two-project role pool, and a DeepSeek-plans / Gemini-reviews run |

## Install the skill

```bash
git clone https://github.com/Xuzhen-Li/multi-bot-agent-framework.git
mkdir -p ~/.cursor/skills
ln -sfn "$(pwd)/multi-bot-agent-framework" ~/.cursor/skills/grok-bot-dispatch
```

The skill is not auto-attached. Ask the agent to read `SKILL.md` first.

```text
Read grok-bot-dispatch/SKILL.md and write a Primary prompt.
Project: gallery. Owner: the Unassigned bot for that repo.
Outcome: one pull request that fixes the badge.
Role: the draft seat writes, the review seat reviews.
The ops seat is busy on another project until that job finishes.
```

## Ask another model from a script

Python 3.9 or newer, standard library only.

```bash
export DEEPSEEK_API_KEY=...   # or GEMINI_API_KEY
python3 scripts/ask_model.py --provider deepseek --model deepseek-v4-pro --effort max \
  --prompt brief.md --out plan_v1.md
python3 scripts/ask_model.py --provider gemini --model gemini-4-hydrogen \
  --prompt review_request.md --out review_v1.md --dry-run
python3 tests/test_ask_model.py
```

`--dry-run` prints the request and makes no network call. Model names and prices were checked
on 2026-11-15; see [`docs/OUTSOURCING.md`](docs/OUTSOURCING.md) for the pages to recheck.

## License

MIT
