from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Абсолютный путь до корня проекта (например, fastapi/project)
BASE_DIR = Path(__file__).resolve().parent.parent / "dipclub"
DB_PATH = BASE_DIR / "db.sqlite3"

# Подключение к SQLite базе
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Для SQLite обязательно указывать check_same_thread=False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Сессия для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс моделей
Base = declarative_base()
