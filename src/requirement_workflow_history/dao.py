from src.database.base_dao import BaseDAO
from src.requirement_workflow_history.models import ReqWorkflowHistory


class ReqWorkflowHistoryDAO(BaseDAO[ReqWorkflowHistory]):
    model = ReqWorkflowHistory

