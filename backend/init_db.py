"""Create application tables in DATABASE_URL."""
from backend.database import create_tables
if __name__ == "__main__":
    create_tables(); print("Database schema is ready")
