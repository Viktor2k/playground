from ..dao.document_dao import DocumentDAO
from .. import schemas
from . import elasticsearch_service as elastic

from typing import List
from sqlalchemy.orm import Session
import os

import tika
tika.initVM()

from io import StringIO
from bs4 import BeautifulSoup
from tika import parser


class DocumentService:

    def __init__(self):
        self.doc_dao = DocumentDAO()

    def get_content_from_document(self, doc: schemas.Document) -> str:
        return "\n\n".join([page.content for page in doc.pages])

    def get_field_values_by_name(self, doc: schemas.Document, field_name: str) -> List[str]:
        return [field.value for field in doc.doc_fields if field.name.lower() == field_name.lower()]

    def create_doc(self, db: Session, path: str) -> schemas.Document:
        pages = self._get_page_content_from_file_path(path)
        doc = schemas.DocumentCreate(title=self._get_file_name_from_path(path), pages=pages)

        db_doc = self.doc_dao.create_doc(db, doc)
        elastic.index_document(db_doc.id, self.get_content_from_document(db_doc), db_doc.title)

        return db_doc

    def create_doc_with_fields(self, db: Session, path: str, metadata: dict) -> schemas.Document:
        pages = self._get_page_content_from_file_path(path)
        fields = self._get_doc_fields_from_dict(metadata)
        doc = schemas.DocumentCreate(title=self._get_file_name_from_path(path), pages=pages, doc_fields=fields)

        db_doc = self.doc_dao.create_doc(db, doc)
        elastic.index_document(db_doc.id, self.get_content_from_document(db_doc), db_doc.title)

        return db_doc

    def update_doc(self, db: Session, doc_id: int, update_doc: schemas.DocumentCreate) -> schemas.Document:
        if update_doc.title:
            print(f"Updating title for document {doc_id}")
            self.doc_dao.set_title_for_document(db, doc_id, update_doc.title)

        if update_doc.doc_fields:
            print(f"Updating fields for document {doc_id}")
            self.doc_dao.set_fields_for_document(db, doc_id, update_doc.doc_fields)

        if update_doc.pages:
            print(f"Updating pages for document {doc_id}")
            self.doc_dao.set_pages_for_document(db, doc_id, update_doc.pages)

        db_doc = self.doc_dao.get_doc_from_id(db, doc_id)
        elastic.index_document(doc_id, self.get_content_from_document(db_doc), db_doc.title)
        return db_doc


    def delete_doc(self, db: Session, doc_id: int):
        self.doc_dao.delete_doc(db, doc_id)
        elastic.delete_document(doc_id)

    def index_all_documents(self, db: Session) -> List[int]:
        start_idx = 0
        doc_ids = []

        while True:
            docs = self.doc_dao.get_docs(db=db, skip=start_idx, limit=100)

            if not docs:
                break
            else:
                self.index_documents(docs)

            start_idx += len(docs)
            doc_ids.extend([doc.id for doc in docs])

        return doc_ids

    def index_documents(self, docs: List[schemas.Document]):
        for doc in docs:
            elastic.index_document(doc_id=doc.id, content=self.get_content_from_document(doc), title=doc.title)


    def _get_page_content_from_file_path(self, path: str) -> List[schemas.PageBase]:
        pages = []
        data = parser.from_file(path, xmlContent=True)
        xhtml_data = BeautifulSoup(data['content'])

        for page_number, content in enumerate(xhtml_data.find_all('div', attrs={'class': 'page'}), start=1):
            print(f"Parsing page {page_number} of pdf file...")
            _buffer = StringIO()
            _buffer.write(str(content))
            parsed_content = parser.from_buffer(_buffer.getvalue())

            pages.append(schemas.PageBase(page_number=page_number, content=parsed_content['content']))

        return pages

    def _get_file_name_from_path(self, path: str) -> str:
        return os.path.basename(path)

    def _get_doc_fields_from_dict(self, dictionary: dict) -> List[schemas.FieldBase]:
        return [schemas.FieldBase(name = key, value = value) for key, value in dictionary.items() if type(key) == str and type(value) == str]

