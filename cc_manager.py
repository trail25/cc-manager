#!/usr/bin/env python3
"""Credit Card Manager — track rewards, perks, fees, and find the best card for any spend."""

import argparse
import calendar
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Optional

DATA_DIR = Path(os.getenv("CC_MANAGER_DATA_DIR", Path.home() / ".cc_manager")).expanduser()
DATA_FILE = DATA_DIR / "cards.json"


# ─── Data Layer ───────────────────────────────────────────────────────────────

def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_cards() -> list[dict]:
    _ensure_dir()
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Could not read {DATA_FILE}: invalid JSON ({exc})")
        sys.exit(1)
    if not isinstance(data, list):
        print(f"Could not read {DATA_FILE}: expected a list of cards")
        sys.exit(1)
    return data


def save_cards(cards: list[dict]):
    _ensure_dir()
    with tempfile.NamedTemporaryFile(
        "w",
        dir=DATA_DIR,
        prefix=f"{DATA_FILE.name}.",
        suffix=".tmp",
        delete=False,
    ) as f:
        json.dump(cards, f, indent=2, default=str)
        f.write("\n")
        tmp_name = f.name
    Path(tmp_name).replace(DATA_FILE)


def _find_card(cards: list[dict], name: str) -> Optional[dict]:
    for c in cards:
        if c["name"].lower() == name.lower():
            return c
    return None


def _next_due(day: int) -> str:
    """Return the next due date as YYYY-MM-DD given a day-of-month."""
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    due = date(today.year, today.month, min(day, last_day))
    if due <= today:
        if today.month == 12:
            next_year, next_month = today.year + 1, 1
        else:
            next_year, next_month = today.year, today.month + 1
        last_day = calendar.monthrange(next_year, next_month)[1]
        due = date(next_year, next_month, min(day, last_day))
    return due.isoformat()


def _due_day(value: str) -> int:
    try:
        day = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("due day must be a number from 1 to 31")
    if day < 1 or day > 31:
        raise argparse.ArgumentTypeError("due day must be from 1 to 31")
    return day


# ─── Pretty Printers ──────────────────────────────────────────────────────────

def _fmt_card(c: dict) -> str:
    lines = []
    lines.append(f"{c['name']}  ({c['issuer']})")
    lines.append(f"  Annual fee: ${c['annual_fee']}")
    lines.append(f"  Next payment due: {_next_due(c['due_day'])}")

    if c.get("reward_categories"):
        lines.append("  Rewards:")
        for rc in c["reward_categories"]:
            lines.append(f"    • {rc['category']}: {rc['rate']}%" if isinstance(rc['rate'], (int, float)) else f"    • {rc['category']}: {rc['rate']}")

    if c.get("annual_credits"):
        lines.append("  Annual credits:")
        for cr in c["annual_credits"]:
            lines.append(f"    • ${cr['amount']} {cr['name']} — {cr.get('description', '')}")

    if c.get("lounge_access"):
        lines.append("  Lounge access:")
        for la in c["lounge_access"]:
            visits = f" ({la['visits_per_year']} visits/yr)" if la.get("visits_per_year") else " (unlimited)"
            lines.append(f"    • {la['name']}{visits}")

    return "\n".join(lines)


# ─── CLI Commands ─────────────────────────────────────────────────────────────

def cmd_add(args):
    cards = load_cards()
    if _find_card(cards, args.name):
        print(f"Card '{args.name}' already exists. Use 'edit' to modify.")
        sys.exit(1)

    card = {
        "name": args.name,
        "issuer": args.issuer,
        "annual_fee": args.annual_fee,
        "due_day": args.due_day,
        "reward_categories": [],
        "annual_credits": [],
        "lounge_access": [],
    }
    cards.append(card)
    save_cards(cards)
    print(f"Added card: {args.name}")


