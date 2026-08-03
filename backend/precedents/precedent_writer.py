from datetime import datetime
from langchain_core.documents import Document
from langchain_chroma import Chroma
from backend.config import Config
from backend.rag.embedder import EmbeddingGenerator


def _build_narrative_summary(
    shipment_id: str,
    strait_id: str,
    final_decision: str,
    expected_cost_stay_usd: float,
    expected_cost_reroute_usd: float,
    estimated_savings_usd: float,
    risk_probability: float,
    cargo_value_usd: float,
) -> str:
    """
    Builds a short, retrieval-friendly text summary of the decision.
    No LLM involved — pure deterministic string formatting, so the
    same decision always produces the same summary text.
    """

    return (
        f"On {datetime.now().date().isoformat()}, a routing decision was made for "
        f"shipment {shipment_id} transiting {strait_id}. "
        f"The assessed disruption risk probability was {risk_probability:.0%}. "
        f"Cargo value was ${cargo_value_usd:,.2f}. "
        f"Expected cost to stay on the current route: ${expected_cost_stay_usd:,.2f}. "
        f"Expected cost to reroute: ${expected_cost_reroute_usd:,.2f}. "
        f"The final decision was to '{final_decision}', "
        f"with an estimated savings of ${estimated_savings_usd:,.2f} "
        f"compared to the alternative option."
    )


def write_precedent(
    shipment_id: str,
    strait_id: str,
    final_decision: str,
    expected_cost_stay_usd: float,
    expected_cost_reroute_usd: float,
    estimated_savings_usd: float,
    risk_probability: float,
    cargo_value_usd: float,
    routing_decision_key: int,
) -> None:
    """
    Embeds and stores a narrative summary of this routing decision
    into the past_routing_precedents collection, tagged with the
    metadata the Logistics Router filters on (strait_id).

    This is safe to call even if the collection doesn't exist yet —
    Chroma creates it on first write.
    """

    embedding_model = EmbeddingGenerator().get_embedding_model()

    vector_db = Chroma(
        persist_directory=str(Config.CHROMA_DB_PATH),
        embedding_function=embedding_model,
        collection_name="past_routing_precedents"
    )

    summary_text = _build_narrative_summary(
        shipment_id=shipment_id,
        strait_id=strait_id,
        final_decision=final_decision,
        expected_cost_stay_usd=expected_cost_stay_usd,
        expected_cost_reroute_usd=expected_cost_reroute_usd,
        estimated_savings_usd=estimated_savings_usd,
        risk_probability=risk_probability,
        cargo_value_usd=cargo_value_usd,
    )

    document = Document(
        page_content=summary_text,
        metadata={
            "strait_id": strait_id,
            "chosen_option": final_decision,
            "decision_date": datetime.now().date().isoformat(),
            "shipment_id": shipment_id,
            "routing_decision_key": routing_decision_key,
        }
    )

    vector_db.add_documents(
        documents=[document],
        ids=[f"decision-{routing_decision_key}"]
    )

    print(f"Precedent written for routing_decision_key={routing_decision_key} "
          f"into past_routing_precedents collection.")