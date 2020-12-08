from .. import schemas, models
from sqlalchemy.orm import Session

from typing import List

class DocumentDAO:

    # Create    [x]
    # Read      [ ]
    # Update    [ ]
    # Delete    [ ]

    def create_doc(self, db: Session, doc: schemas.DocumentCreate) -> schemas.Document:
        pages = [models.Page(page_number=page.page_number, content=page.content) for page in doc.pages]
        fields = [models.Field(name=field.name, value=field.value) for field in doc.doc_fields]

        db_doc = models.Document(title=doc.title, pages=pages, fields=fields)
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc

    def get_docs(self, db: Session, skip, limit) -> List[schemas.Document]:
        return db.query(models.Document).offset(skip).limit(limit).all()

    def get_doc_from_id(self, db: Session, doc_id: int) -> schemas.Document: 
        return db.query(models.Document).get(doc_id)
    