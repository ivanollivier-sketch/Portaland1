"""Conservative interpretation of the supplied M7 rules; no legal judgment."""
from .config import ACTIVE


def run(records):
    interpretations = []
    for r in records:
        d = r["data"]
        r["rag3"] = []
        if "id" not in d:
            continue
        def add(rule, line, conclusion, fields, severity):
            claim = dict(interpretation_id=f"{r['record_id']}:{rule}", record_id=r["record_id"],
                rule=rule, conclusion=conclusion, origin="inference", status="To validate",
                confidence_score=None, severity=severity, cost_ke=d.get("cout_annuel_ke"),
                evidence_ids=[r["evidence"][f] for f in fields] + [f"rule:M7 Écarts:{line}"],
                validation_ids=[f"{r['record_id']}:owner"] if rule == "E13" else [])
            interpretations.append(claim)
            r["rag3"].append(claim["interpretation_id"])
        if d.get("statut") in ACTIVE:
            if not d.get("owner") and "owner" not in r["validated"]:
                add("E13", 17, "Nommer un propriétaire métier", ["owner", "statut", "valeur"], 2 if (d.get("valeur") or 0) >= 4 else 1)
            if d.get("statut") == "Production" and d.get("valeur") is not None and d["valeur"] <= 2 and (
                (d.get("usage") is not None and d["usage"] <= 2) or (d.get("cout_annuel_ke") is not None and d["cout_annuel_ke"] >= 30)):
                add("E7", 11, "Examiner le coût et mesurer la valeur avant arbitrage", ["statut", "valeur", "usage", "cout_annuel_ke"], 2)
            if d.get("statut") == "Production" and (d.get("valeur") or 0) >= 4 and d.get("usage") is not None and d["usage"] <= 2:
                add("E21", 25, "Vérifier le besoin d'accompagnement à l'adoption", ["statut", "valeur", "usage"], 2)
    return interpretations
