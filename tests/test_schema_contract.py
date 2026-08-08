from cockroach_continuity.models import Base


def test_canonical_table_set_is_present() -> None:
    assert set(Base.metadata.tables) == {
        "projects",
        "sessions",
        "project_events",
        "execution_attempts",
        "memory_candidates",
        "memory_assertions",
        "approval_decisions",
        "evidence_links",
        "retrieval_traces",
        "continuity_snapshots",
        "operation_receipts",
    }


def test_event_attempt_identity_constraint_exists() -> None:
    table = Base.metadata.tables["execution_attempts"]
    names = {constraint.name for constraint in table.constraints}
    assert "uq_attempt_event_number" in names


def test_operation_idempotency_constraint_exists() -> None:
    table = Base.metadata.tables["operation_receipts"]
    names = {constraint.name for constraint in table.constraints}
    assert "uq_operation_idempotency" in names


def test_assertion_version_constraint_exists() -> None:
    table = Base.metadata.tables["memory_assertions"]
    names = {constraint.name for constraint in table.constraints}
    assert "uq_assertion_version" in names
