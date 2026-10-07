#!/usr/bin/env python3
"""Materialize G4 B0-B10/O1-O8 representations on deduplicated cases.

These are adapter-state representations of the frozen development carriers.
They use no native action field. B10 is an adapter-state pilot, not a claim
that the generic EEQ/WFC compiler or all G0-G8 gates have closed.
"""
import argparse
import json
from pathlib import Path

IDS = [f"B{i}" for i in range(11)] + [f"O{i}" for i in range(1, 9)]
NA = "__NOT_APPLICABLE__"


def prediction(domain, s):
    if domain == "APT:releaseinfo":
        if not s["qualified"]:
            return "REJECT_AUTH"
        if any(changed and not (s["allow_global"] or field in s["allow_fields"])
               for field, changed in s["protected_changed"].items()):
            return "BLOCK_CONFIRM"
        return "ACCEPT"
    if domain == "K8s:flux-vap":
        return "REJECT" if s["tenant_label"] and s["service_account"] == "flux" and s["operation"] in {"CREATE", "UPDATE"} else "ACCEPT"
    if domain == "K8s:gcsfuse-vap":
        scoped = s["annotation"] and s["sidecar"]
        return "REJECT" if scoped and (s["restart"] != "Always" or s["env"] != "TRUE") else "ACCEPT"
    if domain == "K8s:volcano-vap":
        if s["scheduler"] != "volcano":
            return "ACCEPT"
        active = [s[k] for k in ("min", "max") if s[k] != "absent"]
        if len(active) > 1:
            return "REJECT"
        return "ACCEPT" if not active or active[0] in {"1", "25%"} else "REJECT"
    return None


