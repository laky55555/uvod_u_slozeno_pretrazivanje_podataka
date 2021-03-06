import itertools
import os
import sys
import json

import matplotlib.pyplot as plt

from algorithms import *
from datasets import *


def main():
    interactive = False
    folder = 'tests'
    pdf = False


    _datasets = {
        'BIRCH': BIRCH,
        'PellegMoore': PellegMoore,
    }
    datasets = {}
    __dataset_commands = {
        '--birch': 'BIRCH',
        '--pellegmoore': 'PellegMoore',
        '--pm': 'PellegMoore'
    }


    _algorithms = {
        'K-Means': KMeans,
        'Gaussian Expectation Maximization': GaussianExpectationMaximization,
        'K-harmonic means': KHarmonicMeans,
        'Fuzzy K-Means': FuzzyKMeans,
        'Hybrid1': Hybrid1,
        'Hybrid2': Hybrid2
    }
    algorithms = {}
    __algorithm_commands = {
        '--kmeans': 'K-Means',
        '--km': 'K-Means',
        '--gem': 'Gaussian Expectation Maximization',
        '--khm': 'K-harmonic means',
        '--fkm': 'Fuzzy K-Means',
        '--h1': 'Hybrid1',
        '--h2': 'Hybrid2'
    }


    _initialization = {
        'Forgy': FindClusters.initialize_centroides_forgy,
        'Random Partition': FindClusters.initialize_centroides_random
    }
    initialization = {}
    __initialization_commands = {
        '--forgy': 'Forgy',
        '--rp': 'Random Partition'
    }

    # show plots when generated
    if '--interactive' in sys.argv[1:]:
        interactive = True

    if '--pdf' in sys.argv[1:]:
        pdf = True

    # number of iterations per algorithm
    iterations = 40
    if '--iterations' in sys.argv[1:]:
        i = sys.argv.index('--iterations')
        if i + 1 < len(sys.argv):
            iterations = int(sys.argv[i + 1])


    everything = [
        [datasets, _datasets, __dataset_commands],
        [algorithms, _algorithms, __algorithm_commands],
        [initialization, _initialization, __initialization_commands],
    ]

    for new, all, commands in everything:
        for command, key in commands.items():
            if command in sys.argv[1:]:
                new[key] = all[key]

        if not new:
            for key, value in all.items():
                new[key] = value

    # create tests root folder
    try:
        os.mkdir(folder)
    except OSError:
        pass

    # create test instance folder
    test_folder = None
    for r in itertools.count():
        rname = "%03d" % r
        if rname not in os.listdir(folder):
            test_folder = folder + '/' + rname
            os.mkdir(test_folder)
            break


    test_data = {
        'name': rname,
        'iterations': iterations,
        'algorithms': list(algorithms.keys()),
        'datasets': list(datasets.keys()),
        'initialization': list(initialization.keys())
    }

    with open(test_folder + '/test.json', 'w') as f:
        json.dump(
            test_data,
            f,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )

    print(
        json.dumps(test_data, sort_keys=True, indent=4, separators=(',', ': '))
    )

    for dname, d in datasets.items():
        dataset_folder = test_folder + '/' + dname
        os.mkdir(dataset_folder)

        dataset = d()
        for iname, i in initialization.items():
            initialization_folder = dataset_folder + '/' + iname
            os.mkdir(initialization_folder)

            initial_centroides = i(dataset.data_points, len(dataset.centroids))

            for aname, a in algorithms.items():
                algorithm_folder = initialization_folder + '/' + aname
                os.mkdir(algorithm_folder)
                
                solution_yield = a.test_algorithm_yield(
                    iterations,
                    initial_centroides,
                    dataset.data_points
                )
                
                test_data = []

                for step, i in enumerate(solution_yield):
                    dataset.check_calculated_centroids(i)
                    plt.figure()
                    plt.scatter(
                        dataset.data_points.T[0],
                        dataset.data_points.T[1],
                        c='#51975f',
                        marker='^',
                        edgecolor='#3B8049',
                        alpha=0.3
                    )

                    plt.scatter(
                        dataset.centroids.T[0],
                        dataset.centroids.T[1],
                        c='#DB3B3B',
                        marker='o',
                        edgecolor='#C73131'
                    )

                    plt.scatter(
                        i.T[0],
                        i.T[1],
                        c='#064291',
                        marker='s',
                        edgecolor='#123D75'
                    )

                    log_data = dataset.log_data
                    dataset.print_log_data()

                    log_data['step'] = step
                    test_data.append(log_data)

                    with open(algorithm_folder + '/results.json', 'w') as f:
                        json.dump(
                            test_data,
                            f,
                            sort_keys=True,
                            indent=4,
                            separators=(',', ': ')
                        )

                    number = "%03d" % step

                    if pdf:
                        plt.savefig(algorithm_folder + '/' + number + '.pdf')
                    
                    plt.savefig(algorithm_folder + '/' + number + '.jpg')

                    if interactive:
                        plt.show(block=False)
                    else:
                        plt.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
