import csv

class QuoraDataset():
    def __init__(self, file_path):
        self.file_path = file_path
        self.dict_data = self._read_from_file()

        self.len = len(self.dict_data)
    #end def

    def _read_from_file(self):
        with open(self.file_path, 'r') as f:
            reader = csv.DictReader(f)
            dict_data = [row for row in reader]

        return dict_data
    #end def

    def get_questions(self, n=-1):
        id_to_body = {}
        for row in self.dict_data:
            for idx in [1,2]:
                id_to_body[row.get(f'qid{idx}', -1)] = row.get(f'question{idx}')
                if len(id_to_body) >= n and n != -1:
                    return list(id_to_body.values())
                #end if
            #end for
        #end for

        return list(id_to_body.values())
    #end def

    def get_documents(self, n=-1):
        documents = []
        for row in self.dict_data:
            if int(row.get('is_duplicate')):
                sentences = [row.get(f'question{idx}') for idx in [1,2]] 
                documents.append(sentences)
            else:
                for idx in [1,2]:
                    documents.append([row.get(f'question{idx}')])
            #end if

            if len(documents) >= n and n != -1:
                return documents
            #end if
        #end for

        return documents

    def __len__(self):
        return self.len
    #end def

    def __str__(self):
        return f"I am a collection of {self.len} question pairs from path {self.file_path}"
    #end def


#end class   