def cmd_add_reward(args):
    cards = load_cards()
    card = _find_card(cards, args.name)
    if not card:
        print(f"Card '{args.name}' not found.")
        sys.exit(1)
    card.setdefault("reward_categories", []).append({
        "category": args.category,
        "rate": args.rate,
    })
    save_cards(cards)
    print(f"Added reward: {args.category} @ {args.rate}% to {args.name}")


def cmd_add_credit(args):
    cards = load_cards()
    card = _find_card(cards, args.name)
    if not card:
        print(f"Card '{args.name}' not found.")
        sys.exit(1)
    card.setdefault("annual_credits", []).append({
        "name": args.credit_name,
        "amount": args.amount,
        "description": args.description,
    })
    save_cards(cards)
    print(f"Added credit: ${args.amount} {args.credit_name} to {args.name}")


def cmd_add_lounge(args):
    cards = load_cards()
    card = _find_card(cards, args.name)
    if not card:
        print(f"Card '{args.name}' not found.")
        sys.exit(1)
    card.setdefault("lounge_access", []).append({
        "name": args.lounge_name,
        "visits_per_year": args.visits,
    })
    save_cards(cards)
    print(f"Added lounge: {args.lounge_name} to {args.name}")


def cmd_list(args):
    cards = load_cards()
    if not cards:
        print("No cards saved. Use 'add' to add one.")
        return
    for i, c in enumerate(cards, 1):
        print(f"\n─── Card {i} ───")
        print(_fmt_card(c))


def cmd_remove(args):
    cards = load_cards()
    card = _find_card(cards, args.name)
    if not card:
        print(f"Card '{args.name}' not found.")
        sys.exit(1)
    cards.remove(card)
    save_cards(cards)
    print(f"Removed card: {args.name}")


def cmd_edit(args):
    cards = load_cards()
    card = _find_card(cards, args.name)
    if not card:
        print(f"Card '{args.name}' not found.")
        sys.exit(1)
    if args.field == "name":
        card["name"] = args.value
    elif args.field == "issuer":
        card["issuer"] = args.value
    elif args.field == "annual-fee":
        card["annual_fee"] = int(args.value)
    elif args.field == "due-day":
        card["due_day"] = _due_day(args.value)
    else:
        print(f"Unknown field: {args.field}. Valid: name, issuer, annual-fee, due-day")
        sys.exit(1)
    save_cards(cards)
    print(f"Updated {args.field} → {args.value}")


def cmd_recommend(args):
    """Recommend the best card for a spending category."""
    cards = load_cards()
    if not cards:
        print("No cards saved. Add some cards first.")
        return

    category = args.category.lower()
    results = []
    for c in cards:
        best_rate = 0.0
        for rc in c.get("reward_categories", []):
            if rc["category"].lower() == category:
                rate = float(rc["rate"])
                if rate > best_rate:
                    best_rate = rate
        if best_rate > 0:
            results.append((best_rate, c["name"], c["issuer"]))

    if not results:
        print(f"No cards found with rewards for '{category}'.")
        return

    results.sort(key=lambda x: x[0], reverse=True)
    print(f"Best cards for '{category}':")
    for i, (rate, name, issuer) in enumerate(results, 1):
        print(f"  {i}. {name} ({issuer}) — {rate}% back")


def cmd_perks(args):
    """Show all cards with their annual credits and lounge access."""
    cards = load_cards()
    if not cards:
        print("No cards saved.")
        return

    for c in cards:
        has_perks = c.get("annual_credits") or c.get("lounge_access")
        if not has_perks:
            continue
        print(f"\n─── {c['name']} ({c['issuer']}) ───")
        if c.get("annual_credits"):
            print("  Credits:")
            for cr in c["annual_credits"]:
                print(f"    ${cr['amount']} {cr['name']} — {cr.get('description', '')}")
        if c.get("lounge_access"):
            print("  Lounge access:")
            for la in c["lounge_access"]:
                v = f" ({la['visits_per_year']} visits/yr)" if la.get("visits_per_year") else " (unlimited)"
                print(f"    • {la['name']}{v}")


