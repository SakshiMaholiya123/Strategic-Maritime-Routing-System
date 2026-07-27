from sqlalchemy import text

from backend.database.create_database import engine

try:
    with engine.connect() as connection:

        result = connection.execute(text("SELECT version();"))

        print(result.fetchone()[0])

        print("\nDatabase Connected Successfully!")

except Exception as e:

    print("Connection Failed")

    print(e)