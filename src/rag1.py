"""Extractive local retrieval. No language model or generated facts.

Only explicitly registered, dataset-scoped reference documents are searched.
Lexical match scores are retrieval scores, never confidence probabilities.
"""
import re
import unicodedata
from pathlib import Path
from .loading import digest, read_json

EXCLUDED = ("verite-de-reference", "questions-validation", "resultats-tests", "codex_aidut")
STOP = {"les", "des", "une", "pour", "dans", "avec", "sur", "aux", "par", "de", "et"}


def tokens(text):
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z0-9]{3,}", plain)) - STOP


def load_corpus(manifest):
    chunks = []
    entries = read_json(manifest, {"documents": []})["documents"]
    for entry in entries:
        path = (Path(manifest).parent / entry["path"]).resolve()
        if any(x in path.name.lower() for x in EXCLUDED) or entry.get("purpose") != "reference":
            raise ValueError(f"Evaluation/non-reference document forbidden in corpus: {path.name}")
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            sections = [(f"page {i}", p.extract_text() or "") for i, p in enumerate(PdfReader(path).pages, 1)]
        elif path.suffix.lower() in {".md", ".txt"}:
            sections = [(f"line {i}", line) for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)]
        else:
            raise ValueError(f"Unsupported reference format: {path.suffix}")
        sha = digest(path)
        for locator, value in sections:
            if value.strip():
                chunks.append(dict(evidence_id=f"ref:{entry['dataset']}:{sha[:12]}:{locator}",
                    record_id="reference", field="passage", value=value,
                    file=str(path), locator=locator, sha256=sha, dataset=entry["dataset"], origin="retrieval"))
    return chunks


def retrieve(query, dataset, chunks, limit=3):
    words = tokens(query)
    scored = [(len(words & tokens(c["value"])), c) for c in chunks if c["dataset"] == dataset]
    return [dict(c, retrieval_score=n) for n, c in sorted(scored, key=lambda x: (-x[0], x[1]["evidence_id"])) if n >= 2][:limit]


def run(records, chunks):
    retrieved = {}
    for r in records:
        d = r["data"]
        query = " ".join(str(d.get(k) or "") for k in ("role", "competences_documentees", "nom", "domaine"))
        hits = retrieve(query, r["dataset"], chunks)
        r["rag1"] = {"status": "Retrieved - To validate" if hits else "Not available",
                     "evidence_ids": [h["evidence_id"] for h in hits],
                     "reason": "Passages candidats, sans affirmation automatique" if hits else "Aucune référence pertinente disponible"}
        retrieved.update({h["evidence_id"]: h for h in hits})
    return list(retrieved.values())
