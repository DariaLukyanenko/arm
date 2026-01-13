from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.project.dao import ProjectDAO
from src.project.schemas import (ProjectCreate, ProjectUpdate, Project,
                                 ProjectList)
from src.requirement.dao import RequirementDAO
from src.requirement.schemas import RequirementListResponse

project_router = APIRouter(prefix='/api/projects', tags=['Проекты'])


@project_router.get(
    "/",
    response_model=ProjectList,
    status_code=status.HTTP_200_OK,
    summary="Получить список проектов",
    description="Получение списка проектов с возможностью фильтрации"
)
async def get_projects(
        session: SessionDep,
        user_id: UUID = Query(..., description="ID пользователя"),
        created_by: Optional[UUID] = Query(None, description="Фильтр по создателю"),
        _=Depends(UserDependency())
):
    filters = {"created_by_user_id": user_id}
    if created_by is not None:
        filters["created_by_user_id"] = created_by

    projects = await ProjectDAO.get_by(session, **filters)
    return ProjectList(data=projects)


@project_router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Создать проект",
    description="Создание нового проекта. Требуется право PROJECT_CREATE"
)
async def create_project(
        session: SessionDep,
        project_data: ProjectCreate,
        current_user=Depends(UserDependency())
):
    # TODO: проверка прав PROJECT_CREATE
    existing = await ProjectDAO.get_by(session, name=project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Проект с таким названием уже существует"
        )

    project = await ProjectDAO.create(
        session,
        **project_data.model_dump(),
        created_by_user_id=current_user.id
    )
    return project


@project_router.get(
    "/{project_id}",
    response_model=Project,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о проекте"
)
async def get_project(
        session: SessionDep,
        project_id: UUID,
        _=Depends(UserDependency())
):
    try:
        project = await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    return project


@project_router.put(
    "/{project_id}",
    response_model=Project,
    status_code=status.HTTP_200_OK,
    summary="Обновить проект",
    description="Обновление проекта (возможно изменить описание проекта)"
)
async def update_project(
        session: SessionDep,
        project_id: UUID,
        project_data: ProjectUpdate,
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    update_data = project_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )

    project = await ProjectDAO.update(session, project_id, **update_data)
    return project


@project_router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить проект",
    description="Полное удаление проекта со всеми связанными требованиями и историей"
)
async def delete_project(
        session: SessionDep,
        project_id: UUID,
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # TODO: проверка на активные зависимости (409 Conflict)
    await ProjectDAO.delete(session, project_id)


@project_router.get(
    "/{project_id}/requirements",
    response_model=RequirementListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить требования проекта",
    description="Получение всех требований проекта"
)
async def get_project_requirements(
        session: SessionDep,
        project_id: UUID,
        type: Optional[str] = Query(None, description="Фильтр по типу требования"),
        req_status: Optional[str] = Query(None, alias="status", description="Фильтр по статусу"),
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    filters = {"project_id": project_id}
    if type:
        filters["type"] = type
    if req_status:
        filters["status"] = req_status

    requirements = await RequirementDAO.get_by(session, **filters)
    return RequirementListResponse(data=requirements)