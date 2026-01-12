"""
API endpoints для зависимостей между требованиями
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional

from db.session import get_db
from models.requirement import RequirementDependence, Requirement
from schemas.requirement import (
    DependencyCreate, Dependency as DependencySchema,
    DependencyList
)

router = APIRouter(tags=["Зависимости"])


@router.get("/requirements/{requirement_id}/dependencies", response_model=DependencyList)
async def get_dependencies(
    requirement_id: int,
    direction: str = Query("both", pattern="^(incoming|outgoing|both)$"),
    db: AsyncSession = Depends(get_db)
):
    """Получить зависимости требования"""
    incoming = []
    outgoing = []
    
    if direction in ["incoming", "both"]:
        # Входящие зависимости (другие требования зависят от этого)
        query = select(RequirementDependence).where(RequirementDependence.target_requirement_id == requirement_id)
        result = await db.execute(query)
        incoming = result.scalars().all()
    
    if direction in ["outgoing", "both"]:
        # Исходящие зависимости (это требование зависит от других)
        query = select(RequirementDependence).where(RequirementDependence.source_requirement_id == requirement_id)
        result = await db.execute(query)
        outgoing = result.scalars().all()
    
    return {"incoming": incoming, "outgoing": outgoing}


@router.post("/requirements/{requirement_id}/dependencies", response_model=DependencySchema, status_code=201)
async def create_dependency(
    requirement_id: int,
    dependency_data: DependencyCreate,
    current_user_id: int = 1,  # TODO: Получать из JWT
    db: AsyncSession = Depends(get_db)
):
    """Создать зависимость между требованиями"""
    # Проверяем существование требований
    source_query = select(Requirement).where(Requirement.id == requirement_id)
    target_query = select(Requirement).where(Requirement.id == dependency_data.target_requirement_id)
    
    source_result = await db.execute(source_query)
    target_result = await db.execute(target_query)
    
    source_req = source_result.scalar_one_or_none()
    target_req = target_result.scalar_one_or_none()
    
    if not source_req or not target_req:
        raise HTTPException(status_code=404, detail="One or both requirements not found")
    
    # Проверяем на самозависимость
    if requirement_id == dependency_data.target_requirement_id:
        raise HTTPException(status_code=400, detail="Cannot create dependency to itself")
    
    # Проверяем на дубликаты
    existing_query = select(RequirementDependence).where(
        and_(
            RequirementDependence.source_requirement_id == requirement_id,
            RequirementDependence.target_requirement_id == dependency_data.target_requirement_id,
            RequirementDependence.type == dependency_data.type
        )
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dependency already exists")
    
    # Создаем зависимость
    new_dependency = RequirementDependence(
        source_requirement_id=requirement_id,
        target_requirement_id=dependency_data.target_requirement_id,
        type=dependency_data.type,
        strength=dependency_data.strength,
        description=dependency_data.description,
        created_by_user_id=current_user_id
    )
    db.add(new_dependency)
    await db.commit()
    await db.refresh(new_dependency)
    
    return new_dependency


@router.delete("/dependencies/{dependency_id}", status_code=204)
async def delete_dependency(
    dependency_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить зависимость"""
    query = select(RequirementDependence).where(RequirementDependence.id == dependency_id)
    result = await db.execute(query)
    dependency = result.scalar_one_or_none()
    
    if not dependency:
        raise HTTPException(status_code=404, detail="Dependency not found")
    
    await db.delete(dependency)
    await db.commit()
    
    return None


@router.get("/requirements/{requirement_id}/traceability", response_model=dict)
async def get_traceability_matrix(
    requirement_id: int,
    depth: int = Query(2, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Получить матрицу трассируемости требования"""
    # Получаем само требование
    req_query = select(Requirement).where(Requirement.id == requirement_id)
    req_result = await db.execute(req_query)
    requirement = req_result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    async def get_related_requirements(req_id: int, current_depth: int, direction: str):
        """Рекурсивно получаем связанные требования"""
        if current_depth > depth:
            return []
        
        if direction == "source":
            query = select(RequirementDependence, Requirement).join(
                Requirement, RequirementDependence.target_requirement_id == Requirement.id
            ).where(RequirementDependence.source_requirement_id == req_id)
        else:  # target
            query = select(RequirementDependence, Requirement).join(
                Requirement, RequirementDependence.source_requirement_id == Requirement.id
            ).where(RequirementDependence.target_requirement_id == req_id)
        
        result = await db.execute(query)
        items = result.all()
        
        related = []
        for dep, req in items:
            related.append({
                "requirement_id": req.id,
                "requirement_name": req.name,
                "dependency_type": dep.type,
                "depth": current_depth
            })
            
            # Рекурсивный вызов для следующего уровня
            if current_depth < depth:
                next_id = req.id
                nested = await get_related_requirements(next_id, current_depth + 1, direction)
                related.extend(nested)
        
        return related
    
    # Получаем источники (от чего зависит это требование)
    source_items = await get_related_requirements(requirement_id, 1, "source")
    
    # Получаем цели (что зависит от этого требования)
    target_items = await get_related_requirements(requirement_id, 1, "target")
    
    return {
        "requirement_id": requirement.id,
        "requirement_name": requirement.name,
        "source": source_items,
        "target": target_items
    }

