
FIELDS_TO_KEEP = [
    "id",
    "updated",
    "published",
    "title",
    "summary",
    "authors",
    "author",
    "arxiv_primary_category",
    "tags",
    "pdf_url",
    "arxiv_url",
    "journal_reference",
    "file_path"
]

DICT_KEY_NAME = "term"

def parse_arxiv_metadata(metadata: dict) -> dict:
    parsed_metadata = {}
    for key, value in metadata.items():
        if key not in FIELDS_TO_KEEP or not value:
            continue

        if type(value) == str:
            parsed_metadata[key] = value

        elif type(value) == list:
            first_item = value[0]
            if type(first_item) == str:
                parsed_metadata[key] = ";".join(value)

            elif type(first_item) == dict:
                parsed_metadata[key] = ";".join([v.get(DICT_KEY_NAME) for v in value])


        elif type(value) == dict:
            parsed_metadata[key] = value.get(DICT_KEY_NAME)

    return parsed_metadata

