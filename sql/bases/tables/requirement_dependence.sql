-- Таблица зависимостей между требованиями (переименована из dependency)
CREATE TABLE IF NOT EXISTS requirement_dependence (
    id SERIAL PRIMARY KEY,
    source_requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    target_requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    strength INTEGER DEFAULT 3 CHECK (strength BETWEEN 1 AND 5),
    description TEXT,
    source_requirement_group_id INTEGER REFERENCES requirement_group(id) ON DELETE SET NULL,
    target_requirement_group_id INTEGER REFERENCES requirement_group(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT check_dependence_type CHECK (type IN ('blocks', 'depends_on', 'related_to', 'duplicates', 'refines')),
    CONSTRAINT check_no_self_dependence CHECK (source_requirement_id != target_requirement_id)
);

CREATE INDEX idx_requirement_dependence_source ON requirement_dependence(source_requirement_id);
CREATE INDEX idx_requirement_dependence_target ON requirement_dependence(target_requirement_id);
CREATE INDEX idx_requirement_dependence_type ON requirement_dependence(type);

