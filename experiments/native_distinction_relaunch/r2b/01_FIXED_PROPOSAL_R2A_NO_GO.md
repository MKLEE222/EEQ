# R2-A No-Go Under Fixed Candidate Root-Update Semantics

Date: 2026-10-09.
Status: a SIMPLE STRUCTURAL LEMMA, not a novelty theorem and NOT a statement
about arbitrary TUF, Kubernetes, or dynamic evidence-acquisition actions.

## Precisely restricted machine

Fix a complete candidate-action alphabet A. For each a in A a candidate
root source c(a) is fixed independent of the initial native state.

For a valid, supported, deterministic root-update attempt in the registered
scope, observations are only ACCEPT or REJECT and transitions are:

- ACCEPT: T(s,a) = c(a) (the trusted root becomes the submitted candidate);
- REJECT: T(s,a) = s (the trusted root remains unchanged).

This is the scoped action model tested with tuf-js updateRoot in R1c.
It is NOT a statement about trust expiry, timestamps, network availability,
target-role verification, API publication, different actors, asynchronous
observations, or an action that rewrites a source external to root-update.

Let O(s,a) be the ACCEPT/REJECT observation for action a.

## Lemma (current-observation equivalence is a congruence)

If for two states s,t:

  forall a in A, O(s,a) = O(t,a),

then for EVERY action word w in A*, the resulting complete sequences of
ACCEPT/REJECT observations from s and t coincide.

Proof by induction on the word length:
- Empty word: no observations; equal trivially.
- Let w = a v. Their first observations agree by hypothesis.
  If both ACCEPT, both successor trusted roots equal the SAME candidate
  c(a); hence all subsequent observations agree.
  If both REJECT, successor states remain s and t, which still satisfy
  the hypothesis, so induct on v.
- No other registered outcome exists under the assumption.

Therefore a TUF-R2-A pair that is identical under ALL currently registered
fixed-root proposal actions but necessarily diverges on a future word using
those same fixed candidates **cannot exist**.

This result does not require 8 states or horizon 2. It is an elementary
fact of the fixed-reset-or-self-loop transition model, not a new EEQ
operator theorem.

## What the existing native carrier adds

The old pinned production R1 TUF carrier is an even stronger negative:
all eight states are currently separable by at least one of its seven
registered fixed source proposals (R1e 8/8 singleton classes at r=0).
Thus it has neither a nontrivial B quotient nor an A latent distinction in
the already-registered domain.

## Consequences for research integrity

1. Do NOT artificially choose only one currently uninformative candidate
   after observing the full action table, then call a future divergence
   "new native A evidence."
2. Do NOT introduce a simulated source-publication/key-revocation action
   into the native action alphabet without an actual native mechanism that
   executes and records the state change.
3. The forthcoming controlled targets-key R2-B experiment can demonstrate
   lawful contract-relative merging, but does NOT refute this lemma:
   targets signing is a different claim family.
4. Search for R2-A on a native system with a genuinely action-conditioned
   change in support or qualification, e.g., Kubernetes VAP/binding updates
   with auditable policy mutation and request admission.
5. A positive R2-B native pair is not H3 novelty: the predeclared fair B9
   and a classical quotient are expected to tie at the registered task.

Scientific disposition for fixed-candidate root-update A:
**NO_GO_IN_REGISTERED_MACHINE_CLASS**, not "EEQ failed" and not
"future-action distinctions are impossible in general".
