from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.requirement.dao import RequirementDAO
from src.requirement_workflow.dao import RequirementWorkflowDAO
from src.requirement_workflow.schemas import (
    RequirementWorkflow,
    WorkflowTransition,
    WorkflowHistoryList
)
from src.requirement_workflow_history.dao import ReqWorkflowHistoryDAO
from src.requirement_approver.dao import RequirementApproverDAO
from src.requirement_approver.schemas import (
    ApproveRequest,
    RejectRequest,
    RequirementApprover
)

requirement_workflow_router = APIRouter(
    prefix='/api/requirements',
    tags=['Workflow']
)


# Допустимые переходы статусов
WORKFLOW_TRANSITIONS = {
    'draft': ['review'],
    'review': ['approved', 'rejected'],
    'approved': ['implemented'],
    'rejected': ['draft'],
    'implemented': ['verified'],
    'verified': ['archived'],
    'archived': []
}


@requirement_workflow_router.get(
    "/{requirement_id}/workflow",
    response_model=RequirementWorkflow,
    status_code=status.HTTP_200_OK,
    summary="Получить текущий статус workflow"
)
async def get_workflow_status(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Получение текущего состояния workflow требования"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем workflow
    workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=requirement_id)
    
    if not workflow_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow требования не найден"
        )
    
    return workflow_list[0]


@requirement_workflow_router.post(
    "/{requirement_id}/workflow",
    response_model=RequirementWorkflow,
    status_code=status.HTTP_200_OK,
    summary="Изменить статус workflow"
)
async def change_workflow_status(
        session: SessionDep,
        requirement_id: UUID,
        transition: WorkflowTransition,
        current_user=Depends(UserDependency())
):
    """Изменение статуса требования в соответствии с workflow"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем текущий workflow
    workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=requirement_id)
    
    if not workflow_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow требования не найден"
        )
    
    current_workflow = workflow_list[0]
    
    # Проверяем допустимость перехода
    allowed_transitions = WORKFLOW_TRANSITIONS.get(current_workflow.status, [])
    if transition.new_status.value not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый переход из статуса '{current_workflow.status}' в '{transition.new_status.value}'"
        )
    
    # Обновляем workflow
    workflow = await RequirementWorkflowDAO.update(
        session,
        current_workflow.id,
        status=transition.new_status.value
    )
    
    # Сохраняем НОВОЕ состояние в историю
    # Делаем предыдущую активную запись неактивной
    history_records = await ReqWorkflowHistoryDAO.get_by(
        session,
        requirement_id=requirement_id,
        is_active=True
    )
    for record in history_records:
        await ReqWorkflowHistoryDAO.update(session, record.id, is_active=False)
    
    # Создаем новую запись в истории с НОВЫМ статусом
    prev_history_id = history_records[0].id if history_records else None
    await ReqWorkflowHistoryDAO.create(
        session,
        requirement_id=requirement_id,
        prev_workflow_history_id=prev_history_id,
        created_by_user_id=current_user.id,
        priority=workflow.priority,
        status=workflow.status,
        is_active=True
    )
    
    return workflow


@requirement_workflow_router.get(
    "/{requirement_id}/workflow/history",
    response_model=WorkflowHistoryList,
    status_code=status.HTTP_200_OK,
    summary="История изменений workflow"
)
async def get_workflow_history(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Получение истории изменений статуса требования"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем историю
    history = await ReqWorkflowHistoryDAO.get_by(
        session,
        requirement_id=requirement_id
    )
    
    # Сортируем по created_at в обратном порядке
    history_sorted = sorted(history, key=lambda x: x.created_at, reverse=True)
    
    return WorkflowHistoryList(data=history_sorted)


# ================ Согласование требований ================

@requirement_workflow_router.post(
    "/{requirement_id}/approval",
    response_model=RequirementWorkflow,
    status_code=status.HTTP_200_OK,
    summary="Запустить процесс согласования"
)
async def start_approval(
        session: SessionDep,
        requirement_id: UUID,
        current_user=Depends(UserDependency())
):
    """Запуск процесса согласования - перемещает в статус 'review'"""
    transition = WorkflowTransition(new_status="review")
    return await change_workflow_status(session, requirement_id, transition, current_user)


@requirement_workflow_router.post(
    "/{requirement_id}/approve",
    response_model=RequirementApprover,
    status_code=status.HTTP_200_OK,
    summary="Утвердить требование"
)
async def approve_requirement(
        session: SessionDep,
        requirement_id: UUID,
        approve_data: ApproveRequest,
        current_user=Depends(UserDependency())
):
    """Утверждение требования уполномоченным лицом"""
    # Проверяем существование требования
    try:
        requirement = await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Проверяем workflow - должен быть в статусе review
    workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=requirement_id)
    if not workflow_list or workflow_list[0].status != 'review':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Требование должно быть в статусе 'review' для утверждения"
        )
    
    # Создаем запись о согласовании
    approver = await RequirementApproverDAO.create(
        session,
        requirement_id=requirement_id,
        user_id=current_user.id,
        action='approve',
        comment=approve_data.comment
    )
    
    # Меняем статус на approved
    transition = WorkflowTransition(new_status="approved", comment=approve_data.comment)
    await change_workflow_status(session, requirement_id, transition, current_user)
    
    return approver


@requirement_workflow_router.post(
    "/{requirement_id}/reject",
    response_model=RequirementApprover,
    status_code=status.HTTP_200_OK,
    summary="Отклонить требование"
)
async def reject_requirement(
        session: SessionDep,
        requirement_id: UUID,
        reject_data: RejectRequest,
        current_user=Depends(UserDependency())
):
    """Отклонение требования с комментарием"""
    # Проверяем существование требования
    try:
        requirement = await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Проверяем workflow - должен быть в статусе review
    workflow_list = await RequirementWorkflowDAO.get_by(session, requirement_id=requirement_id)
    if not workflow_list or workflow_list[0].status != 'review':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Требование должно быть в статусе 'review' для отклонения"
        )
    
    # Создаем запись о согласовании
    approver = await RequirementApproverDAO.create(
        session,
        requirement_id=requirement_id,
        user_id=current_user.id,
        action='reject',
        comment=reject_data.comment,
        reason=reject_data.reason.value
    )
    
    # Меняем статус на rejected
    transition = WorkflowTransition(new_status="rejected", comment=reject_data.comment)
    await change_workflow_status(session, requirement_id, transition, current_user)
    
    return approver

