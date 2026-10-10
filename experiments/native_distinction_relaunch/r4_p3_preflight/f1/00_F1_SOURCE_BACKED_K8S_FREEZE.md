# EEQ P3-B F1: Source-backed bounded Kubernetes closure falsification, preregistered

Date: 2026-10-10
New isolated branch: `eeq-p3b-f1-source-backed-audit-20261010`
Parent commit: `9c3302f0017573e9221a97785e3ffdb4e8feec84`
**Status: F1 PRE-IMPLEMENTATION FREEZE. Development reuse, not new native scoring, not P3 human/independent method trial.**

## Prior constraints
- Immutable original G4 protocol: `c15b212ad0c2be3856a03d38802aaffa628aefd1`; v1 G5=285; G6 global C1 under independent dispute; X.509 7/7 chronological caveat; G8 incomplete; no old result, original main, holdout or B10 core modified.
- F0 20/20 synthetic CI success run `37950352399`, code SHA `9c3302f` means **ONLY** `SYNTHETIC_GUARD_DIAGNOSTIC_ONLY`.
- F1 reuses **already scored** Kubernetes R2A source & native development evidence, without new cluster/native calls, without new G5/G8 cases, and without prior outcome features in the new extractor.
- Source-only R2A predictions and frozen native measurements were independently run before F1. This is retrospective to R2A, not prospective held-out validation; F1 registration is prospective only relative to the *new F1 implementation*.

## Immutable input fixtures and evidence class

Original source files in `experiments/native_distinction_relaunch/r2a/sources`, at parent commit, pinned by Git blob SHA1 (verified from exact bytes, including whitespace):
| File | Git blob SHA |
|---|---|
| policy.json | bf5b9f7a99e3cbd11713352e83be2a4e345a03fc |
| binding-a.json | 4dff26ab237254d7de45c2008d68dd03800b4346 |
| binding-b.json | d78be9f01690f4c65b8bff78069dc1ed2aecdd2d |
| namespace-before.json | b998f3e99380e8a04e34629048724726a591dbc1 |
| pod-flux.json | de2f62f788726ed90d5f76889fb33126850d770b |
| pod-default.json | 2dce4b8e5e69b9333d63e24885f94e5639b2d51a |
| update-namespace-label.json | 778c7a043daa2e3c5048a6cd5ed27b4563133368 |

Archived independent R2A native record: Actions `37906692298`; artifact `11604423996`, ZIP SHA256 `1d644a8e98497d097a4b3b4e4354180bfff5bea144ccf89c2790b34bd43fc70c`. All 8 native outcomes are **prior development labels**, never unseen; new method must not load the archived scorer or these outcome labels when generating its source-derived model.

## Bounded grammar and source-to-dependency obligation

Exactly ONE ValidatingAdmissionPolicy with `failurePolicy=Fail`, registered Pod CREATE scope, one CEL predicate `object.spec.serviceAccountName != 'flux'`; ONE binding at a time, `Deny`, one `namespaceSelector.matchLabels` dictionary and NO `matchExpressions`, parameter source, or arbitrary CEL. Exactly one `r2a.mode:strict -> relaxed` namespace-label action; two Pod serviceAccount probes `flux` and `default`.

For a pair of decision histories on the **same registered source scope**, derive the entire registered namespace-key read set by inspecting ALL keys of `matchLabels` (not current truth values and not an externally supplied `complete:true` flag). Pin/validate policy, binding and Pod scopes. Compare the registered read-set values across current/after state; a change to any relevant value forces `REVERIFY_REQUIRED` even if current policy, binding and Pod bytes are unchanged.

This is a conservative *static* over-approximation of dependencies within the whitelisted single-binding grammar. It does NOT prove completeness for general K8s, other VAPs, admission webhooks, authorizer, CEL references, future actions, or source authenticity of an unobserved state. Any unregistered grammar/features must be `MODEL_UNSUPPORTED`, never silently omitted. Missing required source must be `SOURCE_UNAVAILABLE`, not native REJECT. Source SHA consistency and native update observation are provided only by the original archived R2A experiment.

