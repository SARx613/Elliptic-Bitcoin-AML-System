"""
Utilities to relate SNAP node features to job title embeddings.

The idea is to project the high-dimensional, sparse-like SNAP feature vectors
into the same dimensionality as the job embeddings produced by the
SentenceTransformer model used in ``scripts/load_jobs.py``.

This gives each :User a dense ``embedding`` vector that can be compared
directly (via cosine similarity) to ``Job.embedding``.
"""

from __future__ import annotations

from typing import Iterable, List

import numpy as np

# Dimensionality of the job embeddings produced by
# sentence-transformers/all-MiniLM-L6-v2
JOB_EMBED_DIM = 384


def project_features_to_embedding(
    features: Iterable[float],
    dim: int = JOB_EMBED_DIM,
) -> List[float]:
    """
    Convert a SNAP feature vector into a dense embedding with the same
    length as the job title embeddings.

    Implementation details:
    - Convert the iterable to a numpy array
    - Apply L2 normalization (if possible)
    - If vector is longer than ``dim``, keep only the first ``dim`` values
    - If shorter, pad with zeros

    Args:
        features: Iterable of float values representing SNAP features.
        dim: Target dimension for the embedding (default: JOB_EMBED_DIM).

    Returns:
        List of floats representing the normalized embedding vector.
    """
    vec = np.asarray(list(features), dtype=float)

    if vec.size == 0:
        return [0.0] * dim

    # L2 normalization to remove scale effects
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    if vec.size >= dim:
        return vec[:dim].tolist()

    padded = np.zeros(dim, dtype=float)
    padded[: vec.size] = vec
    return padded.tolist()

