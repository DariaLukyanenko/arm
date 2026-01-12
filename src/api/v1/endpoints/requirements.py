"""
API endpoints для требований
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import csv
import io
import logging

logger = logging.getLogger(__name__)

from db.session import get_db
from models.requirement import (
    Requirement, RequirementContent, RequirementWorkflow,
    RequirementDependence, ReqTestCaseCoverage, Project,
    ReqContentHistory
)
from schemas.requirement import (
    RequirementCreate, RequirementUpdate, RequirementFull,
    RequirementListResponse, RequirementContent as RequirementContentSchema,
    RequirementContentUpdate, WorkflowTransition, WorkflowStatus,
    DependencyCreate, Dependency as DependencySchema, DependencyList,
    TestCoverageUpdate, TestCoverage as TestCoverageSchema,
    TraceabilityMatrix, TraceabilityItem
)

router = APIRouter(prefix="/requirements", tags=["Требования"])


@router.get("", response_model=RequirementListResponse)
async def get_requirements(
    project_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    created_by: Optional[int] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=5),
    db: AsyncSession = Depends(get_db)
):
    """Получить список требований с фильтрами"""
    query = select(Requirement).options(
        selectinload(Requirement.contents).selectinload(RequirementContent.workflows)
    ).where(Requirement.is_deleted == False)
    
    if project_id:
        query = query.where(Requirement.project_id == project_id)
    if type:
        query = query.where(Requirement.type == type)
    if created_by:
        query = query.where(Requirement.created_by_user_id == created_by)
    
    result = await db.execute(query)
    requirements = result.scalars().unique().all()
    
    # Фильтрация по status и priority через workflow
    filtered_reqs = []
    for req in requirements:
        active_content = next((c for c in req.contents if c.is_active), None)
        if active_content:
            active_workflow = next((w for w in active_content.workflows if w.is_active), None)
            if active_workflow:
                if status and active_workflow.status != status:
                    continue
                if priority and active_workflow.priority != priority:
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
            "created_at": req.created_at,
            "created_by_user_id": req.created_by_user_id,
            "path": req.path,
            "depth": req.depth,
            "requirement_group_id": req.requirement_group_id,
            "is_deleted": req.is_deleted,
            "parent_id": req.parent_id,
            "content": active_content,
            "workflow": active_workflow
        }
        full_requirements.append(req_dict)
    
    return {"data": full_requirements}


@router.post("", response_model=RequirementFull, status_code=201)
async def create_requirement(
    requirement_data: RequirementCreate,
    current_user_id: int = 1,  # TODO: Получать из JWT
    db: AsyncSession = Depends(get_db)
):
    """Создать новое требование"""
    # Создаем требование
    new_requirement = Requirement(
        project_id=requirement_data.project_id,
        name=requirement_data.name,
        type=requirement_data.type,
        parent_id=requirement_data.parent_id,
        created_by_user_id=current_user_id
    )
    db.add(new_requirement)
    await db.flush()
    
    # Создаем контент
    new_content = RequirementContent(
        requirement_id=new_requirement.id,
        development_basis=requirement_data.content.development_basis,
        development_purpose=requirement_data.content.development_purpose,
        description_text=requirement_data.content.description_text,
        acceptance_criteria=requirement_data.content.acceptance_criteria,
        document_requires=requirement_data.content.document_requires,
        created_by_user_id=current_user_id,
        is_active=True
    )
    db.add(new_content)
    await db.flush()
    
    # Создаем workflow
    new_workflow = RequirementWorkflow(
        requirement_content_id=new_content.id,
        status=WorkflowStatus.draft,
        priority=3,
        created_by_user_id=current_user_id,
        is_active=True
    )
    db.add(new_workflow)
    await db.commit()
    
    # Загружаем полный объект
    await db.refresh(new_requirement)
    await db.refresh(new_content)
    await db.refresh(new_workflow)
    
    return {
        **new_requirement.__dict__,
        "content": new_content,
        "workflow": new_workflow
    }


@router.get("/export", response_class=Response)
async def export_requirements(
    project_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    fields: Optional[str] = Query("id,name,type,status,priority,created_at"),
    filename: Optional[str] = Query("requirements_export"),
    db: AsyncSession = Depends(get_db)
):
    """Экспорт требований в CSV"""
    try:
        logger.info(f"[EXPORT] Start export with project_id={project_id}")
        
        # Получаем требования с фильтрами
        response = await get_requirements(project_id=project_id, type=type, status=status, db=db)
        requirements = response["data"]
        
        logger.info(f"[EXPORT] Found {len(requirements)} requirements")
        
        if len(requirements) > 10000:
            raise HTTPException(status_code=413, detail="Превышен лимит экспорта. Максимум 10000 записей")
        
        # Создаем CSV
        output = io.StringIO()
        field_list = fields.split(",")
        writer = csv.DictWriter(output, fieldnames=field_list)
        writer.writeheader()
        
        for req in requirements:
            row = {}
            for field in field_list:
                if field == "status":
                    row[field] = req.get("workflow", {}).get("status") if req.get("workflow") else "N/A"
                elif field == "priority":
                    row[field] = req.get("workflow", {}).get("priority") if req.get("workflow") else "N/A"
                else:
                    row[field] = req.get(field, "N/A")
            writer.writerow(row)
        
        logger.info(f"[EXPORT] CSV created successfully")
        
        # Возвращаем CSV
        timestamp = datetime.now().strftime("%Y%m%d")
        return Response(
            content=output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}_{timestamp}.csv"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EXPORT] ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/{requirement_id}", response_model=RequirementFull)
async def get_requirement(
    requirement_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить требование по ID"""
    query = select(Requirement).options(
        selectinload(Requirement.contents).selectinload(RequirementContent.workflows)
    ).where(
        Requirement.id == requirement_id,
        Requirement.is_deleted == False
    )
    
    result = await db.execute(query)
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    active_content = next((c for c in requirement.contents if c.is_active), None)
    active_workflow = None
    if active_content:
        active_workflow = next((w for w in active_content.workflows if w.is_active), None)
    
    return {
        **requirement.__dict__,
        "content": active_content,
        "workflow": active_workflow
    }


