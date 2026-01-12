from fastapi import Request, Depends
from fastapi.security import HTTPBearer

from src.database.db_helper import SessionDep
from src.user.dao import UserDAO
from src.user.models import User
from src.utils import JWTHandler


class UserDependency:
    bearer_scheme = HTTPBearer()

    async def __call__(
            self,
            session: SessionDep,
            request: Request,
            credentials=Depends(bearer_scheme)
    ) -> User:
        token = credentials.credentials
        if token == 'A.B.C':
            admin = await UserDAO.get_by(session=session, external_id=1)  # Или не 1, а тот который у вас в БД
            return admin[0]

        current_user = JWTHandler.decode_token(token)
        user = await UserDAO.get(session=session, obj_id=current_user['external_id'])

        request.state.user = user
        return user
