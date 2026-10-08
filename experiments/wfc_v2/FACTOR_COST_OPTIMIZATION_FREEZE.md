# WFC v2 factorized storage hypothesis — frozen after first synthetic pilot

This is an openly post-pilot development optimization, not a previously
unseen holdout. The original v2 source and first CI artifact remain evidence.
No G4 B10, G4 protocol, X.509, or in-toto outcome is modified.

The first v2 controlled synthetic pilot:
- 15/15 unit tests; small exhaustive 120/120 state pairs;
- toy legal action sets: current-only 5/7 versus bounded quotient 7/7;
- six-axis 15 rows, 5 warmups and 30 measured compiles each;
- some byte ratios worsen above 1.0 as contract count or horizon increases.

Predeclared candidate improvement F1:
Intern each unique lawful observation once in a shared dictionary; all
layer/class records refer to an observation ID rather than recopying JSON.

Candidate improvement F2:
If the induced equivalence partition at depth k is identical to depth k-1,
a deterministic complete transition system has reached a partition-refinement
fixed point. Use a same-layer class transition table and do not expand the
declared horizon further. This is classical deterministic automaton theory,
not a newly invented theorem. The earliest fixed-point depth and requested
depth must both be reported.

Failure criteria:
1. Any quotient relation differs from the plain v2 compiler for any of the
   15 frozen synthetic workloads or the independent 16-state exhaustive
   oracle (0..4 horizon).
2. Any same-layer transition is not well-defined for all states in its class.
3. Any claimed byte saving ignores the shared table, dictionary or code
   overhead.
4. Any workload shows a cost regression; retain the regression, including
   the case where factorization is more expensive.
5. Any core change to frozen G4 B10, or relabeling of old holdouts.
6. Any change to generated synthetic cases or scoring solely to make the
   new representation win.

The new factorized implementation is an ALTERNATIVE v2 development candidate,
not a replacement of a pre-frozen experiment. Report ratio to both the full
synthetic state bytes and the plain v2 table+codes.