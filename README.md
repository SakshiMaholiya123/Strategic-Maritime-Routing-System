# Strategic-Maritime-Routing-System

A multi-agent pipeline that fuses structured transit/cost data with unstructured geopolitical intelligence to compute — not debate — the lowest expected-cost routing decision for cargo transiting a contested maritime chokepoint, with a full audit trail from source document to final number.

## Problem

When a chokepoint like the Strait of Hormuz sees a spike in geopolitical tension, a logistics team must decide, same-day, whether to pay a war-risk insurance premium to continue on the direct route or absorb the cost and schedule impact of a multi-day reroute. This decision is normally made by manually synthesizing fast-moving unstructured intelligence (news, insurer bulletins, security advisories) against structured transit-cost data, under time pressure, with no consistent methodology and no audit trail connecting a routing decision back to the intelligence that justified it.

## Solution

Three independent agents each produce a **typed, citation-backed estimate** — never a freeform recommendation:

| Agent | Output | Data Source |
|---|---|---|
| **Risk Assessor** | Disruption probability, confidence range, cited source documents | ChromaDB (`geopolitical_intel`) — recency- and supersession-aware retrieval |
| **Logistics Router** | Best alternate route, reroute delay/distance, similar past precedents | PostgreSQL (`Dim_Route`, `Fact_TransitLegs`) + ChromaDB (`past_routing_precedents`) |
| **Financial Modeler** | Expected cost to stay vs. reroute | PostgreSQL (`Fact_TransitLegs`) + `insurance.csv` |

A **deterministic Decision Engine** — a plain Python function, not an LLM consensus process — applies a fixed expected-cost-minimization formula to the three agents' structured outputs and computes the final routing recommendation. Agent disagreement above a configured tolerance, or a decision above a configured cargo-value threshold, routes to a **mandatory human-approval step** in Streamlit rather than resolving itself through further LLM debate.

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Risk Assessor   │     │  Logistics Router     │     │ Financial Modeler│
│  (ChromaDB RAG)  │     │  (PostgreSQL + Chroma)│     │  (PostgreSQL+CSV)│
└────────┬─────────┘     └──────────┬────────────┘     └────────┬────────┘
         │                          │                            │
         └──────────────┬───────────┴──────────────┬─────────────┘
                         ▼                          ▼
                 ┌───────────────────────────────────────┐
                 │      Deterministic Decision Engine      │
                 │  ExpectedCost(stay) vs ExpectedCost(reroute) │
                 │      + divergence / threshold checks     │
                 └───────────────────┬─────────────────────┘
                                     ▼
                    ┌─────────────────────────────────┐
                    │  Auto-approved  OR  Human Gate    │
                    │  (Streamlit approval screen)      │
                    └────────────────┬───────────────────┘
                                     ▼
                    Fact_RiskEvents / Fact_RoutingDecisions
                    + narrative summary → past_routing_precedents
```

### Decision Logic

```
ExpectedCost(stay)    = CargoValue × WarRiskPremiumRate
ExpectedCost(reroute) = (RerouteDelayDays × DailyHoldingCost)
                         + SLAPenaltyExposure
                         + AdditionalFuelCost
