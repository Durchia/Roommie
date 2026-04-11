class User:
    """Base class representing a user in the Roommie matching system."""

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
    ):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.gender = gender
        self.occupation = occupation
        self.bio = bio
        self.avatar_url = avatar_url
        self.habits = habits
        self.languages = languages

    def get_summary(self) -> str:
        """Returns a short, friendly summary of the user."""
        return f"{self.name}, {self.age} ({self.occupation})"

    def __str__(self) -> str:
        habits_str = ", ".join(self.habits) if self.habits else "none"
        languages_str = ", ".join(self.languages) if self.languages else "none"
        return (
            f"User(id={self.user_id}, name={self.name}, age={self.age}, "
            f"occupation={self.occupation}, habits=[{habits_str}], "
            f"languages=[{languages_str}])"
        )