-- Таблица связи требований и пользователей
CREATE TABLE IF NOT EXISTS requirement_user (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE(requirement_id, user_id)
);

CREATE INDEX idx_requirement_user_requirement ON requirement_user(requirement_id);
CREATE INDEX idx_requirement_user_user ON requirement_user(user_id);