```

The engine selects whichever option has the lower expected cost. Agents produce the inputs to this formula (premium rate, delay days, penalty exposure) — they never argue over the arithmetic.

### Human-in-the-Loop Quality Gate

Two independent conditions trigger mandatory Streamlit approval:

1. The Risk Assessor's confidence-weighted probability range spreads wider than `DIVERGENCE_TOLERANCE`.
2. The shipment's cargo value exceeds `HUMAN_APPROVAL_CARGO_THRESHOLD_USD`.

In either case, the Decision Engine's provisional recommendation, its full numeric inputs, and the cited source documents are surfaced together before the decision is finalized.

## Database Design

A Kimball star schema in PostgreSQL:

- **`Fact_TransitLegs`** — one row per vessel-route-leg shipment
- **`Fact_RiskEvents`** — one row per risk assessment computed for a strait
- **`Fact_RoutingDecisions`** — one row per finalized routing decision
- **`Dim_Strait` / `Dim_Vessel` / `Dim_Route` / `Dim_Port` / `Dim_Date`** — supporting dimensions

Every fact table that feeds or records a decision links back to the specific source evidence that informed it.

### Vector Memory (ChromaDB)

- **`geopolitical_intel`** — one embedding per intelligence report chunk. Metadata: `{strait_id, report_date, source_type, severity, supersedes, superseded_by}`. Queried with a `superseded_by` filter, then re-ranked by `score × exp(−age_days / half_life)` computed in Python — recency is enforced structurally, not left to embedding similarity alone.
- **`past_routing_precedents`** — one embedding per past routing decision's narrative summary. Metadata: `{strait_id, chosen_option, decision_date}`. Queried by the Logistics Router (top-k, filtered by strait) as supporting context — not as a substitute for the Decision Engine's own calculation.

## Project Structure

```
backend/
├── config.py                    # All tunables — no hardcoded values
├── database/
│   ├── build_schema.py          # Single source of truth for the schema
│   ├── create_database.py       # SQLAlchemy engine/session
│   └── crud.py
├── etl/                         # Dimension + fact table loaders
│   ├── generate_date_dimension.py
│   ├── load_dim_port.py
│   ├── load_dim_route.py
│   ├── load_dim_vessel.py
│   ├── seed_straits.py
│   └── load_fact_transit_legs.py
├── rag/                         # ChromaDB ingestion pipeline
│   ├── loader.py                # PDF loading + metadata enrichment
│   ├── splitter.py
│   ├── embedder.py
│   ├── vector_store.py          # geopolitical_intel collection builder
│   └── retriever.py             # Filtered + recency-decay re-ranked retrieval
├── agents/
│   ├── schemas.py               # Pydantic output contracts for all 3 agents
│   ├── db_queries.py            # Route lookups (pure SQL, no LLM)
│   ├── financial_queries.py     # Shipment/insurance lookups (pure SQL/CSV)
│   ├── precedents_retriever.py  # past_routing_precedents lookups
│   ├── context_builder.py       # Citation-context formatting
│   ├── cost_calculator.py       # Fixed expected-cost formula
│   ├── risk_assessor.py
│   ├── logistics_router.py
│   └── financial_modeler.py
├── decision_engine/
│   ├── engine.py                # Orchestrates all 3 agents + fixed decision rule
│   └── db_writer.py             # Persists Fact_RiskEvents / Fact_RoutingDecisions
├── precedents/
│   └── precedent_writer.py      # Writes decision summaries back to ChromaDB
└── knowledge_base/
    ├── chroma_db/                # Persisted vector store
    └── reports/                  # Source PDFs (imo, security, unctad, weather, world_bank, port_reports)

datasets/
├── raw/                          # Source CSVs
└── processed/                    # Cleaned ports/routes/vessels/shipments/insurance CSVs

frontend/
└── streamlit_app.py              # Input form + human-approval gate + decisions dashboard
```

## Setup

### 1. Environment

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
GROQ_API_KEY=your_groq_key
MISTRAL_API_KEY=your_mistral_key
GROQ_MODEL=groq/llama-3.3-70b-versatile
DAILY_HOLDING_COST_RATE=0.0015
SLA_PENALTY_RATE=0.01
DIVERGENCE_TOLERANCE=0.3
HUMAN_APPROVAL_CARGO_THRESHOLD_USD=2000000
PRECEDENTS_TOP_K=3
```

### 2. Build the database schema

```bash
python -m backend.database.build_schema
```

### 3. Load dimension and fact data

```bash
python -m backend.etl.generate_date_dimension
python -m backend.etl.load_dim_port
python -m backend.etl.load_dim_route
python -m backend.etl.load_dim_vessel
python -m backend.etl.seed_straits
python -m backend.etl.load_fact_transit_legs
```

### 4. Build the vector store

```bash
python -m backend.rag.vector_store
```

### 5. Run the full pipeline (CLI)

```bash
python -m backend.decision_engine.engine
```

### 6. Run the frontend

```bash
streamlit run frontend/streamlit_app.py
```

## Key Design Decisions

- **Deterministic decision-making over LLM consensus.** Early designs let agents "debate" to a routing consensus; this produced non-deterministic, contradictory recommendations on identical inputs. The fix was to make agents produce independent structured estimates and hand the actual arithmetic to a fixed Python formula — the same inputs now always produce the same output.
- **Recency enforced structurally, not assumed.** A semantically similar but outdated intelligence report is a realistic failure mode for any RAG-based risk system. Retrieval is filtered on `superseded_by` and re-ranked by an explicit `exp(-age_days / half_life)` decay computed in Python, not left to embedding similarity alone.
- **The same quality-gate pattern used everywhere.** Human review is triggered by a deterministic divergence check or a dollar threshold — never by an agent's self-reported confidence.
- **No hardcoded business inputs.** Model names, cost-rate assumptions, approval thresholds, and test shipment/strait IDs all resolve from `Config` or the database at runtime.

## Notes on Data

Structured transit/freight data (routes, vessels, shipments, insurance premiums) and the geopolitical intelligence corpus are provisioned as two separate, purpose-built feeds — the former synthetically generated for this project, the latter built from real, publicly available reports (IMO, UNCTAD, World Bank, security advisories). No single, formally published "Hormuz Strait Supply Chain Disruption Dataset" exists publicly; this design treats that honestly rather than asserting an unverifiable source.