def cmd_fees(args):
    """Show upcoming annual fees grouped by month."""
    cards = load_cards()
    if not cards:
        print("No cards saved.")
        return

    today = date.today()
    by_month: dict[str, list] = {}
    for c in cards:
        if c["annual_fee"] == 0:
            continue
        due_date = date.fromisoformat(_next_due(c["due_day"]))
        key = due_date.strftime("%B %Y")
        by_month.setdefault(key, []).append(c)

    if not by_month:
        print("No cards with annual fees.")
        return

    print(f"Upcoming annual fees (from {today.isoformat()}):")
    for month in sorted(by_month.keys()):
        print(f"\n  {month}:")
        for c in by_month[month]:
            due = _next_due(c["due_day"])
            print(f"    • ${c['annual_fee']} — {c['name']} (due: {due})")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="cc",
        description="Credit Card Manager — track perks, rewards, and find the best card.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new credit card")
    p_add.add_argument("name", help="Card name (e.g. 'Chase Sapphire Preferred')")
    p_add.add_argument("--issuer", "-i", required=True, help="Bank/issuer name")
    p_add.add_argument("--annual-fee", "-f", type=int, default=0, help="Annual fee in USD")
    p_add.add_argument("--due-day", "-d", type=_due_day, required=True, help="Payment due day of month (1-31)")
    p_add.set_defaults(func=cmd_add)

    # add-reward
    p_rw = sub.add_parser("add-reward", help="Add a reward category to a card")
    p_rw.add_argument("name", help="Card name")
    p_rw.add_argument("--category", "-c", required=True, help="Spend category (e.g. dining, travel)")
    p_rw.add_argument("--rate", "-r", type=float, required=True, help="Reward rate (e.g. 3 for 3%)")
    p_rw.set_defaults(func=cmd_add_reward)

    # add-credit
    p_cr = sub.add_parser("add-credit", help="Add an annual credit to a card")
    p_cr.add_argument("name", help="Card name")
    p_cr.add_argument("--name", "-n", dest="credit_name", required=True, help="Credit name (e.g. Uber Cash)")
    p_cr.add_argument("--amount", "-a", type=int, required=True, help="Credit amount in USD")
    p_cr.add_argument("--description", "-d", default="", help="Optional description")
    p_cr.set_defaults(func=cmd_add_credit)

    # add-lounge
    p_ln = sub.add_parser("add-lounge", help="Add lounge access to a card")
    p_ln.add_argument("name", help="Card name")
    p_ln.add_argument("--lounge", "-l", dest="lounge_name", required=True, help="Lounge network name")
    p_ln.add_argument("--visits", "-v", type=int, default=0,
                      help="Visits per year (0 = unlimited, default)")
    p_ln.set_defaults(func=cmd_add_lounge)

    # list
    p_list = sub.add_parser("list", help="List all cards")
    p_list.set_defaults(func=cmd_list)

    # remove
    p_rm = sub.add_parser("remove", help="Remove a card")
    p_rm.add_argument("name", help="Card name to remove")
    p_rm.set_defaults(func=cmd_remove)

    # edit
    p_ed = sub.add_parser("edit", help="Edit a card field")
    p_ed.add_argument("name", help="Card name")
    p_ed.add_argument("field", choices=["name", "issuer", "annual-fee", "due-day"],
                      help="Field to edit")
    p_ed.add_argument("value", help="New value")
    p_ed.set_defaults(func=cmd_edit)

    # recommend
    p_rec = sub.add_parser("recommend", help="Best card for a spend category")
    p_rec.add_argument("category", help="Spend category (e.g. dining, travel, groceries)")
    p_rec.set_defaults(func=cmd_recommend)

    # perks
    p_perks = sub.add_parser("perks", help="Show all annual credits & lounge access")
    p_perks.set_defaults(func=cmd_perks)

    # fees
    p_fees = sub.add_parser("fees", help="Show upcoming annual fees")
    p_fees.set_defaults(func=cmd_fees)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
