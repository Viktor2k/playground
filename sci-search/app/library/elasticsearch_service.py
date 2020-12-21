from elasticsearch import Elasticsearch

es = Elasticsearch()

INDEX = "index-2"
SUPPORTED_FIELDS = ["title", "content"]


def empty_index():
    es.delete_by_query(index=INDEX, body={"query": {"match_all": {}}})

def delete_document(doc_id: int):
    es.delete(INDEX, id=doc_id)

def index_document(doc_id: int, content: str, title: str):
    es.index(INDEX, id=doc_id, body=_build_body(content, title))

def _build_body(content: str, title: str) -> dict:
    body = {"content": content, "title": title}
    return body


