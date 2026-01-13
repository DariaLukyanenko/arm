from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.requirement.dao import RequirementDAO
from src.requirement_content.dao import RequirementContentDAO
from src.requirement_content.schemas import RequirementContent, RequirementContentUpdate
from src.requirement_content_history.dao import ReqContentHistoryDAO
from src.requirement.schemas import ContentHistoryList

requirement_content_router = APIRouter(
    prefix='/api/requirements',
    tags=['Требования']
)


@requirement_content_router.get(
    "/{requirement_id}/content",
    response_model=RequirementContent,
    status_code=status.HTTP_200_OK,
    summary="Получить содержимое требования"
)
async def get_requirement_content(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Получение текущего содержимого требования"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем содержимое
    content_list = await RequirementContentDAO.get_by(session, requirement_id=requirement_id)
    
    if not content_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Содержимое требования не найдено"
        )
    
    return content_list[0]


@requirement_content_router.put(
    "/{requirement_id}/content",
    response_model=RequirementContent,
    status_code=status.HTTP_200_OK,
    summary="Обновить содержимое требования"
)
async def update_requirement_content(
        session: SessionDep,
        requirement_id: UUID,
        content_data: RequirementContentUpdate,
        current_user=Depends(UserDependency())
):
    """Обновление содержимого с созданием новой версии в истории"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем текущее содержимое
    content_list = await RequirementContentDAO.get_by(session, requirement_id=requirement_id)
    
    if not content_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Содержимое требования не найдено"
        )
    
    current_content = content_list[0]
    
    # Обновляем текущее содержимое
    update_data = content_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )
    
    content = await RequirementContentDAO.update(
        session,
        current_content.id,
        **update_data
    )
    
    # Сохраняем НОВОЕ (обновленное) состояние в историю
    # Сначала делаем предыдущую активную запись неактивной
    history_records = await ReqContentHistoryDAO.get_by(
        session,
        requirement_id=requirement_id,
        is_active=True
    )
    for record in history_records:
        await ReqContentHistoryDAO.update(session, record.id, is_active=False)
    
    # Создаем новую запись в истории с ОБНОВЛЕННЫМИ данными
    prev_history_id = history_records[0].id if history_records else None
    await ReqContentHistoryDAO.create(
        session,
        requirement_id=requirement_id,
        prev_content_history_id=prev_history_id,
        created_by_user_id=current_user.id,
        development_basis=content.development_basis,
        development_purpose=content.development_purpose,
        description_text=content.description_text,
        acceptance_criteria=content.acceptance_criteria,
        document_requires=content.document_requires,
        is_active=True
    )
    
    return content


@requirement_content_router.get(
    "/{requirement_id}/content/history",
    response_model=ContentHistoryList,
    status_code=status.HTTP_200_OK,
    summary="История изменений содержимого"
)
async def get_content_history(
        session: SessionDep,
        requirement_id: UUID,
        limit: int = Query(10, ge=1, le=100, description="Количество записей"),
        _=Depends(UserDependency())
):
    """Получение истории изменений содержимого требования"""
    # Проверяем существование требования
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )
    
    # Получаем историю (TODO: добавить сортировку и лимит через DAO)
    history = await ReqContentHistoryDAO.get_by(
        session,
        requirement_id=requirement_id
    )
    
    # Сортируем по created_at в обратном порядке и применяем limit
    history_sorted = sorted(history, key=lambda x: x.created_at, reverse=True)[:limit]
    
    return ContentHistoryList(data=history_sorted)

