import sys
import argparse
import getpass
sys.stdout.reconfigure(encoding="utf-8")

from data.storage import (
    seed_if_empty, authenticate, register_user,
    get_all_users, find_record_by_email, record_to_user, next_user_id,
)
from engine import MatchingEngine
from models import HouseOwner, HouseSeeker, UserFactory

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_separator(char="-", width=42):
    print(char * width)


def show_profile(user):
    # Derive role label from class name — no isinstance needed for display
    role = type(user).__name__.replace("House", "House ")
    print_separator()
    print(f"  {user.name}  |  {role}  |  Age {user.age}  |  {user.gender.capitalize()}")
    print(f"  Occupation : {user.occupation}")
    print(f"  Bio        : {user.bio}")
    print(f"  Habits     : {', '.join(user.habits)}")
    print(f"  Languages  : {', '.join(user.languages)}")
    print(f"  {user.get_detail()}")   # Polymorphism — each subclass formats its own detail
    print_separator()


def display_matches(matches, current_user, engine):
    current_label = None
    for i, (match, score, label) in enumerate(matches, start=1):
        if label != current_label:
            print_separator()
            header = "  ✔  Perfect Matches" if label == "Perfect" \
                     else "  ~  Suggested (outside preferred neighbourhood)"
            print(header)
            print_separator()
            current_label = label

        detail    = match.get_detail()    # Polymorphism — no isinstance needed
        breakdown = engine.score_breakdown(current_user, match)
        shared_habits = set(current_user.habits) & set(match.habits)
        habits_note   = ", ".join(shared_habits) if shared_habits else "none"
        vibe_tag      = "  ✦ Vibe match!" if breakdown["vibe"] > 0 else ""

        print(f"  {i}. {match.name}  ({match.occupation})")
        print(f"     {detail}")
        print(f"     Compatibility : {score:.1f}%  "
              f"(habits {breakdown['habits']}  "
              f"lang {breakdown['languages']}  "
              f"vibe {breakdown['vibe']})")
        print(f"     Shared habits : {habits_note}{vibe_tag}")
        print(f"     Bio           : {match.bio}")
        print()
    print_separator()


def run_matching(user):
    print("\n  Searching for your best matches...\n")
    engine  = MatchingEngine()
    matches = engine.find_matches(user, get_all_users())

    if not matches:
        print("  No perfect matches yet — but keep looking!\n")
        return

    n_perfect   = sum(1 for *_, label in matches if label == "Perfect")
    n_suggested = sum(1 for *_, label in matches if label == "Suggested")
    parts = []
    if n_perfect:
        parts.append(f"{n_perfect} perfect")
    if n_suggested:
        parts.append(f"{n_suggested} suggested")
    print(f"  Found {' + '.join(parts)} match(es) for you:\n")
    display_matches(matches, user, engine)


# ---------------------------------------------------------------------------
# Low-level input helpers
# ---------------------------------------------------------------------------

def _prompt_str(label: str, allow_empty=False) -> str:
    while True:
        value = input(f"  {label}: ").strip()
        if value or allow_empty:
            return value
        print("    ✗  This field cannot be empty.")


def _prompt_int(label: str, lo: int = 1, hi: int = 10_000) -> int:
    while True:
        raw = input(f"  {label}: ").strip()
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        print(f"    ✗  Please enter a whole number between {lo} and {hi}.")


def _prompt_list(label: str) -> list[str]:
    while True:
        raw = input(f"  {label} (comma-separated): ").strip()
        items = [x.strip() for x in raw.split(",") if x.strip()]
        if items:
            return items
        print("    ✗  Please enter at least one value.")


