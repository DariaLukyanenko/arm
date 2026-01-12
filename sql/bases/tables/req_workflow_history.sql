-- Таблица истории workflow требований
CREATE TABLE IF NOT EXISTS req_workflow_history (
    id SERIAL PRIMARY KEY,
    prev_req_workflow_id INTEGER REFERENCES requirement_workflow(id) ON DELETE SET NULL,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_req_workflow_history_prev ON req_workflow_history(prev_req_workflow_id);
CREATE INDEX idx_req_workflow_history_created_by ON req_workflow_history(created_by_user_id);
CREATE INDEX idx_req_workflow_history_is_active ON req_workflow_history(is_active);

