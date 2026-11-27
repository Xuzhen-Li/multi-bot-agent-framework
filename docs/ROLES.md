# Roles

These are house rules from running this setup. The parts that rest on published work link to [PRACTICE.md](PRACTICE.md); the rest has no outside source.

A role is the job a bot holds for one task. It is written in the brief, not in the bot's name.

| Role | Does | Does not |
| --- | --- | --- |
| Primary | talks to the owner, writes briefs, picks options, merges | write long content itself |
| Project owner | holds one project's state and history | take a second project |
| Executor | does the work in a sandbox, freezes each snapshot | review its own snapshot |
| Reviewer | reads a frozen snapshot, writes blocking/non-blocking findings, PASS or FAIL | edit files |
| Polisher | rewrites finished prose for readability | change facts, numbers, commands |
| Look-only planner | gives a plan, a comparison, or a visual check | log in, edit, open PRs |

Rules that go with the table:

- One bot holds one role for one task at a time. Release it when the task ends.
- The writer and the reviewer are different bots, and if possible different model families.
- Primary may give a subtask to an outside model ([OUTSOURCING.md](OUTSOURCING.md)); the result
  is treated like any worker's output and is checked before use.
- Deleting, publishing, spending money and owner decisions stay with Primary and the owner.
