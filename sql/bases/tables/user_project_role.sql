-- Таблица связи пользователей с проектными ролями
CREATE TABLE IF NOT EXISTS user_project_role (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, project_id, role_id)
);

CREATE INDEX idx_user_project_role_user ON user_project_role(user_id);
CREATE INDEX idx_user_project_role_project ON user_project_role(project_id);
CREATE INDEX idx_user_project_role_role ON user_project_role(role_id);

