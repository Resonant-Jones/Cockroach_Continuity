import pytest

from cockroach_continuity.candidates import _parse_proposals


def test_parse_candidate_payload() -> None:
    proposals = _parse_proposals(
        {
            "candidates": [
                {
                    "kind": "decision",
                    "statement": "Use CockroachDB as canonical continuity storage.",
                    "confidence": 0.98,
                    "sensitivity": "project",
                }
            ]
        }
    )

    assert len(proposals) == 1
    assert proposals[0].kind == "decision"
    assert proposals[0].confidence == 0.98


def test_rejects_unknown_candidate_kind() -> None:
    with pytest.raises(ValueError, match="unsupported candidate kind"):
        _parse_proposals(
            {
                "candidates": [
                    {
                        "kind": "personality_trait",
                        "statement": "User prefers dark mode.",
                        "sensitivity": "private",
                    }
                ]
            }
        )


def test_rejects_confidence_outside_unit_interval() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        _parse_proposals(
            {
                "candidates": [
                    {
                        "kind": "constraint",
                        "statement": "Stay within the hackathon vertical slice.",
                        "confidence": 1.2,
                        "sensitivity": "project",
                    }
                ]
            }
        )
