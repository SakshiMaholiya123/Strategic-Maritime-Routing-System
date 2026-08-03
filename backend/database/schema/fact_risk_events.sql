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