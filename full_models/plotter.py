import pickle
import os
import matplotlib.pyplot as plt
import umap.plot


def main():
    files = os.listdir()
    for file in files:
        if not file.startswith('umap') or not file.endswith('.pickle'):
            continue
        with open(file, 'rb') as fp:
            umap_model = pickle.load(fp)
        # with open('topic_nums.pickle', 'rb') as fp:
        #     topic_nums = pickle.load(fp)

        # umap.plot.points(umap_model, theme='fire')
        # umap.plot.connectivity(umap_model, edge_bundling='hammer')
        print(file)
        umap.plot.diagnostic(umap_model, diagnostic_type='local_dim')
        plt.show()


if __name__ == "__main__":
    main()