Possible reuse status means **decision re-evaluation might be skipped**, not prior source/qualification/provenance certificate may be replayed unchanged; refreshing audit provenance is mandatory when upstream source identity or native revision changes. Not a native ACCEPT authorization.

## Fixed F1 primary *development diagnostic* matrix (N=4 paired cases)

Source labels AFTER update are obtained only from registered source update semantics; method may not use archived native outcomes.
| Pair | Registered selector | Pod | Expected F1 candidate verdict | Archived native pre -> post |
|---|---|---|---|---|
| A-flux | `r2a.team=tenant` | flux | REUSE_DECISION_ONLY | REJECT -> REJECT |
| A-default | `r2a.team=tenant` | default | REUSE_DECISION_ONLY | ACCEPT -> ACCEPT |
| B-flux | `r2a.team=tenant AND r2a.mode=strict` | flux | REVERIFY_REQUIRED | REJECT -> ACCEPT |
| B-default | `r2a.team=tenant AND r2a.mode=strict` | default | REVERIFY_REQUIRED | ACCEPT -> ACCEPT |

The pair-level expected classification has 2 eligible decision-reuse candidates, 2 revalidations, 0 unsafe reuse vs archived native, and 1 conservative extra revalidation (B-default). Do NOT call 2/4 an advantage over a fully informed B9, which may extract the same read set. A simplistic hash-only restriction that sees unchanged Binding/Pod/Policy but ignores namespace-label qualification would unsafely reuse B-flux; it is an **invalid diagnostic ablation**, not the strongest comparator.

Also frozen: original 8 archived development-native cell labels
`a/current/flux=REJECT, a/current/default=ACCEPT, b/current/flux=REJECT, b/current/default=ACCEPT, a/after/flux=REJECT, a/after/default=ACCEPT, b/after/flux=ACCEPT, b/after/default=ACCEPT`.
These are for *post-extractor tests only*; never part of the extractor input.

## Fixed F1 synthetic killer families (each failure retained)
- Remove `namespace-before.json` or action document -> `SOURCE_UNAVAILABLE`.
- Alter `matchLabels` to `matchExpressions` -> `MODEL_UNSUPPORTED`.
- Add `paramRef` to a binding or `paramKind` to policy -> `MODEL_UNSUPPORTED`.
- Change CEL grammar, validation count, matchRules, failurePolicy or enforcement action -> `MODEL_UNSUPPORTED`.
- Add a new selector `r2a.region=west` -> **registered grammar supports it only if full namespace map is present**; missing key is observed *absence*, not `SOURCE_UNAVAILABLE`, and may change binding truth. (This is a synthetic diagnostic, not native.)
- Change registered `r2a.team` between snapshots -> both pairs `REVERIFY_REQUIRED`.
- Change unrelated namespace metadata/labels, while selectors and read-set values unchanged -> `REUSE_DECISION_ONLY` (with provenance refresh).
- Contract/actor/action/horizon scope altered -> `MODEL_UNSUPPORTED`.
- Input file bytes fail original fixture Git-blob pins -> `MODEL_UNSUPPORTED` for a claimed *original-fixture validation*. Synthetic mutations must instead use an explicit `mutation_diagnostic` mode and never be counted as a native run.

## Novelty veto and required next steps
- Treat the F1 proof as trivial structural dependency induction for a **restricted program**; not a novel theorem, not new native policy semantics, and not automatic multi-family source-to-model compilation.
- Full-information B9 and conventional policy-specific rule evaluation are entitled to EXACT same source/read-set/code reuse; baseline on the F1 4-pair native carrier is expected to TIE.
- Compare provenance semiring/dependency tracking, incremental view maintenance, and native policy verification before any independent advantage claim.
- F1 can only authorize deeper adapter-validation research. **P3 independent maintainers, human time advantage, external transfer, and strong baseline superiority remain NOT ESTABLISHED.**
- Prescore denominator remains four paired retrospective-development contrasts, eight archived native label checks, and separately reported synthetic mutation tests. No outcome-driven case exclusion, no new original G5/G8 numbers, no primary P3 metric switch.
