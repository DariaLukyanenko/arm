from src.database.base_dao import BaseDAO
from src.requirement_approver.models import RequirementApprover


class RequirementApproverDAO(BaseDAO[RequirementApprover]):
    model = RequirementApprover

