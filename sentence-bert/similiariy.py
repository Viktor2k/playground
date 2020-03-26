import csv
import json
import time
from typing import List

import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

class SimMeasurer():
    def __init__(self, documents : List[List[str]], model:SentenceTransformer = None):
        self.documents = documents 
        self.sentences, self.sentence_idx_to_doc_idx = self._transform_input(self.documents)
        
        # Load model or default
        if not model:
            self.model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
        else:
            self.model = model

        self.embedded_sentences = self.model.encode(self.sentences)
        
        self.precomputed_norm = norm(self.embedded_sentences, axis=1)
    #end def

    def _transform_input(self, documents: List[List[str]]):
        sentence_idx_to_doc_idx = {}
        sentences = []

        for doc_idx, doc in enumerate(documents):
            for s in doc:
                sentence_idx = len(sentences)
                sentences.append(s)
                sentence_idx_to_doc_idx[sentence_idx] = doc_idx
            #end for
        #end for

        return sentences, sentence_idx_to_doc_idx

    def matrix_cosine_sim(self, query_vector):
        # Query needs to be 2d row vector
        query_norm = norm(query_vector)        

        prod = np.ndarray.flatten(np.matmul(self.embedded_sentences, query_vector))
        #vector_norm = np.ndarray.flatten((query_norm * self.precomputed_norm))

        cosine_sim = np.divide(prod, query_norm * self.precomputed_norm)
        return cosine_sim
    #end def

    def get_n_most_similar(self, query_vector, n=1):
        similarity_scores = self.matrix_cosine_sim(query_vector)

        top_idx = []
        top_scores = []
        for i in range(n):
            idx = np.argmax(similarity_scores)
            score = similarity_scores[idx]

            top_idx.append(idx)
            top_scores.append(score)

            similarity_scores[idx] = 0
        #end for

        return top_idx, top_scores
    #end def

    def get_most_similar(self, query, n=3, scores=False):
        start = time.time()
        query_vector = np.reshape(self.model.encode([query]), (-1,1))
        top_idx, scores = self.get_n_most_similar(query_vector, n)
        print(f'Took {round(time.time()-start, 3)} s to encode query and find {n} most similar sentences')

        if scores:
            return [self.sentences[t] for t in top_idx], scores
        else:
            return [self.sentences[t] for t in top_idx]
    #end def

    def get_most_similar_doc(self, query, n=3, scores=False):
        start = time.time()

        query_vector = np.reshape(self.model.encode([query]), (-1,1))
        top_sentence_idx, scores = self.get_n_most_similar(query_vector, n)

        top_document_idx = [self.sentence_idx_to_doc_idx[s_idx] for s_idx in top_sentence_idx]

        top_documents = [self.documents[d_idx] for d_idx in top_document_idx]

        print(f'Took {round(time.time()-start, 3)} s to encode query and find {n} most similar document')

        if scores:
            return top_documents, scores
        else:
            return top_documents
    #end def

#end class
