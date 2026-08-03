from sqlalchemy import text
from backend.database.create_database import engine

schema_steps = [

    # Schema
    "CREATE SCHEMA IF NOT EXISTS maritime;",

    # Dim_Date
    """
    CREATE TABLE maritime.Dim_Date (
        DateKey INTEGER PRIMARY KEY,
        Full_Date DATE UNIQUE,
        Day_Number INTEGER,
        Day_Name VARCHAR(20),
        Week_Number INTEGER,
        Month_Number INTEGER,
        Month_Name VARCHAR(20),
        Quarter INTEGER,
        Year INTEGER,
        Is_Weekend BOOLEAN
    );
    """,

    # Dim_Port
    """
    CREATE TABLE maritime.Dim_Port (
        PortKey SERIAL PRIMARY KEY,
        Port_ID VARCHAR(20) UNIQUE NOT NULL,
        Port_Name VARCHAR(100) NOT NULL,
        Country VARCHAR(100),
        Port_Type VARCHAR(50),
        Port_Capacity_Tons BIGINT,
        Avg_Vessel_Wait_Time_Hours NUMERIC(6,2),
        Port_Utilization_Percent NUMERIC(5,2),
        Active_Vessels INTEGER,
        Weather_Disruption_Score NUMERIC(5,2),
        Labor_Availability_Percent NUMERIC(5,2),
        Monthly_Port_Revenue_USD NUMERIC(18,2),
        Operational_Status VARCHAR(30),
        Port_Manager VARCHAR(100),
        Last_Inspection_Date DATE,
        Latitude DECIMAL(9,6),
        Longitude DECIMAL(9,6)
    );
    """,

    # Dim_Route
    """
    CREATE TABLE maritime.Dim_Route (
        RouteKey SERIAL PRIMARY KEY,
        Route_ID VARCHAR(20) UNIQUE NOT NULL,
        Origin_Port_ID VARCHAR(20),
        Destination_Port_ID VARCHAR(20),
        Route_Name VARCHAR(200),
        Distance_NM NUMERIC(10,2),
        Expected_Days INTEGER,
        Risk_Zone VARCHAR(30),
        Canal_Used VARCHAR(100),
        Weather_Risk VARCHAR(30)
    );
    """,

    # Dim_Strait
    """
    CREATE TABLE maritime.Dim_Strait (
        StraitKey SERIAL PRIMARY KEY,
        Strait_Name VARCHAR(100) UNIQUE NOT NULL,
        Region VARCHAR(100),
        Risk_Level VARCHAR(30),
        Typical_Daily_Transit INTEGER
    );
    """,

    # Dim_Vessel
    """
    CREATE TABLE maritime.Dim_Vessel (
        VesselKey SERIAL PRIMARY KEY,
        Vessel_ID VARCHAR(20) UNIQUE NOT NULL,
        Vessel_Name VARCHAR(100),
        IMO_Number BIGINT UNIQUE,
        Vessel_Type VARCHAR(50),
        Capacity_Tons INTEGER,
        Fuel_Consumption_TPD NUMERIC(6,2),
        Max_Speed_Knots NUMERIC(5,2),
        Current_Status VARCHAR(30),
        Home_Port_ID VARCHAR(20),
        Year_Built INTEGER,
        Crew_Size INTEGER
    );
    """,

    # Fact_TransitLegs
    """
    CREATE TABLE maritime.Fact_TransitLegs (
        TransitLegKey SERIAL PRIMARY KEY,
        Shipment_ID VARCHAR(30) UNIQUE NOT NULL,
        VesselKey INTEGER NOT NULL,
        RouteKey INTEGER NOT NULL,
        OriginPortKey INTEGER NOT NULL,
        DestinationPortKey INTEGER NOT NULL,
        ShipmentDateKey INTEGER NOT NULL,
        Supplier_ID VARCHAR(30),
        Country VARCHAR(100),
        Product_Type VARCHAR(100),
        Monthly_Demand_Tons NUMERIC(12,2),
        Shipment_Volume_Tons NUMERIC(12,2),
        Route_Risk_Score NUMERIC(5,2),
        Historical_Delay_Days INTEGER,
        Fuel_Price_USD NUMERIC(10,2),
        Political_Risk_Index NUMERIC(5,2),
        Port_Congestion_Index NUMERIC(5,2),
        Inventory_Days INTEGER,
        Supplier_Reliability NUMERIC(5,2),
        Alternative_Supplier_Count INTEGER,
        Transit_Time_Days INTEGER,
        Delay_Probability NUMERIC(5,2),
        Current_Delay_Days INTEGER,
        Freight_Cost_USD NUMERIC(18,2),
        Revenue_Impact_USD NUMERIC(18,2),
        Disruption_Event VARCHAR(100),
        Cargo_Value_USD NUMERIC(18,2),
        Shipment_Status VARCHAR(30),
        Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT fk_transit_vessel
            FOREIGN KEY (VesselKey)
            REFERENCES maritime.Dim_Vessel(VesselKey),

        CONSTRAINT fk_transit_route
            FOREIGN KEY (RouteKey)
            REFERENCES maritime.Dim_Route(RouteKey),

        CONSTRAINT fk_transit_origin
            FOREIGN KEY (OriginPortKey)
            REFERENCES maritime.Dim_Port(PortKey),

        CONSTRAINT fk_transit_destination
            FOREIGN KEY (DestinationPortKey)
            REFERENCES maritime.Dim_Port(PortKey),

        CONSTRAINT fk_transit_date
            FOREIGN KEY (ShipmentDateKey)
            REFERENCES maritime.Dim_Date(DateKey)
    );
    """,

    # Fact_RiskEvents
    """
    CREATE TABLE maritime.Fact_RiskEvents (
        RiskEventKey SERIAL PRIMARY KEY,
        StraitKey INTEGER,
        DateKey INTEGER,
        RouteKey INTEGER,
        Risk_Level VARCHAR(30),
        Disruption_Probability NUMERIC(5,2),
        Estimated_Delay_Days INTEGER,
        Estimated_Extra_Cost_USD NUMERIC(18,2),
        Source_Report VARCHAR(255),

        CONSTRAINT fk_risk_strait
            FOREIGN KEY (StraitKey)
            REFERENCES maritime.Dim_Strait(StraitKey),

        CONSTRAINT fk_risk_date
            FOREIGN KEY (DateKey)
            REFERENCES maritime.Dim_Date(DateKey),

        CONSTRAINT fk_risk_route
            FOREIGN KEY (RouteKey)
            REFERENCES maritime.Dim_Route(RouteKey)
    );
    """,

    # Fact_RoutingDecisions
    """
    CREATE TABLE maritime.Fact_RoutingDecisions (
        DecisionKey SERIAL PRIMARY KEY,
        TransitLegKey INTEGER,
        RiskEventKey INTEGER,
        Decision_Date TIMESTAMP,
        Recommended_Route VARCHAR(200),
        Decision VARCHAR(100),
        Confidence_Score NUMERIC(5,2),
        Estimated_Savings_USD NUMERIC(18,2),
        Generated_By VARCHAR(100),

        CONSTRAINT fk_decision_leg
            FOREIGN KEY (TransitLegKey)
            REFERENCES maritime.Fact_TransitLegs(TransitLegKey),

        CONSTRAINT fk_decision_risk
            FOREIGN KEY (RiskEventKey)
            REFERENCES maritime.Fact_RiskEvents(RiskEventKey)
    );
    """,

    # Indexes
    "CREATE INDEX idx_port_id ON maritime.Dim_Port(Port_ID);",
    "CREATE INDEX idx_vessel_id ON maritime.Dim_Vessel(Vessel_ID);",
    "CREATE INDEX idx_route_id ON maritime.Dim_Route(Route_ID);",
    "CREATE INDEX idx_strait_name ON maritime.Dim_Strait(Strait_Name);",
    "CREATE INDEX idx_shipment_id ON maritime.Fact_TransitLegs(Shipment_ID);",
    "CREATE INDEX idx_transit_vessel ON maritime.Fact_TransitLegs(VesselKey);",
    "CREATE INDEX idx_transit_route ON maritime.Fact_TransitLegs(RouteKey);",
    "CREATE INDEX idx_transit_status ON maritime.Fact_TransitLegs(Shipment_Status);",
    "CREATE INDEX idx_transit_product ON maritime.Fact_TransitLegs(Product_Type);",
    "CREATE INDEX idx_transit_supplier ON maritime.Fact_TransitLegs(Supplier_ID);",
    "CREATE INDEX idx_transit_country ON maritime.Fact_TransitLegs(Country);",
    "CREATE INDEX idx_transit_date ON maritime.Fact_TransitLegs(ShipmentDateKey);",
    "CREATE INDEX idx_risk_strait ON maritime.Fact_RiskEvents(StraitKey);",
    "CREATE INDEX idx_risk_route ON maritime.Fact_RiskEvents(RouteKey);",
    "CREATE INDEX idx_decision_leg ON maritime.Fact_RoutingDecisions(TransitLegKey);",
    "CREATE INDEX idx_decision_risk ON maritime.Fact_RoutingDecisions(RiskEventKey);",

]

with engine.begin() as connection:
    for i, step in enumerate(schema_steps, start=1):
        connection.execute(text(step))
        print(f"Step {i}/{len(schema_steps)} executed successfully")

print("=" * 60)
print("Schema Build Completed Successfully")
print("Tables Created: Dim_Date, Dim_Port, Dim_Route, Dim_Strait,")
print("                Dim_Vessel, Fact_TransitLegs, Fact_RiskEvents,")
print("                Fact_RoutingDecisions")
print("=" * 60)