-- Таблица группировки требований
CREATE TABLE IF NOT EXISTS requirement_group (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    original_req_id INTEGER REFERENCES requirement(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requirement_group_project ON requirement_group(project_id);
CREATE INDEX idx_requirement_group_original ON requirement_group(original_req_id);

