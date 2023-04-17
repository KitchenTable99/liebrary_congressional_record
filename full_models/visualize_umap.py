import umap.plot
from tqdm import tqdm
import pickle
import umap
from top2vec import Top2Vec
import os


def main():
    for file in tqdm(os.listdir()):
        if not file.endswith('.model'):
            continue

        model = Top2Vec.load(file)
        umap_args = {
            "n_neighbors": 15,
            "n_components": 2, # 5 -> 2 for plotting
            "metric": "cosine",
        }
        umap_model = umap.UMAP(**umap_args).fit(model.document_vectors)

        with open(f'umap_{file.split(".")[0]}.pickle', 'wb') as fp:
            pickle.dump(umap_model, fp)


if __name__ == "__main__":
    main()
