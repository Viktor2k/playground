from .database import SessionLocal, Base, engine
from . import models

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def main():
    db = get_db()
    db.add(models.Document(title = "First document", pages = [models.Page(page_number = 1, content = "First page content"), models.Page(page_number = 2, content = "Second Page")], fields = [models.Field(name = "name", value = "value")]))
    db.commit()


if __name__ == "__main__":
    main()

