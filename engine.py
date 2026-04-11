from models.house_owner import HouseOwner
from models.house_seeker import HouseSeeker

BUDGET_MARGIN = 100       # € — how far over budget is still acceptable
SUGGESTION_PENALTY = 30  # pts — score reduction applied to neighbourhood mismatches

# Scoring weights (must sum to 100)
WEIGHT_HABITS    = 70  # Jaccard similarity on habits
WEIGHT_LANGUAGES = 20  # Jaccard similarity on languages
WEIGHT_VIBE      = 10  # flat bonus for matching occupation category

# Occupation categories for vibe matching
OCCUPATION_CATEGORIES = {
    "creative":  {"Artist", "Designer", "Musician", "Photographer", "Architect"},
    "tech":      {"Software Developer", "Engineer", "Data Scientist", "IT Specialist"},
    "academic":  {"Student", "Teacher", "Professor", "Researcher"},
    "food":      {"Chef", "Baker", "Nutritionist"},
    "health":    {"Doctor", "Nurse", "Physiotherapist"},
    "business":  {"Manager", "Accountant", "Lawyer", "Entrepreneur"},
}


class MatchingEngine:
    """
    Matches HouseOwners with HouseSeekers using a weighted compatibility score.

    Score breakdown (max 100 pts)
    ------------------------------
    Habits    : Jaccard similarity * 70   (primary signal)
    Languages : Jaccard similarity * 20   (communication fit)
    Vibe      : flat 10 pts if same       (lifestyle category bonus)
                occupation category

    Match tiers
    -----------
    Perfect   — budget within margin AND neighbourhood preferred → full score
    Suggested — budget within margin, neighbourhood not listed   → score - SUGGESTION_PENALTY
    """

    # ------------------------------------------------------------------
    # Private scoring helpers
    # ------------------------------------------------------------------

    def _habit_score(self, user_a, user_b) -> float:
        """Jaccard on habits, weighted to WEIGHT_HABITS."""
        a = set(user_a.habits)
        b = set(user_b.habits)
        union = a | b
        if not union:
            return 0.0
        return (len(a & b) / len(union)) * WEIGHT_HABITS

    def _language_score(self, user_a, user_b) -> float:
        """Jaccard on languages, weighted to WEIGHT_LANGUAGES."""
        a = set(user_a.languages)
        b = set(user_b.languages)
        union = a | b
        if not union:
            return 0.0
        return (len(a & b) / len(union)) * WEIGHT_LANGUAGES

    def _vibe_score(self, user_a, user_b) -> float:
        """Flat WEIGHT_VIBE bonus if both occupations share a category."""
        for members in OCCUPATION_CATEGORIES.values():
            if user_a.occupation in members and user_b.occupation in members:
                return float(WEIGHT_VIBE)
        return 0.0

    def _compatibility_score(self, user_a, user_b) -> float:
        """Composite score: habits + languages + vibe, capped at 100."""
        score = (
            self._habit_score(user_a, user_b)
            + self._language_score(user_a, user_b)
            + self._vibe_score(user_a, user_b)
        )
        return min(score, 100.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_pair(self, current_user, candidate):
        """Return (owner, seeker) regardless of which is current_user."""
        if isinstance(current_user, HouseOwner):
            return current_user, candidate
        return candidate, current_user

    def score_breakdown(self, user_a, user_b) -> dict:
        """Return individual score components (useful for display/debugging)."""
        return {
            "habits":    round(self._habit_score(user_a, user_b), 1),
            "languages": round(self._language_score(user_a, user_b), 1),
            "vibe":      round(self._vibe_score(user_a, user_b), 1),
            "total":     round(self._compatibility_score(user_a, user_b), 1),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_matches(self, current_user, all_users: list) -> list:
        """
        Return matches sorted by descending compatibility score.

        Each entry: (match_user, score, label)
        label — 'Perfect' or 'Suggested'
        """
        if isinstance(current_user, HouseOwner):
            candidates = [u for u in all_users if isinstance(u, HouseSeeker)]
        elif isinstance(current_user, HouseSeeker):
            candidates = [u for u in all_users if isinstance(u, HouseOwner)]
        else:
            return []

        results = []
        for candidate in candidates:
            owner, seeker = self._resolve_pair(current_user, candidate)

            # Hard filter: budget (with margin)
            if seeker.max_budget < owner.monthly_rent - BUDGET_MARGIN:
                continue

            in_preferred = owner.neighborhood in seeker.preferred_neighborhoods
            label = "Perfect" if in_preferred else "Suggested"

            score = self._compatibility_score(current_user, candidate)
            if not in_preferred:
                score = max(0.0, score - SUGGESTION_PENALTY)

            results.append((candidate, round(score, 1), label))

        # Perfects before Suggested; within each tier, highest score first
        results.sort(key=lambda x: (x[2] != "Perfect", -x[1]))
        return results
