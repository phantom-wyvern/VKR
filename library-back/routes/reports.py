# backend/routes/reports.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, extract, cast, Date, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import Loan, Book, Genre, Author, BookAuthor, BookGenre, Copy, Reader
from schemas.auth_security import get_current_user, require_admin_or_librarian

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/loans-by-month")
async def get_loans_by_month(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Статистика выдач по месяцам (последние N месяцев)"""
    require_admin_or_librarian(current_user)
    
    # Получаем дату начала периода
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months*30)
    
    # Группируем выдачи по месяцу
    query = select(
        func.date_trunc('month', Loan.issue_date).label('month'),
        func.count().label('count')
    ).where(
        Loan.issue_date >= start_date,
        Loan.issue_date <= end_date
    ).group_by('month').order_by('month')
    
    result = await db.execute(query)
    rows = result.all()
    
    # Формируем ответ в формате для Chart.js
    labels = [row[0].strftime('%Y-%m') for row in rows]
    data = [row[1] for row in rows]
    
    return {
        "labels": labels,
        "datasets": [{
            "label": "Выдачи",
            "data": data,
            "backgroundColor": "rgba(187, 134, 252, 0.6)",
            "borderColor": "#bb86fc",
            "borderWidth": 2,
            "borderRadius": 4
        }]
    }


@router.get("/activity-by-day")
async def get_activity_by_day(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Активность по дням недели (выдачи и возвраты)"""
    require_admin_or_librarian(current_user)

    # Выдачи по дням недели (1=Пн, 7=Вс в PostgreSQL)
    loans_query = select(
        extract('isodow', Loan.issue_date).label('day'),  # 1=Пн, 7=Вс
        func.count().label('count')
    ).group_by('day')
    loans_result = await db.execute(loans_query)
    loans_by_day = {int(row[0]): row[1] for row in loans_result.all()}

    # Возвраты по дням недели
    returns_query = select(
        extract('isodow', Loan.return_date).label('day'),
        func.count().label('count')
    ).where(Loan.return_date.isnot(None)).group_by('day')
    returns_result = await db.execute(returns_query)
    returns_by_day = {int(row[0]): row[1] for row in returns_result.all()}

    # Русские названия дней (Пн-Вс)
    day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    labels = day_names

    # Заполняем данные (isodow: 1=Пн, 2=Вт, ..., 7=Вс)
    loans_data = [loans_by_day.get(i, 0) for i in range(1, 8)]
    returns_data = [returns_by_day.get(i, 0) for i in range(1, 8)]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Выдачи",
                "data": loans_data,
                "borderColor": "#bb86fc",
                "backgroundColor": "rgba(187, 134, 252, 0.2)",
                "tension": 0.4,
                "fill": True
            },
            {
                "label": "Возвраты",
                "data": returns_data,
                "borderColor": "#10b981",
                "backgroundColor": "rgba(16, 185, 129, 0.2)",
                "tension": 0.4,
                "fill": True
            }
        ]
    }

@router.get("/genres-distribution")
async def get_genres_distribution(
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Распределение книг по жанрам (для круговой диаграммы)"""
    require_admin_or_librarian(current_user)
    
    query = select(
        Genre.name,
        func.count(BookGenre.id_book).label('count')
    ).join(
        BookGenre, Genre.id_genre == BookGenre.id_genre
    ).group_by(Genre.name).order_by(func.count(BookGenre.id_book).desc()).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    colors = [
        'rgba(187, 134, 252, 0.8)', 'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)', 'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)', 'rgba(156, 163, 175, 0.8)',
        'rgba(236, 72, 153, 0.8)', 'rgba(139, 92, 246, 0.8)'
    ]
    
    return {
        "labels": [row[0] for row in rows],
        "datasets": [{
            "data": [row[1] for row in rows],
            "backgroundColor": colors[:len(rows)],
            "borderWidth": 0,
            "hoverOffset": 8
        }]
    }

@router.get("/top-books")
async def get_top_books(
    limit: int = Query(5, ge=1, le=20),
    period: str = Query('all', pattern='^(all|month|year)$'),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Топ популярных книг по количеству выдач"""
    require_admin_or_librarian(current_user)
    
    # Фильтр по периоду
    where_clause = []
    if period == 'month':
        where_clause.append(Loan.issue_date >= datetime.now().date() - timedelta(days=30))
    elif period == 'year':
        where_clause.append(Loan.issue_date >= datetime.now().date() - timedelta(days=365))
    
    query = select(
        Book.id_book,
        Book.title,
        func.count(Loan.id_loan).label('loans_count'),
        func.string_agg(Author.first_name + ' ' + Author.last_name, ', ').label('authors')
    ).join(
        Copy, Copy.id_book == Book.id_book
    ).join(
        Loan, Loan.id_copy == Copy.id_copy
    ).join(
        BookAuthor, BookAuthor.id_book == Book.id_book
    ).join(
        Author, Author.id_author == BookAuthor.id_author
    ).where(*where_clause).group_by(
        Book.id_book, Book.title
    ).order_by(
        func.count(Loan.id_loan).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "rank": i+1,
            "title": row.title,
            "author": row.authors.split(',')[0].strip() if row.authors else "Неизвестный автор",
            "loansCount": row.loans_count
        }
        for i, row in enumerate(rows)
    ]

@router.get("/stats")
async def get_reports_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Общая статистика для дашборда отчетов"""
    require_admin_or_librarian(current_user)
    
    # Всего выдач
    total_loans = (await db.execute(select(func.count(Loan.id_loan)))).scalar() or 0
    
    # Возвращено
    returned = (await db.execute(
        select(func.count(Loan.id_loan)).where(Loan.return_date.isnot(None))
    )).scalar() or 0
    
    # Активные (не возвращены)
    active = total_loans - returned
    
    # Просроченные (активные и дата возврата прошла)
    overdue = (await db.execute(
        select(func.count(Loan.id_loan)).where(
            Loan.return_date.is_(None),
            Loan.due_date < datetime.now().date()
        )
    )).scalar() or 0
    
    return {
        "totalLoans": total_loans,
        "returned": returned,
        "active": active,
        "overdue": overdue
    }