from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from pathlib import Path


def _database_url(url: str) -> str:
    if not url.startswith("sqlite:///") or url.startswith("sqlite:////"):
        return url
    relative = url.removeprefix("sqlite:///")
    root = Path(__file__).resolve().parents[3]
    path = Path(relative)
    if not path.is_absolute():
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


engine = create_engine(
    _database_url(settings.database_url),
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
