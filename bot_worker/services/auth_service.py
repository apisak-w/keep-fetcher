from domain.user import User, UserRepository

class AuthService:
    """
    Service for handling authentication and authorization.
    """
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate(self, user_id: int) -> User:
        """
        Authenticate a user by ID. 
        Returns a User entity with its authorization status.
        """
        user = await self.user_repository.get_by_id(user_id)
        return user
