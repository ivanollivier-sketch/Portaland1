import json
from .config import UNKNOWN


def consolidate(records):
    rows = []
    for r in records:
        d = r["data"]
        usage = "id" in d
        rows.append(dict(record_id=r["record_id"], dataset=r["dataset"],
            organization=r["validated"].get("organization", {}).get("value", UNKNOWN),
            record_type="usage" if usage else "profile", profile_id=UNKNOWN if usage else d["user_id"],
            role=d.get("role") or UNKNOWN, function=d.get("direction") or d.get("domaine") or UNKNOWN,
            activity=UNKNOWN, objective=UNKNOWN, ai_usage=d.get("nom") or UNKNOWN,
            tool=UNKNOWN, provider=d.get("fournisseur") or UNKNOWN, category=d.get("categorie") or UNKNOWN,
            status=d.get("statut") or UNKNOWN,
            owner=r["validated"].get("owner", {}).get("value", d.get("owner") or UNKNOWN),
            environment=d.get("environnement") or UNKNOWN, annual_cost_ke=d.get("cout_annuel_ke"),
            value_score=d.get("valeur"), adoption_score=d.get("usage"), risk=d.get("risque") or UNKNOWN,
            source_decision=d.get("decision") or UNKNOWN,
            measured_value=r['validated'].get('measured_value', {}).get('value', UNKNOWN),
            human_validations=json.dumps(r['validated'], ensure_ascii=False),
            rag1=r["rag1"]["status"], rag2=r['validation_status'], rag3="; ".join(r["rag3"]) or "Not available",
            confidence_score=None, opportunity="; ".join(r["rag3"]) or UNKNOWN,
            evidence_ids=json.dumps(r["evidence"], ensure_ascii=False),
            retrieval_ids="; ".join(r["rag1"]["evidence_ids"]),
            validation_ids="; ".join(r["rag2"]),
            comment="Jointure profil / activité / usage non établie. Scores déclaratifs, valeur monétaire inconnue."))
    return rows
