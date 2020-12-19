from ..dao.document_dao import DocumentDAO
from .. import schemas, models
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

    def create_doc(self, db: Session, path: str) -> schemas.Document:
        pages = self._get_page_content_from_file_path(path)
        doc = schemas.DocumentCreate(title=self._get_file_name_from_path(path), pages=pages)

        return self.doc_dao.create_doc(db, doc)

    def create_doc_with_fields(self, db: Session, path: str, metadata: dict) -> schemas.Document:
        pages = self._get_page_content_from_file_path(path)
        fields = self._get_doc_fields_from_dict(metadata)
        doc = schemas.DocumentCreate(title=self._get_file_name_from_path(path), pages=pages, doc_fields=fields)

        return self.doc_dao.create_doc(db, doc)

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
