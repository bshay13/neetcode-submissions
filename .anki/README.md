# Anki sync

**Active path: the Anki desktop add-on** (below). The GitHub Action in `.github/workflows/anki-sync.yml` is disabled (`gh workflow disable "Anki sync"`) so only one system writes to the deck. It still works if you re-enable it.

## Desktop add-on

`addon/neetcode_cards/` is an Anki add-on. Each time Anki opens it waits for the first AnkiWeb sync, runs `git pull` on this repo's local clone, and adds a Basic card (deck `NeetCode`) for every committed problem that has none. Then it syncs again so the cards reach AnkiWeb. Manual run: Tools > NeetCode: add missing cards.

Install (re-run after changing the add-on), then restart Anki:

```bash
cp -R .anki/addon/neetcode_cards ~/Library/Application\ Support/Anki2/addons21/
```

- The clone path is in the add-on's `config.json` (Tools > Add-ons > NeetCode cards > Config). Default `~/neetcode-anki/neetcode-submissions`. Keep the clone on `main`.
- It adds nothing until a sync has finished, so a stale local collection never creates duplicates.
- Anki must be signed in to AnkiWeb. If `git pull` fails (offline, no git credentials in Anki's environment), it uses the clone as it is.

The sections below describe the GitHub Action path.

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
