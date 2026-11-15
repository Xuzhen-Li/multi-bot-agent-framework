# What published practice says about multi-agent work

Notes from public write-ups and papers, read on 2026-11-15. Each point links to its source.
The rules in this repo follow from these points.

## 1. Use one agent until the task really splits

Cognition argues that most multi-agent setups are fragile because subagents do not see each
other's decisions. Its two rules are "share context, and share full agent traces" and "actions
carry implicit decisions". A single linear agent is the default it recommends.
Source: Walden Yan, [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents), Cognition, 2025-06-12.

Anthropic's agent guide makes the same first move: start with the simplest prompt, and add
workflows (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer)
only when they measurably help.
Source: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic, 2024-12-19.

What this repo takes from it: split only when the parts do not edit the same place, and hand
each worker the full brief plus the decisions already made, not a one-line subtask.

## 2. Splitting pays off for breadth, and costs tokens

Anthropic's Research feature uses an orchestrator-worker layout. A lead agent writes a plan,
saves it to memory, starts subagents that search in parallel, and a separate citation step
attaches sources at the end. On their internal research eval, Claude Opus 4 as lead with
Claude Sonnet 4 subagents beat single-agent Opus 4 by 90.2%. The same post reports that agents
use about 4 times the tokens of chat, and multi-agent systems about 15 times.
Source: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Anthropic, 2025-06-13.

What this repo takes from it: parallel workers are for independent directions (literature
search across topics, one repo per worker). Do not split a single file edit.

## 3. A strong reasoner plans, a cheaper model applies

Aider's architect mode sends the problem to an "architect" model that describes the fix, then
an "editor" model turns that description into file edits. DeepSeek R1 as architect with
Claude 3.5 Sonnet as editor scored 64.0% on the aider polyglot benchmark, against 61.7% for o1
alone, at $13.29 versus $186.5 for the run.
Sources: [Separating code reasoning and editing](https://aider.chat/2024/09/26/architect.html), aider, 2024-09-26;
[R1+Sonnet set SOTA on aider's polyglot benchmark](https://aider.chat/2025/01/24/r1-sonnet.html), aider, 2025-01-24.

What this repo takes from it: the plan-high / do-cheap recipe in [OUTSOURCING.md](OUTSOURCING.md).

## 4. Asking a second model is now a tool, not a framework

PAL MCP (formerly Zen MCP) lets Claude Code, Gemini CLI, Codex CLI or Cursor call other models
(Gemini, OpenAI, OpenRouter, local Ollama and others) for a second opinion, a code review, or a
"consensus" between two models, inside one session.
Source: [BeehiveInnovations/pal-mcp-server](https://github.com/BeehiveInnovations/pal-mcp-server).

Gemini CLI runs headless with `gemini -p "..." --output-format json`, which makes it usable as
a scripted reviewer.
Source: [Gemini CLI headless mode](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md).

## 5. Where multi-agent systems actually fail

The MAST study annotated more than 1600 traces from 7 frameworks and found 14 failure modes in
3 groups: system design issues, inter-agent misalignment, and task verification.
Source: Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657), arXiv 2503.13657, 2025.

What this repo takes from it: write the role, the stop condition and the acceptance check into
every brief, and make verification a separate seat.

## 6. Review by a different model, and know the judge's biases

Several model instances that propose answers and then debate over rounds improved reasoning
and factual accuracy over a single instance.
Source: Du et al., [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325), arXiv 2305.14325, 2023.

LLM judges show position, verbosity and self-enhancement bias, even though strong judges agree
with humans over 80% of the time.
Source: Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685), arXiv 2306.05685, 2023.

A model can recognise its own text, and the better it recognises it, the more it prefers it.
Source: Panickssery, Bowman and Feng, [LLM Evaluators Recognize and Favor Their Own Generations](https://arxiv.org/abs/2404.13076), arXiv 2404.13076, 2024.

What this repo takes from it: the writer never reviews its own work, and where possible the
reviewer is a different model family. Swap the order when a judge compares two drafts.

## 7. Science-specific multi-agent systems

Google's AI co-scientist, built on Gemini 2.0, uses six agents (Generation, Reflection,
Ranking, Evolution, Proximity, Meta-review). Hypotheses are compared in ranking tournaments
and refined over rounds.
Sources: [Accelerating scientific breakthroughs with an AI co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/), Google Research;
Gottweis et al., [arXiv 2502.18864](https://arxiv.org/abs/2502.18864).

What this repo takes from it: for research work, keep a ranking step where hypotheses are
compared head to head, not scored alone.
