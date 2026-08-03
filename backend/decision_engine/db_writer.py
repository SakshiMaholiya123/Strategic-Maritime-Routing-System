from datetime import datetime
from sqlalchemy import text
from backend.database.create_database import engine


def write_risk_event(
    strait_id: str,
    risk_probability: float,
    estimated_delay_days: int,
    estimated_extra_cost_usd: float,
    cited_doc_ids: list,
) -> int:
    """
    Inserts a row into Fact_RiskEvents and returns its RiskEventKey.
    """

    # Deduplicate and shorten to filenames only (not full paths) to
    # respect the VARCHAR(255) column limit, then hard-truncate as a
    # final safety net.
    unique_sources = []
    for doc_id in cited_doc_ids:
        filename = doc_id.split("\\")[-1].split("/")[-1]
        if filename not in unique_sources:
            unique_sources.append(filename)

    source_report = "; ".join(unique_sources) if unique_sources else "No source documents cited"
    source_report = source_report[:255]

    query = text("""
        INSERT INTO maritime.fact_riskevents (
            straitkey, datekey, routekey, risk_level,
            disruption_probability, estimated_delay_days,
            estimated_extra_cost_usd, source_report
        )
        SELECT
            s.straitkey,
            TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INTEGER,
            NULL,
            CASE
                WHEN :risk_probability >= 0.7 THEN 'High'
                WHEN :risk_probability >= 0.4 THEN 'Medium'
                ELSE 'Low'
            END,
            :risk_probability,
            :estimated_delay_days,
            :estimated_extra_cost_usd,
            :source_report
        FROM maritime.dim_strait s
        WHERE s.strait_name = :strait_id
        RETURNING riskeventkey
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "strait_id": strait_id,
                "risk_probability": risk_probability,
                "estimated_delay_days": estimated_delay_days,
                "estimated_extra_cost_usd": estimated_extra_cost_usd,
                "source_report": source_report,
            },
        )
        row = result.fetchone()

    if row is None:
        raise ValueError(f"Could not insert risk event — strait '{strait_id}' not found in Dim_Strait.")

    return row[0]


def write_routing_decision(
    shipment_id: str,
    risk_event_key: int,
    recommended_route: str,
    decision: str,
    confidence_score: float,
    estimated_savings_usd: float,
) -> int:
    """
    Inserts the final decision into Fact_RoutingDecisions, linked to
    the Fact_TransitLegs row (by shipment) and the Fact_RiskEvents row
    that informed it.
    """

    query = text("""
        INSERT INTO maritime.fact_routingdecisions (
            transitlegkey, riskeventkey, decision_date,
            recommended_route, decision, confidence_score,
            estimated_savings_usd, generated_by
        )
        SELECT
            f.transitlegkey,
            :risk_event_key,
            :decision_date,
            :recommended_route,
            :decision,
            :confidence_score,
            :estimated_savings_usd,
            'DecisionEngine'
        FROM maritime.fact_transitlegs f
        WHERE f.shipment_id = :shipment_id
        RETURNING decisionkey
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "shipment_id": shipment_id,
                "risk_event_key": risk_event_key,
                "decision_date": datetime.now(),
                "recommended_route": recommended_route,
                "decision": decision,
                "confidence_score": confidence_score,
                "estimated_savings_usd": estimated_savings_usd,
            },
        )
        row = result.fetchone()

    if row is None:
        raise ValueError(f"Could not insert routing decision — shipment '{shipment_id}' not found.")

    return row[0]