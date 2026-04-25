from models.house_owner import HouseOwner
from models.house_seeker import HouseSeeker
from models.scoring_strategy import DefaultScoringStrategy, ScoringStrategy

BUDGET_MARGIN      = 100   # € — seeker may exceed owner rent by this much
SUGGESTION_PENALTY = 30    # pts deducted when neighbourhood not preferred


class MatchingEngine:
    """
    Matches HouseOwners with HouseSeekers.

    Design Pattern — Strategy
    -------------------------
    Scoring is delegated to a ScoringStrategy instance injected at
    construction time.  Swap in any ScoringStrategy subclass without
    changing this class.

    Match tiers
    -----------
    Perfect   — budget within margin AND neighbourhood preferred → full score
    Suggested — budget within margin, neighbourhood not listed   → score − SUGGESTION_PENALTY
    """

    def __init__(self, strategy: ScoringStrategy | None = None):
        self.strategy: ScoringStrategy = strategy or DefaultScoringStrategy()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_pair(self, current_user, candidate):
        """Return (owner, seeker) regardless of which is current_user."""
        if isinstance(current_user, HouseOwner):
            return current_user, candidate
        return candidate, current_user

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_breakdown(self, user_a, user_b) -> dict:
        """
        Return component scores for display purposes.
        Full breakdown available when strategy is DefaultScoringStrategy;
        custom strategies return only the total.
        """
        s = self.strategy
        if isinstance(s, DefaultScoringStrategy):
            return {
                "habits":    round(s.habit_score(user_a, user_b), 1),
                "languages": round(s.language_score(user_a, user_b), 1),
                "vibe":      round(s.vibe_score(user_a, user_b), 1),
                "total":     round(s.score(user_a, user_b), 1),
            }
        return {
            "habits":    0.0,
            "languages": 0.0,
            "vibe":      0.0,
            "total":     round(s.score(user_a, user_b), 1),
        }

    def find_matches(self, current_user, all_users: list) -> list:
        """
        Return matches sorted by descending score.

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

            # Hard budget filter (with margin)
            if seeker.max_budget < owner.monthly_rent - BUDGET_MARGIN:
                continue

            in_preferred = owner.neighborhood in seeker.preferred_neighborhoods
            label        = "Perfect" if in_preferred else "Suggested"

            score = self.strategy.score(current_user, candidate)
            if not in_preferred:
                score = max(0.0, score - SUGGESTION_PENALTY)

            results.append((candidate, round(score, 1), label))

        # Perfects first; within each tier highest score first
        results.sort(key=lambda x: (x[2] != "Perfect", -x[1]))
        return results
