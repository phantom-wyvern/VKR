# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from database import async_session, get_db  # ← ДОБАВЛЕНО: get_db
from models import Employee, Reader, Loan, Reservation
from schemas.schemas import (
    UserLogin, UserRegister, AuthResponse, UserResponse, MessageResponse
)
from schemas.auth_security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    ROLE_PERMISSIONS
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_permissions(role: str) -> list:
    return ROLE_PERMISSIONS.get(role, [])

@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    async with async_session() as session:
        # Ищем сотрудника
        result = await session.execute(
            select(Employee).where(Employee.login == credentials.email)
        )
        user = result.scalar_one_or_none()
        
        # Если не нашли — ищем читателя
        if not user:
            result = await session.execute(
                select(Reader).where(
                    (Reader.login == credentials.email) | 
                    (Reader.email == credentials.email)
                )
            )
            user = result.scalar_one_or_none()

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный логин/email или пароль")

        role = user.role if hasattr(user, 'role') else 'reader'
        permissions = get_permissions(role)
        name = f"{user.first_name} {user.last_name}".strip()
        email = getattr(user, 'email', None)
        user_id = user.id_employee if hasattr(user, 'id_employee') else user.id_reader

        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.login, "role": role, "id": user_id},
            expires_delta=expires_delta
        )
        expires_at = datetime.now(timezone.utc) + expires_delta

        return AuthResponse(
            token=access_token,
            user=UserResponse(id=user_id, name=name, email=email, role=role, permissions=permissions),
            expiresAt=expires_at.isoformat()
        )

@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(data: UserRegister):
    if data.password != data.confirm_password:
        raise HTTPException(400, "Пароли не совпадают")
    if len(data.password) < 6:
        raise HTTPException(400, "Пароль должен содержать минимум 6 символов")
    
    name_parts = data.name.strip().split()
    first_name = name_parts[0]
    last_name = name_parts[-1] if len(name_parts) > 1 else ""

    async with async_session() as session:
        # Проверка дубликатов
        for model in [Reader, Employee]:
            res = await session.execute(select(model).where(model.login == data.email))
            if res.scalar_one_or_none():
                raise HTTPException(400, "Аккаунт с таким email уже существует")

        new_reader = Reader(
            login=data.email,
            password_hash=get_password_hash(data.password),
            first_name=first_name,
            last_name=last_name,
            email=data.email,
            registration_date=datetime.utcnow().date()
        )
        session.add(new_reader)
        await session.commit()
        await session.refresh(new_reader)

        return MessageResponse(success=True, message="Пользователь создан", userId=new_reader.id_reader)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    role = current_user.role if hasattr(current_user, 'role') else 'reader'
    name = f"{current_user.first_name} {current_user.last_name}".strip()
    email = getattr(current_user, 'email', None)
    user_id = current_user.id_employee if hasattr(current_user, 'id_employee') else current_user.id_reader
    return UserResponse(
        id=user_id, 
        name=name, 
        email=email, 
        role=role, 
        permissions=get_permissions(role)
    )

@router.get("/user/stats")
async def get_reader_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить статистику для личного кабинета читателя"""

    from models import Loan, Reservation

    # Проверяем, что это читатель
    if hasattr(current_user, "role") and current_user.role != "reader":
        raise HTTPException(status_code=403, detail="Доступ только для читателей")
    
    reader_id = current_user.id_reader
    
    from sqlalchemy import func, and_
    from datetime import date, timedelta
    
    # 1. Активные займы (не возвращённые)
    active_query = select(func.count()).select_from(Loan).where(
        and_(Loan.id_reader == reader_id, Loan.return_date.is_(None))
    )
    active_loans = (await db.execute(active_query)).scalar() or 0
    
    # 2. Предстоящие возвраты (в ближайшие 3 дня)
    soon_date = date.today() + timedelta(days=3)
    upcoming_query = select(func.count()).select_from(Loan).where(
        and_(
            Loan.id_reader == reader_id,
            Loan.return_date.is_(None),
            Loan.due_date <= soon_date
        )
    )
    upcoming_returns = (await db.execute(upcoming_query)).scalar() or 0
    
    # 3. Активные бронирования
    reservations_query = select(func.count()).select_from(Reservation).where(
        and_(
            Reservation.id_reader == reader_id,
            Reservation.status.in_(["pending", "ready"])
        )
    )
    active_reservations = (await db.execute(reservations_query)).scalar() or 0
    
    return {
        "activeLoans": active_loans,
        "upcomingReturns": upcoming_returns,
        "unreadNotifications": 0,  # Заглушка, пока нет таблицы notifications
        "activeReservations": active_reservations
    }

@router.post("/logout", response_model=MessageResponse)
async def logout():
    # JWT stateless, фронтенд сам удалит токен
    return MessageResponse(success=True, message="Выход выполнен")