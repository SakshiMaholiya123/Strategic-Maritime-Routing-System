from crewai import Agent, Task, Crew
from crewai.llm import LLM

from backend.config import Config
from backend.rag.retriever import MaritimeRetriever
from backend.agents.schemas import RiskAssessment
from backend.agents.context_builder import build_citation_context, resolve_cited_sources

import argparse
from backend.agents.db_queries import get_first_strait_id 


class RiskAssessorAgent:
    """
    Assesses disruption risk for a given strait using recency- and
    supersession-aware ChromaDB retrieval, returning a typed
    RiskAssessment (never freeform text).
    """

    def __init__(self):

        self.retriever = MaritimeRetriever()

        self.llm = LLM(
            model=Config.GROQ_MODEL,
            api_key=Config.GROQ_API_KEY,
            temperature=0
        )

        self.agent = Agent(
            role="Maritime Risk Assessor",
            goal=(
                "Assess the current disruption risk for a maritime chokepoint "
                "using ONLY the retrieved intelligence reports provided, and "
                "output a structured, citation-backed risk estimate."
            ),
            backstory=(
                "You are a maritime intelligence analyst. You never speculate "
                "beyond the evidence given to you, and you always cite the "
                "specific report(s) that support each number you produce."
            ),
            llm=self.llm,
            verbose=True
        )

    def assess(self, strait_id: str, query: str) -> RiskAssessment:

        documents = self.retriever.retrieve_documents(
            query=query,
            strait_id=strait_id
        )

        if not documents:
            return RiskAssessment(
                strait_id=strait_id,
                risk_probability=0.0,
                confidence_low=0.0,
                confidence_high=0.0,
                estimated_delay_days=0,
                severity_level=1,
                reasoning="No relevant intelligence reports were retrieved for this query.",
                cited_doc_ids=[]
            )

        context_block, doc_id_map = build_citation_context(documents)

        task = Task(
            description=f"""
Using ONLY the intelligence reports below, assess the disruption risk
for {strait_id}.

Reports:
{context_block}

Question: {query}

Return your assessment strictly as this JSON structure and nothing else:

{{
  "strait_id": "{strait_id}",
  "risk_probability": <float 0-1>,
  "confidence_low": <float 0-1>,
  "confidence_high": <float 0-1>,
  "estimated_delay_days": <int>,
  "severity_level": <int 1-5>,
  "reasoning": "<short justification citing DOC-n labels>",
  "cited_doc_ids": ["DOC-1", "DOC-3"]
}}

Only cite DOC-n labels that you actually used to support a number.
""",
            expected_output="A single JSON object matching the schema above.",
            agent=self.agent,
            output_pydantic=RiskAssessment
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        assessment: RiskAssessment = result.pydantic
        assessment.cited_doc_ids = resolve_cited_sources(assessment.cited_doc_ids, doc_id_map)

        return assessment

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the Risk Assessor agent standalone.")
    parser.add_argument("--strait-id", type=str, default=None, help="Strait to assess. Defaults to the first strait in Dim_Strait.")
    args = parser.parse_args()

    strait_id = args.strait_id or get_first_strait_id()

    agent = RiskAssessorAgent()
    query = f"What is the current geopolitical risk of disruption in {strait_id}?"

    result = agent.assess(strait_id=strait_id, query=query)

    print("\n" + "=" * 60)
    print("RISK ASSESSMENT")
    print("=" * 60)
    print(result.model_dump_json(indent=2))