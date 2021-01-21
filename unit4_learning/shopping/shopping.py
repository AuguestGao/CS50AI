import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
       0 - Administrative, an integer
       1 - Administrative_Duration, a floating point number
       2 - Informational, an integer
       3 - Informational_Duration, a floating point number
       4 - ProductRelated, an integer
       5 - ProductRelated_Duration, a floating point number
       6 - BounceRates, a floating point number
       7 - ExitRates, a floating point number
       8 - PageValues, a floating point number
       9 - SpecialDay, a floating point number
       10 - Month, an index from 0 (January) to 11 (December)
       11 - OperatingSystems, an integer
       12 - Browser, an integer
       13 - Region, an integer
       14 - TrafficType, an integer
       15 - VisitorType, an integer 0 (not returning) or 1 (returning)
       16 - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    months = {
        "JAN": 0,
        "FEB": 1,
        "MAR": 2,
        "APR": 3,
        "MAY": 4,
        "JUNE": 5,
        "JUL": 6,
        "AUG": 7,
        "SEP": 8,
        "OCT": 9,
        "NOV": 10,
        "DEC": 11,
    }

    # read csv
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        evidence = []
        labels = []

        for r in reader:
            admin = int(r[0])
            admin_duration = float(r[1])
            info = int(r[2])
            info_duration = float(r[3])
            product = int(r[4])
            product_duration = float(r[5])
            bounce_rate = float(r[6])
            exit_rate = float(r[7])
            page_values = float(r[8])
            special_day = float(r[9])
            month = months[r[10].upper()]
            os = int(r[11])
            browser = int(r[12])
            region = int(r[13])
            traffic = int(r[14])
            visitor = 1 if r[15] == "Returning_Visitor" else 0
            weekend = 1 if r[16] == "TRUE" else 0
            evidence.append(
                [
                    admin,
                    admin_duration,
                    info,
                    info_duration,
                    product,
                    product_duration,
                    bounce_rate,
                    exit_rate,
                    page_values,
                    special_day,
                    month,
                    os,
                    browser,
                    region,
                    traffic,
                    visitor,
                    weekend,
                ]
            )

            labels.append(1 if r[17] == "TRUE" else 0)
        return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    pos = 0  # True label
    neg = 0  # False Label
    true_pos = 0  # predicted correct for a true label
    true_neg = 0  # predicted correct for a false label

    for l, p in zip(labels, predictions):
        # get true positive count
        if l:  # l == 1
            pos += 1
            if p:  # p == 1
                true_pos += 1
        else:
            neg += 1
            if not p:
                true_neg += 1

    sensitivity = true_pos / pos
    specificity = true_neg / neg
    print(f"true_pos / pos = {true_pos} / {pos}")
    print(f"true_neg / neg = {true_neg} / {neg}")

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
