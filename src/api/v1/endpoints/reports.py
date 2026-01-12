"""
API endpoints для отчетов и аналитики
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, date

from db.session import get_db
from models.requirement import (
    Requirement, RequirementContent, RequirementWorkflow,
    Project, ReqTestCaseCoverage
)
from schemas.requirement import KPIDashboard, RequirementsReport

router = APIRouter(prefix="/reports", tags=["Администрирование", "Отчеты"])


@router.get("/kpi", response_model=dict)
async def get_kpi_dashboard(
    project_id: Optional[int] = Query(None),
    period_start: Optional[date] = Query(None),
    period_end: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Дашборд KPI"""
    # Базовый запрос для требований
    query = select(Requirement).where(Requirement.is_deleted == False)
    
    if project_id:
        query = query.where(Requirement.project_id == project_id)
    
    if period_start:
        query = query.where(Requirement.created_at >= period_start)
    
    if period_end:
        query = query.where(Requirement.created_at <= period_end)
    
    result = await db.execute(query)
    requirements = result.scalars().all()
    
    # Подсчитываем метрики
    total_requirements = len(requirements)
    
    # Получаем статусы через workflow
    status_counts = {
        "draft": 0,
        "review": 0,
        "approved": 0,
        "rejected": 0,
        "implemented": 0,
        "verified": 0,
        "archived": 0
    }
    
    type_counts = {
        "functional": 0,
        "non-functional": 0,
        "business": 0
    }
    
    for req in requirements:
        # Считаем по типам
        if req.type in type_counts:
            type_counts[req.type] += 1
        
        # Получаем активный контент для статуса
        content_query = select(RequirementContent).where(
            and_(
                RequirementContent.requirement_id == req.id,
                RequirementContent.is_active == True
            )
        ).options(selectinload(RequirementContent.workflow))
        
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()
        
        if content and content.workflow and content.workflow.is_active:
            status = content.workflow.status
            if status in status_counts:
                status_counts[status] += 1
    
    # Покрытие тестами
    test_coverage_query = select(func.count(ReqTestCaseCoverage.id)).select_from(ReqTestCaseCoverage).join(
        Requirement
    ).where(Requirement.is_deleted == False)
    
    if project_id:
        test_coverage_query = test_coverage_query.where(Requirement.project_id == project_id)
    
    test_coverage_result = await db.execute(test_coverage_query)
    requirements_with_tests = test_coverage_result.scalar()
    
    test_coverage_percent = (requirements_with_tests / total_requirements * 100) if total_requirements > 0 else 0
    
    return {
        "period": {
            "start": period_start.isoformat() if period_start else None,
            "end": period_end.isoformat() if period_end else None
        },
        "metrics": {
            "total_requirements": total_requirements,
            "requirements_by_status": status_counts,
            "requirements_by_type": type_counts,
            "requirements_approved": status_counts["approved"],
            "requirements_in_review": status_counts["review"],
            "requirements_rejected": status_counts["rejected"],
            "test_coverage_percent": round(test_coverage_percent, 2),
            "requirements_with_tests": requirements_with_tests
        }
    }


@router.get("/requirements", response_model=dict)
async def get_requirements_report(
    project_id: int = Query(...),
    format: str = Query("json", pattern="^(json|pdf|csv)$"),
    include_history: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Отчет по требованиям"""
    # Получаем проект
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Получаем требования
    req_query = select(Requirement).options(
        selectinload(Requirement.contents).selectinload(RequirementContent.workflow)
    ).where(
        and_(
            Requirement.project_id == project_id,
            Requirement.is_deleted == False
        )
    )
    
    result = await db.execute(req_query)
    requirements = result.scalars().unique().all()
    
    # Формируем данные для отчета
    requirements_data = []
    by_type = {"functional": 0, "non-functional": 0, "business": 0}
    by_status = {}
    
    for req in requirements:
        active_content = next((c for c in req.contents if c.is_active), None)
        
        req_data = {
            "id": req.id,
            "name": req.name,
            "type": req.type,
            "created_at": req.created_at,
            "created_by_user_id": req.created_by_user_id,
            "content": active_content,
            "workflow": active_content.workflow if active_content else None
        }
        
        requirements_data.append(req_data)
        
        # Статистика
        if req.type in by_type:
            by_type[req.type] += 1
        
        if active_content and active_content.workflow:
            status = active_content.workflow.status
            by_status[status] = by_status.get(status, 0) + 1
        
        # Если нужна история
        if include_history:
            all_contents = sorted(req.contents, key=lambda c: c.created_at, reverse=True)
            req_data["content_history"] = [
                {
                    "id": c.id,
                    "created_at": c.created_at,
                    "is_active": c.is_active,
                    "workflow": c.workflow
                }
                for c in all_contents
            ]
    
    report = {
        "project_id": project.id,
        "project_name": project.name,
        "generated_at": datetime.now().isoformat(),
        "requirements": requirements_data,
        "summary": {
            "total": len(requirements),
            "by_type": by_type,
            "by_status": by_status
        }
    }
    
    # TODO: Для PDF и CSV форматов нужно добавить генерацию
    if format == "pdf":
        raise HTTPException(status_code=501, detail="PDF export not implemented yet")
    elif format == "csv":
        raise HTTPException(status_code=501, detail="CSV export not implemented yet")
    
    return report


@router.get("/traceability", response_model=dict)
async def get_traceability_report(
    project_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Отчет по трассируемости требований"""
    # Получаем проект
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Получаем требования с зависимостями
    req_query = select(Requirement).options(
        selectinload(Requirement.dependencies_out),
        selectinload(Requirement.dependencies_in),
        selectinload(Requirement.test_coverage)
    ).where(
        and_(
            Requirement.project_id == project_id,
            Requirement.is_deleted == False
        )
    )
    
    result = await db.execute(req_query)
    requirements = result.scalars().unique().all()
    
    # Формируем матрицу трассируемости
    traceability_matrix = []
    
    for req in requirements:
        linked_to = [dep.target_requirement_id for dep in req.dependencies_out]
        linked_from = [dep.source_requirement_id for dep in req.dependencies_in]
        has_tests = len(req.test_coverage) > 0
        
        traceability_matrix.append({
            "requirement_id": req.id,
            "requirement_name": req.name,
            "linked_to": linked_to,
            "linked_from": linked_from,
            "test_coverage": has_tests,
            "dependencies_count": len(linked_to) + len(linked_from),
            "test_cases_count": len(req.test_coverage)
        })
    
    # Статистика
    total_requirements = len(requirements)
    requirements_with_dependencies = sum(1 for item in traceability_matrix if item["dependencies_count"] > 0)
    requirements_with_tests = sum(1 for item in traceability_matrix if item["test_coverage"])
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "generated_at": datetime.now().isoformat(),
        "traceability_matrix": traceability_matrix,
        "summary": {
            "total_requirements": total_requirements,
            "requirements_with_dependencies": requirements_with_dependencies,
            "requirements_with_tests": requirements_with_tests,
            "traceability_coverage_percent": round(
                (requirements_with_dependencies / total_requirements * 100) if total_requirements > 0 else 0,
                2
            ),
            "test_coverage_percent": round(
                (requirements_with_tests / total_requirements * 100) if total_requirements > 0 else 0,
                2
            )
        }
    }

