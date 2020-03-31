from dataset import Dataset
from sentence_similarity import SentenceSimilarity

data = Dataset('data/quora/quora_example.txt')
sentence_sim = SentenceSimilarity(data)

most_similar = sentence_sim.get_most_similar("How is it possible for machines to learn?")
print("\n".join(most_similar))