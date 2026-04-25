from models.base_user import User


class HouseSeeker(User):
    """
    A user who is looking for a place to rent.

    OOP pillars demonstrated here:
      Inheritance   — extends User and inherits all base fields.
      Polymorphism  — provides concrete __str__ and get_detail().
      Encapsulation — max_budget is private and validated (must be > 0).
    """

    def __init__(
        self,
        user_id: int,
        name: str,
        age: int,
        gender: str,
        occupation: str,
        bio: str,
        avatar_url: str,
        habits: list[str],
        languages: list[str],
        max_budget: int,
        preferred_neighborhoods: list[str],
    ):
        super().__init__(user_id, name, age, gender, occupation, bio,
                         avatar_url, habits, languages)
        self.max_budget              = max_budget   
        self.preferred_neighborhoods = preferred_neighborhoods

    # ── Encapsulation: max_budget ─────────────────────────────────────────

    @property
    def max_budget(self) -> int:
        return self._max_budget

    @max_budget.setter
    def max_budget(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                f"max_budget must be greater than 0, got {value!r}."
            )
        self._max_budget = value

    # ── Polymorphism ──────────────────────────────────────────────────────

    def get_detail(self) -> str:
        """Role-specific detail: budget and preferred neighbourhoods."""
        hoods = ", ".join(self.preferred_neighborhoods)
        return f"Budget: €{self.max_budget}/mo  |  Wants: {hoods}"

    def __str__(self) -> str:
        habits_str    = ", ".join(self.habits)               if self.habits               else "none"
        languages_str = ", ".join(self.languages)            if self.languages            else "none"
        hoods_str     = ", ".join(self.preferred_neighborhoods) if self.preferred_neighborhoods else "none"
        return (
            f"HouseSeeker(id={self.user_id}, name={self.name}, age={self.age}, "
            f"occupation={self.occupation}, habits=[{habits_str}], "
            f"languages=[{languages_str}], max_budget=€{self.max_budget}, "
            f"preferred_neighborhoods=[{hoods_str}])"
        )
