from typing import AnyStr, List

class Dataset():
    def __init__(self, file_path: AnyStr):
        self.file_path = file_path
        self.data = self._read_from_file()

        self.len = len(self.data)
    #end def

    def _read_from_file(self) -> List[dict]:
        with open(self.file_path, 'r') as f:
            return [{"id" : row_id, "text" : row.replace("\n", "")} for row_id, row in enumerate(f.readlines())]
    #end def

    def get_documents_by_id(self, doc_ids: List[int]) -> List[str]:
        return [self.data[doc_id]["text"] for doc_id in doc_ids]
    
    def get_documents(self, n: int = -1) -> dict:
        for i, row in enumerate(self.data):
            if i == n:
                break
            yield row
            
    def __len__(self):
        return self.len
    #end def

    def __str__(self):
        return f"I am a collection of {self.len} question pairs from path {self.file_path}"
    #end def
#end class
