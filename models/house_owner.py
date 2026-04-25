from models.base_user import User


class HouseOwner(User):
    """
    A user who owns a place and is looking for a roommate.

    OOP pillars demonstrated here:
      Inheritance   — extends User and inherits all base fields.
      Polymorphism  — provides concrete __str__ and get_detail().
      Encapsulation — monthly_rent is private and validated (must be > 0).
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
        neighborhood: str,
        monthly_rent: int,
    ):
        super().__init__(user_id, name, age, gender, occupation, bio,
                         avatar_url, habits, languages)
        self.neighborhood  = neighborhood
        self.monthly_rent  = monthly_rent   # routed through property setter

    # ── Encapsulation: monthly_rent ───────────────────────────────────────

    @property
    def monthly_rent(self) -> int:
        return self._monthly_rent

    @monthly_rent.setter
    def monthly_rent(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                f"monthly_rent must be greater than 0, got {value!r}."
            )
        self._monthly_rent = value

    # ── Polymorphism ──────────────────────────────────────────────────────

    def get_detail(self) -> str:
        """Role-specific detail: neighbourhood and monthly rent."""
        return f"Neighbourhood: {self.neighborhood}  |  Rent: €{self.monthly_rent}/mo"

    def __str__(self) -> str:
        habits_str    = ", ".join(self.habits)    if self.habits    else "none"
        languages_str = ", ".join(self.languages) if self.languages else "none"
        return (
            f"HouseOwner(id={self.user_id}, name={self.name}, age={self.age}, "
            f"occupation={self.occupation}, habits=[{habits_str}], "
            f"languages=[{languages_str}], neighborhood={self.neighborhood}, "
            f"monthly_rent=€{self.monthly_rent})"
        )
