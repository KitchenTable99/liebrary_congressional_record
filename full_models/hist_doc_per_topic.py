from top2vec import Top2Vec
from pprint import pprint
from bashplotlib.histogram import plot_hist
import sys
import numpy as np


def main():
    file = sys.argv[1]
    model = Top2Vec.load(file)
    sizes, _ = model.get_topic_sizes()
    topic_counts = dict(zip(*np.unique(sizes, return_counts=True)))
    # pprint(topic_counts)
    # print(type(topic_counts))
    hist_list = []
    for key, value in topic_counts.items():
        for _ in range(value):
            hist_list.append(key)

    plot_hist(hist_list, showSummary=True, bincount=150)


if __name__ == '__main__':
    main()
