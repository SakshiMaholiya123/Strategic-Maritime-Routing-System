import argparse
from dataclasses import dataclass, asdict

from backend.config import Config
from backend.agents.risk_assessor import RiskAssessorAgent
from backend.agents.logistics_router import LogisticsRouterAgent
from backend.agents.financial_modeler import FinancialModelerAgent
from backend.agents.financial_queries import get_shipment_financials, get_sample_shipment_id
from backend.agents.db_queries import get_first_strait_id
from backend.decision_engine.db_writer import write_risk_event, write_routing_decision
from backend.precedents.precedent_writer import write_precedent


@dataclass
class RoutingDecisionResult:
    shipment_id: str
    strait_id: str
    final_decision: str
    requires_human_approval: bool
    approval_reason: str
    risk_probability: float
    confidence_low: float
    confidence_high: float
    expected_cost_stay_usd: float
    expected_cost_reroute_usd: float
    estimated_savings_usd: float
    cargo_value_usd: float
    risk_event_key: int
    routing_decision_key: int


def _check_divergence(confidence_low: float, confidence_high: float) -> bool:
    """
    Divergence check per spec Section 4: "The divergence check compares
    the Risk Assessor's stated confidence-weighted probability range...
    a spread wider than the configured tolerance routes to the human gate."
    """
    spread = confidence_high - confidence_low
    return spread > Config.DIVERGENCE_TOLERANCE


def _check_cargo_threshold(cargo_value_usd: float) -> bool:
    return cargo_value_usd > Config.HUMAN_APPROVAL_CARGO_THRESHOLD_USD


def run_decision_pipeline(shipment_id: str, strait_id: str) -> RoutingDecisionResult:
    """
    Runs all three agents for the given shipment/strait, applies the
    fixed expected-cost formula, checks the human-approval gates,
    persists the audit trail, and writes a precedent summary.

    Raises:
        ValueError: if the shipment or strait cannot be resolved.
    """

    shipment = get_shipment_financials(shipment_id)

    # --- Agent 1: Risk Assessor ---
    risk_agent = RiskAssessorAgent()
    risk_query = f"What is the current geopolitical risk of disruption in {strait_id}?"
    risk_result = risk_agent.assess(strait_id=strait_id, query=risk_query)

    # --- Agent 2: Logistics Router ---
    router_agent = LogisticsRouterAgent()
    route_result = router_agent.route(strait_id=strait_id)

    # --- Agent 3: Financial Modeler ---
    financial_agent = FinancialModelerAgent()
    cost_result = financial_agent.evaluate(
        shipment_id=shipment_id,
        reroute_delay_days=route_result.reroute_delay_days,
    )

    # --- Deterministic decision (fixed formula, no LLM) ---
    final_decision = cost_result.recommended_option
    estimated_savings = abs(cost_result.expected_cost_stay_usd - cost_result.expected_cost_reroute_usd)

    # --- Human-approval gate checks ---
    diverges = _check_divergence(risk_result.confidence_low, risk_result.confidence_high)
    exceeds_threshold = _check_cargo_threshold(cost_result.cargo_value_usd)

    requires_human_approval = diverges or exceeds_threshold

    reasons = []
    if diverges:
        reasons.append(
            f"Risk confidence range spread "
            f"({risk_result.confidence_high - risk_result.confidence_low:.2f}) "
            f"exceeds tolerance ({Config.DIVERGENCE_TOLERANCE})"
        )
    if exceeds_threshold:
        reasons.append(
            f"Cargo value (${cost_result.cargo_value_usd:,.2f}) exceeds "
            f"approval threshold (${Config.HUMAN_APPROVAL_CARGO_THRESHOLD_USD:,.2f})"
        )

    approval_reason = "; ".join(reasons) if reasons else "No divergence or threshold trigger — auto-approved"

    # --- Persist audit trail ---
    risk_event_key = write_risk_event(
        strait_id=strait_id,
        risk_probability=risk_result.risk_probability,
        estimated_delay_days=risk_result.estimated_delay_days,
        estimated_extra_cost_usd=cost_result.expected_cost_reroute_usd,
        cited_doc_ids=risk_result.cited_doc_ids,
    )

    recommended_route = (
        route_result.recommended_alternate_route_id
        if final_decision == "reroute"
        else route_result.current_route_id
    )

    routing_decision_key = write_routing_decision(
        shipment_id=shipment_id,
        risk_event_key=risk_event_key,
        recommended_route=recommended_route,
        decision=final_decision,
        confidence_score=(risk_result.confidence_low + risk_result.confidence_high) / 2,
        estimated_savings_usd=estimated_savings,
    )

    # --- Write precedent summary for future Logistics Router retrieval ---
    write_precedent(
        shipment_id=shipment_id,
        strait_id=strait_id,
        final_decision=final_decision,
        expected_cost_stay_usd=cost_result.expected_cost_stay_usd,
        expected_cost_reroute_usd=cost_result.expected_cost_reroute_usd,
        estimated_savings_usd=estimated_savings,
        risk_probability=risk_result.risk_probability,
        cargo_value_usd=cost_result.cargo_value_usd,
        routing_decision_key=routing_decision_key,
    )

    return RoutingDecisionResult(
        shipment_id=shipment_id,
        strait_id=strait_id,
        final_decision=final_decision,
        requires_human_approval=requires_human_approval,
        approval_reason=approval_reason,
        risk_probability=risk_result.risk_probability,
        confidence_low=risk_result.confidence_low,
        confidence_high=risk_result.confidence_high,
        expected_cost_stay_usd=cost_result.expected_cost_stay_usd,
        expected_cost_reroute_usd=cost_result.expected_cost_reroute_usd,
        estimated_savings_usd=estimated_savings,
        cargo_value_usd=cost_result.cargo_value_usd,
        risk_event_key=risk_event_key,
        routing_decision_key=routing_decision_key,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full Decision Engine pipeline.")
    parser.add_argument("--shipment-id", type=str, default=None)
    parser.add_argument("--strait-id", type=str, default=None)
    return parser.parse_args()


if __name__ == "__main__":

    args = _parse_args()

    shipment_id = args.shipment_id or get_sample_shipment_id()
    strait_id = args.strait_id or get_first_strait_id()

    result = run_decision_pipeline(shipment_id=shipment_id, strait_id=strait_id)

    print("\n" + "=" * 60)
    print("ROUTING DECISION")
    print("=" * 60)
    for key, value in asdict(result).items():
        print(f"{key}: {value}")