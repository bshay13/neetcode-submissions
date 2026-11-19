# Anki sync

Every push that adds a `Data Structures & Algorithms/<slug>/submission-N.*` file runs `.github/workflows/anki-sync.yml`.
For each problem slug in the push it:

1. Logs in to AnkiWeb and searches the `NeetCode` deck for the problem's link. If a card exists, it skips.
2. Otherwise adds a Basic card. Front: problem name and neetcode.io link. Back: time, space, trick, category.
3. Searches again to confirm the card landed. The run fails if it did not.

Card text comes from `cards.json`, which has an entry for every NeetCode 150 problem plus a few extras. No AI runs in the workflow.
A problem that is not in `cards.json` fails with a clear message. Add an entry (slug, name, category, time, space, trick) and re-run.

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
