-- Таблица пользователей (без привязки к person, используем external_id)
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL UNIQUE,
    login VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(500),
    email VARCHAR(255),
    global_role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    datetime_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_user_status CHECK (status IN ('active', 'inactive'))
);

CREATE INDEX idx_user_external_id ON "user"(external_id);
CREATE INDEX idx_user_login ON "user"(login);
CREATE INDEX idx_user_status ON "user"(status);

