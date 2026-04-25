"""
Persistent storage layer for Roommie.

All user records are kept in data/users.json as a JSON array.
Each record carries the user's profile fields plus email, a
SHA-256 password hash, and three social fields:

    liked_by : list[int]  — IDs of users who have liked this user
    liked    : list[int]  — IDs this user has liked (outgoing likes)
    matches  : list[int]  — IDs of confirmed mutual matches
"""

import json
import os
import hashlib

from models import HouseOwner, HouseSeeker

_USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _user_to_record(user, email: str, password_hash: str) -> dict:
    record = {
        "user_id":       user.user_id,
        "email":         email,
        "password_hash": password_hash,
        "role":          type(user).__name__,
        "name":          user.name,
        "age":           user.age,
        "gender":        user.gender,
        "occupation":    user.occupation,
        "bio":           user.bio,
        "avatar_url":    user.avatar_url,
        "habits":        user.habits,
        "languages":     user.languages,
        # social fields
        "liked_by":      [],
        "liked":         [],
        "matches":       [],
    }
    if isinstance(user, HouseOwner):
        record["neighborhood"]  = user.neighborhood
        record["monthly_rent"]  = user.monthly_rent
    else:
        record["max_budget"]              = user.max_budget
        record["preferred_neighborhoods"] = user.preferred_neighborhoods
    return record


def _record_to_user(record: dict):
    base = {
        "user_id":    record["user_id"],
        "name":       record["name"],
        "age":        record["age"],
        "gender":     record["gender"],
        "occupation": record["occupation"],
        "bio":        record["bio"],
        "avatar_url": record.get("avatar_url", ""),
        "habits":     record["habits"],
        "languages":  record["languages"],
    }
    if record["role"] == "HouseOwner":
        return HouseOwner(
            **base,
            neighborhood=record["neighborhood"],
            monthly_rent=record["monthly_rent"],
        )
    return HouseSeeker(
        **base,
        max_budget=record["max_budget"],
        preferred_neighborhoods=record["preferred_neighborhoods"],
    )


# ---------------------------------------------------------------------------
# Raw JSON I/O
# ---------------------------------------------------------------------------

