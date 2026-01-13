from src.database.base_dao import BaseDAO
from src.project.models import Project


class ProjectDAO(BaseDAO[Project]):
    model = Project
