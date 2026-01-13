from src.database.base_dao import BaseDAO
from src.requirement_workflow.models import RequirementWorkflow


class RequirementWorkflowDAO(BaseDAO[RequirementWorkflow]):
    model = RequirementWorkflow

