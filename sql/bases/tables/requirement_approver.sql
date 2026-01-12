-- Таблица утверждающих требования
CREATE TABLE IF NOT EXISTS requirement_approver (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    CONSTRAINT check_approver_action CHECK (action IN ('approve', 'reject', 'review'))
);

CREATE INDEX idx_requirement_approver_requirement ON requirement_approver(requirement_id);
CREATE INDEX idx_requirement_approver_role ON requirement_approver(role_id);