def load_records() -> list[dict]:
    if not os.path.exists(_USER_FILE):
        return []
    with open(_USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_records(records: list[dict]) -> None:
    with open(_USER_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Public API — core
# ---------------------------------------------------------------------------

def get_all_users() -> list:
    """Return every user in the JSON file as HouseOwner / HouseSeeker objects."""
    return [_record_to_user(r) for r in load_records()]


def next_user_id() -> int:
    records = load_records()
    return max((r["user_id"] for r in records), default=0) + 1


def find_record_by_email(email: str) -> dict | None:
    for r in load_records():
        if r.get("email", "").lower() == email.lower():
            return r
    return None


def authenticate(email: str, password: str) -> dict | None:
    """Return the matching record if credentials are correct, else None."""
    record = find_record_by_email(email)
    if record and record.get("password_hash") == _hash(password):
        return record
    return None


def register_user(user, email: str, password: str) -> None:
    """Append a new user record. Raises ValueError if email already exists."""
    records = load_records()
    if any(r.get("email", "").lower() == email.lower() for r in records):
        raise ValueError(f"Email '{email}' is already registered.")
    records.append(_user_to_record(user, email, _hash(password)))
    save_records(records)


def record_to_user(record: dict):
    """Public wrapper — convert a raw dict record to a User subclass object."""
    return _record_to_user(record)


# ---------------------------------------------------------------------------
# Public API — social (likes & matches)
# ---------------------------------------------------------------------------

def ensure_social_fields() -> None:
    """
    Migration: add liked_by / liked / matches to any record that predates
    the social update. Safe to call on every app start — no-op if all
    records already have the fields.
    """
    records = load_records()
    changed = False
    for r in records:
        for field in ("liked_by", "liked", "matches"):
            if field not in r:
                r[field] = []
                changed = True
    if changed:
        save_records(records)


def record_like(liker_id: int, candidate_id: int) -> bool:
    """
    Record that liker_id liked candidate_id.

    Updates:
      - liker's     'liked'    list  → appends candidate_id
      - candidate's 'liked_by' list  → appends liker_id

    Returns True if this creates a mutual match (candidate had already
    liked liker), and in that case also updates both 'matches' lists.
    """
    records   = load_records()
    rec_map   = {r["user_id"]: r for r in records}

    liker     = rec_map[liker_id]
    candidate = rec_map[candidate_id]

    if candidate_id not in liker["liked"]:
        liker["liked"].append(candidate_id)

    if liker_id not in candidate["liked_by"]:
        candidate["liked_by"].append(liker_id)

    # Mutual match: did the candidate previously like the liker?
    is_mutual = liker_id in candidate.get("liked", [])

    if is_mutual:
        if candidate_id not in liker["matches"]:
            liker["matches"].append(candidate_id)
        if liker_id not in candidate["matches"]:
            candidate["matches"].append(liker_id)

    save_records(records)
    return is_mutual


def get_mutual_matches(user_id: int) -> list:
    """
    Return User objects for every confirmed mutual match of user_id,
    together with their raw record (for any extra social fields).
    Returns list of User objects.
    """
    records   = load_records()
    rec_map   = {r["user_id"]: r for r in records}
    user_rec  = rec_map.get(user_id, {})
    match_ids = user_rec.get("matches", [])
    return [_record_to_user(rec_map[mid]) for mid in match_ids if mid in rec_map]


def get_seen_ids(user_id: int) -> set:
    """
    Return the set of user IDs that user_id has already liked.
    Used to filter the discovery queue across sessions.
    """
    records = load_records()
    for r in records:
        if r["user_id"] == user_id:
            return set(r.get("liked", []))
    return set()


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

def seed_if_empty() -> None:
    """
    On the very first run (empty JSON), populate the pool with the six
    mock users so the matching engine has real candidates to work with.
    Seed users get the sentinel hash and cannot log in.
    """
    if load_records():
        return
    from data.mock_data import all_roommies
    records = [
        _user_to_record(user, f"user{user.user_id}@roommie.lt", "SEED_NO_LOGIN")
        for user in all_roommies
    ]
    save_records(records)


def seed_vilnius_if_missing() -> None:
    """
    Load the 20 synthetic Vilnius users from vilnius_users.json (project root)
    and append any whose user_id is not already present in users.json.
    Seed records get the SEED_NO_LOGIN sentinel and cannot log in.
    The 'nationality' field and any other unknown fields are ignored.
    """
    _VILNIUS_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "vilnius_users.json"
    )
    if not os.path.exists(_VILNIUS_FILE):
        return

    records = load_records()
    existing_ids = {r["user_id"] for r in records}

    with open(_VILNIUS_FILE, "r", encoding="utf-8") as f:
        vilnius_data = json.load(f)

    changed = False
    for v in vilnius_data:
        if v["user_id"] in existing_ids:
            continue
        base = dict(
            user_id=v["user_id"], name=v["name"], age=v["age"],
            gender=v.get("gender", ""), occupation=v["occupation"],
            bio=v["bio"], avatar_url=v.get("avatar_url", ""),
            habits=v["habits"], languages=v["languages"],
        )
        if v["role"] == "HouseOwner":
            user = HouseOwner(
                **base,
                neighborhood=v["neighborhood"],
                monthly_rent=v["monthly_rent"],
            )
        else:
            user = HouseSeeker(
                **base,
                max_budget=v["max_budget"],
                preferred_neighborhoods=v["preferred_neighborhoods"],
            )
        records.append(
            _user_to_record(user, f"vilnius{user.user_id}@roommie.lt", "SEED_NO_LOGIN")
        )
        existing_ids.add(user.user_id)
        changed = True

    if changed:
        save_records(records)
