from typing import List, Tuple, Dict


def build_citation_context(documents) -> Tuple[str, Dict[str, str]]:
    """
    Format retrieved chunks into a citation-friendly context block,
    assigning each chunk a short DOC-n id the LLM can reference.
    Returns (context_block, doc_id_to_source_map).
    Reusable by any agent that needs citation-backed retrieval.
    """

    context_lines = []
    doc_id_map = {}

    for i, doc in enumerate(documents, start=1):

        doc_id = f"DOC-{i}"
        doc_id_map[doc_id] = doc.metadata.get("source", "unknown")

        context_lines.append(
            f"[{doc_id}] "
            f"(source_type={doc.metadata.get('source_type')}, "
            f"report_date={doc.metadata.get('report_date')}, "
            f"age_days={doc.metadata.get('retrieval_age_days')})\n"
            f"{doc.page_content}\n"
        )

    return "\n---\n".join(context_lines), doc_id_map


def resolve_cited_sources(cited_doc_ids: List[str], doc_id_map: Dict[str, str]) -> List[str]:
    """
    Translate DOC-n placeholders back to real source paths for the audit trail.
    """
    return [doc_id_map.get(doc_id, doc_id) for doc_id in cited_doc_ids]