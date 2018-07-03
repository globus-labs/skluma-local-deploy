import matplotlib
import numpy as np
import pandas as pd
from math import isnan
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.utils import assert_all_finite

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from pylab import rcParams

from ML_util import fill_zeros, get_text_rows, cross_validation, train_and_save, get_best_params

rcParams['figure.figsize'] = 10, 7

np.set_printoptions(threshold=np.nan)


def clean_data(X, y):
    """Removes textual rows and fills zeros.
        :param X: (np.array) data matrix
        :param y: (np.array) true value column vector
        :returns: (np.array) cleaned matrix ready for model"""

    to_remove = get_text_rows(X)
    X = np.delete(X, to_remove, axis=0)
    y = np.delete(y, to_remove, axis=0)

    X = fill_zeros(X)
    y = fill_zeros(y)
    return X, y


def bin_null_values(y):
    """Bins null values into integer bins. This is necessary if using float nulls.
        :param y: (np.array) column vector of data
        :returns: (list, np.array) null values and column vector with index of null in list"""

    y_output = np.zeros(y.shape)

    nulls = [0]
    num_rows, num_cols = y.shape
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            if y[i][j] != 0:
                if y[i][j] not in nulls:
                    nulls.append(y[i][j])
                y_output[i][j] = nulls.index(y[i][j])

    return nulls, y_output


def pca_plot(X, y):
    """Creates PCA plot of null inference feature space.
        :param X: (np.array) data matrix
        :param y: (np.array) true value column vector"""

    # This generates the plot used in the Skluma paper
    pca = PCA(n_components=2)
    X_fit_pca = pca.fit(X)
    X_r = X_fit_pca.transform(X)


    one = plt.scatter([X_r[i, 0] for i in range(0, 4813) if y[i] == 0],
                      [X_r[i, 1] for i in range(0, 4813) if y[i] == 0],
                      c='r', s=30, alpha=.8, lw=0.3)
    plt.scatter([X_r[i, 0] for i in range(0, 4813) if y[i] == 1],
                [X_r[i, 1] for i in range(0, 4813) if y[i] == 1],
                c='#0cd642', s=30, alpha=.8, lw=0.3)
    plt.scatter([X_r[i, 0] for i in range(0, 4813) if y[i] == 2],
                [X_r[i, 1] for i in range(0, 4813) if y[i] == 2],
                c='#4289f4', s=30, alpha=.8, lw=0.3)

    one.axes.get_xaxis().set_visible(False)
    one.axes.get_yaxis().set_visible(False)
    plt.savefig('null2.png', format='png', dpi=600)
    # plt.show()


if __name__ == "__main__":
    print "reading training data"
    data = pd.read_csv('null_training_data.csv')

    X = data.iloc[:, 3:-1].values
    y = data.iloc[:, -1:].values

    print "cleaning training data"
    X, y = clean_data(X, y)

    model = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='euclidean',
                                 metric_params=None, n_jobs=1, n_neighbors=9,
                                 weights='distance')

    print "cross-validating model"
    cross_validation(model, X, y, splits=100)
