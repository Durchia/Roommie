from abc import ABC, abstractmethod


class User(ABC):
    """
    Abstract base class for all Roommie users.

    OOP pillars demonstrated here:
      Abstraction   — ABC enforces __str__ and get_detail() on every subclass.
      Encapsulation — age is private (_age) and validated through a property.
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
    ):
        self.user_id    = user_id
        self.name       = name
        self.age        = age          # routed through the property setter
        self.gender     = gender
        self.occupation = occupation
        self.bio        = bio
        self.avatar_url = avatar_url
        self.habits     = habits
        self.languages  = languages

    # ── Encapsulation: age ────────────────────────────────────────────────

    @property
    def age(self) -> int:
        return self._age
       
    @age.setter
    def age(self, value: int) -> None:
        if not (16 <= value <= 120):
            raise ValueError(
                f"Age must be between 16 and 120, got {value!r}."
            )
        self._age = value

    # ── Concrete shared method ────────────────────────────────────────────

    def get_summary(self) -> str:
        return f"{self.name}, {self.age} ({self.occupation})"

    # ── Abstraction: subclasses must implement both ───────────────────────

    @abstractmethod
    def __str__(self) -> str:
        """Return a full string representation of the user."""

    @abstractmethod
    def get_detail(self) -> str:
        """Return the role-specific detail line (location + rent or budget)."""
