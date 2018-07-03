import numpy as np
import pickle as pkl
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.model_selection import ShuffleSplit, GridSearchCV
from math import isnan

np.set_printoptions(threshold=np.nan)


def is_number_or_none(field):
    """Determine if a string is a number or NaN by attempting to cast to it a float.
        :param field: (str) field
        :returns: (bool) whether field can be cast to a number"""

    if field is None:
        return True
    try:
        float(field)
        return True
    except ValueError:
        return False


def get_text_rows(matrix):
    """Get indices of all rows that have non-numerical aggregates.
        :param matrix: (np.array) matrix of data
        :returns: (list(int)) list of text indices to remove"""

    to_remove = []
    for i in range(0, len(matrix)):
        if not np.vectorize(is_number_or_none)(matrix[i]).all() \
                or np.vectorize(lambda x: str(x).lower() == "nan" or x is None)(matrix[i]).all():
            to_remove.append(i)

    return to_remove


def fill_zeros(matrix):
    """Fills all NaN and infinite entries with zeros.
        :param matrix: (np.array) matrix of data
        :returns: (np.array) matrix with zeros filled"""

    num_rows, num_cols = matrix.shape
    output_matrix = np.empty(matrix.shape)
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            if matrix[i][j] is None or isnan(float(matrix[i][j])) or float(matrix[i][j]) > np.finfo(np.float64).max:
                output_matrix[i][j] = np.float64(0)
            else:
                output_matrix[i][j] = matrix[i][j]

    return output_matrix


def get_best_params(model, params, X, y):
    """Find the best parameters for the model.
            :param model: (sklearn.model) model to fit
            :param X: (np.array) data matrix
            :param y: (np.array) true value column vector
            :return: (dict) optimal parameters"""

    model = GridSearchCV(model, params)

    model.fit(X, y.reshape(y.shape[0], ))

    return model.best_params_


def print_performance(all_y_test, all_y_pred, avg_method='macro'):
    print "accuracy: {}\nprecision: {}\nrecall: {}".format(
        accuracy_score(all_y_test, all_y_pred),
        precision_score(all_y_test, all_y_pred, average=avg_method),
        recall_score(all_y_test, all_y_pred, average=avg_method)
    )


def cross_validation(model, X, y, splits=1000, certainty_threshold=None):
    """Runs cross-validation on a test set to find accuracy of model and prints results.
        :param model: (sklearn.model) model to test
        :param X: (np.array) data matrix
        :param y: (np.array) true value column vector
        :param splits: (int) number of times to perform cross-validation
        :param certainty_threshold: (float | None) if the model has a decision function
        such as SVC's distance to separating hyperplane, this will print statistics for
        only those observations within the threshold
        :returns: (list, np.array) null values and column vector with index of null in list"""

    all_y_test = np.zeros((0, 1))
    all_y_pred = np.zeros((0, 1))

    all_y_decision = np.zeros((0, 1))

    for train_inds, test_inds in ShuffleSplit(n_splits=splits, test_size=0.01).split(X, y):
        # Split off the train and test set
        X_test, y_test = X[test_inds, :], y[test_inds]
        X_train, y_train = X[train_inds, :], y[train_inds]

        # Train the model
        model.fit(X_train, y_train)
        y_proba = model.predict_proba(X_test)
        y_decision = np.asarray([max(row) for row in y_proba]).reshape(-1, 1)
        y_pred = np.asarray([model.classes_[row.argmax()] for row in y_proba]).reshape(-1, 1)

        all_y_test = np.concatenate((all_y_test, y_test))
        all_y_pred = np.concatenate((all_y_pred, y_pred))
        all_y_decision = np.concatenate((all_y_decision, y_decision))

    print_performance(all_y_test, all_y_pred, avg_method='macro')

    if certainty_threshold is not None:
        print "---------------------------------------"
        print "Within certainty threshold of {}".format(certainty_threshold)
        print "---------------------------------------"

        print "certainty min: {}, max: {}".format(min(all_y_decision)[0], max(all_y_decision)[0])
        outside_threshold = [i for i in range(0, all_y_decision.shape[0])
                             if all_y_decision[i][0] < certainty_threshold]
        # print outside_threshold
        all_y_test = np.delete(all_y_test, outside_threshold)
        all_y_pred = np.delete(all_y_pred, outside_threshold)
        print "number of samples within threshold: {} out of {}".format(all_y_pred.shape[0],
                                                                        all_y_pred.shape[0] + len(outside_threshold))

        if all_y_pred.shape[0] > 0:
            print_performance(all_y_test, all_y_pred, avg_method='macro')


def train_and_save(model, X, y, file_name):
    """Train the model on the input data and save it for use in the pipeline.
        :param model: (sklearn.model) model to test
        :param X: (np.array) data matrix
        :param y: (np.array) true value column vector
        :param file_name: (string) file name of model"""

    model.fit(X, y)
    with open(file_name, "wb") as f:
        pkl.dump(model, f)