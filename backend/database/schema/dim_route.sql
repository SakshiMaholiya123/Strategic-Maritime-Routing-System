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