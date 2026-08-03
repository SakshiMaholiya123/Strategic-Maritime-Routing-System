
import sys
from pathlib import Path
# Allow running via `streamlit run frontend/streamlit_app.py` from project root
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
import streamlit as st
from sqlalchemy import text

from backend.database.create_database import engine
from backend.decision_engine.engine import run_decision_pipeline


st.set_page_config(
    page_title="Strategic Maritime Disruption & Routing Simulator",
    page_icon="🚢",
    layout="wide",
)

@st.cache_data(ttl=300)
def load_shipment_options() -> pd.DataFrame:
    query = text("""
        SELECT f.shipment_id, f.cargo_value_usd, f.product_type,
               f.shipment_status, r.canal_used
        FROM maritime.fact_transitlegs f
        JOIN maritime.dim_route r ON f.routekey = r.routekey
        ORDER BY f.shipment_id
    """)
    with engine.begin() as connection:
        return pd.read_sql(query, connection)


@st.cache_data(ttl=300)
def load_strait_options() -> list:

    query = text("""
        SELECT DISTINCT s.strait_name
        FROM maritime.dim_strait s
        JOIN maritime.dim_route r
          ON r.canal_used ILIKE '%' || s.strait_name || '%'
        ORDER BY s.strait_name
    """)
    with engine.begin() as connection:
        result = pd.read_sql(query, connection)
    return result["strait_name"].tolist()


@st.cache_data(ttl=60)
def load_recent_decisions(limit: int = 10) -> pd.DataFrame:
    query = text("""
        SELECT d.decisionkey, f.shipment_id, d.decision,
               d.confidence_score, d.estimated_savings_usd, d.decision_date
        FROM maritime.fact_routingdecisions d
        JOIN maritime.fact_transitlegs f ON d.transitlegkey = f.transitlegkey
        ORDER BY d.decision_date DESC
        LIMIT :limit
    """)
    with engine.begin() as connection:
        return pd.read_sql(query, connection, params={"limit": limit})

#sidebar



st.sidebar.title("🚢 Routing Simulator")

shipments = load_shipment_options()
straits = load_strait_options()

if shipments.empty:
    st.sidebar.error("No shipments found in Fact_TransitLegs. Run the ETL loaders first.")
    st.stop()

if not straits:
    st.sidebar.error("No routable straits found. Check Dim_Strait / Dim_Route canal_used matching.")
    st.stop()

shipment_id = st.sidebar.selectbox("Shipment", options=shipments["shipment_id"].tolist())

selected_shipment_row = shipments[shipments["shipment_id"] == shipment_id].iloc[0]

strait_default_index = 0
matching_strait = next((s for s in straits if s in str(selected_shipment_row["canal_used"])), None)
if matching_strait:
    strait_default_index = straits.index(matching_strait)

strait_id = st.sidebar.selectbox("Strait / Chokepoint", options=straits, index=strait_default_index)

run_clicked = st.sidebar.button("🔍 Run Decision Pipeline", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"Cargo Value: **${selected_shipment_row['cargo_value_usd']:,.2f}**")
st.sidebar.caption(f"Product: **{selected_shipment_row['product_type']}**")
st.sidebar.caption(f"Status: **{selected_shipment_row['shipment_status']}**")


# Main area

st.title("Strategic Maritime Disruption & Routing Simulator")
st.caption(
    "Three independent agents (Risk Assessor, Logistics Router, Financial Modeler) "
    "produce structured estimates. A deterministic Decision Engine — not an LLM "
    "consensus process — computes the minimum-expected-cost routing recommendation."
)

if "decision_result" not in st.session_state:
    st.session_state.decision_result = None

if "approval_decision" not in st.session_state:
    st.session_state.approval_decision = None


if run_clicked:
    with st.spinner("Running Risk Assessor, Logistics Router, and Financial Modeler..."):
        try:
            result = run_decision_pipeline(shipment_id=shipment_id, strait_id=strait_id)
            st.session_state.decision_result = result
            st.session_state.approval_decision = None
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.session_state.decision_result = None


result = st.session_state.decision_result

if result is None:
    st.info("Select a shipment and strait in the sidebar, then click **Run Decision Pipeline**.")

else:

    col1, col2, col3 = st.columns(3)
    col1.metric("Disruption Risk", f"{result.risk_probability:.0%}",
                help=f"Confidence range: {result.confidence_low:.0%} – {result.confidence_high:.0%}")
    col2.metric("Recommended Option", result.final_decision.upper())
    col3.metric("Estimated Savings", f"${result.estimated_savings_usd:,.2f}")

    st.markdown("---")

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.subheader("💰 Expected Cost — Stay")
        st.metric("", f"${result.expected_cost_stay_usd:,.2f}")

    with cost_col2:
        st.subheader("💰 Expected Cost — Reroute")
        st.metric("", f"${result.expected_cost_reroute_usd:,.2f}")

    st.markdown("---")

    # Human-in-the-loop approval gate 

    if result.requires_human_approval and st.session_state.approval_decision is None:

        st.warning(
            "⚠️ **Human approval required.** This decision triggered a quality gate: "
            f"{result.approval_reason}"
        )

        st.markdown("**Provisional recommendation:** " + result.final_decision.upper())
        st.markdown(f"**Cargo value at stake:** ${result.cargo_value_usd:,.2f}")

        approve_col, reject_col = st.columns(2)

        with approve_col:
            if st.button("✅ Approve Recommendation", use_container_width=True):
                st.session_state.approval_decision = "approved"
                st.rerun()

        with reject_col:
            if st.button("❌ Reject / Escalate", use_container_width=True):
                st.session_state.approval_decision = "rejected"
                st.rerun()

    elif result.requires_human_approval and st.session_state.approval_decision is not None:

        if st.session_state.approval_decision == "approved":
            st.success(f"✅ Decision approved: **{result.final_decision.upper()}**")
        else:
            st.error("❌ Decision rejected — escalated for manual review.")

    else:
        st.success(f"✅ Auto-approved: {result.approval_reason}")

    st.markdown("---")

    # Audit trail

    with st.expander("📋 Full Audit Trail"):
        st.json({
            "shipment_id": result.shipment_id,
            "strait_id": result.strait_id,
            "risk_probability": result.risk_probability,
            "confidence_range": [result.confidence_low, result.confidence_high],
            "expected_cost_stay_usd": result.expected_cost_stay_usd,
            "expected_cost_reroute_usd": result.expected_cost_reroute_usd,
            "estimated_savings_usd": result.estimated_savings_usd,
            "cargo_value_usd": result.cargo_value_usd,
            "risk_event_key": result.risk_event_key,
            "routing_decision_key": result.routing_decision_key,
        })


# Recent decisions dashboard
st.markdown("---")
st.subheader("📊 Recent Routing Decisions")

recent = load_recent_decisions()

if recent.empty:
    st.caption("No decisions logged yet.")
else:
    st.dataframe(
        recent.rename(columns={
            "shipment_id": "Shipment",
            "decision": "Decision",
            "confidence_score": "Confidence",
            "estimated_savings_usd": "Savings ($)",
            "decision_date": "Date",
        }).drop(columns=["decisionkey"]),
        use_container_width=True,
        hide_index=True,
    )