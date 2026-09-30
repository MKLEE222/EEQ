"""Compile claim qualification across irreversible object lifecycle actions.

The component extracts public observation routes, lifecycle guards, returned
fields, and the lifecycle action's field write set from Java source.  It then
separates value persistence from post-action API availability: a field can stay
unchanged while its ordinary observation route becomes illegal, and another
route can preserve qualification for one claim only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from java_source_facts import analyze_java_source

from qualification_opportunity_compiler import (
    JointOpportunityState,
    JointQualificationActionCandidate,
    JointQualificationOpportunityProblem,
    OpportunityState,
    QualificationActionCandidate,
    QualificationOpportunityProblem,
)


@dataclass(frozen=True)
class JavaLifecycleMethod:
    name: str
    parameter_count: int
    return_field: str
    guarded: bool
    declared_exceptions: tuple[str, ...]
    written_fields: tuple[str, ...]


@dataclass(frozen=True)
class LifecycleRouteTransition:
    method: str
    parameter_count: int
    returned_field: str
    before_guarded: bool | None
    after_guarded: bool | None
    before_declared_exceptions: tuple[str, ...] | None
    after_declared_exceptions: tuple[str, ...] | None


@dataclass(frozen=True)
class LifecycleClaimQualification:
    field: str
    post_action_routes: tuple[str, ...]
    pre_action_snapshot_routes: tuple[str, ...]
    value_preserved_by_action: bool
    qualification: str
    opportunity: Fraction


@dataclass(frozen=True)
class LifecycleQualificationCertificate:
    instance_id: str
    class_name: str
    action_method: str
    action_written_fields: tuple[str, ...]
    action_preserved_fields: tuple[str, ...]
    route_transitions: tuple[LifecycleRouteTransition, ...]
    claims: tuple[LifecycleClaimQualification, ...]


def extract_java_lifecycle_methods(source: str, class_name: str = "*") -> tuple[JavaLifecycleMethod, ...]:
    """Direct observation routes and transitive may-write sets, under admission v2."""
    facts = analyze_java_source(source, class_name)
    return tuple(JavaLifecycleMethod(item['name'], item['arity'], item['return_field'],
        item['guarded'], tuple(item['exceptions']), tuple(item['writes']))
        for item in facts['methods'] if item['public'] and not item['static'])


def extract_java_lifecycle_fields(source: str, class_name: str = "*") -> tuple[str, ...]:
    return tuple(analyze_java_source(source, class_name)['fields'])


def compile_lifecycle_qualification(
    instance_id: str,
    class_name: str,
    before_source: str,
    after_source: str,
    claim_fields: tuple[str, ...],
    action_method: str = "close",
    capsule_cost: Fraction = Fraction(1),
    failure_loss: Fraction = Fraction(10),
) -> LifecycleQualificationCertificate:
    if not instance_id or not class_name or capsule_cost < 0 or failure_loss <= 0:
        raise ValueError("invalid lifecycle qualification contract")
    before = extract_java_lifecycle_methods(before_source, class_name)
    after = extract_java_lifecycle_methods(after_source, class_name)
    before_by_key = {(item.name, item.parameter_count): item for item in before}
    after_by_key = {(item.name, item.parameter_count): item for item in after}
    facts = analyze_java_source(after_source, class_name)
    action_facts = [item for item in facts['methods']
                    if item['name'] == action_method and item['arity'] == 0]
    if len(action_facts) != 1 or action_facts[0]['issues']:
        issues = '; '.join(action_facts[0]['issues']) if len(action_facts) == 1 else 'ambiguous action'
        raise ValueError('unresolved lifecycle action effects: ' + issues)
    action = after_by_key.get((action_method, 0))
    if action is None or not action.written_fields:
        raise ValueError("lifecycle action write set is unavailable")

    all_fields = set(extract_java_lifecycle_fields(after_source, class_name))
    unknown_claims = set(claim_fields) - all_fields
    if unknown_claims:
        raise ValueError("registered claim is not a declared instance field")
    preserved = tuple(sorted(all_fields - set(action.written_fields)))
    transitions = tuple(
        LifecycleRouteTransition(
            key[0],
            key[1],
            (after_by_key.get(key) or before_by_key[key]).return_field,
            before_by_key[key].guarded if key in before_by_key else None,
            after_by_key[key].guarded if key in after_by_key else None,
            before_by_key[key].declared_exceptions if key in before_by_key else None,
            after_by_key[key].declared_exceptions if key in after_by_key else None,
        )
        for key in sorted(set(before_by_key) | set(after_by_key))
        if key not in before_by_key
        or key not in after_by_key
        or before_by_key[key].guarded != after_by_key[key].guarded
        or before_by_key[key].declared_exceptions
        != after_by_key[key].declared_exceptions
    )

    claims = []
    for field in sorted(set(claim_fields)):
        post_routes = tuple(
            sorted(
                method.name
                for method in after
                if method.parameter_count == 0
                and method.return_field == field
                and not method.guarded
            )
        )
        snapshot_routes = tuple(
            sorted(
                method.name
                for method in before
                if method.parameter_count == 0
                and method.return_field == field
                and not method.guarded
            )
        )
        value_preserved = field in preserved
        if post_routes:
            qualification, opportunity = "qualified-after-action", Fraction(0)
        elif snapshot_routes and value_preserved:
            qualification, opportunity = "qualified-if-capsuled", capsule_cost
        else:
            qualification, opportunity = "unqualified-after-action", failure_loss
        claims.append(
            LifecycleClaimQualification(
                field,
                post_routes,
                snapshot_routes,
                value_preserved,
                qualification,
                opportunity,
            )
        )
    return LifecycleQualificationCertificate(
        instance_id,
        class_name,
        action_method,
        action.written_fields,
        preserved,
        transitions,
        tuple(claims),
    )


def compile_lifecycle_decision_problem(
    certificate: LifecycleQualificationCertificate,
    field: str,
    capsule_cost: Fraction = Fraction(1),
    failure_loss: Fraction = Fraction(10),
) -> tuple[QualificationOpportunityProblem, tuple[QualificationActionCandidate, ...]]:
    claim = next((item for item in certificate.claims if item.field == field), None)
    if claim is None:
        raise ValueError("unknown lifecycle claim field")
    post_qualified = bool(claim.post_action_routes)
    capsule_qualified = bool(
        claim.pre_action_snapshot_routes and claim.value_preserved_by_action
    )
    problem = QualificationOpportunityProblem(
        f"{certificate.instance_id}:{field}-after-{certificate.action_method}",
        f"{field} remains qualified after {certificate.action_method}",
        field,
        "before-action",
        failure_loss,
        (
            OpportunityState("before-action", "live", field, False),
            OpportunityState(
                "after-action", "closed", ",".join(claim.post_action_routes),
                post_qualified,
            ),
            OpportunityState(
                "after-action-with-capsule", "closed", f"{field}-capsule",
                capsule_qualified,
            ),
        ),
        (),
    )
    candidates = (
        QualificationActionCandidate(
            f"{certificate.action_method}-without-capsule",
            "after-action",
            Fraction(0),
        ),
        QualificationActionCandidate(
            f"snapshot-{field}-then-{certificate.action_method}",
            "after-action-with-capsule",
            capsule_cost,
        ),
    )
    return problem, candidates


def compile_lifecycle_joint_decision_problem(
    certificate: LifecycleQualificationCertificate,
    claim_fields: tuple[str, ...],
    capsule_cost: Fraction = Fraction(1),
) -> tuple[
    JointQualificationOpportunityProblem,
    tuple[JointQualificationActionCandidate, ...],
]:
    """Compile the joint post-lifecycle claim vector and capsule choices.

    Claims with a legal post-action route remain qualified directly. Claims
    whose values persist behind a closed route may be snapshotted before the
    lifecycle action. The current exact compiler enumerates distinct qualified
    sets after removing dominated duplicate states; this supplies the small-width
    oracle for later graph-factorized capsule selection.
    """
    if not claim_fields or capsule_cost < 0:
        raise ValueError("invalid lifecycle joint decision contract")
    by_field = {item.field: item for item in certificate.claims}
    fields = tuple(sorted(set(claim_fields)))
    if any(field not in by_field for field in fields):
        raise ValueError("unknown lifecycle claim field")

    direct = {
        field for field in fields if by_field[field].post_action_routes
    }
    capturable = tuple(
        field
        for field in fields
        if not by_field[field].post_action_routes
        and by_field[field].pre_action_snapshot_routes
        and by_field[field].value_preserved_by_action
    )
    states = []
    candidates = []
    for mask in range(1 << len(capturable)):
        captured = tuple(
            capturable[index]
            for index in range(len(capturable))
            if mask & (1 << index)
        )
        qualified = tuple(sorted(direct | set(captured)))
        state_name = "after-action:" + (
            "+".join(qualified) if qualified else "no-qualified-claim"
        )
        states.append(JointOpportunityState(state_name, qualified))
        if captured:
            action_name = (
                "snapshot-" + "+".join(captured) + f"-then-{certificate.action_method}"
            )
        else:
            action_name = f"{certificate.action_method}-without-capsule"
        candidates.append(
            JointQualificationActionCandidate(
                action_name, state_name, capsule_cost * len(captured)
            )
        )
    return (
        JointQualificationOpportunityProblem(
            f"{certificate.instance_id}:joint-after-{certificate.action_method}",
            tuple(states),
            (),
        ),
        tuple(candidates),
    )


def verify_lifecycle_qualification(
    before_source: str,
    after_source: str,
    certificate: LifecycleQualificationCertificate,
) -> tuple[bool, str]:
    expected = compile_lifecycle_qualification(
        certificate.instance_id,
        certificate.class_name,
        before_source,
        after_source,
        tuple(item.field for item in certificate.claims),
        certificate.action_method,
    )
    if certificate != expected:
        return False, "lifecycle qualification certificate mismatch"
    return True, "certificate consistency verified; native validation is separate"
