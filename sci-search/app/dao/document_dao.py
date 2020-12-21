from .. import schemas, models
from sqlalchemy.orm import Session

from fastapi import HTTPException

from typing import List

class DocumentDAO:

    def create_doc(self, db: Session, doc: schemas.DocumentCreate) -> schemas.Document:
        db_doc = models.Document(title=doc.title)
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        doc_id = db_doc.id

        self.set_fields_for_document(db, doc_id, doc.doc_fields)
        self.set_pages_for_document(db, doc_id, doc.pages)

        return db_doc

    def get_docs(self, db: Session, skip, limit) -> List[schemas.Document]:
        return db.query(models.Document).offset(skip).limit(limit).all()

    def get_doc_from_id(self, db: Session, doc_id: int) -> schemas.Document:
        db_doc = db.query(models.Document).get(doc_id)
        if db_doc is None:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")
        
        return db_doc
    
    def set_title_for_document(self, db: Session, doc_id: int, title: str) -> schemas.Document:
        db_doc = self.get_doc_from_id(db, doc_id)
        db_doc.title = title
        db.commit()
        return db_doc

    def set_fields_for_document(self, db: Session, doc_id: int, fields: List[schemas.FieldBase]) -> schemas.Document:
        for f in fields: 
            self.set_field_for_document(db, doc_id, f) 
        
        return self.get_doc_from_id(db, doc_id)
    
    def set_field_for_document(self, db: Session, doc_id: int, field: schemas.FieldBase) -> schemas.Field:
        db_field = models.Field(**field.dict(), document_id=doc_id)
        db.add(db_field)
        db.commit()
        db.refresh(db_field)
        return db_field

    def set_pages_for_document(self, db: Session, doc_id: int, pages: List[schemas.PageBase]) -> schemas.Document:
        for p in pages:
            self.set_page_for_document(db, doc_id, p)

        return self.get_doc_from_id(db, doc_id)

    def set_page_for_document(self, db: Session, doc_id: int, page: schemas.PageBase) -> schemas.Page:
        db_page = models.Page(**page.dict(), document_id=doc_id)
        db.add(db_page)
        db.commit()
        db.refresh(db_page)
        return db_page
    
    def replace_fields_for_document(self, db: Session, doc_id: int, fields: List[schemas.FieldBase]) -> schemas.Document:
        self.delete_document_fields(db, doc_id)
        return self.set_fields_for_document(db, doc_id, fields)
    
    def replace_pages_for_document(self, db: Session, doc_id: int, pages: List[schemas.PageBase]):
        self.delete_document_pages(db, doc_id)
        return self.set_pages_for_document(db, doc_id, pages)

    def delete_document_fields(self, db: Session, doc_id: int):
        db_fields = self.get_doc_from_id(db, doc_id).doc_fields
        for f in db_fields:
            db.delete(f)
        db.commit()

    def delete_document_pages(self, db: Session, doc_id: int):
        db_pages = self.get_doc_from_id(db, doc_id).pages
        for p in db_pages:
            db.delete(p)
        db.commit()


    def delete_doc(self, db: Session, doc_id: int) -> schemas.Document:
        db_doc = self.get_doc_from_id(db, doc_id)
        db.delete(db_doc)
        db.commit()
        
        return db_doc




