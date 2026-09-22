"""
Database connection setup.

This file creates:
1. The SQLAlchemy 'engine' - the actual connection to MySQL
2. A 'SessionLocal' factory - used to create a DB session per request
3. 'Base' - the class every model (table) will inherit from

Every FastAPI route that touches the DB will use `get_db()` below
as a dependency to get a session, use it, then close it automatically.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Example .env value:
# DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/lms_db
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Create a .env file in /server "
        "with DATABASE_URL=mysql+pymysql://user:password@localhost:3306/lms_db"
    )

# pool_pre_ping checks the connection is alive before using it -
# prevents "MySQL server has gone away" errors after idle time
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    FastAPI dependency. Yields a DB session and guarantees it closes
    after the request finishes, even if an error happens.

    Usage in a route:
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
