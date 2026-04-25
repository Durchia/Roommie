from models.house_owner import HouseOwner
from models.house_seeker import HouseSeeker


class UserFactory:
    """
    Design Pattern — Factory
    ------------------------
    Centralises object creation so callers never reference HouseOwner or
    HouseSeeker constructors directly.  Adding a new role only requires a
    change here, not at every call site.
    """

    @staticmethod
    def create(role: str, **kwargs) -> HouseOwner | HouseSeeker:
        """
        Return a HouseOwner or HouseSeeker based on *role*.

        Parameters
        ----------
        role   : "House Owner" | "House Seeker"
        kwargs : all constructor keyword arguments for the target class

        Raises
        ------
        ValueError if role is not recognised.
        """
        if role == "House Owner":
            return HouseOwner(**kwargs)
        if role == "House Seeker":
            return HouseSeeker(**kwargs)
        raise ValueError(
            f"Unknown role {role!r}. Expected 'House Owner' or 'House Seeker'."
        )