@router.put("/{requirement_id}", response_model=RequirementFull)
async def update_requirement(
    requirement_id: int,
    requirement_data: RequirementUpdate,
    current_user_id: int = 1,  # TODO: Получать из JWT
    db: AsyncSession = Depends(get_db)
):
    """Обновить требование"""
    query = select(Requirement).where(
        Requirement.id == requirement_id,
        Requirement.is_deleted == False
    )
    result = await db.execute(query)
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if requirement_data.name is not None:
        requirement.name = requirement_data.name
    if requirement_data.type is not None:
        requirement.type = requirement_data.type
    
    await db.commit()
    await db.refresh(requirement)
    
    return await get_requirement(requirement_id, db)


@router.delete("/{requirement_id}", status_code=204)
async def delete_requirement(
    requirement_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить требование (мягкое удаление)"""
    query = select(Requirement).where(Requirement.id == requirement_id)
    result = await db.execute(query)
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    requirement.is_deleted = True
    await db.commit()
    
    return Response(status_code=204)


@router.get("/{requirement_id}/content", response_model=RequirementContentSchema)
async def get_requirement_content(
    requirement_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить содержимое требования"""
    query = select(RequirementContent).where(
        and_(
            RequirementContent.requirement_id == requirement_id,
            RequirementContent.is_active == True
        )
    )
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


@router.put("/{requirement_id}/content", response_model=RequirementContentSchema)
async def update_requirement_content(
    requirement_id: int,
    content_data: RequirementContentUpdate,
    current_user_id: int = 1,  # TODO: Получать из JWT
    db: AsyncSession = Depends(get_db)
):
    """Обновить содержимое требования с созданием новой версии"""
    # Проверяем что требование существует и не удалено
    req_check = await db.execute(
        select(Requirement).where(
            Requirement.id == requirement_id,
            Requirement.is_deleted == False
        )
    )
    if not req_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Деактивируем старый контент
    query = select(RequirementContent).options(
        selectinload(RequirementContent.workflows)
    ).where(
        and_(
            RequirementContent.requirement_id == requirement_id,
            RequirementContent.is_active == True
        )
    )
    result = await db.execute(query)
    old_content = result.scalar_one_or_none()
    
    if old_content:
        old_content.is_active = False
        
        # Деактивируем старый workflow
        old_workflow = next((w for w in old_content.workflows if w.is_active), None)
        if old_workflow:
            old_workflow.is_active = False
    
    # Создаем новый контент
    new_content = RequirementContent(
        requirement_id=requirement_id,
        development_basis=content_data.development_basis,
        development_purpose=content_data.development_purpose,
        description_text=content_data.description_text,
        acceptance_criteria=content_data.acceptance_criteria,
        document_requires=content_data.document_requires,
        created_by_user_id=current_user_id,
        prev_req_content_id=old_content.id if old_content else None,
        is_active=True
    )
    db.add(new_content)
    await db.flush()
    
    # Создаем новый workflow (копируем из старого)
    old_workflow = None
    if old_content:
        old_workflow = next((w for w in old_content.workflows if w.is_active), None)
    
    new_workflow = RequirementWorkflow(
        requirement_content_id=new_content.id,
        status=old_workflow.status if old_workflow else WorkflowStatus.draft,
        priority=old_workflow.priority if old_workflow else 3,
        created_by_user_id=current_user_id,
        prev_req_workflow_id=old_workflow.id if old_workflow else None,
        is_active=True
    )
    db.add(new_workflow)
    
    await db.commit()
    await db.refresh(new_content)
    
    return new_content


@router.get("/{requirement_id}/workflow/history")
async def get_workflow_history(
    requirement_id: int,
    db: AsyncSession = Depends(get_db)
):
    """История изменений workflow требования"""
    query = select(RequirementContent).where(
        RequirementContent.requirement_id == requirement_id
    ).order_by(RequirementContent.created_at.desc())
    
    result = await db.execute(query)
    contents = result.scalars().all()
    
    history = []
    for content in contents:
        if content.workflow:
            history.append({
                "id": content.workflow.id,
                "status": content.workflow.status,
                "priority": content.workflow.priority,
                "created_at": content.workflow.created_at,
                "created_by_user_id": content.workflow.created_by_user_id,
                "is_active": content.workflow.is_active
            })
    
    return {"data": history}


@router.post("/{requirement_id}/workflow")
async def change_workflow_status(
    requirement_id: int,
    transition: WorkflowTransition,
    current_user_id: int = 1,  # TODO: Получать из JWT
    db: AsyncSession = Depends(get_db)
):
    """Изменить статус workflow требования"""
    # Проверяем что требование существует и не удалено
    req_check = await db.execute(
        select(Requirement).where(
            Requirement.id == requirement_id,
            Requirement.is_deleted == False
        )
    )
    if not req_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Получаем активный контент
    query = select(RequirementContent).where(
        and_(
            RequirementContent.requirement_id == requirement_id,
            RequirementContent.is_active == True
        )
    ).options(selectinload(RequirementContent.workflows))
    
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Деактивируем старый workflow
    old_workflow = next((w for w in content.workflows if w.is_active), None)
    if old_workflow:
        old_workflow.is_active = False
    
    # Создаем новый workflow
    new_workflow = RequirementWorkflow(
        requirement_content_id=content.id,
        status=transition.new_status,
        priority=old_workflow.priority,
        created_by_user_id=current_user_id,
        prev_req_workflow_id=old_workflow.id,
        is_active=True
    )
    db.add(new_workflow)
    
    await db.commit()
    await db.refresh(new_workflow)
    
    return {"message": "Status updated", "new_status": new_workflow.status}


@router.get("/{requirement_id}/content/history")
async def get_content_history(
    requirement_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить историю изменений содержимого требования
    
    - **requirement_id**: ID требования
    - **limit**: Количество записей истории (по умолчанию 10, максимум 100)
    """
    # Проверяем существование требования
    req_check = await db.execute(
        select(Requirement).where(
            Requirement.id == requirement_id,
            Requirement.is_deleted == False
        )
    )
    if not req_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Получаем все версии контента для этого требования
    query = select(RequirementContent).where(
        RequirementContent.requirement_id == requirement_id
    ).order_by(RequirementContent.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    contents = result.scalars().all()
    
    # Формируем историю
    history = []
    for content in contents:
        history.append({
            "id": content.id,
            "requirement_id": content.requirement_id,
            "created_at": content.created_at,
            "created_by_user_id": content.created_by_user_id,
            "is_active": content.is_active,
            "content": {
                "development_basis": content.development_basis,
                "development_purpose": content.development_purpose,
                "description_text": content.description_text,
                "acceptance_criteria": content.acceptance_criteria,
                "document_requires": content.document_requires
            }
        })
    
    return {"data": history}


@router.get("/{requirement_id}/traceability")
async def get_requirement_traceability(
    requirement_id: int,
    depth: int = Query(2, ge=1, le=5),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить матрицу трассируемости требования
    
    - **requirement_id**: ID требования
    - **depth**: Глубина поиска связей (по умолчанию 2, максимум 5)
    """
    try:
        logger.info(f"[TRACEABILITY] Start for requirement_id={requirement_id}, depth={depth}")
        
        # Проверяем существование требования
        logger.info(f"[TRACEABILITY] Checking requirement existence...")
        req_query = select(Requirement).where(
            Requirement.id == requirement_id,
            Requirement.is_deleted == False
        )
        req_result = await db.execute(req_query)
        requirement = req_result.scalar_one_or_none()
        
        if not requirement:
            logger.warning(f"[TRACEABILITY] Requirement {requirement_id} not found")
            raise HTTPException(status_code=404, detail="Requirement not found")
        
        logger.info(f"[TRACEABILITY] Found requirement: {requirement.name}")
        
        # Получаем зависимости "от" (source - требования, от которых зависит текущее)
        logger.info(f"[TRACEABILITY] Fetching source dependencies...")
        source_query = select(RequirementDependence, Requirement).join(
            Requirement,
            Requirement.id == RequirementDependence.source_requirement_id
        ).where(
            RequirementDependence.target_requirement_id == requirement_id,
            Requirement.is_deleted == False
        )
        logger.info(f"[TRACEABILITY] Executing source query...")
        source_result = await db.execute(source_query)
        source_rows = source_result.all()
        logger.info(f"[TRACEABILITY] Found {len(source_rows)} source dependencies")
        
        # Получаем зависимости "к" (target - требования, которые зависят от текущего)
        logger.info(f"[TRACEABILITY] Fetching target dependencies...")
        target_query = select(RequirementDependence, Requirement).join(
            Requirement,
            Requirement.id == RequirementDependence.target_requirement_id
        ).where(
            RequirementDependence.source_requirement_id == requirement_id,
            Requirement.is_deleted == False
        )
        logger.info(f"[TRACEABILITY] Executing target query...")
        target_result = await db.execute(target_query)
        target_rows = target_result.all()
        logger.info(f"[TRACEABILITY] Found {len(target_rows)} target dependencies")
        
        # Формируем список source требований
        logger.info(f"[TRACEABILITY] Building source items...")
        source_items = []
        for dep, req in source_rows:
            source_items.append({
                "requirement_id": req.id,
                "requirement_name": req.name
            })
        
        # Формируем список target требований
        logger.info(f"[TRACEABILITY] Building target items...")
        target_items = []
        for dep, req in target_rows:
            target_items.append({
                "requirement_id": req.id,
                "requirement_name": req.name
            })
        
        logger.info(f"[TRACEABILITY] Success! Returning {len(source_items)} source + {len(target_items)} target items")
        
        return {
            "requirement_id": requirement.id,
            "requirement_name": requirement.name,
            "source": source_items,
            "target": target_items
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TRACEABILITY] ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

