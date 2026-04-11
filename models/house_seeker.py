from models.base_user import User


class HouseSeeker(User):
    """A user who is looking for a place to rent."""

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
        super().__init__(user_id, name, age, gender, occupation, bio, avatar_url, habits, languages)
        self.max_budget = max_budget
        self.preferred_neighborhoods = preferred_neighborhoods

    def __str__(self) -> str:
        base = super().__str__()
        neighborhoods_str = ", ".join(self.preferred_neighborhoods) if self.preferred_neighborhoods else "any"
        return (
            f"HouseSeeker({base}, max_budget={self.max_budget}€, "
            f"preferred_neighborhoods=[{neighborhoods_str}])"
        )
