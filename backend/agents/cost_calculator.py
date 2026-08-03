from backend.config import Config


def calculate_expected_cost_stay(cargo_value_usd: float, war_risk_premium_rate: float) -> float:
    """
    ExpectedCost(stay) = CargoValue x WarRiskPremiumRate
    """
    return cargo_value_usd * war_risk_premium_rate


def calculate_expected_cost_reroute(
    reroute_delay_days: int,
    cargo_value_usd: float,
    fuel_price_usd: float,
    fuel_consumption_tpd: float,
) -> dict:
    """
    ExpectedCost(reroute) = (RerouteDelayDays x DailyHoldingCost)
                            + SLAPenaltyExposure
                            + AdditionalFuelCost

    DailyHoldingCost and SLAPenaltyExposure are derived as configurable
    fractions of cargo value (DAILY_HOLDING_COST_RATE, SLA_PENALTY_RATE),
    a standard approximation when explicit contract terms aren't available.
    AdditionalFuelCost is computed from the vessel's real fuel consumption
    rate and the shipment's fuel price — not assumed.
    """

    daily_holding_cost = cargo_value_usd * Config.DAILY_HOLDING_COST_RATE
    sla_penalty_exposure = cargo_value_usd * Config.SLA_PENALTY_RATE
    additional_fuel_cost = reroute_delay_days * fuel_consumption_tpd * fuel_price_usd

    expected_cost_reroute = (
        (reroute_delay_days * daily_holding_cost)
        + sla_penalty_exposure
        + additional_fuel_cost
    )

    return {
        "daily_holding_cost_usd": daily_holding_cost,
        "sla_penalty_exposure_usd": sla_penalty_exposure,
        "additional_fuel_cost_usd": additional_fuel_cost,
        "expected_cost_reroute_usd": expected_cost_reroute,
    }