"""
SQLAlchemy модели для требований и связанных сущностей (обновленные под схему БД)
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.session import Base


class Permission(Base):
    __tablename__ = "permission"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)


class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    permissions = relationship("RolePermission", back_populates="role")


class RolePermission(Base):
    __tablename__ = "role_permission"
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
        {"schema": "arms_schema"}
    )

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("arms_schema.role.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("arms_schema.permission.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    role = relationship("Role", back_populates="permissions")


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(500))
    email = Column(String(255))
    global_role_id = Column(Integer, ForeignKey("arms_schema.role.id", ondelete="SET NULL"))
    status = Column(String(50), nullable=False, default="active")
    datetime_created = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    global_role = relationship("Role", foreign_keys=[global_role_id])
    project_roles = relationship("UserProjectRole", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "project"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, nullable=False)

    # Relationships
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    requirement_groups = relationship("RequirementGroup", back_populates="project", cascade="all, delete-orphan")


class UserProjectRole(Base):
    __tablename__ = "user_project_role"
    __table_args__ = (
        UniqueConstraint('user_id', 'project_id', 'role_id', name='uq_user_project_role'),
        {"schema": "arms_schema"}
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("arms_schema.project.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("arms_schema.role.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="project_roles")


class RequirementGroup(Base):
    __tablename__ = "requirement_group"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("arms_schema.project.id", ondelete="CASCADE"), nullable=False)
    original_req_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="requirement_groups")


class Requirement(Base):
    __tablename__ = "requirement"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("arms_schema.project.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, nullable=False)
    path = Column(String(500))
    depth = Column(Integer, default=0)
    requirement_group_id = Column(Integer)
    parent_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="SET NULL"))
    is_deleted = Column(Boolean, default=False)

    # Relationships
    project = relationship("Project", back_populates="requirements")
    parent = relationship("Requirement", remote_side=[id], backref="children")
    contents = relationship("RequirementContent", back_populates="requirement", cascade="all, delete-orphan")
    users = relationship("RequirementUser", back_populates="requirement", cascade="all, delete-orphan")
    approvers = relationship("RequirementApprover", back_populates="requirement", cascade="all, delete-orphan")
    dependencies_out = relationship(
        "RequirementDependence",
        foreign_keys="RequirementDependence.source_requirement_id",
        back_populates="source_requirement",
        cascade="all, delete-orphan"
    )
    dependencies_in = relationship(
        "RequirementDependence",
        foreign_keys="RequirementDependence.target_requirement_id",
        back_populates="target_requirement",
        cascade="all, delete-orphan"
    )
    test_coverage = relationship("ReqTestCaseCoverage", back_populates="requirement", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="requirement", cascade="all, delete-orphan")


class RequirementUser(Base):
    __tablename__ = "requirement_user"
    __table_args__ = (
        UniqueConstraint('requirement_id', 'user_id', name='uq_requirement_user'),
        {"schema": "arms_schema"}
    )

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="users")


class RequirementApprover(Base):
    __tablename__ = "requirement_approver"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("arms_schema.role.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    requirement_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="approvers")


class RequirementContent(Base):
    __tablename__ = "requirement_content"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"), nullable=False)
    development_basis = Column(Text)
    development_purpose = Column(Text)
    description_text = Column(Text, nullable=False)
    acceptance_criteria = Column(Text)
    document_requires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, nullable=False)
    prev_req_content_id = Column(Integer, ForeignKey("arms_schema.requirement_content.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="contents")
    workflows = relationship("RequirementWorkflow", back_populates="content", cascade="all, delete-orphan")
    previous_version = relationship("RequirementContent", remote_side=[id])
    history_records = relationship("ReqContentHistory", back_populates="content")


class ReqContentHistory(Base):
    __tablename__ = "req_content_history"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    prev_req_content_id = Column(Integer, ForeignKey("arms_schema.requirement_content.id", ondelete="SET NULL"))
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False)

    # Relationships
    content = relationship("RequirementContent", back_populates="history_records")


class RequirementWorkflow(Base):
    __tablename__ = "requirement_workflow"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    requirement_content_id = Column(
        Integer,
        ForeignKey("arms_schema.requirement_content.id", ondelete="CASCADE"),
        nullable=False
    )
    priority = Column(Integer, default=3)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, nullable=False)
    prev_req_workflow_id = Column(Integer, ForeignKey("arms_schema.requirement_workflow.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)

    # Relationships
    content = relationship("RequirementContent", back_populates="workflows")
    previous_version = relationship("RequirementWorkflow", remote_side=[id])
    history_records = relationship("ReqWorkflowHistory", back_populates="workflow")


class ReqWorkflowHistory(Base):
    __tablename__ = "req_workflow_history"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    prev_req_workflow_id = Column(Integer, ForeignKey("arms_schema.requirement_workflow.id", ondelete="SET NULL"))
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False)

    # Relationships
    workflow = relationship("RequirementWorkflow", back_populates="history_records")


class RequirementDependence(Base):
    __tablename__ = "requirement_dependence"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    source_requirement_id = Column(
        Integer,
        ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"),
        nullable=False
    )
    target_requirement_id = Column(
        Integer,
        ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"),
        nullable=False
    )
    dependency_type = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    source_requirement = relationship("Requirement", foreign_keys=[source_requirement_id], back_populates="dependencies_out")
    target_requirement = relationship("Requirement", foreign_keys=[target_requirement_id], back_populates="dependencies_in")
    history_records = relationship("ReqDependenceHistory", back_populates="dependence")


class ReqDependenceHistory(Base):
    __tablename__ = "req_dependence_history"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    prev_req_dependence_id = Column(Integer, ForeignKey("arms_schema.requirement_dependence.id", ondelete="SET NULL"))
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dependence = relationship("RequirementDependence", back_populates="history_records")


class ReqTestCaseCoverage(Base):
    __tablename__ = "req_test_case_coverage"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    test_case_version_id = Column(String(255), nullable=False)
    requirement_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    test_case_status = Column(String(50), nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="test_coverage")


class Discussion(Base):
    __tablename__ = "discussion"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("arms_schema.requirement.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="discussions")
    comments = relationship("Comment", back_populates="discussion", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = {"schema": "arms_schema"}

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("arms_schema.discussion.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("arms_schema.user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text, nullable=False)

    # Relationships
    discussion = relationship("Discussion", back_populates="comments")
