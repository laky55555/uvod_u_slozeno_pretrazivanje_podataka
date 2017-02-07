from abc import ABCMeta, abstractmethod
from math import sqrt
from numpy.random import multivariate_normal, rand, randint
from numpy.linalg import norm
from numpy import array, identity, sum, mean
from algorithms import KMeans


class DataSet(metaclass=ABCMeta):

    @abstractmethod
    def create_centroides(self):
        ...

    @abstractmethod
    def create_data_points(self):
        ...

    @abstractmethod
    def check_calculated_centroids(self, calculated_centroids):
        ...

    def create_point(self, mean, covariance, number_of_points):
        return multivariate_normal(mean, covariance, number_of_points)


class PellegMoore(DataSet):
    """Class for constructing dataset for testing clustering algorithms ."""

    coefficient = 0.00012

    def __init__(self, dimension=2, number_of_points=2500, number_of_clusters=50, deviation_coefficient=0.012):
        self.__dict__.update(locals())

        self.create_centroides()
        self.create_data_points()

    def create_centroides(self):
        self.centroids = array(
            [rand(self.dimension,) - 0.5 for i in range(self.number_of_clusters)])

    def create_data_points(self):
        cov = (identity(self.dimension) * self.dimension *
               PellegMoore.coefficient)  # [[1, 0], [0, 1]] * 2 * 0.012
        self.data_points = array([self.create_point(self.centroids[randint(
            0, self.number_of_clusters)], cov, 1)[0] for i in range(self.number_of_points)])

    def check_calculated_centroids(self, calculated_centroids):
        score = KMeans.objective(self.data_points, calculated_centroids)/KMeans.objective(self.data_points, self.centroids)
        print("True centroids =", KMeans.objective(self.data_points, self.centroids))
        print("Calculated centroids =", KMeans.objective(self.data_points, calculated_centroids))
        print("Clustering score =", score)
        return score



class BIRCH(DataSet):
    """Class for constructing dataset for testing clustering algorithms ."""

    critical_distance = 1

    def __init__(self, dimensions=(10, 10), number_of_points_per_cluster=100,
                 distance_between_clusters=4 * sqrt(2), cluster_radius=sqrt(2)):
        self.__dict__.update(locals())
        # TODO: napraviti za dimenzije vece od 2

        self.create_centroides()
        self.create_data_points()

    def create_centroides(self):
        self.centroids = []
        height = sqrt(self.distance_between_clusters**2 -
                      (self.distance_between_clusters / 2)**2)
        for i in range(self.dimensions[1]):
            stride = 0 if(i % 2 == 0) else self.distance_between_clusters / 2
            for j in range(self.dimensions[0]):
                self.centroids.append(
                    array([j * self.distance_between_clusters + stride, i * height]))

        # Translating all centroid around (0,0)
        self.centroids -= mean(self.centroids, axis=0)

    def create_data_points(self):
        self.data_points = []
        cov = identity(len(self.dimensions))  # [[1, 0], [0, 1]]
        for i in self.centroids:
            self.data_points.extend(self.create_point(
                i, cov, self.number_of_points_per_cluster))
        self.data_points = array(self.data_points)

    def check_calculated_centroids(self, calculated_centroids):
        number_of_guessed = 0
        for centroid in self.centroids:
            for calculated_centroid in calculated_centroids:
                if (norm(centroid - calculated_centroid) < self.critical_distance):
                    number_of_guessed += 1
                    break

        print("Number of found centroids =", number_of_guessed)
        print("Percentage is:", number_of_guessed/len(calculated_centroids)*100)
        return number_of_guessed


    def test_data(self, print_radius=False):
        sums_per_cluster = []
        # Radius per claster = sqrt[(sum(Xi - X0)^2)/N] i=1,...N
        # where N is number_of_points_per_cluster and Xi data in claster and X0
        # centroid
        for i in range(len(self.centroids)):
            suma = 0
            for j in range(self.number_of_points_per_cluster):
                suma += sum((self.centroids[i] -
                             self.data_points[i * self.number_of_points_per_cluster + j])**2)
            sums_per_cluster.append(sqrt(
                                    suma / self.number_of_points_per_cluster))

        if(print_radius):
            print("Radius per centroids = ", sums_per_cluster)
        average = sum(sums_per_cluster) / len(sums_per_cluster)
        print("Average cluster radius = ", average)
        return average
