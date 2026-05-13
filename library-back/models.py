# backend/models.py
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


# === Справочники ===

class Publisher(Base):
    __tablename__ = "publishing_house"

    id_publishing_house = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100))
    contact_info = Column(Text)


class Genre(Base):
    __tablename__ = "genre"
    id_genre = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    books = relationship("Book", secondary="book_genre", back_populates="genres")


class Author(Base):
    __tablename__ = "author"
    id_author = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50))
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    birth_date = Column(Date)
    books = relationship("Book", secondary="book_author", back_populates="authors")


# === Книги и связи ===

class Book(Base):
    __tablename__ = "book"

    id_book = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False)
    isbn = Column(String(20), unique=True)
    number_of_pages = Column(Integer)
    annotation = Column(Text)
    edition = Column(String(100))
    cover_url = Column(String)
    publisher_id = Column(Integer, ForeignKey("publishing_house.id_publishing_house"))

    # Связи
    publisher = relationship("Publisher")
    copies = relationship("Copy", back_populates="book")
    genres = relationship("Genre", secondary="book_genre", back_populates="books")
    authors = relationship("Author", secondary="book_author", back_populates="books")


class BookAuthor(Base):
    __tablename__ = "book_author"
    id_book = Column(Integer, ForeignKey("book.id_book", ondelete="CASCADE"), primary_key=True)
    id_author = Column(Integer, ForeignKey("author.id_author", ondelete="CASCADE"), primary_key=True)


class BookGenre(Base):
    __tablename__ = "book_genre"
    id_book = Column(Integer, ForeignKey("book.id_book", ondelete="CASCADE"), primary_key=True)
    id_genre = Column(Integer, ForeignKey("genre.id_genre", ondelete="CASCADE"), primary_key=True)


# === Фонд ===

class Copy(Base):
    __tablename__ = "copy"

    id_copy = Column(Integer, primary_key=True, index=True)
    inventory_number = Column(String(30), unique=True, nullable=False)
    id_book = Column(Integer, ForeignKey("book.id_book", ondelete="CASCADE"), nullable=False)
    location = Column(String(100))
    status = Column(String(20), nullable=False, default="available")  # available, borrowed, reserved, lost
    date_of_receipt = Column(Date)

    book = relationship("Book", back_populates="copies")


# === Пользователи ===

class Employee(Base):
    __tablename__ = "employee"

    id_employee = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    role = Column(String(20), nullable=False)  # admin, librarian
    position = Column(String(100))


class Reader(Base):
    __tablename__ = "reader"

    id_reader = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))
    library_card_number = Column(String(20), unique=True)
    registration_date = Column(Date)
    is_active = Column(Boolean, default=True)


# === Транзакции ===

class Loan(Base):
    __tablename__ = "loan"

    id_loan = Column(Integer, primary_key=True, index=True)
    id_reader = Column(Integer, ForeignKey("reader.id_reader"), nullable=False)
    id_copy = Column(Integer, ForeignKey("copy.id_copy"), nullable=False)
    id_employee = Column(Integer, ForeignKey("employee.id_employee"), nullable=False)

    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)  # NULL если не возвращена

    reader = relationship("Reader")
    copy = relationship("Copy")
    employee = relationship("Employee")


class Reservation(Base):
    __tablename__ = "reservation"

    id_reservation = Column(Integer, primary_key=True, index=True)
    id_reader = Column(Integer, ForeignKey("reader.id_reader"), nullable=False)
    id_book = Column(Integer, ForeignKey("book.id_book"), nullable=False)
    created_at = Column(TIMESTAMP)
    status = Column(String(20), default="pending")  # pending, ready, fulfilled, cancelled
    reader = relationship("Reader")
    book = relationship("Book")


# === Системные ===

class AuditLog(Base):
    __tablename__ = "audit_log"

    id_audit = Column(Integer, primary_key=True, index=True)
    id_employee = Column(Integer, ForeignKey("employee.id_employee"))
    action_type = Column(String(50), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    details = Column(JSONB)  # Используем JSONB для гибкости
    created_at = Column(TIMESTAMP)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    setting_key = Column(String(50), primary_key=True)
    setting_value = Column(Text)