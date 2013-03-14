from utils import jsonize_phrase_dict
import json
import matplotlib.pyplot as plt
from os.path import join

def plot_phrase_frequencies(phrase_frequencies, output_path=None):
    if output_path:
        jsonized_frequencies = jsonize_phrase_dict(phrase_frequencies)
        frequencies_descending = sorted(jsonized_frequencies, key=lambda d: d['frequency'], reverse=True)
        with open(join(output_path, 'phrase_frequencies_sorted'), 'w') as f:
            f.write(json.dumps(frequencies_descending, indent=4))
        with open(join(output_path, 'phrase_frequencies_dict'), 'w') as f:
            f.write(json.dumps(jsonized_frequencies, indent=4))

    plt.figure(0)
    frequencies = phrase_frequencies.values()
    plt.hist(frequencies, bins=max(frequencies))
    plt.xlabel('number of occurrences')
    plt.ylabel('number of terms')
    plt.title('Histogram of Term Frequencies')
    plt.savefig(join(output_path,'phrase_frequencies_all.pdf'), bbox_inches=0)

    plt.figure(1)
    frequencies = phrase_frequencies.values()
    plt.hist(frequencies, bins=9, range=(1,10))
    plt.xlabel('number of occurrences')
    plt.ylabel('number of terms')
    plt.title('Histogram of Term Frequencies (few occurrences)')
    plt.savefig(join(output_path,'phrase_frequencies_top.pdf'), bbox_inches=0)
