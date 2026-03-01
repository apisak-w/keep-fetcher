import json
from domain.user import User, UserRepository

class KVUserRepository(UserRepository):
    """
    Cloudflare KV implementation of the UserRepository.
    """
    def __init__(self, kv_namespace):
        self.kv = kv_namespace

    async def get_by_id(self, user_id: int) -> User:
        if not self.kv:
            print("KVUserRepository: No KV namespace binding found.")
            return User(user_id=user_id, is_authorized=False)
            
        key = f"user:{user_id}"
        print(f"KVUserRepository: Fetching key '{key}'")
        
        kv_data_str = await self.kv.get(key)
        print(f"KVUserRepository: Raw data from KV for '{key}': {kv_data_str}")
        
        if not kv_data_str:
            return User(user_id=user_id, is_authorized=False)
            
        try:
            data = json.loads(kv_data_str)
            user = User.from_dict(user_id, data)
            print(f"KVUserRepository: Parsed user: {user_id}, Authorized: {user.is_authorized}")
            return user
        except Exception as e:
            print(f"Error parsing KV data for user {user_id}: {e}")
            return User(user_id=user_id, is_authorized=False)
