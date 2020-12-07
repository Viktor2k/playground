from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy import Column, Integer, String, ForeignKey

from .database import Base

class Field(Base):
    __tablename__ = "field"

    id = Column(Integer, primary_key = True)
    name = Column(String)
    value = Column(String)
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="fields")

    def __str__(self):
        return f"Id:   {self.id}\nName:  {self.name}\nValue: {self.value}"

class Page(Base):
    __tablename__ = "page"

    id = Column(Integer, primary_key = True)
    page_number = Column(Integer)
    content = Column(String)
    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship("Document", back_populates='pages')
    
    def __str__(self):
        return f"Id:           {self.id}\nPage number: {self.page_number}\nDocument:    {self.document_id}\nContent:     {self.content}"

class Document(Base):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    pages = relationship(
        "Page",
        order_by = Page.id,
        back_populates = "document",
        cascade = "all, delete, delete-orphan"
    )

    fields = relationship(
        "Field",
        order_by = Field.name,
        back_populates = "document",
        cascade = "all, delete, delete-orphan"
    )
    
    def __str__(self):
        return f"Id:      {self.id}\nTitle:   {self.title}"

