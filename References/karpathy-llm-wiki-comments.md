# Karpathy LLM Wiki: Useful Comment Takeaways

This note keeps only the comments that add workflow ideas, cautions, or design refinements beyond "I built a tool for this."

## Source

- Gist: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

## Highest-Signal Comments

### Citation-first and review-gated wiki

- `laphilosophia` (2026-04-04): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079377>
- Main addition: a robust version of this pattern should be source-grounded, citation-first, and review-gated rather than fully autonomous.
- Useful constraints:
  - Separate facts, inferences, and open questions explicitly.
  - Require source links for important claims.
  - Make ingest idempotent.
  - Prefer proposed diffs over silent overwrites.
  - Lint for unsupported claims and stale claims, not only missing links.

### Classify before extracting, and make updates compound by rule

- `bluewater8008` (2026-04-05): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079549>
- Main additions:
  - Classify source type before extraction so reports, letters, transcripts, and declarations are not handled identically.
  - Give the index an explicit token budget with progressive disclosure.
  - Use one template per entity type instead of one generic page template.
  - Make every task produce two outputs: the user-facing answer and wiki updates.
  - Add domain tags early if the knowledge base may span multiple domains.
  - Keep human verification explicit even if the LLM writes the wiki.

### Provenance, no content invention, and a split between reference and drafts

- `peas` (2026-04-05): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079483>
- Main additions:
  - The LLM should behave like an editor or stenographer, not a ghostwriter.
  - If the source does not support a statement, mark a gap instead of filling it with plausible prose.
  - Preserve provenance back to the original captured source.
  - Consider separating machine-maintained reference pages from writing/draft pages.
  - Mechanical or rule-based cross-linking can be safer than freeform link invention.

### Watch for the point where markdown files want a queryable backend

- `mpazik` (2026-04-05): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079689>
- Main warning:
  - Once the wiki grows into the hundreds of pages, asking questions by reading files and scanning a hand-maintained index stops scaling well.
- Suggested direction:
  - Let structured data or a database back the wiki while still rendering pages as markdown.
  - Treat the index as a query or generated view once the corpus gets large enough.

### Add a counter-argument or data-gap pass

- `localwolfpackai` (2026-04-05): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079697>
- Main addition:
  - When updating concept pages, add a deliberate counter-argument or data-gap section so the wiki does not quietly drift toward a single flattering narrative.

### Project-local "working memory" files are useful for software repositories

- `samflipppy` (2026-04-04): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6078982>
- Main addition:
  - For software projects, a small local memory folder can complement the wiki with files like `index.md`, `architecture.md`, `decisions.md`, `changelog.md`, and deployment/schema notes.
- Why it matters:
  - This is a more operational, repo-local version of the same pattern and is helpful when the main problem is session continuity rather than long-form knowledge synthesis.

### Inline image context can be preserved with generated descriptions

- `jamesalmeida` (2026-04-04): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-6079011>
- Main addition:
  - If images matter, pre-generate textual descriptions so future passes can retain more visual context without always re-opening the original image files.

## Practical Conclusions For This Workspace

- The existing raw-source/wiki/schema split in this workspace already matches the core gist closely.
- The most useful refinements for future maintenance are:
  - Preserve citation discipline and provenance.
  - Keep facts, inferences, and open questions visibly separate where stakes are high.
  - Use more type-specific page sections if the wiki broadens beyond campaign notes.
  - Revisit search/index strategy if the page count becomes much larger.

## Not Included

- Most comments in the gist thread were either short praise, open-source announcements, or product links without new workflow ideas.
