from pathlib import Path

import pandas as pd
from sqlalchemy import text

from backend.config import Config
from backend.database.create_database import engine


def get_sample_shipment_id() -> str:
    """
    Fetch any one existing Shipment_ID from Fact_TransitLegs,
    for use as a default/demo input — avoids hardcoding a
    specific shipment ID anywhere in the codebase.
    """

    query = text("""
        SELECT shipment_id
        FROM maritime.fact_transitlegs
        LIMIT 1
    """)

    with engine.begin() as connection:
        result = pd.read_sql(query, connection)

    if result.empty:
        raise ValueError("No shipments found in Fact_TransitLegs")

    return result.iloc[0]["shipment_id"]


def get_shipment_financials(shipment_id: str) -> pd.Series:
    """
    Fetch cargo value, fuel price, route, and vessel for a shipment
    from Fact_TransitLegs.
    """

    query = text("""
        SELECT f.shipment_id, f.cargo_value_usd, f.fuel_price_usd,
               r.route_id, r.canal_used, v.fuel_consumption_tpd
        FROM maritime.fact_transitlegs f
        JOIN maritime.dim_route r ON f.routekey = r.routekey
        JOIN maritime.dim_vessel v ON f.vesselkey = v.vesselkey
        WHERE f.shipment_id = :shipment_id
    """)

    with engine.begin() as connection:
        result = pd.read_sql(query, connection, params={"shipment_id": shipment_id})

    if result.empty:
        raise ValueError(f"Shipment {shipment_id} not found in Fact_TransitLegs")

    return result.iloc[0]


def get_war_risk_premium_rate(route_id: str) -> float:
    """
    Look up the war-risk insurance premium rate for a route from
    insurance.csv (Premium_Percentage). Falls back with a clear
    error if no exact Route_ID match exists.
    """

    insurance = pd.read_csv(Config.DATASET_PATH / "insurance.csv")

    match = insurance[insurance["Route_ID"] == route_id]

    if match.empty:
        raise ValueError(f"No insurance record found for route {route_id}")

    return float(match.iloc[0]["Premium_Percentage"]) / 100

def get_sample_shipment_id() -> str:
    """
    Fetch any one existing Shipment_ID from Fact_TransitLegs,
    for use as a default/demo input — avoids hardcoding a
    specific shipment ID anywhere in the codebase.
    """

    query = text("""
        SELECT shipment_id
        FROM maritime.fact_transitlegs
        LIMIT 1
    """)

    with engine.begin() as connection:
        result = pd.read_sql(query, connection)

    if result.empty:
        raise ValueError("No shipments found in Fact_TransitLegs")

    return result.iloc[0]["shipment_id"]