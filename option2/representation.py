from sentence_transformers import SentenceTransformer
import os

class Representation:
    def __init__(self):
        root = os.environ['DSDIR'] + '/HuggingFace_Models'
        model_name = root + '/' + 'sentence-transformers/all-MiniLM-L6-v2'
        self.model = SentenceTransformer(model_name)
    def __call__(self,x):
        embeddings = self.model.encode(sentences)
        return embeddings
    def update(self,x=None):
        pass

representation = Representation()
sentences = ["This is an example sentence", "Each sentence is converted"]
print(representation(sentences))

