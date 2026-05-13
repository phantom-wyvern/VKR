-- ==========================================
-- DDL Скрипт: Структура БД Библиотеки
-- СУБД: PostgreSQL 16
-- Соответствует ER-модели и требованиям ВКР
-- ==========================================

-- Включаем расширение для хеширования паролей (требование 152-ФЗ)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Справочники (Словари)
-- Таблица: Издательства
CREATE TABLE publishing_house (
    id_publishing_house SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    contact_info TEXT
);

-- Таблица: Жанры
CREATE TABLE genre (
    id_genre SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Таблица: Авторы (Нормализация: один автор - одна запись)
CREATE TABLE author (
    id_author SERIAL PRIMARY KEY,
    nickname VARCHAR(50),
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    birth_date DATE
);

-- 2. Библиографические записи (Сами книги как произведения)
-- Соответствует сущности Bibliographic_record из ER-модели
CREATE TABLE book (
    id_book SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    publication_year INTEGER NOT NULL CHECK (publication_year > 1800),
    isbn VARCHAR(20) UNIQUE,
    number_of_pages INTEGER,
    annotation TEXT,
    edition VARCHAR(100),
    cover_url TEXT, -- Добавлено для фронтенда (хранение ссылки на картинку)
    publisher_id INTEGER REFERENCES publishing_house(id_publishing_house) ON DELETE SET NULL
);

-- 3. Связи Многие-ко-Многим
-- Таблица: Связь Книга - Автор
CREATE TABLE book_author (
    id_book INTEGER NOT NULL REFERENCES book(id_book) ON DELETE CASCADE,
    id_author INTEGER NOT NULL REFERENCES author(id_author) ON DELETE CASCADE,
    PRIMARY KEY (id_book, id_author)
);

-- Таблица: Связь Книга - Жанр
CREATE TABLE book_genre (
    id_book INTEGER NOT NULL REFERENCES book(id_book) ON DELETE CASCADE,
    id_genre INTEGER NOT NULL REFERENCES genre(id_genre) ON DELETE CASCADE,
    PRIMARY KEY (id_book, id_genre)
);

-- 4. Физический фонд (Экземпляры)
-- Таблица: Экземпляр книги (Copy)
CREATE TABLE copy (
    id_copy SERIAL PRIMARY KEY,
    inventory_number VARCHAR(30) NOT NULL UNIQUE, -- Инвентарный номер/Штрихкод
    id_book INTEGER NOT NULL REFERENCES book(id_book) ON DELETE CASCADE,
    location VARCHAR(100), -- Где стоит на полке
    status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'borrowed', 'reserved', 'lost')),
    date_of_receipt DATE DEFAULT CURRENT_DATE
);

-- 5. Пользователи
-- Таблица: Сотрудники (Библиотекари/Админы)
CREATE TABLE employee (
    id_employee SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Хранить только хеш!
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'librarian')),
    position VARCHAR(100)
);

-- Таблица: Читатели
CREATE TABLE reader (
    id_reader SERIAL PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    phone VARCHAR(20),
    email VARCHAR(100),
    library_card_number VARCHAR(20) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE -- "Мягкое удаление" вместо DROP
);

-- 6. Транзакции (Выдача и Бронь)
-- Таблица: Выдача (Loan/Issue)
-- Штрафов нет, но есть даты возврата
CREATE TABLE loan (
    id_loan SERIAL PRIMARY KEY,
    id_reader INTEGER NOT NULL REFERENCES reader(id_reader),
    id_copy INTEGER NOT NULL REFERENCES copy(id_copy),
    id_employee INTEGER NOT NULL REFERENCES employee(id_employee), -- Кто выдал
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL, -- Плановая дата возврата
    return_date DATE DEFAULT NULL, -- Фактическая дата (NULL если книга на руках)
    CHECK (return_date IS NULL OR return_date >= issue_date),
    CHECK (due_date >= issue_date)
);

-- Индекс для предотвращения двойной выдачи одной копии
CREATE UNIQUE INDEX idx_loan_active_copy ON loan(id_copy) WHERE return_date IS NULL;

-- Индексы для FK loan
CREATE INDEX idx_loan_id_reader ON loan(id_reader);
CREATE INDEX idx_loan_id_copy ON loan(id_copy);
CREATE INDEX idx_loan_id_employee ON loan(id_employee);
CREATE INDEX idx_loan_due_date ON loan(due_date);

-- Таблица: Бронирование (Reservation/Order)
CREATE TABLE reservation (
    id_reservation SERIAL PRIMARY KEY,
    id_reader INTEGER NOT NULL REFERENCES reader(id_reader),
    id_book INTEGER NOT NULL REFERENCES book(id_book), -- Бронируем книгу в целом
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'fulfilled', 'cancelled'))
);

