"""Adds an Anki card for every NeetCode problem committed to the submissions repo.

Runs once per Anki session, right after the first AnkiWeb sync finishes (so existing cards
are already local and nothing is duplicated). Also available as Tools > NeetCode: add missing cards.
Card text comes from .anki/cards.json in the repo.
"""
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

DECK = "NeetCode"
NOTETYPE = "Basic"
SUBMISSION = re.compile(r"^submission-\d+\.[^/]+$")


def problem_url(slug):
    return f"https://neetcode.io/problems/{slug}/question"


def card_fields(card):
    url = card.get("url") or problem_url(card["slug"])
    rows = card.get("back") or [
        ["Time", card["time"]],
        ["Space", card["space"]],
        ["Category", card["category"]],
        ["Trick", card["trick"]],
    ]
    front = f'{html.escape(card["name"], quote=False)}<br><a href="{url}">{url}</a>'
    back = "<br>".join(f"<b>{html.escape(k, quote=False)}:</b> {html.escape(v, quote=False)}" for k, v in rows)
    return front, back


def slugs_in_repo(repo):
    """<section folder>/<slug>/submission-N.<ext>. Dot folders never count."""
    slugs = set()
    for section in Path(repo).iterdir():
        if not section.is_dir() or section.name.startswith("."):
            continue
        for problem in section.iterdir():
            if problem.is_dir() and any(SUBMISSION.match(f.name) for f in problem.iterdir()):
                slugs.add(problem.name)
    return sorted(slugs)


def _search_text(url):
    key = re.sub(r"^https?://", "", url)
    return re.sub(r'([\\"*_])', r"\\\1", key)


def add_missing(col, repo):
    """Adds a card for each committed problem that has none. Returns (added, skipped, unknown)."""
    repo = Path(repo)
    cards = {c["slug"]: c for c in json.loads((repo / ".anki" / "cards.json").read_text())["cards"]}
    model = col.models.by_name(NOTETYPE)
    if not model or [f["name"] for f in model["flds"]][:2] != ["Front", "Back"]:
        raise RuntimeError(f'Note type "{NOTETYPE}" with fields Front and Back not found')
    deck_id = col.decks.id(DECK)
    added, skipped, unknown = [], [], []
    for slug in slugs_in_repo(repo):
        card = cards.get(slug)
        url = (card or {}).get("url") or problem_url(slug)
        if col.find_notes(f'deck:{DECK} "{_search_text(url)}"'):
            skipped.append(slug)
        elif not card:
            unknown.append(slug)
        else:
            note = col.new_note(model)
            note.fields[0], note.fields[1] = card_fields(card)
            col.add_note(note, deck_id)
            added.append(slug)
    return added, skipped, unknown


def git_pull(repo):
    """Best effort: offline or a dirty clone must not stop the run."""
    git = shutil.which("git") or "/usr/bin/git"
    try:
        subprocess.run([git, "-C", str(repo), "pull", "--ff-only", "--quiet"],
                       check=True, timeout=60, capture_output=True)
        return None
    except Exception as err:  # noqa: BLE001
        return str(err)


try:
    from aqt import gui_hooks, mw
except ImportError:  # imported outside Anki (tests)
    mw = None

if mw is not None:
    from aqt.operations import QueryOp
    from aqt.qt import QAction
    from aqt.utils import showInfo, tooltip

    def _repo():
        cfg = mw.addonManager.getConfig(__name__) or {}
        return Path(cfg.get("repo", "~/neetcode-anki/neetcode-submissions")).expanduser()

    def _finish(pull_error, manual):
        try:
            added, skipped, unknown = add_missing(mw.col, _repo())
        except Exception as err:  # noqa: BLE001
            showInfo(f"NeetCode cards: {err}")
            return
        lines = []
        if added:
            lines.append(f"Added {len(added)}: {', '.join(added)}")
        if unknown:
            lines.append(f"No card text in cards.json for: {', '.join(unknown)}")
        if pull_error:
            lines.append("git pull failed, used the local clone as is")
        if manual and not lines:
            lines.append(f"All {len(skipped)} committed problems already have cards")
        if lines:
            (showInfo if unknown or pull_error else tooltip)("NeetCode cards\n" + "\n".join(lines))
        if added:
            try:
                mw.on_sync_button_clicked()  # push the new cards to AnkiWeb
            except Exception:  # noqa: BLE001
                pass

    def run(manual=False):
        repo = _repo()
        QueryOp(
            parent=mw,
            op=lambda _col: git_pull(repo),
            success=lambda err: _finish(err, manual),
        ).run_in_background()

    _state = {"done": False}

    def _after_sync():
        if not _state["done"]:
            _state["done"] = True
            run()

    def _on_profile_open():
        _state["done"] = False
        if not mw.pm.sync_auth():
            tooltip("NeetCode cards: sign in to AnkiWeb and sync, then use Tools > NeetCode: add missing cards")

    gui_hooks.profile_did_open.append(_on_profile_open)
    gui_hooks.sync_did_finish.append(_after_sync)
    action = QAction("NeetCode: add missing cards", mw)
    action.triggered.connect(lambda: run(manual=True))
    mw.form.menuTools.addAction(action)
