-- Таблица проектов
CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    CONSTRAINT check_project_status CHECK (status IN ('active', 'archived', 'draft'))
);

CREATE INDEX idx_project_status ON project(status);
CREATE INDEX idx_project_created_by ON project(created_by_user_id);

