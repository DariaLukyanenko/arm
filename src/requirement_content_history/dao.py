from src.database.base_dao import BaseDAO
from src.requirement_content_history.models import ReqContentHistory


class ReqContentHistoryDAO(BaseDAO[ReqContentHistory]):
    model = ReqContentHistory

