"""Project-neutral prospective wrapper with versioned Java source admission."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import re

from lifecycle_qualification_compiler import compile_lifecycle_qualification


@dataclass(frozen=True)
class JavaLifecycleEpisode:
    episode_id: str
    repository: str
    parent_commit: str
    action_commit: str
    class_name: str
    claim_field: str
    action_method: str
    before_source: str
    after_source: str


@dataclass(frozen=True)
class JavaLifecycleProspective:
    episode_id: str
    evidence_digest: str
    status: str
    selected_action: str
    qualification: str
    value_preserved: bool
    pre_action_routes: tuple[str, ...]
    post_action_routes: tuple[str, ...]
    unsupported_reason: str


_UNSUPPORTED = (
    re.compile(r"\b(invoke|invokeExact)\s*\("),
    re.compile(r"\bClass\.forName\s*\("),
    re.compile(r"\bProxy\.newProxyInstance\s*\("),
)


def _digest(episode: JavaLifecycleEpisode) -> str:
    payload = "\0".join(
        (
            "java-admission-v2",
            episode.episode_id,
            episode.repository,
            episode.parent_commit,
            episode.action_commit,
            episode.class_name,
            episode.claim_field,
            episode.action_method,
            episode.before_source,
            episode.after_source,
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def compile_java_lifecycle_prospectively(
    episode: JavaLifecycleEpisode,
) -> JavaLifecycleProspective:
    digest = _digest(episode)
    if any(pattern.search(episode.after_source) for pattern in _UNSUPPORTED):
        return JavaLifecycleProspective(
            episode.episode_id, digest, "unidentified", "withhold",
            "unsupported-dynamic-dispatch", False, (), (),
            "reflection or dynamic proxy crosses the frozen source grammar",
        )
    try:
        certificate = compile_lifecycle_qualification(
            episode.episode_id,
            episode.class_name,
            episode.before_source,
            episode.after_source,
            (episode.claim_field,),
            action_method=episode.action_method,
            capsule_cost=Fraction(1),
            failure_loss=Fraction(10),
        )
    except ValueError as exc:
        return JavaLifecycleProspective(
            episode.episode_id, digest, "unidentified", "withhold",
            "unsupported-source-contract", False, (), (), str(exc),
        )
    claim = certificate.claims[0]
    if claim.post_action_routes:
        status, action = "licensed-update", episode.action_method
    elif claim.pre_action_snapshot_routes and claim.value_preserved_by_action:
        status, action = "licensed-update", f"snapshot-{episode.claim_field}-then-{episode.action_method}"
    else:
        status, action = "withhold", "withhold"
    return JavaLifecycleProspective(
        episode.episode_id,
        digest,
        status,
        action,
        claim.qualification,
        claim.value_preserved_by_action,
        claim.pre_action_snapshot_routes,
        claim.post_action_routes,
        "",
    )


def verify_java_lifecycle_prospective(
    episode: JavaLifecycleEpisode,
    certificate: JavaLifecycleProspective,
) -> tuple[bool, str]:
    # Consistency only: native replay uses a separate execution path.
    expected = compile_java_lifecycle_prospectively(episode)
    if expected != certificate:
        return False, "Java lifecycle prospective certificate mismatch"
    return True, "Java certificate consistency verified; not independent native validation"
