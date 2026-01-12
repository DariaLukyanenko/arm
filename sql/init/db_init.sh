#!/bin/bash
set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[ARMS DB Init] Starting minimal database initialization...${NC}"

# Создаем схему и пользователей
echo -e "${YELLOW}[1/3] Creating schema and users...${NC}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Создаем схему
    DROP SCHEMA IF EXISTS ${POSTGRES_SCHEMA} CASCADE;
    CREATE SCHEMA ${POSTGRES_SCHEMA};
    
    -- Создаем пользователей если не существуют
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_APP_USER}') THEN
            CREATE USER ${POSTGRES_APP_USER} WITH PASSWORD '${POSTGRES_APP_PASSWORD}';
        END IF;
    END\$\$;
    
    -- Выдаем права
    GRANT USAGE ON SCHEMA ${POSTGRES_SCHEMA} TO ${POSTGRES_APP_USER};
    ALTER DATABASE ${POSTGRES_DB} SET search_path TO ${POSTGRES_SCHEMA}, public;
EOSQL

# Создаем таблицы
echo -e "${YELLOW}[2/3] Creating minimal tables for requirements, dependencies, reports...${NC}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SET search_path TO ${POSTGRES_SCHEMA};
    
    -- Роли
    CREATE TABLE role (
        id SERIAL PRIMARY KEY,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT
    );
    
    -- Пользователи (без person, с external_id)
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
    
    -- Проекты
    CREATE TABLE project (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by_user_id INTEGER NOT NULL
    );
    
    -- Группы требований
    CREATE TABLE requirement_group (
        id SERIAL PRIMARY KEY,
        project_id INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description TEXT
    );
    
    -- Требования
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
    
    -- Контент требований
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
    
    -- Workflow требований
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
    
    -- Зависимости между требованиями
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
EOSQL

# Вставляем тестовые данные
echo -e "${YELLOW}[3/3] Inserting test data...${NC}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SET search_path TO ${POSTGRES_SCHEMA};
    
    -- Роли
    INSERT INTO role (code, name, description) VALUES
    ('admin', 'Администратор', 'Полный доступ'),
    ('analyst', 'Аналитик', 'Работа с требованиями');
    
    -- Пользователи
    INSERT INTO "user" (external_id, login, full_name, email, global_role_id) VALUES
    ('ldap://admin', 'admin', 'Администратор', 'admin@arms.local', 1);
    
    -- Проекты
    INSERT INTO project (name, description, status, created_by_user_id) VALUES
    ('ARMS Project', 'Система управления требованиями', 'active', 1);
    
    -- Выдаем права приложению
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${POSTGRES_SCHEMA} TO ${POSTGRES_APP_USER};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA ${POSTGRES_SCHEMA} TO ${POSTGRES_APP_USER};
    
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRES_SCHEMA} GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${POSTGRES_APP_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRES_SCHEMA} GRANT ALL ON SEQUENCES TO ${POSTGRES_APP_USER};
EOSQL

echo -e "${GREEN}[ARMS DB Init] Initialization completed!${NC}"
echo -e "${GREEN}Created: role, user, project, requirement_group, requirement, requirement_content, requirement_workflow, requirement_dependence${NC}"
