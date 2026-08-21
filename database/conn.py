from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
try:
    engine = create_engine(settings.DATABASE_URL)
except Exception as e:
    print(f'{e}')
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine, autoflush=False, autocommit= False)

def get_db():
    with Session() as session:
        yield session