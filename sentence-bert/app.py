from flask import Flask, render_template, request
from similiariy import SimMeasurer
from sentence_transformers import SentenceTransformer
from quora_dataset import QuoraDataset
import time

app = Flask(__name__)

def timer(f, *args, **kwargs):
    start = time.time()
    out = f(*args, **kwargs)
    print(f"Took {round(time.time() - start , 3)} to execute {f.__name__}")
    return out
#end def

model = timer(SentenceTransformer, 'bert-base-nli-stsb-mean-tokens')
dataset = timer(QuoraDataset, 'data/quora/train.csv')

documents = dataset.get_documents(n=25)

sim = SimMeasurer(documents)

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]
    most_sim, scores = sim.get_most_similar(search_term, n=10)

    res = {}
    res['total'] = len(most_sim)
    hits = []
    for t, s in zip(most_sim, scores):
        hits.append({"score": round(s, 3), "body": t})
    res['hits'] = hits

    return render_template('results.html', res=res )

@app.route('/doc/search/results', methods=['GET', 'POST'])
def doc_search_request():
    search_term = request.form["input"]
    top_documents, scores = sim.get_most_similar_doc(search_term, n=5)
    print(top_documents)
    res = {}
    res['total'] = len(top_documents)
    hits = []
    for t, s in zip(top_documents, scores):
        hits.append({"score": round(s, 3), "body": '\n\n'.join(t)})
    res['hits'] = hits
    
    return render_template('results.html', res=res )

@app.route("/doc", methods=['GET'])
def list_docs():
    docs = sim.documents
    print(docs)
    return render_template('list.html', res={"total": len(docs), "docs": [' --- '.join(d) for d in docs] })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
