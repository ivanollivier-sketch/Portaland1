from datetime import datetime
from .config import ACTIVE


def run(records, answers):
    questions = []
    for r in records:
        d = r["data"]
        specs = [("organization", "Confirmer l'organisation et le périmètre de ce jeu."),
                 ("activity_link", "Fournir le lien explicite profil, activité et usage dans ce même périmètre.")]
        if "id" in d:
            if not d.get("owner"):
                specs.append(("owner", "Qui est le propriétaire métier de cet usage ?"))
            specs.append(("measured_value", "Quelle valeur annuelle mesurée et quelle preuve sont disponibles ?"))
            if d.get("risque") in (None, "Non classé", "Haut risque"):
                specs.append(("risk_review", "Confirmer la classification et documenter la revue de risque."))
            if d.get("decision") == "Arrêter" and (d.get("valeur") or 0) > 2:
                specs.append(("decision_conflict", "Justifier Arrêter malgré une valeur supérieure à 2 (condition E7 non satisfaite)."))
        r["validated"] = {}
        for field, prompt in specs:
            qid = f"{r['record_id']}:{field}"
            answer = answers.get(qid)
            if answer:
                if not isinstance(answer, dict) or answer.get("value") is None or any(not answer.get(k) for k in ("reviewer", "timestamp", "evidence")):
                    raise ValueError(f"Incomplete human validation: {qid}")
                if field in {"organization", "owner"} and (not isinstance(answer['value'], str) or not answer['value'].strip()):
                    raise ValueError(f"Expected a non-empty name: {qid}")
                datetime.fromisoformat(answer["timestamp"].replace("Z", "+00:00"))
                r["validated"][field] = answer
            questions.append(dict(question_id=qid, record_id=r["record_id"], field=field,
                question=prompt, status="Human confirmed" if answer else "To validate",
                answer=answer.get("value") if answer else None,
                reviewer=answer.get("reviewer") if answer else None,
                timestamp=answer.get("timestamp") if answer else None,
                answer_evidence=answer.get("evidence") if answer else None,
                evidence_ids=list(r["evidence"].values()) + r["rag1"]["evidence_ids"]))
        r["rag2"] = [q["question_id"] for q in questions if q["record_id"] == r["record_id"]]
        r["validation_status"] = "Human confirmed" if all(q['status']=='Human confirmed' for q in questions if q['record_id']==r['record_id']) else "To validate"
    unused = set(answers) - {q["question_id"] for q in questions}
    if unused:
        raise ValueError(f"Unknown or obsolete answer keys: {sorted(unused)}")
    return questions
