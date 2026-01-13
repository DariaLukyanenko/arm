from src.database.base_dao import BaseDAO
from src.requirement_content.models import RequirementContent


class RequirementContentDAO(BaseDAO[RequirementContent]):
    model = RequirementContent

