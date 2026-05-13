from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, distinct, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import Optional, List

from database import get_db
from models import Book, Author, Genre, Copy, BookAuthor, BookGenre
from schemas.schemas import MessageResponse

router = APIRouter(prefix="/api/books", tags=["books"])

@router.get("/")
async def get_books(
    db: AsyncSession = Depends(get_db),
    search: str = Query(None),
    genre: str = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[str] = Query(None), # 'available' или 'borrowed'
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    # Базовый запрос с загрузкой связей
    query = select(Book).options(
        joinedload(Book.authors),
        joinedload(Book.genres),
        joinedload(Book.copies)
    ).distinct()

    # 1. Поиск по тексту (название, автор, ISBN)
    if search:
        q = f"%{search}%"
        # Подзапрос для поиска авторов
        author_subquery = (
            select(BookAuthor.id_book)
            .join(Author, Author.id_author == BookAuthor.id_author)
            .where(or_(
                Author.first_name.ilike(q),
                Author.last_name.ilike(q)
            ))
        )
        
        query = query.where(or_(
            Book.title.ilike(q),
            Book.isbn.ilike(q),
            Book.id_book.in_(author_subquery)
        ))

    # 2. Фильтр по году
    if year:
        query = query.where(Book.publication_year == year)

    # 3. Фильтр по жанру (название жанра)
    if genre:
        genre_subquery = (
            select(BookGenre.id_book)
            .join(Genre, Genre.id_genre == BookGenre.id_genre)
            .where(Genre.name == genre)
        )
        query = query.where(Book.id_book.in_(genre_subquery))

    # 4. Фильтр по статусу наличия (доступна / выдана)
    if status:
        # Подзапрос для проверки статуса экземпляров
        copy_subquery = (
            select(Copy.id_book)
            .where(Copy.status == status)
        )
        # Для status='available' нужно, чтобы хотя бы одна копия была available
        if status == 'available':
            query = query.where(Book.id_book.in_(copy_subquery))
        # Для status='borrowed' (все выданы) — сложнее, упростим: показываем книги, у которых есть выданные копии
        elif status == 'borrowed':
            query = query.where(Book.id_book.in_(copy_subquery))

    # Считаем общее количество для пагинации (до применения offset/limit)
    count_query = select(func.count(distinct(Book.id_book))).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Применяем пагинацию
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    books = result.unique().scalars().all()

    # Формируем ответ, похожий на структуру фронтенда
    data = []
    for book in books:
        # Определяем авторов
        authors_str = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors])
        # Определяем жанры
        genres_list = [g.name for g in book.genres]
        
        # Список копий
        copies_data = [{"id": c.id_copy, "status": c.status, "location": c.location} for c in book.copies]
        
        # Статус книги (на основе копий)
        available_count = sum(1 for c in book.copies if c.status == 'available')
        total_copies = len(book.copies)
        
        if total_copies == 0:
            book_status = "unknown"
        elif available_count == total_copies:
            book_status = "available"
        elif available_count == 0:
            book_status = "borrowed"
        else:
            book_status = "partial"

        data.append({
            "id": book.id_book,
            "title": book.title,
            "author": authors_str,
            "year": book.publication_year,
            "genre": genres_list[0] if genres_list else "Без жанра", # Для простоты берем первый
            "isbn": book.isbn,
            "description": book.annotation,
            "cover": book.cover_url,
            "copies": copies_data,
            "status": book_status 
        })

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit if limit > 0 else 0
    }

@router.get("/{book_id}")
async def get_book_by_id(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(Book).options(
        joinedload(Book.authors),
        joinedload(Book.genres),
        joinedload(Book.copies)
    ).where(Book.id_book == book_id)
    
    result = await db.execute(query)
    book = result.unique().scalar_one_or_none()
    
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    authors_str = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors])
    genres_list = [g.name for g in book.genres]
    copies_data = [{"id": c.id_copy, "status": c.status, "location": c.location} for c in book.copies]

    return {
        "id": book.id_book,
        "title": book.title,
        "author": authors_str,
        "year": book.publication_year,
        "genre": genres_list[0] if genres_list else "Без жанра",
        "isbn": book.isbn,
        "description": book.annotation,
        "cover": book.cover_url,
        "copies": copies_data
    }

@router.get("/filters/genres")
async def get_book_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genre.name).order_by(Genre.name))
    return [row[0] for row in result.all()]

@router.get("/filters/years")
async def get_book_years(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(distinct(Book.publication_year)).order_by(Book.publication_year.desc()))
    return [row[0] for row in result.all()]