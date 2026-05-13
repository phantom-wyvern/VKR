# backend/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# === Модели для Запросов (Request Models) ===

class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


# === Модели для Ответов (Response Models) ===

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    login: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    role: str
    permissions: List[str] = []
    avatar: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    token: str
    user: UserResponse
    expiresAt: str

class MessageResponse(BaseModel):
    success: bool
    message: str
    userId: Optional[int] = None

# === Административные схемы ===

class UserAdminResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    role: str  # 'reader', 'librarian', 'admin'
    status: str  # 'active', 'blocked' (для читателей), для сотрудников всегда 'active'
    createdAt: str  # дата регистрации в ISO формате
    model_config = ConfigDict(from_attributes=True)

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # 'reader', 'librarian', 'admin'
    # дополнительные поля можно добавить при необходимости

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class SettingsResponse(BaseModel):
    loanPeriod: int = Field(alias="loan_period_days")
    maxBooksPerUser: int = Field(alias="max_books_per_user")
    finePerDay: int = 0  # пока нет в БД, можно добавить
    enableReservations: bool = Field(alias="enable_reservations")
    enableEmailNotifications: bool = Field(alias="enable_email_notifications")
    libraryName: str = Field(alias="library_name")
    libraryAddress: str = Field(alias="library_address")
    libraryPhone: str = Field(alias="library_phone")
    libraryEmail: str = Field(alias="library_email")
    workHoursStart: str = Field(alias="work_hours_start")
    workHoursEnd: str = Field(alias="work_hours_end")

    model_config = ConfigDict(populate_by_name=True)

class SaveSettingsRequest(BaseModel):
    loanPeriod: Optional[int] = None
    maxBooksPerUser: Optional[int] = None
    finePerDay: Optional[int] = None
    enableReservations: Optional[bool] = None
    enableEmailNotifications: Optional[bool] = None
    libraryName: Optional[str] = None
    libraryAddress: Optional[str] = None
    libraryPhone: Optional[str] = None
    libraryEmail: Optional[str] = None
    workHoursStart: Optional[str] = None
    workHoursEnd: Optional[str] = None

class GenreAdminResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class CreateGenreRequest(BaseModel):
    name: str

class UpdateGenreRequest(BaseModel):
    name: str

class AuditLogResponse(BaseModel):
    id: int
    userId: Optional[int] = None
    userName: Optional[str] = None
    action: str
    details: Optional[str] = None
    timestamp: str
    model_config = ConfigDict(from_attributes=True)

class AuditLogsPage(BaseModel):
    data: List[AuditLogResponse]
    total: int
    page: int
    limit: int
    totalPages: int