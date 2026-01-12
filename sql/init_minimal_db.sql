-- Minimal DB Schema for ARMS (Requirements, Dependencies, Reports only)
SET search_path TO arms_schema;

-- 1. Роли
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- 2. Пользователи
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,
    login VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(500),
    email VARCHAR(255),
    global_role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    datetime_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_user_status CHECK (status IN ('active', 'inactive'))
);

CREATE INDEX idx_user_external_id ON "user"(external_id);
CREATE INDEX idx_user_login ON "user"(login);

-- 3. Проекты
CREATE TABLE project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL
);

-- 4. Группы требований
CREATE TABLE requirement_group (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    original_group_id INTEGER REFERENCES requirement_group(id) ON DELETE SET NULL
);

-- 5. Требования
CREATE TABLE requirement (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    path VARCHAR(500),
    depth INTEGER DEFAULT 0,
    requirement_group_id INTEGER REFERENCES requirement_group(id) ON DELETE SET NULL,
    parent_id INTEGER REFERENCES requirement(id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT check_requirement_type CHECK (type IN ('functional', 'non-functional', 'business'))
);

CREATE INDEX idx_requirement_project_id ON requirement(project_id);
CREATE INDEX idx_requirement_type ON requirement(type);
CREATE INDEX idx_requirement_is_deleted ON requirement(is_deleted);

-- 6. Контент требований
CREATE TABLE requirement_content (
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

-- 7. Workflow требований
CREATE TABLE requirement_workflow (
    id SERIAL PRIMARY KEY,
    requirement_content_id INTEGER NOT NULL REFERENCES requirement_content(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 3,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    prev_req_workflow_id INTEGER REFERENCES requirement_workflow(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_workflow_status CHECK (status IN ('draft', 'review', 'approved', 'rejected', 'deprecated')),
    CONSTRAINT check_workflow_priority CHECK (priority >= 1 AND priority <= 5)
);

CREATE INDEX idx_req_workflow_content_id ON requirement_workflow(requirement_content_id);
CREATE INDEX idx_req_workflow_status ON requirement_workflow(status);

-- 8. Зависимости между требованиями
CREATE TABLE requirement_dependence (
    id SERIAL PRIMARY KEY,
    source_requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    target_requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT check_dependence_type CHECK (dependency_type IN ('blocks', 'depends_on', 'related_to', 'derived_from', 'conflicts_with'))
);

CREATE INDEX idx_requirement_dependence_source ON requirement_dependence(source_requirement_id);
CREATE INDEX idx_requirement_dependence_target ON requirement_dependence(target_requirement_id);

-- Вставка тестовых данных
INSERT INTO role (code, name, description) VALUES
('admin', 'Администратор', 'Полный доступ'),
('analyst', 'Аналитик', 'Работа с требованиями');

INSERT INTO "user" (external_id, login, full_name, email, global_role_id) VALUES
('ldap://admin', 'admin', 'Администратор', 'admin@arms.local', 1);

INSERT INTO project (name, description, status, created_by_user_id) VALUES
('ARMS Project', 'Система управления требованиями', 'active', 1);

