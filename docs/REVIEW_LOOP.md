# Review loop

These are house rules from running this setup. The parts that rest on published work link to [PRACTICE.md](PRACTICE.md); the rest has no outside source.

1. The writer finishes a draft and freezes it: one new folder per snapshot, a `SHA256SUMS` file,
   and a short `CHANGES_vN.md`.
2. Each reviewer reads the frozen folder and writes a new report file. Reviewers do not edit.
3. Findings use two levels:
   - Blocking: must fix before merge (wrong fact, broken command, rule violation)
   - Non-blocking: should fix, does not block
4. The report ends with PASS or FAIL. FAIL means at least one blocking finding.
5. The main agent decides each finding, writes the decision into the plan, and sends the fixes
   to the original writer.
6. The next revision is a new folder. Previous revisions are kept.
7. If the same finding comes back three times, stop and ask the owner.

Reviewer choice:

- never the writer
- a different model family when one is available ([PRACTICE.md](PRACTICE.md) §6)
- subject reviewers (for example genetics, methods, literature) each check their own area;
  all must PASS

Polish comes after all reviewers PASS, and the polished text gets a diff check against the
reviewed text before it is published.
