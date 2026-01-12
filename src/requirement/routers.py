from fastapi import APIRouter, Depends, status

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.requirement.dao import RequirementDAO
from src.requirement.schemas import RequirementResponse, RequirementRequest

requirement_router = APIRouter(prefix='/api/requirement', tags=['Requirement'])


@requirement_router.post(
    "/",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_requirement(
    session: SessionDep,
    requirement_data: RequirementRequest,
    _=Depends(UserDependency())
):
    requirement = await RequirementDAO.create(
        session,
        **requirement_data.model_dump()
    )

    return requirement
