import math

from google import genai
from google.genai import types

from app.config import settings


def get_embedding_client() -> genai.Client | None:
    if not settings.GEMINI_API_KEY:
        return None
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embed_texts(texts: list[str]) -> list[list[float] | None]:
    if not texts:
        return []

    client = get_embedding_client()
    if client is None:
        return [None for _ in texts]

    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=settings.EMBEDDING_DIMENSIONS),
    )

    embeddings = response.embeddings or []
    result: list[list[float] | None] = []
    for embedding in embeddings:
        values = getattr(embedding, "values", None)
        if values is None:
            result.append(None)
            continue
        # Only the model's native (3072-dim) output is pre-normalized; any other
        # output_dimensionality requires normalizing manually for cosine distance to be meaningful.
        result.append(_normalize([float(value) for value in values]))

    if len(result) < len(texts):
        result.extend([None] * (len(texts) - len(result)))

    return result
