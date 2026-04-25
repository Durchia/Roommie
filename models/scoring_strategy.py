from abc import ABC, abstractmethod

# Scoring weights — must sum to 100
WEIGHT_HABITS    = 70
WEIGHT_LANGUAGES = 20
WEIGHT_VIBE      = 10

OCCUPATION_CATEGORIES: dict[str, set[str]] = {
    "creative": {"Artist", "Designer", "Musician", "Photographer", "Architect"},
    "tech":     {"Software Developer", "Engineer", "Data Scientist", "IT Specialist"},
    "academic": {"Student", "Teacher", "Professor", "Researcher"},
    "food":     {"Chef", "Baker", "Nutritionist"},
    "health":   {"Doctor", "Nurse", "Physiotherapist"},
    "business": {"Manager", "Accountant", "Lawyer", "Entrepreneur"},
}


class ScoringStrategy(ABC):
    """
    Design Pattern — Strategy
    -------------------------
    Abstract base that defines the interface for all scoring algorithms.
    Swap out DefaultScoringStrategy for any alternative without touching
    MatchingEngine.
    """

    @abstractmethod
    def score(self, user_a, user_b) -> float:
        """Return a compatibility score in [0, 100] between user_a and user_b."""


class DefaultScoringStrategy(ScoringStrategy):
    """
    Composite Jaccard scorer.

    Breakdown (max 100 pts)
    -----------------------
    Habits    : Jaccard similarity × 70
    Languages : Jaccard similarity × 20
    Vibe      : flat 10 pts if occupations share a category
    """

    def habit_score(self, user_a, user_b) -> float:
        """Jaccard on habit sets, scaled to WEIGHT_HABITS."""
        a, b = set(user_a.habits), set(user_b.habits)
        union = a | b
        if not union:
            return 0.0
        return (len(a & b) / len(union)) * WEIGHT_HABITS

    def language_score(self, user_a, user_b) -> float:
        """Jaccard on language sets, scaled to WEIGHT_LANGUAGES."""
        a, b = set(user_a.languages), set(user_b.languages)
        union = a | b
        if not union:
            return 0.0
        return (len(a & b) / len(union)) * WEIGHT_LANGUAGES

    def vibe_score(self, user_a, user_b) -> float:
        """Flat WEIGHT_VIBE bonus when both occupations share a category.

        Normalises with .strip().title() so 'software developer' matches
        'Software Developer' regardless of how the string was stored.
        """
        occ_a = user_a.occupation.strip().title()
        occ_b = user_b.occupation.strip().title()
        for members in OCCUPATION_CATEGORIES.values():
            if occ_a in members and occ_b in members:
                return float(WEIGHT_VIBE)
        return 0.0

    def score(self, user_a, user_b) -> float:
        """Composite score capped at 100."""
        return min(
            self.habit_score(user_a, user_b)
            + self.language_score(user_a, user_b)
            + self.vibe_score(user_a, user_b),
            100.0,
        )
