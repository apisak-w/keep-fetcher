import json

class User:
    """
    Domain model representing a bot user.
    """
    def __init__(self, user_id: int, is_authorized: bool = False):
        self.user_id = user_id
        self.is_authorized = is_authorized

    @classmethod
    def from_dict(cls, user_id: int, data: dict):
        return cls(
            user_id=user_id,
            is_authorized=data.get("is_authorized", False)
        )

class UserRepository:
    """
    Repository interface for User data access.
    """
    async def get_by_id(self, user_id: int) -> User:
        raise NotImplementedError
