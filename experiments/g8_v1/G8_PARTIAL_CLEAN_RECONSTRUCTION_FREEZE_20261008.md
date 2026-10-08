# G8 independent reconstruction of archived scoring artifacts — frozen plan

Date: 2026-10-08; evidence role: **partial clean reconstruction**.

No native oracle is re-executed in this workflow. It cannot close the
original G8 clean-reproduction requirement on its own.

Inputs pinned by outer ZIP SHA256:

- G6 285-case full matrix run 37577515052 / artifact 11463213360,
  SHA256 `90f6b9562aa7e76caf1f8c252cf5483dbcca4729b61687a8805a3cd105c81d85`.
- GitHub v2 nine-case matrix run 37650255613 / artifact 11495203512,
  SHA256 `381225c9c54153c4950af6f5ba1d60e655cbdb54dfdc53ff23c848a8393f059b`.
- X.509 holdout run 37579211753 / artifact 11464410280,
  SHA256 `b3d451ceb272750a910f0800aa819d9bc8c4538b86eaa4e6053c958b4500de6c`.

Unchanged compiler Git blob:
`9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`.
Unchanged strict scorer Git blob:
`545eb2f994796c8ef78134c4cbce9f131bab4d5d`.

Exact operations:
1. Fetch pinned archives and validate outer ZIP hashes before unpacking.
2. Recompile B10 from the saved G6 adapter inputs; byte-compare generated
   JSON to archived G6 generic WFC output.
3. Run strict G4 evaluator on the saved G6 285-case 19-ID rows; byte-compare
   output to archived original matrix.
4. Independently recompile GitHub v2 B10 from saved v2 adapter inputs and
   rerun the strict 19-ID evaluator with the unchanged accept label;
   byte-compare both outputs.
5. Verify the original X.509 archived result reports 7/7 native matches,
   pre/post-B10 identity, and no core/schema changes, without rerunning native
   `openssl verify` and without changing X.509 predictions.
6. Hash the new reconstruction outputs and retain PASS/FAIL per component.

A failed byte-compare is a reproducibility failure; do not silently fall back
to value-only comparison, rerun native or rewrite a frozen input.

This reconstruction is an **intermediate audit**. Full G8 still requires
fresh native reproducibility where legally possible, all applicable
robustness, per-family downstream and cost accounting.
