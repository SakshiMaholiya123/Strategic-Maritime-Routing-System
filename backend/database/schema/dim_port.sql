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