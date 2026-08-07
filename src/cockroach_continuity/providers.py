from __future__ import annotations

from typing import Any

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]

from cockroach_continuity.candidates import BedrockCandidateExtractor
from cockroach_continuity.config import Settings, get_settings
from cockroach_continuity.embeddings import BedrockTitanEmbeddingProvider


def build_bedrock_client(settings: Settings | None = None) -> Any:
    resolved = settings or get_settings()
    return boto3.client(
        "bedrock-runtime",
        region_name=resolved.aws_region,
        config=Config(
            connect_timeout=10,
            read_timeout=120,
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )


def build_candidate_extractor(settings: Settings | None = None) -> BedrockCandidateExtractor:
    resolved = settings or get_settings()
    return BedrockCandidateExtractor(
        client=build_bedrock_client(resolved),
        model_id=resolved.candidate_model_id,
    )


def build_embedding_provider(settings: Settings | None = None) -> BedrockTitanEmbeddingProvider:
    resolved = settings or get_settings()
    return BedrockTitanEmbeddingProvider(
        client=build_bedrock_client(resolved),
        model_id=resolved.embedding_model_id,
    )
