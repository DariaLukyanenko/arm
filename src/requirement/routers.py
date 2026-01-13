from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.requirement.dao import RequirementDAO
from src.requirement.schemas import (
    RequirementCreate,
    RequirementUpdate,
    RequirementFull,
    RequirementListResponse,
    Requirement
)
from src.requirement_content.dao import RequirementContentDAO
from src.requirement_content_history.dao import ReqContentHistoryDAO
from src.requirement_workflow.dao import RequirementWorkflowDAO
from src.requirement_workflow_history.dao import ReqWorkflowHistoryDAO

requirement_router = APIRouter(prefix='/api/requirements', tags=['Требования'])


@requirement_router.get(
    "/",
    response_model=RequirementListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список требований с фильтрами"
)
async def get_requirements(
        session: SessionDep,
        project_id: Optional[UUID] = Query(None, description="Фильтр по проекту"),
        type: Optional[str] = Query(None, description="Фильтр по типу"),
        created_by: Optional[UUID] = Query(None, description="Фильтр по создателю"),
        priority: Optional[int] = Query(None, ge=1, le=5, description="Фильтр по приоритету"),
        _=Depends(UserDependency())
):
    """Получение списка требований с фильтрацией"""
    filters = {}
    if project_id:
        filters["project_id"] = project_id
    if type:
        filters["type"] = type
    if created_by:
        filters["created_by_user_id"] = created_by

    requirements = await RequirementDAO.get_by(session, **filters)
    
    # Формируем полные объекты с content и workflow
    result = []
    for req in requirements:
        # Получаем content
        content_list = await RequirementContentDAO.get_by(session, requirement_id=req.id)
        content = content_list[0] if content_list else None
        
        # Получаем workflow
        workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=req.id)
        workflow = workflow_list[0] if workflow_list else None
        
        # Фильтруем по priority если указан
        if priority and workflow and workflow.priority != priority:
            continue
            
        result.append(RequirementFull(
            requirement=req,
            content=content,
            workflow=workflow
        ))
    
    return RequirementListResponse(data=result)


@requirement_router.post(
    "/",
    response_model=RequirementFull,
    status_code=status.HTTP_201_CREATED,
    summary="Создать требование"
)
async def create_requirement(
        session: SessionDep,
        requirement_data: RequirementCreate,
        current_user=Depends(UserDependency())
):
    """Создание нового требования с валидацией данных"""
    # Вычисляем path и depth на основе parent_id
    path = ""
    depth = 0
    
    if requirement_data.parent_id:
        parent = await RequirementDAO.get(session, requirement_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительское требование не найдено"
            )
        depth = parent.depth + 1
        path = f"{parent.path}.{depth}"
    else:
        # Корневое требование
        # Считаем количество корневых требований в проекте
        siblings = await RequirementDAO.get_by(
            session,
            project_id=requirement_data.project_id,
            depth=0
        )
        path = str(len(siblings) + 1)
    
    # Создаем требование
    requirement = await RequirementDAO.create(
        session,
        project_id=requirement_data.project_id,
        name=requirement_data.name,
        type=requirement_data.type.value,
        path=path,
        depth=depth,
        parent_id=requirement_data.parent_id,
        created_by_user_id=current_user.id
    )
    
    # Создаем содержимое
    content = await RequirementContentDAO.create(
        session,
        requirement_id=requirement.id,
        development_basis=requirement_data.development_basis,
        development_purpose=requirement_data.development_purpose,
        description_text=requirement_data.description_text,
        acceptance_criteria=requirement_data.acceptance_criteria,
        document_requires=requirement_data.document_requires
    )
    
    # Создаем первую запись в истории содержимого (is_active=True)
    await ReqContentHistoryDAO.create(
        session,
        requirement_id=requirement.id,
        prev_content_history_id=None,
        created_by_user_id=current_user.id,
        development_basis=requirement_data.development_basis,
        development_purpose=requirement_data.development_purpose,
        description_text=requirement_data.description_text,
        acceptance_criteria=requirement_data.acceptance_criteria,
        document_requires=requirement_data.document_requires,
        is_active=True
    )
    
    # Создаем workflow со статусом draft
    workflow = await RequirementWorkflowDAO.create(
        session,
        requirement_id=requirement.id,
        priority=1,
        status='draft'
    )
    
    # Создаем первую запись в истории workflow (is_active=True)
    await ReqWorkflowHistoryDAO.create(
        session,
        requirement_id=requirement.id,
        prev_workflow_history_id=None,
        created_by_user_id=current_user.id,
        priority=1,
        status='draft',
        is_active=True
    )
    
    return RequirementFull(
        requirement=requirement,
        content=content,
        workflow=workflow
    )


@requirement_router.get(
    "/{requirement_id}",
    response_model=RequirementFull,
    status_code=status.HTTP_200_OK,
    summary="Получить требование"
)
async def get_requirement(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Получение полной информации о требовании"""
    try:
        requirement = await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем content
    content_list = await RequirementContentDAO.get_by(session, requirement_id=requirement.id)
    content = content_list[0] if content_list else None
    
    # Получаем workflow
    workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=requirement.id)
    workflow = workflow_list[0] if workflow_list else None
    
    return RequirementFull(
        requirement=requirement,
        content=content,
        workflow=workflow
    )


@requirement_router.put(
    "/{requirement_id}",
    response_model=Requirement,
    status_code=status.HTTP_200_OK,
    summary="Обновить требование"
)
async def update_requirement(
        session: SessionDep,
        requirement_id: UUID,
        requirement_data: RequirementUpdate,
        _=Depends(UserDependency())
):
    """Обновление требования с версионированием"""
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    update_data = requirement_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )
    
    # Если тип меняется, конвертируем enum в строку
    if "type" in update_data and update_data["type"]:
        update_data["type"] = update_data["type"].value
    
    requirement = await RequirementDAO.update(session, requirement_id, **update_data)
    return requirement


@requirement_router.delete(
    "/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить требование"
)
async def delete_requirement(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Удаление требования (мягкое удаление)"""
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    await RequirementDAO.delete(session, requirement_id)
