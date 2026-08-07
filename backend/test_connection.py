from backend.database.create_database import engine
from sqlalchemy import text 

try:
    with engine.connect() as conn:
        
        result = conn.execute(text("SELECT 1"))
        print("Database Connected Successfully")

except Exception as e:
    print("Connection Failed")
    print(e)