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