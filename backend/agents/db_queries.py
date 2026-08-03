from typing import Optional

import pandas as pd
from sqlalchemy import text

from backend.database.create_database import engine


def find_route_through_strait(strait_id: str) -> Optional[str]:
    """
    Dynamically find a route currently passing through the given
    strait/chokepoint, by matching canal_used against the strait name.
    """

    query = text("""
        SELECT route_id
        FROM maritime.dim_route
        WHERE canal_used ILIKE :strait_pattern
        LIMIT 1
    """)

    with engine.begin() as connection:
        result = pd.read_sql(
            query, connection, params={"strait_pattern": f"%{strait_id}%"}
        )

    return None if result.empty else result.iloc[0]["route_id"]


def get_route(route_id: str) -> pd.Series:

    query = text("""
        SELECT route_id, origin_port_id, destination_port_id,
               distance_nm, expected_days, risk_zone, canal_used, weather_risk
        FROM maritime.dim_route
        WHERE route_id = :route_id
    """)

    with engine.begin() as connection:
        result = pd.read_sql(query, connection, params={"route_id": route_id})

    if result.empty:
        raise ValueError(f"Route {route_id} not found in Dim_Route")

    return result.iloc[0]


from typing import Optional

import pandas as pd
from sqlalchemy import text

from backend.database.create_database import engine


def find_route_through_strait(strait_id: str) -> Optional[str]:
    """
    Dynamically find a route currently passing through the given
    strait/chokepoint, by matching canal_used against the strait name.
    """

    query = text("""
        SELECT route_id
        FROM maritime.dim_route
        WHERE canal_used ILIKE :strait_pattern
        LIMIT 1
    """)

    with engine.begin() as connection:
        result = pd.read_sql(
            query, connection, params={"strait_pattern": f"%{strait_id}%"}
        )

    return None if result.empty else result.iloc[0]["route_id"]


def get_route(route_id: str) -> pd.Series:

    query = text("""
        SELECT route_id, origin_port_id, destination_port_id,
               distance_nm, expected_days, risk_zone, canal_used, weather_risk
        FROM maritime.dim_route
        WHERE route_id = :route_id
    """)

    with engine.begin() as connection:
        result = pd.read_sql(query, connection, params={"route_id": route_id})

    if result.empty:
        raise ValueError(f"Route {route_id} not found in Dim_Route")

    return result.iloc[0]


def get_best_alternate(current_route: pd.Series) -> Optional[pd.Series]:
    """
    Best alternate route that avoids the current route's canal/chokepoint,
    preferring the shortest distance among all candidates. Does NOT require
    the same origin/destination pair, since a real-world reroute around a
    chokepoint commonly means taking a structurally different passage
    (e.g. Cape of Good Hope instead of Suez), not just an alternate route
    between the identical two ports.
    """

    query = text("""
        SELECT route_id, origin_port_id, destination_port_id,
               distance_nm, expected_days, risk_zone, canal_used, weather_risk
        FROM maritime.dim_route
        WHERE route_id != :current_route_id
          AND (canal_used IS DISTINCT FROM :current_canal)
        ORDER BY distance_nm ASC
        LIMIT 1
    """)

    with engine.begin() as connection:
        result = pd.read_sql(
            query,
            connection,
            params={
                "current_route_id": current_route["route_id"],
                "current_canal": current_route["canal_used"],
            }
        )

    return None if result.empty else result.iloc[0]


def get_first_strait_id() -> str:
    """
    Return one existing Strait_Name from Dim_Strait.
    Used only as a fallback default for standalone/CLI runs.
    """

    query = text("SELECT strait_name FROM maritime.dim_strait LIMIT 1")

    with engine.begin() as connection:
        result = pd.read_sql(query, connection)

    if result.empty:
        raise ValueError("No straits found in Dim_Strait.")

    return result.iloc[0]["strait_name"]