# backend/routes/inventory.py
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db
from models import Book, Copy, Loan, Reservation, Reader, Employee, AuditLog, SystemSetting, Genre, Author, BookAuthor, BookGenre
from schemas.auth_security import get_current_user, require_admin_or_librarian

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

@router.get("/books")
async def get_inventory_books(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список книг с экземплярами для рабочего места библиотекаря"""
    require_admin_or_librarian(current_user)
    
    query = select(Book).options(
        joinedload(Book.copies),
        joinedload(Book.authors),
        joinedload(Book.genres)
    )
    
    result = await db.execute(query)
    books = result.unique().scalars().all()
    
    data = []
    for book in books:
        authors_str = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in book.authors]) if book.authors else "Неизвестный автор"
        genre_name = book.genres[0].name if book.genres else "Без жанра"
        
        copies = [{"id": c.id_copy, "status": c.status, "location": c.location, "inventory_number": c.inventory_number} for c in book.copies]
        
        data.append({
            "id": book.id_book,
            "title": book.title,
            "author": authors_str,
            "year": book.publication_year,
            "genre": genre_name,
            "isbn": book.isbn,
            "description": book.annotation,
            "cover": book.cover_url,
            "copies": copies
        })
    
    return data

@router.post("/checkout")
async def checkout_book(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Выдать книгу читателю"""
    require_admin_or_librarian(current_user)

    copy_id = data.get("copyId")
    user_id = data.get("userId")
    user_name = data.get("userName", "")
    reservation_id = data.get("reservationId")

    # Валидация входных данных
    if not copy_id or not user_id:
        raise HTTPException(400, "Необходимо указать ID экземпляра и ID читателя")

    # Находим копию
    copy = await db.get(Copy, copy_id)
    if not copy:
        raise HTTPException(400, f"Экземпляр с ID {copy_id} не найден")
    if copy.status != "available":
        raise HTTPException(400, f"Экземпляр недоступен для выдачи (статус: {copy.status})")

    # Находим читателя
    reader = await db.get(Reader, user_id)
    if not reader:
        raise HTTPException(404, f"Читатель с ID {user_id} не найден")
    if not reader.is_active:
        raise HTTPException(400, "Читатель заблокирован")

    # Получаем ID сотрудника — current_user может быть detached,
    # поэтому берём ID напрямую через hasattr-проверку
    if hasattr(current_user, 'id_employee') and current_user.id_employee is not None:
        employee_id = current_user.id_employee
    else:
        # Фолбэк: ищем сотрудника по login из токена
        emp_result = await db.execute(select(Employee).where(Employee.login == current_user.login))
        emp = emp_result.scalar_one_or_none()
        if not emp:
            raise HTTPException(500, "Не удалось определить сотрудника")
        employee_id = emp.id_employee

    # Получаем срок займа из настроек
    settings_stmt = select(SystemSetting.setting_value).where(SystemSetting.setting_key == "loan_period_days")
    settings_result = await db.execute(settings_stmt)
    settings_value = settings_result.scalar_one_or_none()
    days = int(settings_value or 14)
    due_date = date.today() + timedelta(days=days)

    # Создаём займ
    loan = Loan(
        id_reader=reader.id_reader,
        id_copy=copy.id_copy,
        id_employee=employee_id,
        issue_date=date.today(),
        due_date=due_date
    )
    db.add(loan)
    copy.status = "borrowed"
    await db.flush()  # Получаем loan.id_loan до commit

    db.add(AuditLog(
        id_employee=employee_id,
        action_type="CHECKOUT",
        table_name="loan",
        record_id=loan.id_loan,
        details={"reader": user_name, "copy_id": copy_id, "reader_id": user_id}
    ))
    await db.commit()

    # Если выдача по бронированию — отмечаем его как выполненное
    if reservation_id:
        res = await db.get(Reservation, reservation_id)
        if res and res.status == "ready":
            res.status = "fulfilled"
            await db.commit()

    return {"success": True, "message": f"Книга выдана до {due_date.isoformat()}", "dueDate": due_date.isoformat()}

@router.post("/return")
async def return_book(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Вернуть книгу"""
    require_admin_or_librarian(current_user)

    copy_id = data.get("copyId")

    if not copy_id:
        raise HTTPException(400, "Необходимо указать ID экземпляра")

    copy = await db.get(Copy, copy_id)

    if not copy:
        raise HTTPException(404, f"Экземпляр с ID {copy_id} не найден")
    if copy.status == "available":
        raise HTTPException(400, "Экземпляр уже доступен")

    from sqlalchemy import and_
    from datetime import date
    loan_stmt = select(Loan).where(
        and_(Loan.id_copy == copy_id, Loan.return_date.is_(None))
    )
    loan_result = await db.execute(loan_stmt)
    loan = loan_result.scalar_one_or_none()

    if loan:
        loan.return_date = date.today()
        copy.status = "available"

        # Получаем ID сотрудника через текущую сессию
        if hasattr(current_user, 'id_employee') and current_user.id_employee is not None:
            emp_id = current_user.id_employee
        else:
            emp_result = await db.execute(select(Employee).where(Employee.login == current_user.login))
            emp = emp_result.scalar_one_or_none()
            emp_id = emp.id_employee if emp else None

        db.add(AuditLog(
            id_employee=emp_id,
            action_type="RETURN",
            table_name="loan",
            record_id=loan.id_loan,
            details={"copy_id": copy_id}
        ))
        await db.commit()
        return {"success": True, "message": "Книга возвращена"}

    raise HTTPException(404, "Активный займ не найден")

@router.get("/loans/active")
async def get_active_loans(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список активных займов для панели библиотекаря"""
    require_admin_or_librarian(current_user)

    query = select(Loan).options(
        joinedload(Loan.reader),
        joinedload(Loan.copy).joinedload(Copy.book),
        joinedload(Loan.employee)
    ).where(
        Loan.return_date.is_(None)
    ).order_by(Loan.due_date.asc())

    result = await db.execute(query)
    loans = result.unique().scalars().all()

    from datetime import date
    today = date.today()

    data = []
    for loan in loans:
        book = loan.copy.book if loan.copy else None
        book_title = book.title if book else "Неизвестная книга"

        data.append({
            "id": loan.id_loan,
            "readerId": loan.reader.id_reader,
            "readerName": f"{loan.reader.first_name} {loan.reader.last_name}",
            "bookId": book.id_book if book else None,
            "bookTitle": book_title,
            "copyId": loan.copy.id_copy if loan.copy else None,
            "inventoryNumber": loan.copy.inventory_number if loan.copy else None,
            "issueDate": loan.issue_date.isoformat() if loan.issue_date else None,
            "dueDate": loan.due_date.isoformat() if loan.due_date else None,
            "employeeId": loan.id_employee
        })

    return {"data": data}


@router.get("/reservations")
async def get_reservations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список бронирований"""
    require_admin_or_librarian(current_user)

    query = select(Reservation).options(
        joinedload(Reservation.reader),
        joinedload(Reservation.book).joinedload(Book.authors)
    ).order_by(Reservation.created_at.desc())

    result = await db.execute(query)
    reservations = result.unique().scalars().all()

    data = []
    for r in reservations:
        # Вычисляем позицию в очереди
        from sqlalchemy import func
        queue_query = select(func.count()).select_from(Reservation).where(
            Reservation.id_book == r.id_book,
            Reservation.status.in_(["pending", "ready"]),
            Reservation.created_at <= r.created_at
        )
        queue_pos = (await db.execute(queue_query)).scalar() or 1

        authors_str = ", ".join([f"{a.first_name[0]}. {a.last_name}" for a in r.book.authors]) if r.book.authors else "Неизвестный автор"

        data.append({
            "id": r.id_reservation,
            "bookId": r.book.id_book,
            "bookTitle": r.book.title,
            "author": authors_str,
            "userName": f"{r.reader.first_name} {r.reader.last_name}",
            "userId": r.reader.id_reader,
            "date": r.created_at.isoformat() if r.created_at else None,
            "status": r.status,
            "queuePosition": queue_pos
        })
    return data

@router.patch("/reservations/{res_id}/approve")
async def approve_reservation(
    res_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Подтвердить бронирование"""
    require_admin_or_librarian(current_user)

    res = await db.get(Reservation, res_id)
    if not res:
        raise HTTPException(404, "Бронирование не найдено")
    if res.status != "pending":
        raise HTTPException(400, f"Невозможно подтвердить бронь со статусом '{res.status}'")

    res.status = "ready"
    await db.commit()
    return {"success": True, "message": "Бронирование подтверждено"}

@router.delete("/reservations/{res_id}")
async def cancel_reservation_by_librarian(
    res_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отменить бронирование (библиотекарь)"""
    require_admin_or_librarian(current_user)

    res = await db.get(Reservation, res_id)
    if not res:
        raise HTTPException(404, "Бронирование не найдено")
    if res.status not in ("pending", "ready"):
        raise HTTPException(400, f"Нельзя отменить бронь со статусом '{res.status}'")

    res.status = "cancelled"
    await db.commit()
    return {"success": True, "message": "Бронирование отменено"}

@router.patch("/reservations/{res_id}/fulfill")
async def fulfill_reservation(
    res_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отметить бронирование как выполненное (книга выдана)"""
    require_admin_or_librarian(current_user)

    res = await db.get(Reservation, res_id)
    if not res:
        raise HTTPException(404, "Бронирование не найдено")
    if res.status != "ready":
        raise HTTPException(400, f"Можно отметить как выполненное только бронирование со статусом 'ready', текущий: '{res.status}'")

    res.status = "fulfilled"
    await db.commit()
    return {"success": True, "message": "Бронирование отмечено как выполненное"}

@router.get("/fines")
async def get_fines(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список штрафов (просроченные займы)"""
    require_admin_or_librarian(current_user)
    
    from datetime import date
    from sqlalchemy import and_
    
    today = date.today()
    loan_stmt = select(Loan).options(
        joinedload(Loan.reader),
        joinedload(Loan.copy)
    ).where(
        and_(Loan.return_date.is_(None), Loan.due_date < today)
    )
    
    result = await db.execute(loan_stmt)
    overdue_loans = result.unique().scalars().all()
    
    data = []
    for loan in overdue_loans:
        days_overdue = (today - loan.due_date).days
        amount = days_overdue * 10
        data.append({
            "id": loan.id_loan,
            "userId": loan.reader.id_reader,
            "userName": f"{loan.reader.first_name} {loan.reader.last_name}",
            "amount": amount,
            "reason": f"Просрочка: {loan.copy.inventory_number}",
            "paid": False,
            "date": loan.due_date.isoformat()
        })
    return data

@router.patch("/fines/{fine_id}/pay")
async def mark_fine_paid(
    fine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отметить штраф как оплаченный (заглушка)"""
    require_admin_or_librarian(current_user)
    return {"success": True, "message": "Штраф отмечен как оплаченный"}

@router.get("/activities")
async def get_recent_activities(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить последние операции"""
    require_admin_or_librarian(current_user)
    
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [{
        "id": log.id_audit,
        "type": log.action_type.lower(),
        "description": f"{log.action_type}: {log.table_name} #{log.record_id}",
        "timestamp": log.created_at.isoformat() if log.created_at else None
    } for log in logs]

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """Получить статистику для дашборда библиотекаря"""
    require_admin_or_librarian(current_user)
    
    # 1. Активные займы (всего книг на руках)
    active_loans_q = select(func.count()).select_from(Loan).where(Loan.return_date.is_(None))
    active_loans = (await db.execute(active_loans_q)).scalar() or 0
    
    # 2. Просроченные займы (не возвращены И дата возврата прошла)
    overdue_loans_q = select(func.count()).select_from(Loan).where(
        and_(Loan.return_date.is_(None), Loan.due_date < date.today())
    )
    overdue_loans = (await db.execute(overdue_loans_q)).scalar() or 0
    
    # 3. Бронирования (ожидающие обработки: pending или ready)
    pending_res_q = select(func.count()).select_from(Reservation).where(
        Reservation.status.in_(['pending', 'ready'])
    )
    pending_res = (await db.execute(pending_res_q)).scalar() or 0
    
    # 4. Книги к обработке (например, книги без физических экземпляров)
    books_no_copies_q = select(func.count()).select_from(Book).outerjoin(Copy).where(Copy.id_copy.is_(None))
    books_to_process = (await db.execute(books_no_copies_q)).scalar() or 0
    
    return {
        "activeLoans": active_loans,
        "overdueLoans": overdue_loans,
        "pendingReservations": pending_res,
        "booksToProcess": books_to_process
    }