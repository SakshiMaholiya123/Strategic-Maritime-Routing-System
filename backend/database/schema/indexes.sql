CREATE INDEX idx_port_id ON Dim_Port(Port_ID);
CREATE INDEX idx_vessel_id ON Dim_Vessel(Vessel_ID);
CREATE INDEX idx_route_id ON Dim_Route(Route_ID);
CREATE INDEX idx_strait_name ON Dim_Strait(Strait_Name);

CREATE INDEX idx_shipment_id ON Fact_TransitLegs(Shipment_ID);
CREATE INDEX idx_transit_vessel ON Fact_TransitLegs(VesselKey);
CREATE INDEX idx_transit_route ON Fact_TransitLegs(RouteKey);
CREATE INDEX idx_transit_status ON Fact_TransitLegs(Shipment_Status);
CREATE INDEX idx_transit_product ON Fact_TransitLegs(Product_Type);
CREATE INDEX idx_transit_supplier ON Fact_TransitLegs(Supplier_ID);
CREATE INDEX idx_transit_country ON Fact_TransitLegs(Country);
CREATE INDEX idx_transit_date ON Fact_TransitLegs(ShipmentDateKey);

CREATE INDEX idx_risk_strait ON Fact_RiskEvents(StraitKey);
CREATE INDEX idx_risk_route ON Fact_RiskEvents(RouteKey);
CREATE INDEX idx_decision_leg ON Fact_RoutingDecisions(TransitLegKey);
CREATE INDEX idx_decision_risk ON Fact_RoutingDecisions(RiskEventKey);