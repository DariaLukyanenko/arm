-- Таблица workflow требований (с версионированием)
CREATE TABLE IF NOT EXISTS requirement_workflow (
    id SERIAL PRIMARY KEY,
    requirement_content_id INTEGER NOT NULL REFERENCES requirement_content(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    prev_req_workflow_id INTEGER REFERENCES requirement_workflow(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_workflow_status CHECK (status IN ('draft', 'review', 'approved', 'rejected', 'implemented', 'verified', 'archived'))
);

CREATE INDEX idx_req_workflow_content_id ON requirement_workflow(requirement_content_id);
CREATE INDEX idx_req_workflow_status ON requirement_workflow(status);
CREATE INDEX idx_req_workflow_priority ON requirement_workflow(priority);
CREATE INDEX idx_req_workflow_is_active ON requirement_workflow(is_active);

