from src.database.base_dao import BaseDAO
from src.user.models import User


class UserDAO(BaseDAO[User]):
    model = User
