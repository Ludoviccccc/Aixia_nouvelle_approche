from sentence_transformers import SentenceTransformer
import os
sentences = ["This is an example sentence", "Each sentence is converted"]



root = os.environ['DSDIR'] + '/HuggingFace_Models'
model_name = root + '/' + 'sentence-transformers/all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)
embeddings = model.encode(sentences)
print(embeddings)

