from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.db.database import SessionLocal


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()