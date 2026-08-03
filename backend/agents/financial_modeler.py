from crewai import Agent, Task, Crew
from crewai.llm import LLM

from backend.config import Config
from backend.agents.schemas import CostEstimate
from backend.agents.financial_queries import get_shipment_financials, get_war_risk_premium_rate
from backend.agents.cost_calculator import calculate_expected_cost_stay, calculate_expected_cost_reroute


class FinancialModelerAgent:
    """
    Computes ExpectedCost(stay) vs ExpectedCost(reroute) using a fixed
    formula (Section 4 of the spec) — the LLM never touches the arithmetic,
    it only explains the already-computed comparison.
    """

    def __init__(self):

        self.llm = LLM(
            model=Config.GROQ_MODEL,
            api_key=Config.GROQ_API_KEY,
            temperature=0
        )

        self.agent = Agent(
            role="Maritime Financial Modeler",
            goal=(
                "Explain, in plain terms, why the cheaper of two "
                "already-computed routing costs should be recommended. "
                "Never recalculate or invent any number."
            ),
            backstory=(
                "You are a shipping cost analyst. You are handed final, "
                "verified cost figures and only need to explain the "
                "comparison clearly — you never do the arithmetic yourself."
            ),
            llm=self.llm,
            verbose=True
        )

    def evaluate(self, shipment_id: str, reroute_delay_days: int) -> CostEstimate:

        shipment = get_shipment_financials(shipment_id)
        premium_rate = get_war_risk_premium_rate(shipment["route_id"])

        cargo_value = float(shipment["cargo_value_usd"])
        fuel_price = float(shipment["fuel_price_usd"])
        fuel_consumption = float(shipment["fuel_consumption_tpd"])

        expected_cost_stay = calculate_expected_cost_stay(cargo_value, premium_rate)

        reroute_breakdown = calculate_expected_cost_reroute(
            reroute_delay_days=reroute_delay_days,
            cargo_value_usd=cargo_value,
            fuel_price_usd=fuel_price,
            fuel_consumption_tpd=fuel_consumption,
        )

        expected_cost_reroute = reroute_breakdown["expected_cost_reroute_usd"]
        recommended_option = "stay" if expected_cost_stay <= expected_cost_reroute else "reroute"

        task = Task(
            description=f"""
Shipment: {shipment_id}
Cargo Value: ${cargo_value:,.2f}

Option 1 — Stay on current route:
  War-risk premium rate: {premium_rate:.2%}
  Expected Cost (stay): ${expected_cost_stay:,.2f}

Option 2 — Reroute:
  Delay: {reroute_delay_days} days
  Daily holding cost: ${reroute_breakdown['daily_holding_cost_usd']:,.2f}/day
  SLA penalty exposure: ${reroute_breakdown['sla_penalty_exposure_usd']:,.2f}
  Additional fuel cost: ${reroute_breakdown['additional_fuel_cost_usd']:,.2f}
  Expected Cost (reroute): ${expected_cost_reroute:,.2f}

Computed recommendation: {recommended_option}

Using ONLY the numbers above (do not recalculate anything), write a
brief reasoning for why '{recommended_option}' is the lower-cost option.

Return strictly this JSON and nothing else:

{{
  "shipment_id": "{shipment_id}",
  "cargo_value_usd": {cargo_value},
  "war_risk_premium_rate": {premium_rate},
  "expected_cost_stay_usd": {expected_cost_stay},
  "reroute_delay_days": {reroute_delay_days},
  "daily_holding_cost_usd": {reroute_breakdown['daily_holding_cost_usd']},
  "sla_penalty_exposure_usd": {reroute_breakdown['sla_penalty_exposure_usd']},
  "additional_fuel_cost_usd": {reroute_breakdown['additional_fuel_cost_usd']},
  "expected_cost_reroute_usd": {expected_cost_reroute},
  "recommended_option": "{recommended_option}",
  "reasoning": "<your brief reasoning>"
}}
""",
            expected_output="A single JSON object matching the schema above.",
            agent=self.agent,
            output_pydantic=CostEstimate
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        cost_estimate: CostEstimate = result.pydantic

        # Enforce the deterministic numbers regardless of what the LLM echoed
        cost_estimate.cargo_value_usd = cargo_value
        cost_estimate.war_risk_premium_rate = premium_rate
        cost_estimate.expected_cost_stay_usd = expected_cost_stay
        cost_estimate.reroute_delay_days = reroute_delay_days
        cost_estimate.daily_holding_cost_usd = reroute_breakdown["daily_holding_cost_usd"]
        cost_estimate.sla_penalty_exposure_usd = reroute_breakdown["sla_penalty_exposure_usd"]
        cost_estimate.additional_fuel_cost_usd = reroute_breakdown["additional_fuel_cost_usd"]
        cost_estimate.expected_cost_reroute_usd = expected_cost_reroute
        cost_estimate.recommended_option = recommended_option

        return cost_estimate
if __name__ == "__main__":

    from backend.agents.financial_queries import get_sample_shipment_id
    from backend.agents.logistics_router import LogisticsRouterAgent
    from backend.agents.db_queries import find_route_through_strait, get_route

    agent = FinancialModelerAgent()

    shipment_id = get_sample_shipment_id()

    # Derive strait from the shipment's route dynamically, then get real reroute delay
    shipment = get_shipment_financials(shipment_id)
    strait_id = shipment["canal_used"]

    router = LogisticsRouterAgent()
    route_option = router.route(strait_id=strait_id)

    result = agent.evaluate(
        shipment_id=shipment_id,
        reroute_delay_days=route_option.reroute_delay_days
    )

    print("\n" + "=" * 60)
    print("COST ESTIMATE")
    print("=" * 60)
    print(result.model_dump_json(indent=2))