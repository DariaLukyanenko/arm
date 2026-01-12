-- Таблица обсуждений требований
CREATE TABLE IF NOT EXISTS discussion (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_discussion_requirement ON discussion(requirement_id);
CREATE INDEX idx_discussion_created_by ON discussion(created_by_user_id);
CREATE INDEX idx_discussion_is_active ON discussion(is_active);

