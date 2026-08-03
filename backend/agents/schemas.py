from typing import List, Optional
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    """
    Structured output of the Risk Assessor agent.
    Never a freeform recommendation — always a typed estimate
    with a citation trail back to the source documents.
    """

    strait_id: str = Field(description="Name of the maritime chokepoint assessed")

    risk_probability: float = Field(
        ge=0, le=1,
        description="Point estimate of disruption probability (0-1)"
    )

    confidence_low: float = Field(
        ge=0, le=1,
        description="Lower bound of the confidence-weighted probability range"
    )

    confidence_high: float = Field(
        ge=0, le=1,
        description="Upper bound of the confidence-weighted probability range"
    )

    estimated_delay_days: int = Field(
        ge=0,
        description="Estimated additional delay in days if disruption occurs"
    )

    severity_level: int = Field(
        ge=1, le=5,
        description="Overall severity rating derived from cited reports"
    )

    reasoning: str = Field(
        description="Brief justification grounded only in the cited reports"
    )

    cited_doc_ids: List[str] = Field(
        description="Chroma document/source IDs that informed this estimate"
    )


class RouteOption(BaseModel):
    """
    Structured output of the Logistics Router agent.
    Compares the current route against the best viable alternate,
    informed by structured route data and similar past precedents.
    """

    strait_id: str = Field(description="Chokepoint being evaluated")

    current_route_id: str = Field(description="Route ID currently in use")

    recommended_alternate_route_id: Optional[str] = Field(
        default=None,
        description="Route ID of the best alternate if rerouting is viable"
    )

    reroute_delay_days: int = Field(
        ge=0,
        description="Additional transit days if rerouting vs current route"
    )

    reroute_distance_nm: float = Field(
        ge=0,
        description="Distance in nautical miles of the alternate route"
    )

    similar_past_incidents: List[str] = Field(
        default_factory=list,
        description="Summaries of similar past routing decisions on this strait, if any"
    )

    reasoning: str = Field(
        description="Justification for the recommended route option"
    )

class CostEstimate(BaseModel):
    """
    Structured output of the Financial Modeler agent.
    The cost numbers are computed deterministically in Python —
    the LLM only explains the comparison, never recalculates it.
    """

    shipment_id: str = Field(description="Shipment being evaluated")

    cargo_value_usd: float = Field(ge=0)

    war_risk_premium_rate: float = Field(
        ge=0, description="Insurance premium as a fraction of cargo value (e.g. 0.02 = 2%)"
    )

    expected_cost_stay_usd: float = Field(
        ge=0, description="CargoValue x WarRiskPremiumRate"
    )

    reroute_delay_days: int = Field(ge=0)

    daily_holding_cost_usd: float = Field(ge=0)

    sla_penalty_exposure_usd: float = Field(ge=0)

    additional_fuel_cost_usd: float = Field(ge=0)

    expected_cost_reroute_usd: float = Field(
        ge=0, description="(RerouteDelayDays x DailyHoldingCost) + SLAPenaltyExposure + AdditionalFuelCost"
    )

    recommended_option: str = Field(
        description="'stay' or 'reroute' — whichever has the lower expected cost"
    )

    reasoning: str = Field(
        description="Brief explanation grounded only in the numbers above"
    )