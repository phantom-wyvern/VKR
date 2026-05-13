# backend/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_, case, literal
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import Optional, List

from database import get_db
from models import Reader, Employee, SystemSetting, Genre, AuditLog
from schemas.auth_security import (
    get_current_user, 
    get_password_hash,
    require_admin, 
    require_admin_or_librarian
)
from schemas.schemas import (
    UserAdminResponse, CreateUserRequest, UpdateUserRequest,
    SettingsResponse, SaveSettingsRequest,
    GenreAdminResponse, CreateGenreRequest, UpdateGenreRequest,
    AuditLogResponse, AuditLogsPage, MessageResponse
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# =============================================================================
# === Пользователи ===
# =============================================================================

@router.get("/users", response_model=List[UserAdminResponse])
async def get_users(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    require_admin_or_librarian(current_user)

    # Получаем читателей
    readers_query = select(
        Reader.id_reader.label("id"),
        func.concat(Reader.first_name, ' ', Reader.last_name).label("name"),
        Reader.email,
        literal("reader").label("role"),
        case((Reader.is_active == True, "active"), else_="blocked").label("status"),
        Reader.registration_date.label("createdAt")
    )
    readers_result = await db.execute(readers_query)
    readers = readers_result.mappings().all()

    # Получаем сотрудников
    employees_query = select(
        Employee.id_employee.label("id"),
        func.concat(Employee.first_name, ' ', Employee.last_name).label("name"),
        literal(None).label("email"),
        Employee.role,
        literal("active").label("status"),
        func.current_date().label("createdAt")
    )
    employees_result = await db.execute(employees_query)
    employees = employees_result.mappings().all()

    # === ИСПРАВЛЕНИЕ: Конвертируем date → ISO string ===
    def normalize_user(user_row):
        user_dict = dict(user_row)
        # Конвертируем createdAt в строку, если это date/datetime
        if isinstance(user_dict.get("createdAt"), (date, datetime)):
            user_dict["createdAt"] = user_dict["createdAt"].isoformat()
        return user_dict

    users = [normalize_user(u) for u in list(readers) + list(employees)]
    users.sort(key=lambda u: u["id"])

    return users


@router.post("/users", response_model=UserAdminResponse)
async def create_user(
    data: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    
    name_parts = data.name.strip().split()
    first_name = name_parts[0]
    last_name = name_parts[-1] if len(name_parts) > 1 else ""

    if data.role == "reader":
        stmt = select(Reader).where(Reader.email == data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(400, "Email уже используется")
        
        new_reader = Reader(
            login=data.email,
            password_hash=get_password_hash(data.password),
            first_name=first_name,
            last_name=last_name,
            email=data.email,
            registration_date=datetime.utcnow().date(),
            is_active=True
        )
        db.add(new_reader)
        await db.commit()
        await db.refresh(new_reader)
        
        return {
            "id": new_reader.id_reader,
            "name": f"{new_reader.first_name} {new_reader.last_name}",
            "email": new_reader.email,
            "role": "reader",
            "status": "active",
            "createdAt": new_reader.registration_date.isoformat()
        }
    else:
        stmt = select(Employee).where(Employee.login == data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(400, "Логин уже используется")
        
        new_emp = Employee(
            login=data.email,
            password_hash=get_password_hash(data.password),
            first_name=first_name,
            last_name=last_name,
            role=data.role,
            position="Не указана"
        )
        db.add(new_emp)
        await db.commit()
        await db.refresh(new_emp)
        
        return {
            "id": new_emp.id_employee,
            "name": f"{new_emp.first_name} {new_emp.last_name}",
            "email": None,
            "role": new_emp.role,
            "status": "active",
            "createdAt": datetime.utcnow().date().isoformat()
        }


@router.put("/users/{user_id}", response_model=UserAdminResponse)
async def update_user(
    user_id: int,
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    
    reader = await db.get(Reader, user_id)
    if reader:
        if data.name:
            parts = data.name.strip().split()
            reader.first_name = parts[0]
            reader.last_name = parts[-1] if len(parts) > 1 else ""
        if data.email:
            reader.email = data.email
            reader.login = data.email
        await db.commit()
        await db.refresh(reader)
        return {
            "id": reader.id_reader,
            "name": f"{reader.first_name} {reader.last_name}",
            "email": reader.email,
            "role": "reader",
            "status": "active" if reader.is_active else "blocked",
            "createdAt": reader.registration_date.isoformat()
        }
    else:
        emp = await db.get(Employee, user_id)
        if not emp:
            raise HTTPException(404, "Пользователь не найден")
        
        if data.name:
            parts = data.name.strip().split()
            emp.first_name = parts[0]
            emp.last_name = parts[-1] if len(parts) > 1 else ""
        if data.email:
            emp.login = data.email
        if data.role and data.role in ["admin", "librarian"]:
            emp.role = data.role
        
        await db.commit()
        await db.refresh(emp)
        return {
            "id": emp.id_employee,
            "name": f"{emp.first_name} {emp.last_name}",
            "email": None,
            "role": emp.role,
            "status": "active",
            "createdAt": datetime.utcnow().date().isoformat()
        }


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    
    reader = await db.get(Reader, user_id)
    if reader:
        reader.is_active = False
        await db.commit()
        return MessageResponse(success=True, message="Читатель деактивирован")
    else:
        emp = await db.get(Employee, user_id)
        if emp:
            await db.delete(emp)
            await db.commit()
            return MessageResponse(success=True, message="Сотрудник удалён")
        else:
            raise HTTPException(404, "Пользователь не найден")


@router.patch("/users/{user_id}/toggle-status", response_model=UserAdminResponse)
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    
    reader = await db.get(Reader, user_id)
    if not reader:
        raise HTTPException(404, "Читатель не найден")
    
    reader.is_active = not reader.is_active
    await db.commit()
    await db.refresh(reader)
    
    return {
        "id": reader.id_reader,
        "name": f"{reader.first_name} {reader.last_name}",
        "email": reader.email,
        "role": "reader",
        "status": "active" if reader.is_active else "blocked",
        "createdAt": reader.registration_date.isoformat()
    }


# =============================================================================
# === Настройки ===
# =============================================================================

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin_or_librarian(current_user)
    
    stmt = select(SystemSetting)
    result = await db.execute(stmt)
    settings_rows = result.scalars().all()
    settings_dict = {row.setting_key: row.setting_value for row in settings_rows}
    
    return SettingsResponse(
        loan_period_days=int(settings_dict.get("loan_period_days", 14)),
        max_books_per_user=int(settings_dict.get("max_books_per_user", 5)),
        finePerDay=0,
        enable_reservations=settings_dict.get("enable_reservations", "true").lower() == "true",
        enable_email_notifications=settings_dict.get("enable_email_notifications", "true").lower() == "true",
        library_name=settings_dict.get("library_name", "Библиотека"),
        library_address=settings_dict.get("library_address", ""),
        library_phone=settings_dict.get("library_phone", ""),
        library_email=settings_dict.get("library_email", ""),
        work_hours_start=settings_dict.get("work_hours_start", "9:00"),
        work_hours_end=settings_dict.get("work_hours_end", "21:00")
    )


@router.put("/settings", response_model=SettingsResponse)
async def save_settings(
    data: SaveSettingsRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    
    mapping = {
        "loanPeriod": "loan_period_days",
        "maxBooksPerUser": "max_books_per_user",
        "enableReservations": "enable_reservations",
        "enableEmailNotifications": "enable_email_notifications",
        "libraryName": "library_name",
        "libraryAddress": "library_address",
        "libraryPhone": "library_phone",
        "libraryEmail": "library_email",
        "workHoursStart": "work_hours_start",
        "workHoursEnd": "work_hours_end"
    }
    
    for field, key in mapping.items():
        value = getattr(data, field, None)
        if value is not None:
            stmt = select(SystemSetting).where(SystemSetting.setting_key == key)
            result = await db.execute(stmt)
            setting = result.scalar_one_or_none()
            
            if setting:
                setting.setting_value = str(value).lower() if isinstance(value, bool) else str(value)
            else:
                new_setting = SystemSetting(
                    setting_key=key, 
                    setting_value=str(value).lower() if isinstance(value, bool) else str(value)
                )
                db.add(new_setting)
    
    await db.commit()
    return await get_settings(db, current_user)


# =============================================================================
# === Жанры ===
# =============================================================================

@router.get("/genres", response_model=List[GenreAdminResponse])
async def get_genres(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin_or_librarian(current_user)
    result = await db.execute(select(Genre))
    genres = result.scalars().all()
    return [{"id": g.id_genre, "name": g.name} for g in genres]


@router.post("/genres", response_model=GenreAdminResponse)
async def create_genre(
    data: CreateGenreRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    existing = await db.execute(select(Genre).where(Genre.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Жанр с таким названием уже существует")
    
    new_genre = Genre(name=data.name)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return {"id": new_genre.id_genre, "name": new_genre.name}


@router.put("/genres/{genre_id}", response_model=GenreAdminResponse)
async def update_genre(
    genre_id: int,
    data: UpdateGenreRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    genre = await db.get(Genre, genre_id)
    if not genre:
        raise HTTPException(404, "Жанр не найден")
    genre.name = data.name
    await db.commit()
    await db.refresh(genre)
    return {"id": genre.id_genre, "name": genre.name}


@router.delete("/genres/{genre_id}", response_model=MessageResponse)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin(current_user)
    genre = await db.get(Genre, genre_id)
    if not genre:
        raise HTTPException(404, "Жанр не найден")
    await db.delete(genre)
    await db.commit()
    return MessageResponse(success=True, message="Жанр удалён")


# =============================================================================
# === Аудит ===
# =============================================================================

@router.get("/audit", response_model=AuditLogsPage)
async def get_audit_logs(
    search: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    require_admin_or_librarian(current_user)
    
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    conditions = []
    
    if search:
        conditions.append(AuditLog.action_type.ilike(f"%{search}%"))
    if startDate:
        start_dt = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
        conditions.append(AuditLog.created_at >= start_dt)
    if endDate:
        end_dt = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
        conditions.append(AuditLog.created_at <= end_dt)

    if conditions:
        query = query.where(and_(*conditions))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()

    data = []
    for log in logs:
        user_name = None
        if log.id_employee:
            emp = await db.get(Employee, log.id_employee)
            if emp:
                user_name = f"{emp.first_name} {emp.last_name}"
        data.append({
            "id": log.id_audit,
            "userId": log.id_employee,
            "userName": user_name,
            "action": log.action_type,
            "details": str(log.details) if log.details else None,
            "timestamp": log.created_at.isoformat() if log.created_at else datetime.utcnow().isoformat()
        })

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit
    }