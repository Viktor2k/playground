from typing import List, Optional
from pydantic import BaseModel


class FieldBase(BaseModel):
    name: str
    value: str

class Field(FieldBase):
    id: int
    
    class Config:
        orm_mode = True



class PageBase(BaseModel):
    page_number: int
    content: str

class Page(PageBase):
    id: int

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    title: str
    doc_fields: List[Field] = [] 
    pages: List[Page] = []

class DocumentCreate(DocumentBase):
    doc_fields: List[FieldBase] = [] 
    pages: List[PageBase] = []

class Document(DocumentBase):
    id: int
    
    class Config:
        orm_mode = True


