-- Таблица комментариев к обсуждениям
CREATE TABLE IF NOT EXISTS comment (
    id SERIAL PRIMARY KEY,
    discussion_id INTEGER NOT NULL REFERENCES discussion(id) ON DELETE CASCADE,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL
);

CREATE INDEX idx_comment_discussion ON comment(discussion_id);
CREATE INDEX idx_comment_created_by ON comment(created_by_user_id);

