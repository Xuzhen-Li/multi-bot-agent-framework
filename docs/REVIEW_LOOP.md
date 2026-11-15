# Review loop

These are house rules from running this setup. The parts that rest on published work link to [PRACTICE.md](PRACTICE.md); the rest has no outside source.

1. The writer finishes a round and seals it: one new folder per round, a `SHA256SUMS` file,
   and a short `CHANGES_vN.md`.
2. Each reviewer reads the sealed folder and writes a new report file. Reviewers do not edit.
3. Findings use two levels:
   - ① must fix before merge (wrong fact, broken command, rule violation)
   - ② should fix, does not block
4. The report ends with PASS or FAIL. FAIL means at least one ①.
5. The main agent decides each finding, writes the decision into the plan, and sends the fixes
   to the original writer.
6. The next round is a new folder. Old rounds are kept.
7. If the same finding comes back three times, stop and ask the owner.

Reviewer choice:

- never the writer
- a different model family when one is available ([PRACTICE.md](PRACTICE.md) §6)
- subject reviewers (for example genetics, methods, literature) each check their own area;
  all must PASS

Polish comes after all reviewers PASS, and the polished text gets a diff check against the
reviewed text before it is published.
