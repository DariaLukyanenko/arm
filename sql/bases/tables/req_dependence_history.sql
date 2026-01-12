-- Таблица истории зависимостей
CREATE TABLE IF NOT EXISTS req_dependence_history (
    id SERIAL PRIMARY KEY,
    prev_req_dependence_id INTEGER REFERENCES requirement_dependence(id) ON DELETE SET NULL,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_req_dependence_history_prev ON req_dependence_history(prev_req_dependence_id);
CREATE INDEX idx_req_dependence_history_created_by ON req_dependence_history(created_by_user_id);

