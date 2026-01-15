import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class DatabaseConnection:
    """Handles database connections for the recruitment system"""

    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "sqlite")
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_engine(self):
        """Create database engine based on configuration"""
        if self.db_type == "sqlite":
            db_path = os.getenv("SQLITE_DB_PATH", "recruitment.db")
            connection_string = f"sqlite:///{db_path}"
            print(f"Using SQLite database: {db_path}")

        elif self.db_type == "mysql":
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "3306")
            db_name = os.getenv("DB_NAME", "recruitment_db")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")

            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            print(f"Using MySQL database: {db_name}")

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

        return create_engine(connection_string, echo=False)

    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()

    def init_database(self):
        """Initialize database with schema"""
        print("Initializing database schema...")

        # Use SQLite-specific schema if using SQLite
        if self.db_type == "sqlite":
            schema_file = "schema_sqlite.sql"
        else:
            schema_file = "schema.sql"

        schema_path = os.path.join(os.path.dirname(__file__), schema_file)

        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

                with self.engine.begin() as conn:
                    for statement in statements:
                        if statement:
                            try:
                                conn.execute(text(statement))
                            except Exception as e:
                                print(f"Warning executing statement: {e}")

            print("Database schema initialized successfully!")
        else:
            print(f"Schema file not found at {schema_path}")

    def execute_query(self, query, params=None):
        """Execute a raw SQL query"""
        with self.engine.begin() as conn:
            result = conn.execute(text(query), params or {})
            return result

    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()

    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchone()

# Global database instance
db = DatabaseConnection()

def get_db():
    """Dependency for getting database sessions"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
