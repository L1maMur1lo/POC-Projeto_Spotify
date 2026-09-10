from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from modules.shared.Settings import settings

__engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

__SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=__engine)


def get_session() -> Session:
    return __SessionLocal()
