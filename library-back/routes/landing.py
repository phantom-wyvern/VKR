# backend/routes/landing.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import SystemSetting, Book, Author, BookAuthor
from typing import Optional, List

router = APIRouter(prefix="/api/landing", tags=["landing"])

@router.get("/content")
async def get_landing_content(db: AsyncSession = Depends(get_db)):
    """Получить контент для главной страницы (лендинга)"""
    
    # 1. Загружаем настройки библиотеки из БД
    settings_stmt = select(SystemSetting)
    settings_result = await db.execute(settings_stmt)
    settings = {row.setting_key: row.setting_value for row in settings_result.scalars().all()}
    
    # 2. Получаем 3 новые книги для блока "Популярное"
    books_stmt = select(Book).options(
        joinedload(Book.authors)
    ).order_by(Book.publication_year.desc()).limit(3)
    
    books_result = await db.execute(books_stmt)
    new_books = books_result.unique().scalars().all()
    
    featured_books = []
    for book in new_books:
        authors = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors]) if book.authors else "Неизвестный автор"
        featured_books.append({
            "id": book.id_book,
            "title": book.title,
            "author": authors,
            "cover": book.cover_url or "https://placehold.co/200x300/e2e8f0/1e293b?text=Book",
            "year": book.publication_year,
            "isbn": book.isbn
        })
    
    # 3. Формируем ответ (фичи — статика, так как это дизайн)
    return {
        "heroTitle": settings.get("library_name", "Библиотека нового поколения"),
        "heroSubtitle": "Мгновенный поиск, удобное бронирование и полный контроль над вашими займами. Присоединяйтесь к цифровой экосистеме чтения.",
        "features": [
            {
                "icon": "pi pi-search",
                "title": "Умный поиск",
                "desc": "Находите книги за секунды по автору, жанру или ISBN. Фильтрация по статусу наличия.",
                "bg": "rgba(187, 134, 252, 0.15)",
                "color": "#bb86fc"
            },
            {
                "icon": "pi pi-calendar-plus",
                "title": "Онлайн бронь",
                "desc": "Забронируйте книгу в один клик. Система уведомит вас, когда она будет готова к выдаче.",
                "bg": "rgba(3, 218, 198, 0.15)",
                "color": "#03dac6"
            },
            {
                "icon": "pi pi-chart-bar",
                "title": "Ваш профиль",
                "desc": "История чтений, активные займы и статистика — всё в личном кабинете.",
                "bg": "rgba(239, 68, 68, 0.15)",
                "color": "#ef4444"
            }
        ],
        "footerLinks": [
            {"label": "О нас", "url": "/about"},
            {"label": "Контакты", "url": "/contacts"},
            {"label": "Правила", "url": "/rules"}
        ],
        "contactInfo": {
            "address": settings.get("library_address", ""),
            "phone": settings.get("library_phone", ""),
            "email": settings.get("library_email", ""),
            "workHours": f"{settings.get('work_hours_start', '9:00')} - {settings.get('work_hours_end', '21:00')}"
        },
        "featuredBooks": featured_books
    }