-- Индексы для FK reservation
CREATE INDEX idx_reservation_id_reader ON reservation(id_reader);
CREATE INDEX idx_reservation_id_book ON reservation(id_book);
CREATE INDEX idx_reservation_status ON reservation(status);
CREATE INDEX idx_reservation_created_at ON reservation(created_at);

-- 7. Системные таблицы (Аудит и Настройки)
-- Таблица: Журнал действий (Audit Log) - требование безопасности ВКР
CREATE TABLE audit_log (
    id_audit SERIAL PRIMARY KEY,
    id_employee INTEGER REFERENCES employee(id_employee), -- NULL если действие системное
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    details JSONB, -- Гибкое хранение деталей (кто, что изменил)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для audit_log
CREATE INDEX idx_audit_log_id_employee ON audit_log(id_employee);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action_type ON audit_log(action_type);

-- Таблица: Настройки системы
CREATE TABLE system_settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value TEXT
);

-- ==========================================
-- Индексы (Оптимизация производительности)
-- ==========================================
-- Ускоряем поиск по ISBN и названию
CREATE INDEX idx_book_isbn ON book(isbn);
CREATE INDEX idx_book_title ON book(title);
-- Ускоряем поиск по инвентарному номеру (для сканера штрихкодов)
CREATE INDEX idx_copy_inventory ON copy(inventory_number);
-- Ускоряем поиск активных займов по дате возврата
CREATE INDEX idx_loan_due_date ON loan(due_date) WHERE return_date IS NULL;
-- Ускоряем поиск по читателю
CREATE INDEX idx_loan_reader ON loan(id_reader);
-- Ускоряем поиск по сотруднику (для аудита)
CREATE INDEX idx_audit_employee ON audit_log(id_employee);

-- ==========================================
-- Триггер Аудита (Автоматическое логирование)
-- ==========================================
-- CREATE OR REPLACE FUNCTION fn_audit_trigger()
-- RETURNS TRIGGER AS $$
-- DECLARE
--     record_id_val INTEGER;
-- BEGIN
--     -- Пытаемся найти первичный ключ динамически
--     IF TG_OP = 'INSERT' THEN
--         record_id_val := (row_to_json(NEW) ->> 'id')::INTEGER;
--         IF record_id_val IS NULL THEN
--             record_id_val := COALESCE(NEW.id_book, NEW.id_reader, NEW.id_copy, NEW.id_loan, NEW.id_reservation, NEW.id_audit);
--         END IF;
--         INSERT INTO audit_log (action_type, table_name, record_id, details, created_at)
--         VALUES ('INSERT', TG_TABLE_NAME, record_id_val, row_to_json(NEW)::jsonb, CURRENT_TIMESTAMP);
--         RETURN NEW;
--     ELSIF TG_OP = 'UPDATE' THEN
--         record_id_val := (row_to_json(NEW) ->> 'id')::INTEGER;
--         IF record_id_val IS NULL THEN
--             record_id_val := COALESCE(NEW.id_book, NEW.id_reader, NEW.id_copy, NEW.id_loan, NEW.id_reservation, NEW.id_audit);
--         END IF;
--         INSERT INTO audit_log (action_type, table_name, record_id, details, created_at)
--         VALUES ('UPDATE', TG_TABLE_NAME, record_id_val, jsonb_build_object('old', row_to_json(OLD)::jsonb, 'new', row_to_json(NEW)::jsonb), CURRENT_TIMESTAMP);
--         RETURN NEW;
--     ELSIF TG_OP = 'DELETE' THEN
--         record_id_val := (row_to_json(OLD) ->> 'id')::INTEGER;
--         IF record_id_val IS NULL THEN
--             record_id_val := COALESCE(OLD.id_book, OLD.id_reader, OLD.id_copy, OLD.id_loan, OLD.id_reservation, OLD.id_audit);
--         END IF;
--         INSERT INTO audit_log (action_type, table_name, record_id, details, created_at)
--         VALUES ('DELETE', TG_TABLE_NAME, record_id_val, row_to_json(OLD)::jsonb, CURRENT_TIMESTAMP);
--         RETURN OLD;
--     END IF;
--     RETURN NULL;
-- END;
-- $$ LANGUAGE plpgsql;

-- Вешаем триггер на важные таблицы (например, на книги)
CREATE TRIGGER trg_book_audit
AFTER INSERT OR UPDATE OR DELETE ON book
FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

-- ==========================================
-- Начальные данные (Seed)
-- ==========================================
-- Админ по умолчанию (пароль: admin123 - хеш сгенерирован pgcrypto)
INSERT INTO employee (login, password_hash, first_name, last_name, role, position) VALUES
('admin', crypt('admin123', gen_salt('bf')), 'Системный', 'Администратор', 'admin', 'Главный админ');

-- Настройки по умолчанию
INSERT INTO system_settings (setting_key, setting_value) VALUES
('loan_period_days', '14'),
('max_books_per_user', '5');