from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Protocol

EMBEDDING_DIMENSION = 1024
DEFAULT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> tuple[float, ...]: ...


class BedrockTitanEmbeddingProvider:
    """Amazon Titan Text Embeddings V2 adapter with an injected Bedrock client."""

    def __init__(
        self,
        *,
        client: Any,
        model_id: str = DEFAULT_EMBEDDING_MODEL_ID,
        dimensions: int = EMBEDDING_DIMENSION,
    ) -> None:
        if dimensions != EMBEDDING_DIMENSION:
            raise ValueError(f"hackathon baseline requires {EMBEDDING_DIMENSION} dimensions")
        self._client = client
        self._model_id = model_id
        self._dimensions = dimensions

    def embed(self, text: str) -> tuple[float, ...]:
        normalized = text.strip()
        if not normalized:
            raise ValueError("embedding text must not be empty")

        response = self._client.invoke_model(
            modelId=self._model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "inputText": normalized,
                    "dimensions": self._dimensions,
                    "normalize": True,
                    "embeddingTypes": ["float"],
                }
            ),
        )
        payload = json.loads(response["body"].read())
        raw_embedding = payload.get("embedding")
        if not isinstance(raw_embedding, list):
            raise RuntimeError("embedding provider returned no float embedding")
        embedding = tuple(float(value) for value in raw_embedding)
        _validate_embedding(embedding)
        return embedding


def _validate_embedding(embedding: Sequence[float]) -> None:
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {len(embedding)}"
        )


def vector_literal(embedding: Sequence[float]) -> str:
    _validate_embedding(embedding)
    return "[" + ",".join(format(float(value), ".9g") for value in embedding) + "]"
