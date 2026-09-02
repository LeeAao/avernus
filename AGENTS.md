# Workspace Notes

## Lore Source

- For setting, faction, city, religion, cosmology, race, and history questions related to this campaign, check `Лор/` first.
- Start with `Лор/INDEX.md` to find the most relevant files quickly.
- Prefer the most specific file available over broad summaries.
- If multiple lore files conflict, mention the conflict instead of merging them silently.
- Treat files in `Лор/` as campaign reference material, not canon beyond this workspace.

## Knowledge Base Architecture

This workspace now follows a lightweight LLM-wiki pattern.

- Raw sources are the source of truth and should not be rewritten by the agent.
- The wiki is a maintained markdown layer in `Wiki/`.
- This `AGENTS.md` file is the schema and workflow guide for maintaining the wiki.

### Raw Sources

Treat these as immutable unless the user explicitly asks to edit them:

- `Лор/` for world lore and reference material.
- Top-level campaign files such as `Campaign.txt`, `Янтарь.txt`, `Наставления Корвина.txt`, `Цитатник.txt`, and `Создание персонажа.txt`.
- Local images such as `Ян 1.png`, `Ян 2.png`, and `Ян 3.png`.

### Wiki Layer

`Wiki/` is the maintained knowledge base. Prefer updating existing pages over creating near-duplicates.

### Wiki Language

- From this point forward, all new content added to `Wiki/` should be written in Russian by default.
- When updating existing wiki pages, prefer adding new material in Russian as well.
- Do not make large retroactive language-conversion passes unless the user explicitly asks for one.
- Existing English-language wiki pages may remain in English for now.
- Lore-derived pages or older pages already written in English do not need to be rewritten just to satisfy this rule.

Current structure:

- `Wiki/INDEX.md` is the main directory of wiki pages.
- `Wiki/STYLE.md` is the page-style guide: template, reliability labels, canonical names, tone.
- `Wiki/Start.md`, `Wiki/Overview.md`, and `Wiki/Timeline.md` are the top-level entry, summary, and chronology pages.
- `Wiki/LOG.md` is the chronological, append-only maintenance log.
- `Wiki/Sources/` stores source digest pages.
- `Wiki/Cases/` stores investigation pages, case summaries, victim clusters, and evidence trails.
- `Wiki/Characters/` stores character pages.
- `Wiki/Places/` stores campaign-location pages.
- `Wiki/Groups/` stores factions, caravans, and social clusters relevant to the campaign.
- `Wiki/Party/` stores player-party rosters and session-facing party notes.

There is deliberately no `Wiki/Themes/` directory. It was removed on purpose and must not be
recreated: the theme material belongs to the dead character Янтарь and lives in `Янтарь/Themes/`.

## Working Order

When answering campaign questions or maintaining notes, use this order:

1. Read `Wiki/INDEX.md` to find relevant maintained pages.
2. Read the relevant wiki pages.
3. Read the underlying raw sources they cite when detail or verification is needed.
4. For pure lore questions, consult `Лор/INDEX.md` and the most specific lore files first.

## Editing Rules

- Do not silently merge contradictions between sources. Record the conflict plainly.
- Keep raw facts, inferred conclusions, and open questions clearly separated where useful.
- Prefer many small linked pages over one huge catch-all page.
- Keep page names stable once created so links remain reliable.
- When a campaign fact is uncertain, say so directly instead of smoothing it over.
- `Wiki/` is published as a public site by `.github/workflows`, so pages must not contain
  absolute local paths (`C:\Users\...`, `G:\My Drive\...`). Cite the `Wiki/Sources/` digest
  instead, or name the material without a path when no digest exists.
- Do not link from `Wiki/` to files outside `Wiki/` (for example `../../Лор/...`). Those links
  are stripped by the site build. Point at a digest page or use plain text.

## Ingest Workflow

When the user asks to add or process a new source:

1. Read the source file.
2. Create or update a digest page in `Wiki/Sources/`.
3. Update all relevant wiki pages in `Wiki/Characters/`, `Wiki/Places/`, `Wiki/Groups/`, `Wiki/Cases/`, and `Wiki/Party/`.
4. Update `Wiki/INDEX.md`.
5. Append a timestamped entry to `Wiki/LOG.md`.

An ingest should preserve:

- Key facts.
- Relationships between people, places, and organizations.
- Timeline anchors.
- Open questions, contradictions, and unresolved leads.
- Pointers back to the raw source files.

## Query Workflow

When answering from the wiki:

- Prefer the maintained wiki layer first.
- Cite the underlying source files when answering anything specific.
- If the answer depends on lore rather than campaign events, say that the basis is `Лор/`.
- If the answer depends on campaign notes rather than world lore, say that the basis is the relevant top-level source files.

## Lint Workflow

When asked to clean up or health-check the wiki, look for:

- Orphan pages with no useful links.
- Duplicate pages that should be merged.
- Pages that mention a person, place, or faction that deserves its own page.
- Contradictions between campaign notes and lore notes.
- Missing source digests.
- Stale summaries that no longer match the latest notes.
- Absolute local paths leaking into published pages.
- Markdown links pointing outside `Wiki/`.
- Broken internal links. Note that wiki filenames contain parentheses, so a link checker must
  handle the `[label](<path (qualifier).md>)` form.
- Pages still on the old `## Роль` / `## Текущее понимание` template instead of `Wiki/STYLE.md`.
  Convert these opportunistically, when a page is being touched anyway; do not do a mass
  mechanical rewrite unless the user asks for one.
