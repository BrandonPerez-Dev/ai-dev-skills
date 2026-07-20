#!/usr/bin/env python3
"""
study.py — spaced-repetition reviewer for codebase-course / pr-walkthrough decks.

Stdlib only, single file, no installs. Copy it anywhere Python 3.9+ runs.

    study.py sync path/to/study/deck.json [more-decks...]   # import/refresh content
    study.py review [--deck NAME] [--limit N]               # review what's due
    study.py stats                                          # what's waiting
    study.py rebuild                                        # replay the log into state

Files (default ~/.study, override with $STUDY_DIR or --dir):
    state.json        scheduling + card content. The precious file. Atomic writes,
                      sorted keys — diffable, VCS-friendly.
    review-log.jsonl  append-only record of every review. With fuzz off, replaying
                      this reproduces state.json exactly (see `rebuild`), which is
                      also what makes retraining FSRS parameters possible later.

Scheduling is FSRS-6, ported from ts-fsrs 5.4.1 and verified against it by a
differential test (scripts/test_fsrs_parity.mjs). Fuzz is disabled deliberately:
determinism is what makes the review log replayable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import textwrap
from datetime import date, datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# FSRS-6 — ported from ts-fsrs 5.4.1 (MIT). Do not "simplify" the rounding or
# the clamp order: both are load-bearing for parity with the reference impl.
# ---------------------------------------------------------------------------

W = (
    0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722,
    0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014, 1.8729, 0.5425,
    0.0912, 0.0658, 0.1542,
)
S_MIN = 1e-3
S_MAX = 36500.0
REQUEST_RETENTION = 0.9
MAXIMUM_INTERVAL = 36500
ENABLE_SHORT_TERM = True

AGAIN, HARD, GOOD, EASY = 1, 2, 3, 4
GRADE_NAMES = {AGAIN: "Again", HARD: "Hard", GOOD: "Good", EASY: "Easy"}


def _js_round(x: float) -> int:
    """JS Math.round — half rounds toward +inf. Python's round() is banker's."""
    return math.floor(x + 0.5)


def _round_to(num: float, decimals: int = 8) -> float:
    factor = 10 ** decimals
    return _js_round(num * factor) / factor


def _clamp(value: float, lo: float, hi: float) -> float:
    return min(max(value, lo), hi)


def _decay_factor():
    decay = -W[20]
    factor = _round_to(math.exp(math.log(0.9) / decay) - 1, 8)
    return decay, factor


_DECAY, _FACTOR = _decay_factor()
_INTERVAL_MODIFIER = _round_to((REQUEST_RETENTION ** (1 / _DECAY) - 1) / _FACTOR, 8)


def forgetting_curve(elapsed_days: float, stability: float) -> float:
    return _round_to((1 + _FACTOR * elapsed_days / stability) ** _DECAY, 8)


def init_stability(g: int) -> float:
    return max(W[g - 1], 0.1)


def init_difficulty(g: int) -> float:
    return _round_to(W[4] - math.exp((g - 1) * W[5]) + 1, 8)


def _linear_damping(delta_d: float, old_d: float) -> float:
    return _round_to(delta_d * (10 - old_d) / 9, 8)


def _mean_reversion(init: float, current: float) -> float:
    return _round_to(W[7] * init + (1 - W[7]) * current, 8)


def next_difficulty(d: float, g: int) -> float:
    delta_d = -W[6] * (g - 3)
    next_d = d + _linear_damping(delta_d, d)
    return _clamp(_mean_reversion(init_difficulty(EASY), next_d), 1, 10)


def next_recall_stability(d: float, s: float, r: float, g: int) -> float:
    hard_penalty = W[15] if g == HARD else 1
    easy_bound = W[16] if g == EASY else 1
    return _round_to(
        _clamp(
            s * (1 + math.exp(W[8]) * (11 - d) * (s ** -W[9])
                 * (math.exp((1 - r) * W[10]) - 1) * hard_penalty * easy_bound),
            S_MIN, S_MAX,
        ), 8,
    )


def next_forget_stability(d: float, s: float, r: float) -> float:
    return _round_to(
        _clamp(
            W[11] * (d ** -W[12]) * ((s + 1) ** W[13] - 1) * math.exp((1 - r) * W[14]),
            S_MIN, S_MAX,
        ), 8,
    )


def next_short_term_stability(s: float, g: int) -> float:
    sinc = (s ** -W[19]) * math.exp(W[17] * (g - 3 + W[18]))
    masked = max(sinc, 1) if g >= HARD else sinc
    return _round_to(_clamp(s * masked, S_MIN, S_MAX), 8)


def next_state(d: float, s: float, t: float, g: int):
    """(difficulty, stability) -> next (difficulty, stability). d=s=0 means new."""
    if d == 0 and s == 0:
        return _clamp(init_difficulty(g), 1, 10), init_stability(g)
    r = forgetting_curve(t, s)
    if t == 0 and ENABLE_SHORT_TERM:
        new_s = next_short_term_stability(s, g)
    elif g == AGAIN:
        s_after_fail = next_forget_stability(d, s, r)
        w17, w18 = (W[17], W[18]) if ENABLE_SHORT_TERM else (0, 0)
        next_s_min = s / math.exp(w17 * w18)
        new_s = _clamp(_round_to(next_s_min, 8), S_MIN, s_after_fail)
    else:
        new_s = next_recall_stability(d, s, r, g)
    return next_difficulty(d, g), new_s


def next_interval(s: float) -> int:
    return int(min(max(1, _js_round(s * _INTERVAL_MODIFIER)), MAXIMUM_INTERVAL))


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

STORE_VERSION = 1
CONTENT_FIELDS = ("concept", "module", "type", "front", "back", "files", "tags")


def store_dir(cli_dir=None) -> str:
    return os.path.abspath(
        cli_dir or os.environ.get("STUDY_DIR") or os.path.expanduser("~/.study")
    )


def state_path(d: str) -> str:
    return os.path.join(d, "state.json")


def log_path(d: str) -> str:
    return os.path.join(d, "review-log.jsonl")


def load_state(d: str) -> dict:
    p = state_path(d)
    if not os.path.exists(p):
        return {"version": STORE_VERSION, "cards": {}}
    with open(p, encoding="utf-8") as f:
        state = json.load(f)
    if state.get("version") != STORE_VERSION:
        die(f"state.json is version {state.get('version')}, this script speaks {STORE_VERSION}")
    return state


def save_state(d: str, state: dict) -> None:
    os.makedirs(d, exist_ok=True)
    p = state_path(d)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def append_log(d: str, entry: dict) -> None:
    os.makedirs(d, exist_ok=True)
    with open(log_path(d), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def content_hash(card: dict) -> str:
    payload = {k: card.get(k) for k in CONTENT_FIELDS}
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def fresh_srs() -> dict:
    return {
        "stability": None, "difficulty": None, "interval_days": None,
        "repetitions": 0, "last_grade": None, "last_review": None, "due": None,
    }


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

def cmd_sync(args) -> None:
    d = store_dir(args.dir)
    state = load_state(d)
    cards = state["cards"]

    for deck_path in args.decks:
        deck_path = os.path.abspath(deck_path)
        try:
            with open(deck_path, encoding="utf-8") as f:
                deck = json.load(f)
        except FileNotFoundError:
            die(f"no such deck: {deck_path}")
        except json.JSONDecodeError as e:
            die(f"{deck_path} is not valid JSON: {e}")

        if deck.get("version") != 1:
            die(f"{deck_path}: deck version {deck.get('version')} unsupported")
        src = deck.get("source") or {}
        deck_name = src.get("repo") or os.path.basename(os.path.dirname(deck_path)) or "unknown"

        added = updated = unchanged = 0
        seen = set()
        for card in deck.get("cards", []):
            cid = card.get("id")
            if not cid:
                die(f"{deck_path}: a card is missing its id")
            if cid in seen:
                die(f"{deck_path}: duplicate card id {cid!r}")
            seen.add(cid)

            h = content_hash(card)
            existing = cards.get(cid)
            record = {
                "deck": deck_name,
                "deck_path": deck_path,
                "deck_ref": src.get("ref"),
                "content_hash": h,
                "status": "active",
                **{k: card.get(k) for k in CONTENT_FIELDS},
            }
            if existing is None:
                record["added_at"] = today_utc().isoformat()
                record["srs"] = fresh_srs()
                cards[cid] = record
                added += 1
            else:
                was = existing.get("content_hash")
                # Content is replaceable; scheduling is earned. Stable ids mean
                # "same idea", so a regenerated card keeps its review history.
                record["added_at"] = existing.get("added_at", today_utc().isoformat())
                record["srs"] = existing.get("srs", fresh_srs())
                cards[cid] = record
                if was == h:
                    unchanged += 1
                else:
                    updated += 1

        orphaned = 0
        for cid, c in cards.items():
            if c.get("deck") == deck_name and cid not in seen and c.get("status") != "orphaned":
                c["status"] = "orphaned"
                c["orphaned_at"] = today_utc().isoformat()
                orphaned += 1

        print(f"{deck_name}: +{added} new, {updated} updated, {unchanged} unchanged"
              + (f", {orphaned} orphaned" if orphaned else ""))
        if orphaned:
            print("  (orphaned cards keep their history and are skipped in review; "
                  "they no longer appear in this deck)")

    save_state(d, state)
    total = sum(1 for c in cards.values() if c.get("status") == "active")
    print(f"state: {total} active cards → {state_path(d)}")


# ---------------------------------------------------------------------------
# review
# ---------------------------------------------------------------------------

def collect_due(state: dict, today: date, deck=None, include_new=True):
    reviews, news = [], []
    for cid, c in state["cards"].items():
        if c.get("status") != "active":
            continue
        if deck and c.get("deck") != deck:
            continue
        due = c["srs"].get("due")
        if due is None:
            if include_new:
                news.append((cid, c))
        elif date.fromisoformat(due) <= today:
            reviews.append((cid, c))
    reviews.sort(key=lambda kv: (kv[1]["srs"]["due"], kv[1].get("deck", ""), kv[0]))
    news.sort(key=lambda kv: (kv[1].get("added_at", ""), kv[1].get("deck", ""), kv[0]))
    return reviews + news


def _wrap(text: str, indent: str = "  ") -> str:
    width = min(shutil.get_terminal_size((80, 24)).columns, 92) - len(indent)
    out = []
    for para in (text or "").split("\n"):
        out.append(textwrap.fill(para, width=width, initial_indent=indent,
                                 subsequent_indent=indent) if para.strip() else "")
    return "\n".join(out)


class Style:
    def __init__(self, enabled: bool):
        self.on = enabled

    def _w(self, code, s):
        return f"\033[{code}m{s}\033[0m" if self.on else s

    def dim(self, s): return self._w("2", s)
    def bold(self, s): return self._w("1", s)
    def accent(self, s): return self._w("36", s)
    def good(self, s): return self._w("32", s)
    def bad(self, s): return self._w("31", s)


def cmd_review(args) -> None:
    d = store_dir(args.dir)
    state = load_state(d)
    if not state["cards"]:
        die(f"no cards yet — run: {os.path.basename(sys.argv[0])} sync path/to/deck.json")

    today = today_utc()
    queue = collect_due(state, today, deck=args.deck, include_new=not args.no_new)
    if args.limit:
        queue = queue[: args.limit]
    if not queue:
        print("nothing due. next up:")
        cmd_stats(args)
        return

    st = Style(sys.stdout.isatty() and not args.no_color)
    total = len(queue)
    done = correct = 0

    for i, (cid, card) in enumerate(queue, 1):
        srs = card["srs"]
        is_new = srs.get("due") is None
        header = f"{i}/{total} · {card.get('deck','?')} · {card.get('concept','')}"
        print("\n" + st.dim("─" * min(shutil.get_terminal_size((80, 24)).columns, 92)))
        print(st.accent(header) + ("  " + st.dim("[new]") if is_new else ""))
        print()
        print(_wrap(card.get("front", "")))
        print()
        try:
            ans = input(st.dim("  [enter] answer · [q] quit  "))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if ans.strip().lower() == "q":
            break

        print()
        print(_wrap(card.get("back", "")))
        files = card.get("files") or []
        if files:
            print()
            print(st.dim(_wrap("src: " + ", ".join(files))))
        print()

        grade = None
        while grade is None:
            try:
                raw = input(st.dim("  [1] Again  [2] Hard  [3] Good  [4] Easy · [q] quit  "))
            except (EOFError, KeyboardInterrupt):
                print()
                raw = "q"
            raw = raw.strip().lower()
            if raw == "q":
                grade = "q"
            elif raw in ("1", "2", "3", "4"):
                grade = int(raw)
            else:
                print(st.dim("  ? 1-4 or q"))
        if grade == "q":
            break

        entry = apply_review(card, grade, today)
        entry["card_id"] = cid
        append_log(d, entry)
        save_state(d, state)  # every review is durable before the next card
        done += 1
        if grade >= GOOD:
            correct += 1
        nxt = card["srs"]["due"]
        days = card["srs"]["interval_days"]
        tag = st.good(GRADE_NAMES[grade]) if grade >= GOOD else st.bad(GRADE_NAMES[grade])
        print(f"  {tag} → next in {days}d ({nxt})")

    print()
    if done:
        print(st.bold(f"{done} reviewed") + st.dim(f" · {correct} recalled · {total - done} left in queue"))
    else:
        print(st.dim("nothing reviewed"))


def apply_review(card: dict, grade: int, today: date) -> dict:
    """Mutates card['srs'] in place; returns the log entry."""
    srs = card["srs"]
    d_before = srs.get("difficulty") or 0
    s_before = srs.get("stability") or 0
    last = srs.get("last_review")
    if s_before and last:
        elapsed = (today - date.fromisoformat(last)).days
        elapsed = max(0, elapsed)
    else:
        elapsed = 0

    d_after, s_after = next_state(d_before, s_before, elapsed, grade)
    interval = next_interval(s_after)
    due = today + timedelta(days=interval)

    srs.update({
        "stability": s_after,
        "difficulty": d_after,
        "interval_days": interval,
        "repetitions": (srs.get("repetitions") or 0) + 1,
        "last_grade": grade,
        "last_review": today.isoformat(),
        "due": due.isoformat(),
    })
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "deck": card.get("deck"),
        "grade": grade,
        "elapsed_days": elapsed,
        "stability_before": s_before or None,
        "stability_after": s_after,
        "difficulty_before": d_before or None,
        "difficulty_after": d_after,
        "interval_days": interval,
        "due": due.isoformat(),
    }


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------

def cmd_stats(args) -> None:
    d = store_dir(args.dir)
    state = load_state(d)
    cards = state["cards"]
    if not cards:
        print("no cards yet. sync a deck.json to start.")
        return
    today = today_utc()
    st = Style(sys.stdout.isatty() and not getattr(args, "no_color", False))

    decks = {}
    for c in cards.values():
        name = c.get("deck", "?")
        b = decks.setdefault(name, {"active": 0, "new": 0, "due": 0, "orphaned": 0, "later": 0})
        if c.get("status") != "active":
            b["orphaned"] += 1
            continue
        b["active"] += 1
        due = c["srs"].get("due")
        if due is None:
            b["new"] += 1
        elif date.fromisoformat(due) <= today:
            b["due"] += 1
        else:
            b["later"] += 1

    w = max(len(n) for n in decks) + 2
    print(st.bold(f"{'deck'.ljust(w)}{'due':>5}{'new':>5}{'later':>7}{'total':>7}"))
    for name in sorted(decks):
        b = decks[name]
        line = f"{name.ljust(w)}{b['due']:>5}{b['new']:>5}{b['later']:>7}{b['active']:>7}"
        print(line + (st.dim(f"  ({b['orphaned']} orphaned)") if b["orphaned"] else ""))

    upcoming = {}
    for c in cards.values():
        if c.get("status") != "active":
            continue
        due = c["srs"].get("due")
        if not due:
            continue
        dd = date.fromisoformat(due)
        if today < dd <= today + timedelta(days=7):
            upcoming[dd] = upcoming.get(dd, 0) + 1
    if upcoming:
        print()
        print(st.dim("next 7 days: ") + "  ".join(
            f"{k.strftime('%a')} {v}" for k, v in sorted(upcoming.items())))


# ---------------------------------------------------------------------------
# rebuild — replay the log. The payoff of fuzz-free determinism.
# ---------------------------------------------------------------------------

def cmd_rebuild(args) -> None:
    d = store_dir(args.dir)
    state = load_state(d)
    if not os.path.exists(log_path(d)):
        die("no review-log.jsonl to replay")

    for c in state["cards"].values():
        c["srs"] = fresh_srs()

    replayed = skipped = 0
    with open(log_path(d), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            card = state["cards"].get(e["card_id"])
            if card is None:
                skipped += 1
                continue
            srs = card["srs"]
            d_before = srs.get("difficulty") or 0
            s_before = srs.get("stability") or 0
            d_after, s_after = next_state(d_before, s_before, e["elapsed_days"], e["grade"])
            interval = next_interval(s_after)
            review_day = date.fromisoformat(e["ts"][:10])
            srs.update({
                "stability": s_after, "difficulty": d_after, "interval_days": interval,
                "repetitions": (srs.get("repetitions") or 0) + 1, "last_grade": e["grade"],
                "last_review": review_day.isoformat(),
                "due": (review_day + timedelta(days=interval)).isoformat(),
            })
            replayed += 1

    save_state(d, state)
    print(f"replayed {replayed} reviews" + (f", skipped {skipped} (unknown card)" if skipped else ""))
    print(f"state rebuilt → {state_path(d)}")


# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        prog="study.py",
        description="Spaced-repetition reviewer for codebase-course / pr-walkthrough decks.",
    )
    p.add_argument("--dir", help="store directory (default $STUDY_DIR or ~/.study)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sync", help="import or refresh deck.json content")
    s.add_argument("decks", nargs="+")
    s.set_defaults(func=cmd_sync)

    r = sub.add_parser("review", help="review due cards")
    r.add_argument("--deck", help="limit to one deck")
    r.add_argument("--limit", type=int, help="max cards this session")
    r.add_argument("--no-new", action="store_true", help="reviews only, no new cards")
    r.add_argument("--no-color", action="store_true")
    r.set_defaults(func=cmd_review)

    t = sub.add_parser("stats", help="what's due, new, and upcoming")
    t.add_argument("--no-color", action="store_true")
    t.set_defaults(func=cmd_stats)

    b = sub.add_parser("rebuild", help="replay review-log.jsonl into state.json")
    b.set_defaults(func=cmd_rebuild)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
