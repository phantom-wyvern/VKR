-- ==========================================
-- Шаг 3: Безопасность и роли (152-ФЗ)
-- ==========================================

-- Создаем роли для разных типов пользователей
-- Эти роли будут использоваться приложением для подключения к БД

-- 1. Роль для читателя (только чтение своих данных)
CREATE ROLE lib_reader WITH LOGIN PASSWORD 'reader_password_123';

-- 2. Роль для библиотекаря (чтение + операции с займами)
CREATE ROLE lib_librarian WITH LOGIN PASSWORD 'librarian_password_123';

-- 3. Роль для администратора (полный доступ)
CREATE ROLE lib_admin WITH LOGIN PASSWORD 'admin_password_123';

-- ==========================================
-- GRANT для роли lib_reader (Читатель)
-- ==========================================
-- Читатель может:
-- - Просматривать каталог книг
-- - Просматривать свои займы и бронирования
-- - Редактировать свой профиль

-- Доступ к справочникам (только чтение)
GRANT SELECT ON publishing_house TO lib_reader;
GRANT SELECT ON genre TO lib_reader;
GRANT SELECT ON author TO lib_reader;
GRANT SELECT ON book TO lib_reader;
GRANT SELECT ON book_author TO lib_reader;
GRANT SELECT ON book_genre TO lib_reader;

-- Доступ к экземплярам (только чтение)
GRANT SELECT ON copy TO lib_reader;

-- Доступ к своим данным (через представления или RLS)
-- Пока даем SELECT на всю таблицу, в проде лучше использовать RLS
GRANT SELECT ON reader TO lib_reader;
GRANT SELECT ON loan TO lib_reader;
GRANT SELECT ON reservation TO lib_reader;

-- Запрет на изменение чужих данных
REVOKE ALL ON employee FROM lib_reader;
REVOKE ALL ON audit_log FROM lib_reader;
REVOKE ALL ON system_settings FROM lib_reader;

-- ==========================================
-- GRANT для роли lib_librarian (Библиотекарь)
-- ==========================================
-- Библиотекарь может:
-- - Всё, что читатель
-- - Управлять займами (выдача/возврат)
-- - Управлять бронированиями
-- - Просматривать всех читателей
-- - Просматривать статистику

-- Наследуем права читателя
GRANT lib_reader TO lib_librarian;

-- Полный доступ к транзакциям (займы и бронирования)
GRANT SELECT, INSERT, UPDATE ON loan TO lib_librarian;
GRANT SELECT, INSERT, UPDATE, DELETE ON reservation TO lib_librarian;

-- Чтение всех читателей
GRANT SELECT ON reader TO lib_librarian;

-- Чтение статистики и аудита
GRANT SELECT ON audit_log TO lib_librarian;
GRANT SELECT ON system_settings TO lib_librarian;

-- Ограниченный доступ к сотрудникам (только профиль)
GRANT SELECT (id_employee, first_name, last_name, position) ON employee TO lib_librarian;

-- ==========================================
-- GRANT для роли lib_admin (Администратор)
-- ==========================================
-- Администратор может:
-- - Всё, что библиотекарь
-- - Управлять пользователями
-- - Управлять настройками системы
-- - Просматривать полный аудит
-- - Управлять справочниками

-- Наследуем права библиотекаря
GRANT lib_librarian TO lib_admin;

-- Полный доступ ко всем таблицам
GRANT ALL ON ALL TABLES IN SCHEMA public TO lib_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO lib_admin;

-- ==========================================
-- Row Level Security (RLS) - Опционально
-- ==========================================
-- Для соответствия 152-ФЗ можно включить RLS, чтобы каждый 
-- пользователь видел только свои данные

-- Пример для таблицы reader (персональные данные)
-- ALTER TABLE reader ENABLE ROW LEVEL SECURITY;

-- Политика: пользователи видят только свои записи
-- CREATE POLICY reader_isolation_policy ON reader
--     FOR ALL
--     USING (id_reader = current_setting('app.current_user_id', true)::integer);

