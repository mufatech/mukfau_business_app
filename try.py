import sys
from sqlalchemy import create_engine

def check_db_version(db_url):
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            if "postgresql" in db_url:
                version = connection.execute("SELECT version();").fetchone()
            elif "mysql" in db_url:
                version = connection.execute("SELECT VERSION();").fetchone()
            elif "sqlite" in db_url:
                version = connection.execute("SELECT sqlite_version();").fetchone()
            else:
                print("Unsupported database type.")
                return

            print(f"Database Version: {version[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_version_checker.py <DATABASE_URL>")
    else:
        db_url = sys.argv[1]
        check_db_version(db_url)