def _prompt_choice(label: str, options: list[str]) -> str:
    """Print numbered options and return the chosen string."""
    print(f"\n  {label}")
    for i, opt in enumerate(options, 1):
        print(f"    [{i}] {opt}")
    while True:
        raw = input("  Your choice: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"    ✗  Enter a number between 1 and {len(options)}.")


def _prompt_password(label="Password") -> str:
    while True:
        try:
            pw = getpass.getpass(f"  {label}: ")
        except Exception:
            pw = input(f"  {label} (visible): ").strip()
        if len(pw) >= 6:
            return pw
        print("    ✗  Password must be at least 6 characters.")


# ---------------------------------------------------------------------------
# Auth flows
# ---------------------------------------------------------------------------

def login_flow():
    print("\n  --- Login ---")
    email    = _prompt_str("Email")
    password = _prompt_password()

    record = authenticate(email, password)
    if not record:
        print("\n  ✗  Incorrect email or password.\n")
        return

    user = record_to_user(record)
    print(f"\n  Welcome back, {user.name}!\n")
    show_profile(user)
    run_matching(user)


def signup_flow():
    print("\n  --- Sign Up ---")

    # ── Credentials ──────────────────────────────────────────────────────
    while True:
        email = _prompt_str("Email")
        if find_record_by_email(email):
            print("    ✗  That email is already registered. Try logging in.")
        else:
            break

    password = _prompt_password("Choose a password (min 6 chars)")

    # ── Profile ──────────────────────────────────────────────────────────
    print("\n  --- Profile Creation ---")
    name       = _prompt_str("Full name")
    age        = _prompt_int("Age", lo=16, hi=120)
    gender     = _prompt_choice("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
    occupation = _prompt_str("Occupation")
    bio        = _prompt_str("Short bio")
    habits     = _prompt_list("Habits")
    languages  = _prompt_list("Languages")

    # ── Role ─────────────────────────────────────────────────────────────
    role = _prompt_choice("I am a ...", ["House Owner", "House Seeker"])

    uid = next_user_id()

    if role == "House Owner":
        neighborhood = _prompt_str("Your neighbourhood")
        monthly_rent = _prompt_int("Monthly rent (€)", lo=1, hi=100_000)
        user = UserFactory.create(
            "House Owner",
            user_id=uid, name=name, age=age, gender=gender.lower(),
            occupation=occupation, bio=bio, avatar_url="",
            habits=habits, languages=languages,
            neighborhood=neighborhood, monthly_rent=monthly_rent,
        )
    else:
        max_budget              = _prompt_int("Max monthly budget (€)", lo=1, hi=100_000)
        preferred_neighborhoods = _prompt_list("Preferred neighbourhoods")
        user = UserFactory.create(
            "House Seeker",
            user_id=uid, name=name, age=age, gender=gender.lower(),
            occupation=occupation, bio=bio, avatar_url="",
            habits=habits, languages=languages,
            max_budget=max_budget,
            preferred_neighborhoods=preferred_neighborhoods,
        )

    try:
        register_user(user, email, password)
    except ValueError as e:
        print(f"\n  ✗  {e}\n")
        return

    print(f"\n  ✔  Account created! Welcome to Roommie, {name}!\n")
    show_profile(user)
    run_matching(user)


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def main_menu():
    while True:
        print()
        print_separator("=", 42)
        print("       --- Welcome to Roommie Vilnius ---")
        print_separator("=", 42)
        print("    [1]  Login")
        print("    [2]  Sign Up")
        print("    [3]  Exit")
        print_separator("=", 42)

        choice = input("\n  Choose an option: ").strip()
        if choice == "1":
            login_flow()
        elif choice == "2":
            signup_flow()
        elif choice == "3":
            print("\n  See you soon!\n")
            sys.exit(0)
        else:
            print("  ✗  Please enter 1, 2, or 3.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="roommie",
        description="Roommie Vilnius — terminal roommate matcher",
    )
    parser.add_argument(
        "-u", "--user",
        type=int,
        metavar="ID",
        help="skip the menu and show matches directly for this user ID",
    )
    args = parser.parse_args()

    seed_if_empty()

    if args.user is not None:
        all_users = get_all_users()
        user_index = {u.user_id: u for u in all_users}
        if args.user not in user_index:
            print(f"  Error: no user with ID {args.user}. "
                  f"Valid IDs: {sorted(user_index)}")
            sys.exit(1)
        user = user_index[args.user]
        show_profile(user)
        run_matching(user)
    else:
        main_menu()


if __name__ == "__main__":
    main()
