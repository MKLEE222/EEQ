"""P3-B F0 conservative guard. Synthetic diagnosis only; NOT a native oracle or domain semantics verifier."""
import re
SHA=re.compile(r"^[0-9a-f]{64}$")
def valid_rows(rows):
    return isinstance(rows,dict) and all(isinstance(k,str) and k and isinstance(v,dict) and
        set(v)=={"digest","status"} and
        (v["digest"] is None or (isinstance(v["digest"],str) and SHA.fullmatch(v["digest"]))) and
        v["status"] in {"AVAILABLE","QUALIFIED","UNQUALIFIED","INVALID","UNAVAILABLE"}
        for k,v in rows.items())
def check(previous,fresh,independent_closure):
    """Trusted callback MUST independently re-enumerate all claim-relevant dependencies.
    This conditional guard cannot prove callback soundness; it never emits native ACCEPT/REJECT.
    """
    try:
        if previous.get("schema")!="eeq-p3b-dependency-snapshot-f0" or fresh.get("schema")!=previous["schema"]:
            return "MODEL_UNSUPPORTED"
        scope=previous.get("scope")
        if not isinstance(scope,dict) or set(scope)!={"contract","claim","actor","action","horizon"} or any(
            not isinstance(scope.get(k),str) or not scope[k] for k in ("contract","claim","actor","action")
        ) or type(scope["horizon"]) is not int or scope["horizon"]<0 or scope!=fresh.get("scope"):
            return "MODEL_UNSUPPORTED"
        os,oq=previous.get("sources"),previous.get("qualifications")
        ns,nq=fresh.get("sources"),fresh.get("qualifications")
        if not all(valid_rows(x) for x in (os,oq,ns,nq)):
            return "MODEL_UNSUPPORTED"
        old=previous.get("closure")
        if not isinstance(old,dict) or set(old)!={"sources","qualifications"}:
            return "MODEL_UNSUPPORTED"
        def valid_ids(obj):
            return all(isinstance(obj[k],list) and bool(obj[k]) and all(isinstance(v,str) and v for v in obj[k]) and len(set(obj[k]))==len(obj[k]) for k in ("sources","qualifications"))
        if not valid_ids(old) or any(k not in rows for typ,rows in (("sources",os),("qualifications",oq)) for k in old[typ]):
            return "MODEL_UNSUPPORTED"
        closure=independent_closure(fresh)
        if not isinstance(closure,dict) or set(closure)!={"complete","sources","qualifications"} or closure["complete"] is not True or not valid_ids(closure):
            return "MODEL_UNSUPPORTED"
        if any(k not in rows for typ,rows in (("sources",ns),("qualifications",nq)) for k in closure[typ]):
            return "MODEL_UNSUPPORTED"
        if any(rows[k]["status"]=="UNAVAILABLE" for typ,rows in (("sources",ns),("qualifications",nq)) for k in closure[typ]):
            return "SOURCE_UNAVAILABLE"
        if any(rows[k]["digest"] is None or rows[k]["status"]!=needed for typ,rows,needed in (("sources",ns,"AVAILABLE"),("qualifications",nq,"QUALIFIED")) for k in closure[typ]):
            return "REVERIFY_REQUIRED"
        if any(set(old[k])!=set(closure[k]) for k in ("sources","qualifications")):
            return "REVERIFY_REQUIRED"
        if any(a[k]!=b[k] for typ,a,b in (("sources",os,ns),("qualifications",oq,nq)) for k in closure[typ]):
            return "REVERIFY_REQUIRED"
        return "REUSE_CANDIDATE_CONDITIONAL"
    except Exception:
        return "MODEL_UNSUPPORTED"
