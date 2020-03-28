import time
import logging

from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer

from utils import timer
from dataset import Dataset
from sentence_similarity import SentenceSimilarity


app = Flask(__name__)
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

dataset = timer(Dataset, 'data/quora/train_for_similarity.txt')
n = round(len(dataset)*0.1)

sentence_sim = timer(SentenceSimilarity, dataset=dataset, n_docs=n)

@app.route('/')
def home():
    return render_template('search.html')
#end def

@app.route('/search', methods=["GET", "POST"])
def search_request():
    query = request.form["input"]
    most_sim_doc_ids = sentence_sim.get_most_similar(query)
    most_sim_docs = dataset.get_documents_by_id(most_sim_doc_ids)

    hits = [{"body": doc} for doc in most_sim_docs]
    
    res = {}
    res['total'] = len(most_sim_doc_ids)
    res['hits'] = hits

    return render_template('results.html', res=res)
#end def

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
