-- Таблица требований
CREATE TABLE IF NOT EXISTS requirement (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    path VARCHAR(500),
    depth INTEGER DEFAULT 0,
    requirement_group_id INTEGER,
    parent_id INTEGER REFERENCES requirement(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT check_requirement_type CHECK (type IN ('functional', 'non-functional', 'business'))
);

CREATE INDEX idx_requirement_project_id ON requirement(project_id);
CREATE INDEX idx_requirement_type ON requirement(type);
CREATE INDEX idx_requirement_created_by ON requirement(created_by_user_id);
CREATE INDEX idx_requirement_parent_id ON requirement(parent_id);
CREATE INDEX idx_requirement_is_deleted ON requirement(is_deleted);

