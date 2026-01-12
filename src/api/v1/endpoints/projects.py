"""
API endpoints для работы с проектами
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.session import get_db
from models.requirement import Project, Requirement, RequirementContent, RequirementWorkflow
from schemas.requirement import RequirementListResponse

router = APIRouter(prefix="/projects", tags=["Проекты"])


@router.get("/{project_id}/requirements", response_model=RequirementListResponse)
async def get_project_requirements(
    project_id: int,
    type: Optional[str] = Query(None, description="Фильтр по типу требования"),
    status: Optional[str] = Query(None, description="Фильтр по статусу workflow"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все требования проекта с фильтрами
    
    - **project_id**: ID проекта (обязательный параметр в path)
    - **type**: фильтр по типу требования (functional, non-functional, business)
    - **status**: фильтр по статусу workflow (draft, review, approved, rejected)
    """
    # Проверяем существование проекта
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Получаем требования проекта
    query = select(Requirement).options(
        selectinload(Requirement.contents).selectinload(RequirementContent.workflows)
    ).where(
        Requirement.project_id == project_id,
        Requirement.is_deleted == False
    )
    
    # Фильтр по типу
    if type:
        query = query.where(Requirement.type == type)
    
    result = await db.execute(query)
    requirements = result.scalars().unique().all()
    
    # Фильтрация по status через workflow
    filtered_reqs = []
    for req in requirements:
        active_content = next((c for c in req.contents if c.is_active), None)
        if active_content:
            active_workflow = next((w for w in active_content.workflows if w.is_active), None)
            if active_workflow:
                if status and active_workflow.status != status:
                    continue
        filtered_reqs.append(req)
    
    # Преобразуем в полные схемы
    full_requirements = []
    for req in filtered_reqs:
        active_content = next((c for c in req.contents if c.is_active), None)
        active_workflow = None
        if active_content:
            active_workflow = next((w for w in active_content.workflows if w.is_active), None)
        
        req_dict = {
            "id": req.id,
            "project_id": req.project_id,
            "name": req.name,
            "type": req.type,
            "parent_id": req.parent_id,
            "created_at": req.created_at,
            "created_by_user_id": req.created_by_user_id,
            "path": req.path,
            "depth": req.depth,
            "requirement_group_id": req.requirement_group_id,
            "is_deleted": req.is_deleted,
            "content": active_content.__dict__ if active_content else None,
            "workflow": active_workflow.__dict__ if active_workflow else None
        }
        full_requirements.append(req_dict)
    
    return {"data": full_requirements}

