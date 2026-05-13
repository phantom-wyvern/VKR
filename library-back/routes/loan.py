# backend/routes/loan.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from datetime import date, datetime, timedelta, timezone

from database import get_db
from models import Loan, Reservation, Book, Copy, Reader, Author, BookAuthor
from schemas.auth_security import get_current_user

router = APIRouter(prefix="/api/loans", tags=["loans"])

# Вспомогательная функция для проверки роли читателя
def _require_reader(user):
    # Если у пользователя есть атрибут role и он не 'reader' — ошибка
    if hasattr(user, "role") and user.role != "reader":
        raise HTTPException(status_code=403, detail="Доступ только для читателей")
    return user


@router.post("/reserve")
async def reserve_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Забронировать книгу (создать резервирование для читателя)"""
    _require_reader(current_user)
    reader_id = await _get_reader_id(current_user, db)

    # Проверяем что читатель активен
    reader_check = await db.execute(select(Reader).where(Reader.id_reader == reader_id))
    reader_obj = reader_check.scalar_one_or_none()
    if not reader_obj or not reader_obj.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    # Проверяем, существует ли книга
    book_result = await db.execute(select(Book).where(Book.id_book == book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    # Проверяем, есть ли уже у читателя активная бронь на эту книгу
    existing_res = await db.execute(
        select(Reservation).where(
            Reservation.id_reader == reader_id,
            Reservation.id_book == book_id,
            Reservation.status.in_(["pending", "ready"])
        )
    )
    if existing_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="У вас уже есть активная бронь на эту книгу")

    # Проверяем, есть ли свободные экземпляры
    copies_result = await db.execute(
        select(Copy).where(
            Copy.id_book == book_id,
            Copy.status == "available"
        )
    )
    available_copies = copies_result.scalars().all()
    if not available_copies:
        raise HTTPException(status_code=400, detail="Нет свободных экземпляров для бронирования")

    # Создаём бронирование
    new_reservation = Reservation(
        id_reader=reader_id,
        id_book=book_id,
        created_at=datetime.now(),
        status="pending"
    )
    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)

    return {
        "success": True,
        "reservationId": new_reservation.id_reservation,
        "message": f"Книга '{book.title}' успешно забронирована",
        "bookTitle": book.title
    }

# Вспомогательная функция для получения ID читателя
async def _get_reader_id(user, db: AsyncSession):
    if hasattr(user, "id_reader"):
        return user.id_reader
    # Если это Employee, ищем Reader по login (упрощённо)
    if hasattr(user, "login"):
        result = await db.execute(select(Reader).where(Reader.login == user.login))
        reader = result.scalar_one_or_none()
        if reader:
            return reader.id_reader
    raise HTTPException(status_code=404, detail="Читатель не найден")


@router.get("/active")
async def get_active_loans(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    _require_reader(current_user)
    reader_id = await _get_reader_id(current_user, db)
    
    query = select(Loan).options(
        joinedload(Loan.copy).joinedload(Copy.book).joinedload(Book.authors)
    ).where(
        Loan.id_reader == reader_id,
        Loan.return_date.is_(None)
    )
    
    result = await db.execute(query)
    loans = result.unique().scalars().all()
    
    data = []
    today = date.today()
    for loan in loans:
        book = loan.copy.book
        authors = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors]) if book.authors else "Неизвестный автор"
        is_overdue = loan.due_date < today
        fine = (today - loan.due_date).days * 10 if is_overdue else 0
        
        data.append({
            "id": loan.id_loan,
            "bookId": book.id_book,
            "bookTitle": book.title,
            "author": authors,
            "borrowDate": loan.issue_date.isoformat(),
            "dueDate": loan.due_date.isoformat(),
            "status": "overdue" if is_overdue else "active",
            "copyId": loan.copy.id_copy,
            "canRenew": not is_overdue,
            "renewalsCount": 0,
            "fineAmount": fine
        })
    return data


@router.get("/reservations")
async def get_reservations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить бронирования текущего читателя"""
    _require_reader(current_user)
    reader_id = await _get_reader_id(current_user, db)
    
    query = select(Reservation).options(
        joinedload(Reservation.book).joinedload(Book.authors)
    ).where(
        Reservation.id_reader == reader_id
    ).order_by(Reservation.created_at.desc())
    
    result = await db.execute(query)
    reservations = result.unique().scalars().all()
    
    data = []
    for res in reservations:
        book = res.book
        authors = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors]) if book.authors else "Неизвестный автор"

        expires_at = None
        if res.status == "ready" and res.created_at:
            expires_at = (res.created_at + timedelta(hours=48)).isoformat()

        data.append({
            "id": res.id_reservation,
            "bookId": book.id_book,
            "bookTitle": book.title,
            "author": authors,
            "status": res.status,
            "queuePosition": 1,
            "createdAt": res.created_at.isoformat() if res.created_at else None,
            "expiresAt": expires_at
        })
    return data


@router.get("/history")
async def get_loan_history(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    _require_reader(current_user)
    reader_id = await _get_reader_id(current_user, db)
    
    # Считаем общее количество
    from sqlalchemy import func
    count_q = select(func.count()).select_from(
        select(Loan.id_loan).where(
            Loan.id_reader == reader_id,
            Loan.return_date.isnot(None)
        ).subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0
    
    query = select(Loan).options(
        joinedload(Loan.copy).joinedload(Copy.book).joinedload(Book.authors)
    ).where(
        Loan.id_reader == reader_id,
        Loan.return_date.isnot(None)
    ).order_by(Loan.issue_date.desc()).offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    history = result.unique().scalars().all()
    
    data = []
    for loan in history:
        book = loan.copy.book
        authors = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors]) if book.authors else "Неизвестный автор"
        data.append({
            "id": loan.id_loan,
            "bookId": book.id_book,
            "bookTitle": book.title,
            "author": authors,
            "borrowDate": loan.issue_date.isoformat(),
            "returnDate": loan.return_date.isoformat(),
            "rating": None,
            "wasOverdue": loan.return_date > loan.due_date
        })
        
    return {"data": data, "total": total, "page": page, "limit": limit}


@router.delete("/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отменить бронирование читателем"""
    _require_reader(current_user)
    reader_id = await _get_reader_id(current_user, db)

    # Ищем бронирование
    res_result = await db.execute(
        select(Reservation).where(
            Reservation.id_reservation == reservation_id,
            Reservation.id_reader == reader_id,
            Reservation.status.in_(["pending", "ready"])
        )
    )
    reservation = res_result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или уже обработано")

    # Отменяем бронирование
    reservation.status = "cancelled"
    await db.commit()

    return {
        "success": True,
        "message": "Бронирование отменено"
    }