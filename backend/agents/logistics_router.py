from typing import Optional

from crewai import Agent, Task, Crew
from crewai.llm import LLM

from backend.config import Config
from backend.agents.schemas import RouteOption
from backend.agents.db_queries import find_route_through_strait, get_route, get_best_alternate
from backend.agents.precedents_retriever import get_similar_precedents
import argparse
from backend.agents.db_queries import get_first_strait_id



class LogisticsRouterAgent:
    """
    Compares the current route against the best viable alternate.
    All numbers come from PostgreSQL (deterministic) — the LLM only
    writes the reasoning, never recalculates or invents figures.
    """

    def __init__(self):

        self.llm = LLM(
            model=Config.GROQ_MODEL,
            api_key=Config.GROQ_API_KEY,
            temperature=0
        )

        self.agent = Agent(
            role="Maritime Logistics Router",
            goal=(
                "Given a current route and a computed best alternate route, "
                "along with any similar past precedents, write a clear "
                "justification for the recommendation. Never invent numbers "
                "not present in the provided data."
            ),
            backstory=(
                "You are a logistics planner. You are given exact route "
                "distances and delay figures already computed from the "
                "database — you never recalculate or guess these numbers, "
                "you only explain and contextualize them."
            ),
            llm=self.llm,
            verbose=True
        )

    def route(self, strait_id: str, current_route_id: Optional[str] = None) -> RouteOption:

        if current_route_id is None:
            current_route_id = find_route_through_strait(strait_id)

            if current_route_id is None:
                raise ValueError(
                    f"No route found in Dim_Route passing through '{strait_id}'."
                )

        current_route = get_route(current_route_id)
        alternate = get_best_alternate(current_route)
        precedents = get_similar_precedents(strait_id)

        if alternate is None:
            return RouteOption(
                strait_id=strait_id,
                current_route_id=current_route_id,
                recommended_alternate_route_id=None,
                reroute_delay_days=0,
                reroute_distance_nm=0,
                similar_past_incidents=precedents,
                reasoning="No viable alternate route avoiding the current canal was found in Dim_Route."
            )

        reroute_delay_days = max(
            int(alternate["expected_days"] - current_route["expected_days"]), 0
        )

        precedent_block = (
            "\n".join(f"- {p[:300]}" for p in precedents)
            if precedents else "No past precedents available for this strait yet."
        )

        task = Task(
            description=f"""
Current route: {current_route['route_id']} via {current_route['canal_used']}
  Distance: {current_route['distance_nm']} NM, Expected Days: {current_route['expected_days']}

Best computed alternate: {alternate['route_id']} via {alternate['canal_used']}
  Distance: {alternate['distance_nm']} NM, Expected Days: {alternate['expected_days']}
  Additional delay vs current route: {reroute_delay_days} days

Similar past precedents on {strait_id}:
{precedent_block}

Using ONLY the numbers above, write a brief reasoning for recommending
route {alternate['route_id']} as the alternate to {current_route['route_id']}.

Return strictly this JSON and nothing else:

{{
  "strait_id": "{strait_id}",
  "current_route_id": "{current_route['route_id']}",
  "recommended_alternate_route_id": "{alternate['route_id']}",
  "reroute_delay_days": {reroute_delay_days},
  "reroute_distance_nm": {alternate['distance_nm']},
  "similar_past_incidents": {precedents},
  "reasoning": "<your brief reasoning>"
}}
""",
            expected_output="A single JSON object matching the schema above.",
            agent=self.agent,
            output_pydantic=RouteOption
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        route_option: RouteOption = result.pydantic
        route_option.reroute_delay_days = reroute_delay_days
        route_option.reroute_distance_nm = float(alternate["distance_nm"])
        route_option.recommended_alternate_route_id = alternate["route_id"]
        route_option.similar_past_incidents = precedents

        return route_option

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the Logistics Router agent standalone.")
    parser.add_argument("--strait-id", type=str, default=None, help="Strait to evaluate. Defaults to the first strait in Dim_Strait.")
    args = parser.parse_args()

    strait_id = args.strait_id or get_first_strait_id()

    agent = LogisticsRouterAgent()
    result = agent.route(strait_id=strait_id)

    print("\n" + "=" * 60)
    print("ROUTE OPTION")
    print("=" * 60)
    print(result.model_dump_json(indent=2))