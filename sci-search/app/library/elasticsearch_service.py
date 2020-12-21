from elasticsearch import Elasticsearch

es = Elasticsearch()

INDEX = "index-2"
SUPPORTED_FIELDS = ["title", "content"]


def index_document(doc_id: int, content: str, title: str):
    es.index(INDEX, id=doc_id, body=_build_body(content, title))

def _build_body(content: str, title: str) -> dict:
    body = {"content": content, "title": title}
    print(body)
    return body


