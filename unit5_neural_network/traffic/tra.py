import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    filters = []
    for n in [5, 10, 25, 50, 100, 150, 200, 250]:
        print(f"At {n}")
        # Get a compiled neural network
        model = get_model(n)

        # Fit model on training data
        model.fit(x_train, y_train, epochs=EPOCHS)

        # Evaluate neural network performance
        x = model.evaluate(x_test,  y_test, verbose=0)
        filters.append((n, x[0], x[1]))  # filter number, loss, accuracy

    filtersnp = np.array(filters)

    fig, (f1, f2) = plt.subplots(2, 1)
    fig.suptitle("2 hidden layer with num_neuron vs loss/accuracy plot")
    f1.plot(filtersnp[:, 0], filtersnp[:, 1], '.-')
    f1.set_ylabel('loss')

    f2.plot(filtersnp[:, 0], filtersnp[:, 2], 'o-')
    f2.set_ylabel('acc')

    plt.savefig('trail')

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    for cate in range(NUM_CATEGORIES):
        directory = os.path.join(data_dir, str(cate))
        for i in os.listdir(directory):
            file = os.path.join(directory, i)
            print(i)
            print(file)
            img = cv2.imread(file)

            if img is None:
                sys.exit("Can not read the image")

            # unifying image size by resizing before appending to images
            images.append(cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT)))
            labels.append(cate)

    return (images, labels)


def get_model(n):
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # model 1
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(
            12, (2, 2), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),
        tf.keras.layers.MaxPooling2D(pool_size=(3, 3)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(n, activation='relu'),
        tf.keras.layers.Dense(n, activation='relu'),
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    model.compile(
        optimizer='adam',
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
