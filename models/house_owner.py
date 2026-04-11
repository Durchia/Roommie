from models.base_user import User


class HouseOwner(User):
    """A user who owns a place and is looking for a roommate."""

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
        super().__init__(user_id, name, age, gender, occupation, bio, avatar_url, habits, languages)
        self.neighborhood = neighborhood
        self.monthly_rent = monthly_rent

    def __str__(self) -> str:
        base = super().__str__()
        return (
            f"HouseOwner({base}, neighborhood={self.neighborhood}, "
            f"monthly_rent={self.monthly_rent}€)"
        )
