"""Compile and verify claim-specific future qualification opportunity.

The component receives typed, partial evidence about an action-changing
system and builds the smallest claim-local action graph justified by that
evidence.  Its output is the future cost of making a required claim qualified
at the task endpoint, plus the opportunity erosion caused by each action.

The graph solver is elementary and intentionally replaceable by a POMDP/VOI
backend.  The research object is the compiler contract: conceptual continuity,
data/evidence bridges, consumer changes, recoverable locations, and irreversible
cuts remain distinct until the task claim licenses their composition.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import heapq
import re

from schema_history_lineage_ambiguity_v0 import (
    DDLVersionSnapshot,
    compile_schema_lineage_ambiguities,
)


@dataclass(frozen=True)
class CommitFilePatch:
    filename: str
    status: str
    patch: str
    previous_filename: str = ""


@dataclass(frozen=True)
class RepositoryCommitEvidence:
    repository: str
    commit_sha: str
    parent_sha: str
    committed_at: str
    message: str
    files: tuple[CommitFilePatch, ...]


@dataclass(frozen=True)
class EvidenceAtom:
    kind: str
    source: str
    detail: str


@dataclass(frozen=True)
class OpportunityState:
    name: str
    consumer_relation: str
    evidence_location: str
    claim_qualified: bool


@dataclass(frozen=True)
class OpportunityEdge:
    action: str
    source: str
    target: str
    cost: Fraction
    evidence_kind: str


@dataclass(frozen=True)
class QualificationOpportunityProblem:
    problem_id: str
    claim: str
    required_endpoint: str
    initial_state: str
    failure_loss: Fraction
    states: tuple[OpportunityState, ...]
    edges: tuple[OpportunityEdge, ...]


@dataclass(frozen=True)
class TypedOpportunitySeed:
    phase: str
    consumer_relation: str
    evidence_locations: tuple[str, ...]


@dataclass(frozen=True)
class TypedQualificationAction:
    name: str
    source_phase: str
    target_phase: str
    cost: Fraction
    evidence_kind: str
    require_locations: tuple[str, ...] = ()
    add_locations: tuple[str, ...] = ()
    remove_locations: tuple[str, ...] = ()
    set_consumer_relation: str = ""


@dataclass(frozen=True)
class StateOpportunity:
    state: str
    value: Fraction
    action: str
    qualification_reachable: bool


@dataclass(frozen=True)
class ActionOpportunityErosion:
    action: str
    source: str
    target: str
    erosion: Fraction


@dataclass(frozen=True)
class QualificationOpportunityCertificate:
    problem_id: str
    claim: str
    commit_sha: str
    removed_relation: str
    added_relation: str
    concept_continuity: tuple[EvidenceAtom, ...]
    data_bridges: tuple[EvidenceAtom, ...]
    consumer_switch: tuple[EvidenceAtom, ...]
    deployment_stage_identified: bool
    state_opportunities: tuple[StateOpportunity, ...]
    action_erosions: tuple[ActionOpportunityErosion, ...]


@dataclass(frozen=True)
class QualificationActionCandidate:
    name: str
    post_state: str
    immediate_cost: Fraction


@dataclass(frozen=True)
class QualificationActionEvaluation:
    action: str
    post_state: str
    immediate_cost: Fraction
    expected_qualification_cost: Fraction
    total_cost: Fraction


@dataclass(frozen=True)
class QualificationDecisionCertificate:
    problem_id: str
    future_claim_probability: Fraction
    evaluations: tuple[QualificationActionEvaluation, ...]
    qualification_aware_action: str
    current_objective_action: str
    current_objective_regret: Fraction


@dataclass(frozen=True)
class JointOpportunityState:
    name: str
    qualified_claims: tuple[str, ...]


@dataclass(frozen=True)
class ClaimSetDemand:
    claims: tuple[str, ...]
    probability: Fraction
    failure_loss: Fraction


@dataclass(frozen=True)
class JointQualificationOpportunityProblem:
    problem_id: str
    states: tuple[JointOpportunityState, ...]
    edges: tuple[OpportunityEdge, ...]


@dataclass(frozen=True)
class JointQualificationActionCandidate:
    name: str
    post_state: str
    immediate_cost: Fraction


@dataclass(frozen=True)
class ClaimSetOpportunity:
    claims: tuple[str, ...]
    probability: Fraction
    failure_loss: Fraction
    recovery_cost: Fraction


@dataclass(frozen=True)
class JointQualificationActionEvaluation:
    action: str
    post_state: str
    immediate_cost: Fraction
    claim_set_opportunities: tuple[ClaimSetOpportunity, ...]
    expected_qualification_cost: Fraction
    total_cost: Fraction


@dataclass(frozen=True)
class JointQualificationDecisionCertificate:
    problem_id: str
    demands: tuple[ClaimSetDemand, ...]
    evaluations: tuple[JointQualificationActionEvaluation, ...]
    qualification_aware_action: str
    current_objective_action: str
    current_objective_regret: Fraction


def solve_qualification_opportunity(
    problem: QualificationOpportunityProblem,
) -> tuple[StateOpportunity, ...]:
    states = {state.name: state for state in problem.states}
    if (
        not problem.problem_id
        or problem.initial_state not in states
        or problem.failure_loss <= 0
        or len(states) != len(problem.states)
    ):
        raise ValueError("invalid qualification opportunity problem")
    outgoing: dict[str, list[OpportunityEdge]] = {name: [] for name in states}
    for edge in problem.edges:
        if edge.source not in states or edge.target not in states or edge.cost < 0:
            raise ValueError("invalid opportunity edge")
        outgoing[edge.source].append(edge)

    values = {
        name: Fraction(0) if state.claim_qualified else problem.failure_loss
        for name, state in states.items()
    }
    actions = {
        name: "endpoint-qualified" if state.claim_qualified else "accept-failure"
        for name, state in states.items()
    }
    for _ in range(max(1, len(states))):
        changed = False
        for name, state in states.items():
            if state.claim_qualified:
                continue
            candidates = [(problem.failure_loss, "accept-failure")]
            candidates.extend(
                (edge.cost + values[edge.target], edge.action)
                for edge in outgoing[name]
            )
            value, action = min(candidates, key=lambda item: (item[0], item[1]))
            if value != values[name] or action != actions[name]:
                values[name], actions[name], changed = value, action, True
        if not changed:
            break
    reachable = {name: states[name].claim_qualified for name in states}
    for _ in range(max(1, len(states))):
        for name in states:
            reachable[name] = reachable[name] or any(
                reachable[edge.target] for edge in outgoing[name]
            )
    return tuple(
        StateOpportunity(name, values[name], actions[name], reachable[name])
        for name in sorted(states)
    )


def choose_qualification_action(
    problem: QualificationOpportunityProblem,
    candidates: tuple[QualificationActionCandidate, ...],
    future_claim_probability: Fraction,
) -> QualificationDecisionCertificate:
    """Choose an action using immediate cost plus future qualification cost.

    The probability is the registered chance that the claim will be required at
    the persistent endpoint.  A current-objective control sees the same actions
    and immediate costs while omitting that future qualification obligation.
    General POMDP or real-options solvers can reproduce this choice once given
    the same compiled post-action opportunity values.
    """
    if not candidates or not 0 <= future_claim_probability <= 1:
        raise ValueError("invalid qualification decision contract")
    values = {item.state: item.value for item in solve_qualification_opportunity(problem)}
    if any(candidate.post_state not in values or candidate.immediate_cost < 0 for candidate in candidates):
        raise ValueError("invalid qualification action candidate")
    evaluations = tuple(
        QualificationActionEvaluation(
            candidate.name,
            candidate.post_state,
            candidate.immediate_cost,
            future_claim_probability * values[candidate.post_state],
            candidate.immediate_cost + future_claim_probability * values[candidate.post_state],
        )
        for candidate in sorted(candidates, key=lambda item: item.name)
    )
    aware = min(evaluations, key=lambda item: (item.total_cost, item.action))
    current = min(evaluations, key=lambda item: (item.immediate_cost, item.action))
    return QualificationDecisionCertificate(
        problem.problem_id,
        future_claim_probability,
        evaluations,
        aware.action,
        current.action,
        current.total_cost - aware.total_cost,
    )


def verify_qualification_decision(
    problem: QualificationOpportunityProblem,
    candidates: tuple[QualificationActionCandidate, ...],
    certificate: QualificationDecisionCertificate,
) -> tuple[bool, str]:
    expected = choose_qualification_action(
        problem, candidates, certificate.future_claim_probability
    )
    if certificate != expected:
        return False, "qualification decision certificate mismatch"
    return True, "verified"


def _claim_set_opportunities(
    problem: JointQualificationOpportunityProblem,
    demand: ClaimSetDemand,
) -> dict[str, Fraction]:
    """Compute joint recovery cost without decomposing a demanded claim set."""
    states = {state.name: state for state in problem.states}
    if not states or len(states) != len(problem.states):
        raise ValueError("invalid joint qualification opportunity problem")
    if (
        not demand.claims
        or len(set(demand.claims)) != len(demand.claims)
        or not 0 <= demand.probability <= 1
        or demand.failure_loss <= 0
    ):
        raise ValueError("invalid claim-set demand")
    reverse: dict[str, list[tuple[str, Fraction]]] = {name: [] for name in states}
    for edge in problem.edges:
        if edge.source not in states or edge.target not in states or edge.cost < 0:
            raise ValueError("invalid joint opportunity edge")
        reverse[edge.target].append((edge.source, edge.cost))

    required = set(demand.claims)
    values = {name: demand.failure_loss for name in states}
    queue: list[tuple[Fraction, str]] = []
    for name, state in states.items():
        if required <= set(state.qualified_claims):
            values[name] = Fraction(0)
            heapq.heappush(queue, (Fraction(0), name))
    while queue:
        value, target = heapq.heappop(queue)
        if value != values[target]:
            continue
        for source, cost in reverse[target]:
            candidate = min(demand.failure_loss, value + cost)
            if candidate < values[source]:
                values[source] = candidate
                heapq.heappush(queue, (candidate, source))
    return values


def choose_joint_qualification_action(
    problem: JointQualificationOpportunityProblem,
    candidates: tuple[JointQualificationActionCandidate, ...],
    demands: tuple[ClaimSetDemand, ...],
) -> JointQualificationDecisionCertificate:
    """Choose from a joint claim-set demand distribution.

    A demand event may require several claims simultaneously.  Its recovery cost
    is solved on the shared action graph, so common evidence routes are paid once
    and dependencies encoded by qualified joint states remain intact.
    """
    if not problem.problem_id or not candidates or not demands:
        raise ValueError("invalid joint qualification decision contract")
    if sum((item.probability for item in demands), Fraction(0)) > 1:
        raise ValueError("claim-set demand probability exceeds one")
    if len({tuple(sorted(item.claims)) for item in demands}) != len(demands):
        raise ValueError("duplicate claim-set demand")
    states = {state.name for state in problem.states}
    if any(
        candidate.post_state not in states or candidate.immediate_cost < 0
        for candidate in candidates
    ):
        raise ValueError("invalid joint qualification action candidate")

    normalized_demands = tuple(
        sorted(
            (
                ClaimSetDemand(tuple(sorted(item.claims)), item.probability, item.failure_loss)
                for item in demands
            ),
            key=lambda item: item.claims,
        )
    )
    values_by_demand = {
        demand.claims: _claim_set_opportunities(problem, demand)
        for demand in normalized_demands
    }
    evaluations = []
    for candidate in sorted(candidates, key=lambda item: item.name):
        opportunities = tuple(
            ClaimSetOpportunity(
                demand.claims,
                demand.probability,
                demand.failure_loss,
                values_by_demand[demand.claims][candidate.post_state],
            )
            for demand in normalized_demands
        )
        expected = sum(
            (item.probability * item.recovery_cost for item in opportunities),
            Fraction(0),
        )
        evaluations.append(
            JointQualificationActionEvaluation(
                candidate.name,
                candidate.post_state,
                candidate.immediate_cost,
                opportunities,
                expected,
                candidate.immediate_cost + expected,
            )
        )
    evaluations_tuple = tuple(evaluations)
    aware = min(evaluations_tuple, key=lambda item: (item.total_cost, item.action))
    current = min(
        evaluations_tuple, key=lambda item: (item.immediate_cost, item.action)
    )
    return JointQualificationDecisionCertificate(
        problem.problem_id,
        normalized_demands,
        evaluations_tuple,
        aware.action,
        current.action,
        current.total_cost - aware.total_cost,
    )


def verify_joint_qualification_decision(
    problem: JointQualificationOpportunityProblem,
    candidates: tuple[JointQualificationActionCandidate, ...],
    certificate: JointQualificationDecisionCertificate,
) -> tuple[bool, str]:
    expected = choose_joint_qualification_action(
        problem, candidates, certificate.demands
    )
    if certificate != expected:
        return False, "joint qualification decision certificate mismatch"
    return True, "verified"


def compile_typed_opportunity_problem(
    problem_id: str,
    claim: str,
    required_endpoint: str,
    initial: TypedOpportunitySeed,
    actions: tuple[TypedQualificationAction, ...],
    failure_loss: Fraction,
) -> QualificationOpportunityProblem:
    """Expand a task graph from typed effects, without supplied answer states."""
    if not problem_id or not claim or not required_endpoint or failure_loss <= 0:
        raise ValueError("invalid typed opportunity contract")
    by_source: dict[str, list[TypedQualificationAction]] = {}
    for action in actions:
        if action.cost < 0 or not action.name or not action.source_phase or not action.target_phase:
            raise ValueError("invalid typed qualification action")
        by_source.setdefault(action.source_phase, []).append(action)

    reached: dict[str, TypedOpportunitySeed] = {initial.phase: initial}
    pending = [initial.phase]
    edges = []
    while pending:
        phase = pending.pop(0)
        state = reached[phase]
        locations = set(state.evidence_locations)
        for action in sorted(by_source.get(phase, ()), key=lambda item: item.name):
            if set(action.require_locations) - locations:
                continue
            next_locations = (locations - set(action.remove_locations)) | set(action.add_locations)
            target = TypedOpportunitySeed(
                action.target_phase,
                action.set_consumer_relation or state.consumer_relation,
                tuple(sorted(next_locations)),
            )
            if target.phase in reached and reached[target.phase] != target:
                raise ValueError("one phase names incompatible typed states")
            if target.phase not in reached:
                reached[target.phase] = target
                pending.append(target.phase)
            edges.append(
                OpportunityEdge(
                    action.name,
                    phase,
                    target.phase,
                    action.cost,
                    action.evidence_kind,
                )
            )
    states = tuple(
        OpportunityState(
            phase,
            state.consumer_relation,
            ",".join(state.evidence_locations) if state.evidence_locations else "destroyed",
            state.consumer_relation == required_endpoint
            and required_endpoint in state.evidence_locations,
        )
        for phase, state in sorted(reached.items())
    )
    return QualificationOpportunityProblem(
        problem_id,
        claim,
        required_endpoint,
        initial.phase,
        failure_loss,
        states,
        tuple(edges),
    )


def _erosions(
    problem: QualificationOpportunityProblem,
    opportunities: tuple[StateOpportunity, ...],
) -> tuple[ActionOpportunityErosion, ...]:
    values = {item.state: item.value for item in opportunities}
    return tuple(
        ActionOpportunityErosion(
            edge.action,
            edge.source,
            edge.target,
            values[edge.target] - values[edge.source],
        )
        for edge in sorted(problem.edges, key=lambda item: (item.source, item.action))
    )


def _added_text(files: tuple[CommitFilePatch, ...]) -> str:
    return "\n".join(
        line[1:]
        for file in files
        for line in file.patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def _data_bridges(
    files: tuple[CommitFilePatch, ...], old: str, new: str
) -> tuple[EvidenceAtom, ...]:
    text = _added_text(files)
    old_re, new_re = re.escape(old), re.escape(new)
    patterns = (
        ("rename-table", rf"RENAME\s+TABLE\s+`?{old_re}`?\s+TO\s+`?{new_re}`?"),
        ("alter-rename", rf"ALTER\s+TABLE\s+`?{old_re}`?\s+RENAME\s+(?:TO\s+)?`?{new_re}`?"),
        ("insert-select", rf"INSERT\s+INTO\s+`?{new_re}`?[\s\S]*?SELECT[\s\S]*?FROM\s+`?{old_re}`?"),
        ("create-as-select", rf"CREATE\s+TABLE\s+`?{new_re}`?[\s\S]*?AS\s+SELECT[\s\S]*?FROM\s+`?{old_re}`?"),
    )
    return tuple(
        EvidenceAtom(kind, "added commit lines", pattern)
        for kind, pattern in patterns
        if re.search(pattern, text, re.I)
    )


def _commit_atoms(
    files: tuple[CommitFilePatch, ...], old: str, new: str
) -> tuple[tuple[EvidenceAtom, ...], tuple[EvidenceAtom, ...]]:
    concept, consumers = [], []
    for file in files:
        if file.status == "renamed" and old in file.previous_filename and new in file.filename:
            concept.append(EvidenceAtom("configuration-rename", file.filename, file.previous_filename))
        if file.filename == "ext_tables.sql" and f"-CREATE TABLE {old}" in file.patch and f"+CREATE TABLE {new}" in file.patch:
            concept.append(EvidenceAtom("ddl-name-substitution", file.filename, f"{old} -> {new}"))
        if any(
            line.startswith("-") and not line.startswith("---") and old in line
            for line in file.patch.splitlines()
        ):
            consumers.append(EvidenceAtom("legacy-consumer-removed", file.filename, old))
        if (
            any(
                line.startswith("+") and not line.startswith("+++") and new in line
                for line in file.patch.splitlines()
            )
            or (file.status == "renamed" and new in file.filename)
        ):
            consumers.append(EvidenceAtom("target-consumer-added", file.filename, new))
    unique_consumers = {atom.kind: atom for atom in consumers}
    return tuple(concept), tuple(unique_consumers[k] for k in sorted(unique_consumers))


def compile_repository_qualification_opportunity(
    old_snapshot: DDLVersionSnapshot,
    new_snapshot: DDLVersionSnapshot,
    commit: RepositoryCommitEvidence,
) -> tuple[QualificationOpportunityProblem, QualificationOpportunityCertificate]:
    ambiguities = compile_schema_lineage_ambiguities(old_snapshot, new_snapshot)
    if len(ambiguities) != 1:
        raise ValueError("expected exactly one claim-local schema ambiguity")
    ambiguity = ambiguities[0]
    old, new = ambiguity.removed_table, ambiguity.added_table
    concept, consumers = _commit_atoms(commit.files, old, new)
    bridges = _data_bridges(commit.files, old, new)
    preserved = bool(bridges)

    safe_additions = (new,) if preserved else ()
    problem = compile_typed_opportunity_problem(
        "tev-label-row-availability",
        "registered legacy labels remain available to the Extbase consumer",
        new,
        TypedOpportunitySeed("pre-upgrade", old, (old,)),
        (
            TypedQualificationAction(
                "install-copy-bridge", "pre-upgrade", "qualified-from-pre",
                Fraction(1), "pre-action bridge", (old,), (new,), (), new,
            ),
            TypedQualificationAction(
                "apply-safe-schema-update", "pre-upgrade", "safe-schema-update",
                Fraction(0), "runtime schema compare", (), safe_additions, (), new,
            ),
            TypedQualificationAction(
                "recover-from-legacy", "safe-schema-update", "qualified-from-legacy",
                Fraction(2), "retained legacy rows", (old,), (new,), (), new,
            ),
            TypedQualificationAction(
                "prefix-unused-table", "safe-schema-update", "prefix-cleanup",
                Fraction(0), "runtime cleanup", (old,), (f"zzz_deleted_{old}",), (old,), new,
            ),
            TypedQualificationAction(
                "recover-from-prefix", "prefix-cleanup", "qualified-from-prefix",
                Fraction(3), "prefixed legacy rows", (f"zzz_deleted_{old}",), (new,), (), new,
            ),
            TypedQualificationAction(
                "drop-unused-table", "prefix-cleanup", "drop-cleanup",
                Fraction(0), "destructive cleanup", (f"zzz_deleted_{old}",), (), (f"zzz_deleted_{old}",), new,
            ),
        ),
        Fraction(10),
    )
    opportunities = solve_qualification_opportunity(problem)
    certificate = QualificationOpportunityCertificate(
        problem.problem_id,
        problem.claim,
        commit.commit_sha,
        old,
        new,
        concept,
        bridges,
        consumers,
        False,
        opportunities,
        _erosions(problem, opportunities),
    )
    return problem, certificate


def verify_qualification_opportunity(
    problem: QualificationOpportunityProblem,
    certificate: QualificationOpportunityCertificate,
) -> tuple[bool, str]:
    opportunities = solve_qualification_opportunity(problem)
    if certificate.state_opportunities != opportunities:
        return False, "qualification opportunity values mismatch"
    if certificate.action_erosions != _erosions(problem, opportunities):
        return False, "qualification opportunity erosion mismatch"
    if certificate.deployment_stage_identified:
        return False, "repository history does not identify the deployed stage"
    return True, "qualification opportunity certificate verified"


def build_tev_label_commit_evidence() -> RepositoryCommitEvidence:
    old, new = "tx_tevlabel_labels", "tx_tevlabel_domain_model_label"
    return RepositoryCommitEvidence(
        "https://github.com/3ev/tev_label",
        "44cfcc231f9a7fc72cacef6cca18cd027050351e",
        "44b7189f736ef94902cc8fb7ac729ac3026a9fd2",
        "2015-08-04T19:53:42Z",
        "Refactor to Extbase models",
        (
            CommitFilePatch("ext_tables.sql", "modified", f"-CREATE TABLE {old} (\n+CREATE TABLE {new} ("),
            CommitFilePatch(f"Configuration/TCA/{new}.php", "renamed", f"-'{old}'\n+'{new}'", f"Configuration/TCA/{old}.php"),
            CommitFilePatch("Classes/Utility/Label.php", "removed", f"-'{old}',\n-{old}"),
            CommitFilePatch("Classes/Domain/Repository/LabelRepository.php", "added", "+class LabelRepository extends Repository"),
        ),
    )
