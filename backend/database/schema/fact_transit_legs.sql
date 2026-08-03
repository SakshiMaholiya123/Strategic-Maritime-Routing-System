CREATE TABLE Fact_TransitLegs (
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