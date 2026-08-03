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