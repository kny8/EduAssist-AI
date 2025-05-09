from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

host = "aws-0-ap-southeast-1.pooler.supabase.com"
database = "postgres"
user = "postgres.cjvmmuhnjgiprsdlgpap"
password = "GLFaXGqrwiwCjps0"
port = 6543
# schema = os.getenv("DB_SCHEMA")


SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Create-engine part remains the same, so this is not necessary in generator.
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=10,  # Adjust this according to your system
                       max_overflow=20,  # Allow some overflow connections beyond pool_size
                       pool_timeout=30,  # Timeout for getting a connection from the pool
                       pool_recycle=1800,  # Recycle connections after 30 minutes
                       pool_pre_ping=True,
                       # This is the suggested method to pre-check a connection after picking from a pool
                       # echo=True
                       )
print(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
