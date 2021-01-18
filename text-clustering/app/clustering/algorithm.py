import pandas as pd
import texthero as hero
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter

CLEAN = "clean"
VALID = "valid"
RAW = "raw"
CLUSTER_ID = "cluster_id"

def main(file_path: str, column_name: str, threshold: int = 0.5) -> list[dict]:
    df = pd.DataFrame({RAW: list(pd.read_csv("../books.csv")["title"][:250])})
    preprocess(df, RAW)
    texts = df.clean.unique()

    X, texts = vectorize_and_validate(texts)
    D = distance(X)

    cluster_dict = run_optimal_clustering(texts, D, threshold)
    inverse_cluster_dict = inverse_map(cluster_dict)

    df[CLUSTER_ID] = df.apply(lambda row: find_cluster(row[CLEAN], inverse_cluster_dict), axis=1)

    c = Counter(list(df[CLUSTER_ID]))
    clusters_sorted_by_size = [cluster_id for (cluster_id, count) in c.most_common()]

    clusters = []
    for c in clusters_sorted_by_size:
        l = list(df[df[CLUSTER_ID] == c][RAW])
        clusters.append({"content": l, "count": len(l)})

    return clusters


def preprocess(df, col):
    df[CLEAN] = hero.clean(hero.remove_stopwords(df[col]))

def one_hot(x):
        return int(x != 0)

vec_one_hot = np.vectorize(one_hot)

def vectorize_and_validate(texts):
    X = vectorize(texts)
    valid_ids = [idx for (idx, x) in enumerate(X) if validate(x)]
    return X[valid_ids,:], texts[valid_ids]

count_vectorizer = CountVectorizer(ngram_range=(1,1), min_df=1, max_df=1.0)

def vectorize(text):
    X = count_vectorizer.fit_transform(text)
    return vec_one_hot(X.todense())

def validate(x):
    return np.sum(x) > 0

def distance(X):
    W = np.matmul(X, X.T)

    L = np.diag(W)
    L = np.tile(L, (L.size, 1))
    L = L+L.T

    return 2*np.divide(W,L)

def optimal_cluster_based_on_distance(texts, D, threshold):
    idx_larges_cluster = np.argmax(np.sum(D > threshold, axis=1))
    bool_idx = np.array(D[:,idx_larges_cluster] > threshold).reshape(1,-1)[0,:]
    idx = [i for i, b in enumerate(bool_idx) if b]
    if idx:
        cluster = list(texts[idx])

    all_idx = [i for i in range(len(texts))]
    remaining_idx = [i for i in all_idx if i not in idx]

    return texts[remaining_idx], D[remaining_idx][:, remaining_idx], cluster

def run_optimal_clustering(texts, D, threshold):
    all_clusters = {}
    for i in range(len(texts)):
        if len(texts) <= 1:
            all_clusters[len(all_clusters)] = list(texts)
            break

        texts, D, cluster = optimal_cluster_based_on_distance(texts, D, threshold)
        all_clusters[len(all_clusters)] = cluster

    return all_clusters

def inverse_map(dict_to_inverse):
    inverse = {}
    for key, values in dict_to_inverse.items():
        for v in values:
            inverse[v] = key
    return inverse

def find_cluster(text, clean_to_cluster_id):
    if text in clean_to_cluster_id:
        return clean_to_cluster_id[text]
    else:
        return -1

