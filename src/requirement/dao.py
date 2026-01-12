from src.database.base_dao import BaseDAO
from src.requirement.models import Requirement


class RequirementDAO(BaseDAO[Requirement]):
    model = Requirement
