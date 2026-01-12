-- Таблица разрешений (permissions)
CREATE TABLE IF NOT EXISTS permission (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE INDEX idx_permission_code ON permission(code);

