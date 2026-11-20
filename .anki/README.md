# Anki sync

Every push that adds a `<section folder>/<slug>/submission-N.*` file runs `.github/workflows/anki-sync.yml`.
For each problem slug in the push it:

1. Logs in to AnkiWeb and searches the `NeetCode` deck for the problem's link. If a card exists, it skips.
2. Otherwise adds a Basic card. Front: problem name and neetcode.io link. Back: time, space, trick, category.
3. Searches again to confirm the card landed. The run fails if it did not.

Card text comes from `cards.json`: every coding problem on NeetCode (the 1,097 with problem pages), the Machine Learning, Design Patterns, SQL and AI Coding problems, and the 19 System Design problems. No AI runs in the workflow.
A problem that is not in `cards.json` fails with a clear message. Add an entry and re-run.

- Coding cards: Back has Time, Space, Category, Trick.
- Other sections: Back has Category, Key idea, How it works, Watch out. System Design cards link to systemdesignschool.io, as NeetCode does.
- Slugs for manual runs: coding, ML, SQL and design patterns use the NeetCode slug. System Design uses `system-design-<id>` (for example `system-design-url-shortener`). AI Coding uses `ai-coding-<id>`.
- `needs-review.txt` lists entries the writer was unsure about. The text was written by Claude from general knowledge, so skim any you plan to rely on.

## Secrets (repo Settings > Secrets and variables > Actions)

- `ANKIWEB_EMAIL`, `ANKIWEB_PASSWORD`: your AnkiWeb login.

Set them from a terminal so the values never touch chat:

```bash
gh secret set ANKIWEB_EMAIL -R bshay13/neetcode-submissions
gh secret set ANKIWEB_PASSWORD -R bshay13/neetcode-submissions
```

## Manual run

Actions tab, "Anki sync", Run workflow. Optional `slugs` input, for example `binary-search,plus-one`.

## Limits

- A push that adds more than 15 problems stops with an error. Use the manual run for bulk adds.
- AnkiWeb has no API. If AnkiWeb changes its pages, the run fails loudly and the selectors in `sync.mjs` need an update.
- The workflow never commits to this repo, so it cannot trigger itself.
- The script does not pick a deck or note type. It uses whatever AnkiWeb's Add page remembers as last used, so keep that as `NeetCode` and `Basic`. If a card lands elsewhere, the confirm-search fails and the run goes red.
