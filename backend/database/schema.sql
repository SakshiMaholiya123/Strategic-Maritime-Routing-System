CREATE SCHEMA IF NOT EXISTS maritime;

SET search_path TO maritime;

-- DROP TABLE IF EXISTS Fact_RoutingDecisions CASCADE;
-- DROP TABLE IF EXISTS Fact_RiskEvents CASCADE;
-- DROP TABLE IF EXISTS Fact_TransitLegs CASCADE;

-- DROP TABLE IF EXISTS Dim_Date CASCADE;
-- DROP TABLE IF EXISTS Dim_Strait CASCADE;
-- DROP TABLE IF EXISTS Dim_Route CASCADE;
-- DROP TABLE IF EXISTS Dim_Vessel CASCADE;
-- DROP TABLE IF EXISTS Dim_Port CASCADE



-- DIMENSION TABLE : PORT


CREATE TABLE Dim_Port (

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


-- DIMENSION TABLE : VESSEL


CREATE TABLE Dim_Vessel (

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


-- DIMENSION TABLE : ROUTE


CREATE TABLE Dim_Route (

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

-- DIMENSION TABLE : DATE


CREATE TABLE Dim_Date (

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

-- DIMENSION TABLE : STRAIT


CREATE TABLE Dim_Strait (

    StraitKey SERIAL PRIMARY KEY,

    Strait_Name VARCHAR(100) UNIQUE,

    Region VARCHAR(100),

    Risk_Level VARCHAR(30),

    Typical_Daily_Transit INTEGER
);


-- FACT TABLE : TRANSIT LEGS


CREATE TABLE Fact_TransitLegs (

    TransitLegKey SERIAL PRIMARY KEY,

    Shipment_ID VARCHAR(30),

    VesselKey INTEGER,

    RouteKey INTEGER,

    OriginPortKey INTEGER,

    DestinationPortKey INTEGER,

    ShipmentDateKey INTEGER,

    Cargo_Value_USD NUMERIC(18,2),

    Quantity INTEGER,

    Transportation_Cost_USD NUMERIC(18,2),

    Delay_Days INTEGER,

    Shipment_Status VARCHAR(30),

    CONSTRAINT fk_transit_vessel
        FOREIGN KEY (VesselKey)
        REFERENCES Dim_Vessel(VesselKey),

    CONSTRAINT fk_transit_route
        FOREIGN KEY (RouteKey)
        REFERENCES Dim_Route(RouteKey),

    CONSTRAINT fk_transit_origin
        FOREIGN KEY (OriginPortKey)
        REFERENCES Dim_Port(PortKey),

    CONSTRAINT fk_transit_destination
        FOREIGN KEY (DestinationPortKey)
        REFERENCES Dim_Port(PortKey),

    CONSTRAINT fk_transit_date
        FOREIGN KEY (ShipmentDateKey)
        REFERENCES Dim_Date(DateKey)
);

-- FACT TABLE : RISK EVENTS

CREATE TABLE Fact_RiskEvents (

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
        REFERENCES Dim_Strait(StraitKey),

    CONSTRAINT fk_risk_date
        FOREIGN KEY (DateKey)
        REFERENCES Dim_Date(DateKey),

    CONSTRAINT fk_risk_route
        FOREIGN KEY (RouteKey)
        REFERENCES Dim_Route(RouteKey)
);

-- FACT TABLE : ROUTING DECISIONS


CREATE TABLE Fact_RoutingDecisions (

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
        REFERENCES Fact_TransitLegs(TransitLegKey),

    CONSTRAINT fk_decision_risk
        FOREIGN KEY (RiskEventKey)
        REFERENCES Fact_RiskEvents(RiskEventKey)
);


-- INDEXES


CREATE INDEX idx_port_id
ON Dim_Port(Port_ID);

CREATE INDEX idx_vessel_id
ON Dim_Vessel(Vessel_ID);

CREATE INDEX idx_route_id
ON Dim_Route(Route_ID);

CREATE INDEX idx_shipment_id
ON Fact_TransitLegs(Shipment_ID);

CREATE INDEX idx_risk_route
ON Fact_RiskEvents(RouteKey);

CREATE INDEX idx_decision_leg
ON Fact_RoutingDecisions(TransitLegKey);
