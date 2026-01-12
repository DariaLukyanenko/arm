-- Таблица покрытия требований тестами (переименована)
CREATE TABLE IF NOT EXISTS req_test_case_coverage (
    id SERIAL PRIMARY KEY,
    test_case_version_id VARCHAR(255) NOT NULL,
    requirement_id INTEGER NOT NULL REFERENCES requirement(id) ON DELETE CASCADE,
    created_by_user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    test_case_status VARCHAR(50) NOT NULL,
    CONSTRAINT check_test_case_status CHECK (test_case_status IN ('passed', 'failed', 'blocked', 'not_executed'))
);

CREATE INDEX idx_req_test_case_coverage_requirement ON req_test_case_coverage(requirement_id);
CREATE INDEX idx_req_test_case_coverage_status ON req_test_case_coverage(test_case_status);
CREATE INDEX idx_req_test_case_coverage_test_case ON req_test_case_coverage(test_case_version_id);

