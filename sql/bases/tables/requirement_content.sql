-- Таблица содержимого требований (с версионированием)
CREATE TABLE IF NOT EXISTS requirement_content (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    development_basis TEXT,
    development_purpose TEXT,
    description_text TEXT NOT NULL,
    acceptance_criteria TEXT,
    document_requires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    prev_req_content_id INTEGER REFERENCES requirement_content(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_req_content_requirement_id ON requirement_content(requirement_id);
CREATE INDEX idx_req_content_is_active ON requirement_content(is_active);
CREATE INDEX idx_req_content_created_at ON requirement_content(created_at);