def represent(case):
    domain = case["signature"]["semantic_domain"]
    s = case["signature"]["pre_action_state"]
    r = {k: NA for k in IDS}
    reasons = {}
    r["B0"] = s
    if domain == "APT:releaseinfo":
        q, delta, glob, allowed = s["qualified"], s["protected_changed"], s["allow_global"], s["allow_fields"]
        unallowed = sorted(k for k, v in delta.items() if v and not (glob or k in allowed))
        r.update({
            "B1": {"current_signer_qualified": q}, "B2": {"signed_by_qualified": q},
            "B3": {"allow_global": glob, "allow_fields": allowed}, "B4": delta,
            "B5": {"allow_global": glob, "allow_fields": allowed, "protected_delta": delta},
            "B6": {"qualified": q, "protected_delta": delta},
            "B7": {"frozen_mechanism_forecast": prediction(domain, s)},
            "B8": {"qualified": q, "protected_delta": delta, "allow_global": glob, "allow_count": len(allowed)},
            "B9": {"qualified": q, "unallowed_fields": unallowed},
            "B10": {"qualified_support": q, "action_delta": delta, "continuation_allowance": {"global": glob, "fields": allowed}},
            "O1": {"protected_delta": delta, "allow_global": glob, "allow_fields": allowed},
            "O2": {"protected_delta": delta, "allow_global": glob, "allow_fields": allowed},
            "O3": {"qualified": q, "protected_delta": delta, "allow_global": glob, "allow_count": len(allowed)},
            "O4": {"qualified": q, "allow_global": glob, "allow_fields": allowed},
            "O5": {"qualified": q, "protected_delta": delta},
            "O6": {"qualified": q, "allow_global": glob, "allow_fields": allowed},
        })
        reasons["O7"] = "Only one registered release transition; no longer horizon in this carrier"
        reasons["O8"] = "One registered Signed-By support mechanism"
    elif domain == "K8s:flux-vap":
        tenant, sa, op = s["tenant_label"], s["service_account"], s["operation"]
        r.update({
            "B1": {"service_account": sa}, "B3": {"tenant_label": tenant, "operation": op},
            "B6": {"tenant_label": tenant, "service_account": sa, "operation": op},
            "B7": {"frozen_mechanism_forecast": prediction(domain, s)},
            "B8": {"tenant_label": tenant, "is_flux_sa": sa == "flux", "operation": op},
            "B9": {"policy_applies": tenant and op in {"CREATE", "UPDATE"}, "is_flux_sa": sa == "flux"},
            "B10": {"qualified_policy_source": tenant, "claim_binding": sa == "flux", "registered_action": op},
            "O2": {"service_account": sa, "operation": op},
            "O3": {"tenant_label": tenant, "operation": op},
        })
    elif domain == "K8s:gcsfuse-vap":
        ann, side, restart, env = s["annotation"], s["sidecar"], s["restart"], s["env"]
        r.update({
            "B1": {"annotation": ann, "sidecar": side, "restart": restart, "env": env},
            "B3": {"annotation": ann, "sidecar": side},
            "B6": {"annotation": ann, "sidecar": side, "restart": restart, "env": env},
            "B7": {"frozen_mechanism_forecast": prediction(domain, s)},
            "B8": {"scoped": ann and side, "restart": restart, "env": env},
            "B9": {"scoped": ann and side, "sidecar_valid": restart == "Always" and env == "TRUE"},
            "B10": {"qualified_policy_source": ann and side, "claim_binding": side,
                    "continuation_predicates": {"restart_always": restart == "Always", "native_env": env == "TRUE"}},
            "O2": {"restart": restart, "env": env},
            "O3": {"annotation": ann, "restart": restart, "env": env},
        })
    elif domain == "K8s:volcano-vap":
        scheduler, minimum, maximum = s["scheduler"], s["min"], s["max"]
        valid = lambda x: x in {"absent", "1", "25%"}
        r.update({
            "B1": {"scheduler": scheduler, "min": minimum, "max": maximum},
            "B3": {"scheduler": scheduler},
            "B6": {"scheduler": scheduler, "min": minimum, "max": maximum},
            "B7": {"frozen_mechanism_forecast": prediction(domain, s)},
            "B8": {"volcano": scheduler == "volcano", "min_present": minimum != "absent",
                   "max_present": maximum != "absent", "min_valid": valid(minimum), "max_valid": valid(maximum)},
            "B9": {"volcano": scheduler == "volcano", "both_present": minimum != "absent" and maximum != "absent",
                   "min_valid": valid(minimum), "max_valid": valid(maximum)},
            "B10": {"qualified_scheduler": scheduler == "volcano", "registered_action": "CREATE",
                    "claim_binding": {"min": minimum != "absent", "max": maximum != "absent"},
                    "continuation_predicates": {"min_valid": valid(minimum), "max_valid": valid(maximum)}},
            "O2": {"min": minimum, "max": maximum},
            "O3": {"scheduler": scheduler, "min_valid": valid(minimum), "max_valid": valid(maximum)},
        })
    else:
        # The production root chain is native-verified, but a full TUF
        # representation and negative/qualification carrier are not frozen.
        for k in IDS[1:]:
            reasons[k] = "TUF representation carrier not frozen before native chain; pending adapter instance"
    if domain.startswith("K8s:"):
        for k in ("B2", "B4", "B5", "O1", "O4", "O5", "O6", "O7", "O8"):
            reasons[k] = {
                "B2": "No authentication or cryptographic-validity distinction in registered Pod carrier",
                "B4": "One policy source; no registered provenance alternatives",
                "B5": "No registered provenance alternatives",
                "O1": "One policy source; source provenance has no variable distinction",
                "O4": "One-step admission carrier has no prior continuation history",
                "O5": "No future continuation contract in one-step admission carrier",
                "O6": "Grid scores the request, not a later action-induced evidence change",
                "O7": "One-step admission is the full registered horizon",
                "O8": "One registered matching policy support mechanism",
            }[k]
    for key in IDS:
        if r[key] == NA and key not in reasons:
            raise ValueError(f"Missing reason for {domain}/{key}")
    return r, reasons


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ledger", type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    rows = []
    for case in ledger["cases"]:
        reps, na_reasons = represent(case)
        rows.append({"semantic_id": case["semantic_id"], "domain": case["signature"]["semantic_domain"],
                     "native_action": case["native_action"], "representations": reps,
                     "not_applicable_reasons": na_reasons})
    with args.out.open("w", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps({"schema": "eeq-g4-representations-v1", "rows": rows,
                              "b10_status": "adapter-state pilot; generic compiler integration pending"},
                             indent=2, sort_keys=True) + "\n")
    print(f"materialized={len(rows)}")


if __name__ == "__main__":
    main()
