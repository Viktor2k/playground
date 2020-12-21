from typing import List
import json
import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal, Base, engine
from .models import Document, Page, Field
from . import schemas
from .library import elasticsearch_service as elastic

from .dao.document_dao import DocumentDAO
from .library.document_service import DocumentService
from .library.arxiv_parser import parse_arxiv_metadata

Base.metadata.create_all(engine)

app = FastAPI()
document_dao = DocumentDAO()
document_service = DocumentService()


def get_db_return():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/docs/raw", response_model=schemas.Document)
def create_doc(doc: schemas.DocumentCreate, db: Session = Depends(get_db)):
    return document_dao.create_doc(db, doc)


@app.post("/docs/path", response_model=schemas.Document)
def create_doc_from_path(path: str, db: Session = Depends(get_db)):
    return document_service.create_doc(db, path)


@app.post("/docs/arxiv-folder", response_model=List[schemas.Document])
def create_docs_from_arxiv_folder(folder_path: str, db: Session = Depends(get_db)):
    documents = []

    metadata_file_path = os.path.join(folder_path, "metadata.json")
    if not os.path.isfile(metadata_file_path):
        raise HTTPException(status_code=404,
                            detail=f"Could not find metadata.json file in selected folder '{os.path.abspath(folder_path)}'")

    with open(metadata_file_path, "r") as metadata_file:
        for row in metadata_file:
            document = parse_arxiv_metadata(json.loads(row))
            try:
                documents.append(document_service.create_doc_with_fields(db, document["file_path"], document))
            except Exception as e:
                print(f"Failed to create document from file at path ${document['file_path']}!")
                print(e)

    return documents

@app.post("/docs/reindex", response_model=List[int])
def reindex_documents(db: Session = Depends(get_db)):
    elastic.empty_index()
    index_documents(db)

@app.post("/docs/index", response_model=List[int])
def index_documents(db: Session = Depends(get_db)):
    return document_service.index_all_documents(db)


@app.get("/docs/", response_model=List[schemas.Document])
def read_docs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return document_dao.get_docs(db, skip, limit)


@app.get("/docs/{doc_id}", response_model=schemas.Document)
def read_doc(doc_id: int, db: Session = Depends(get_db)):
    return document_dao.get_doc_from_id(db, doc_id)


@app.post("/docs/{doc_id}/title", response_model=schemas.Document)
def set_doc_title(doc_id: int, title: str, db: Session = Depends(get_db)):
    return document_dao.set_title_for_document(db, doc_id, title)


@app.post("/docs/{doc_id}/fields", response_model=schemas.Document)
def set_doc_fields(doc_id: int, fields: List[schemas.FieldBase], db: Session = Depends(get_db)):
    return document_dao.set_fields_for_document(db, doc_id, fields)


@app.post("/docs/{doc_id}/pages", response_model=schemas.Document)
def set_doc_pages(doc_id: int, pages: List[schemas.PageBase], db: Session = Depends(get_db)):
    return document_dao.set_pages_for_document(db, doc_id, pages)


@app.put("/docs/{doc_id}/fields", response_model=schemas.Document)
def replace_doc_fields(doc_id: int, fields: List[schemas.FieldBase], db: Session = Depends(get_db)):
    return document_dao.replace_fields_for_document(db, doc_id, fields)


@app.put("/docs/{doc_id}/pages", response_model=schemas.Document)
def replace_doc_pages(doc_id: int, pages: List[schemas.PageBase], db: Session = Depends(get_db)):
    return document_dao.replace_pages_for_document(db, doc_id, pages)


@app.delete("/docs/{doc_id}", response_model=schemas.Document)
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    return document_service.delete_doc(db, doc_id)


# def simple_main():
#     db = get_db_return()
#     db.add(Document(title = "First document", pages = [Page(page_number = 1, content = "First page content"), Page(page_number = 2, content = "Second Page")], fields = [Field(name = "name", value = "value")]))
#     db.commit()


# if __name__ == "__main__":
#     simple_main()
