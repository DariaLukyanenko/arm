-- Таблица истории содержимого требований
CREATE TABLE IF NOT EXISTS req_content_history (
    id SERIAL PRIMARY KEY,
    prev_req_content_id INTEGER REFERENCES requirement_content(id) ON DELETE SET NULL,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_req_content_history_prev ON req_content_history(prev_req_content_id);
CREATE INDEX idx_req_content_history_created_by ON req_content_history(created_by_user_id);
CREATE INDEX idx_req_content_history_is_active ON req_content_history(is_active);

