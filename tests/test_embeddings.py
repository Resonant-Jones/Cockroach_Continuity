import pytest

from cockroach_continuity.embeddings import EMBEDDING_DIMENSION, vector_literal


def test_vector_literal_uses_frozen_dimension() -> None:
    embedding = [0.0] * EMBEDDING_DIMENSION
    embedding[0] = 1.0

    rendered = vector_literal(embedding)

    assert rendered.startswith("[1,")
    assert rendered.endswith("]")
    assert rendered.count(",") == EMBEDDING_DIMENSION - 1


def test_vector_literal_rejects_wrong_dimension() -> None:
    with pytest.raises(ValueError, match="dimension mismatch"):
        vector_literal([1.0, 0.0])