-- Политика для loan (займы)
-- ALTER TABLE loan ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY loan_isolation_policy ON loan
--     FOR ALL
--     USING (
--         -- Админ и библиотекарь видят всё
--         EXISTS (
--             SELECT 1 FROM pg_roles 
--             WHERE pg_roles.rolname = 'lib_admin' 
--             AND pg_roles.rolname = current_user
--         )
--         OR
--         EXISTS (
--             SELECT 1 FROM pg_roles 
--             WHERE pg_roles.rolname = 'lib_librarian' 
--             AND pg_roles.rolname = current_user
--         )
--         OR
--         -- Читатель видит только свои займы
--         id_reader = current_setting('app.current_reader_id', true)::integer
--     );

-- ==========================================
-- Хеширование паролей (pgcrypto)
-- ==========================================
-- Расширение pgcrypto уже включено в schema.sql
-- Пример использования при вставке пользователя:

-- Вставка администратора с хешированным паролем
-- INSERT INTO employee (login, password_hash, first_name, last_name, role)
-- VALUES ('admin', crypt('admin123', gen_salt('bf')), 'Админ', 'Системы', 'admin');

-- ==========================================
-- Аудит доступа к персональным данным
-- ==========================================
-- Создаем триггер для аудита доступа к таблице reader

CREATE OR REPLACE FUNCTION log_reader_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Логируем каждый SELECT к персональным данным
    IF TG_OP = 'SELECT' THEN
        INSERT INTO audit_log (action_type, table_name, record_id, details, created_at)
        VALUES (
            'SELECT', 
            'reader', 
            NEW.id_reader, 
            jsonb_build_object('accessed_by', current_user, 'fields', 'personal_data'),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Вешаем триггер (опционально, может замедлить работу)
-- CREATE TRIGGER trg_reader_audit_select
-- AFTER SELECT ON reader
-- FOR EACH ROW EXECUTE FUNCTION log_reader_access();

-- ==========================================
-- Настройка прав по умолчанию
-- ==========================================
-- Для будущих таблиц

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO lib_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO lib_librarian;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO lib_admin;

-- ==========================================
-- Тестовые данные для проверки ролей
-- ==========================================
-- Создаем тестовых пользователей с разными ролями

-- Читатель
INSERT INTO reader (login, password_hash, first_name, last_name, email, phone)
VALUES (
    'reader@test.ru',
    crypt('reader123', gen_salt('bf')),
    'Иван',
    'Читатель',
    'reader@test.ru',
    '+7 (999) 111-22-33'
);

-- Библиотекарь
INSERT INTO employee (login, password_hash, first_name, last_name, role, position)
VALUES (
    'librarian@test.ru',
    crypt('librarian123', gen_salt('bf')),
    'Анна',
    'Библиотекарь',
    'librarian',
    'Старший библиотекарь'
);

-- ==========================================
-- Проверка прав (для отладки)
-- ==========================================
-- Выполните от имени разных ролей для проверки:

-- SET ROLE lib_reader;
-- SELECT * FROM book; -- Должно работать
-- SELECT * FROM employee; -- Должно выдать ошибку
-- RESET ROLE;

-- ==========================================
-- Рекомендации по безопасности
-- ==========================================
/*
1. В production смените пароли на сложные:
   ALTER ROLE lib_admin WITH PASSWORD 'very_strong_password_here';

2. Включите SSL-соединение в postgresql.conf:
   ssl = on
   ssl_cert_file = 'server.crt'
   ssl_key_file = 'server.key'

3. Настройте pg_hba.conf для ограничения доступа по IP:
   host    library_system    lib_reader    192.168.1.0/24    md5

4. Регулярно делайте backup:
   pg_dump -U library_user library_system > backup.sql

5. Включите логирование в postgresql.conf:
   log_connections = on
   log_disconnections = on
   log_statement = 'ddl'
*/