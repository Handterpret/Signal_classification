# This code is made to try various classification techniques on Infrared datas
# Please make sure you have follow https://github.com/Handterpret/Infrared_Analysis for how to generate datas

import argparse
import json
import numpy as np
import tensorflow as tf
import os
import logging

logging.basicConfig(
    # Define logging level
    level=logging.DEBUG,
    # Declare the object we created to format the log messages
    format=(
    '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s'),
    # Declare handlers
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("tf_train")
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()

parser.add_argument("--data_path", help="Path to folder containing datas to train")
parser.add_argument("--model", help="Model to train. Choose from: perceptron", default="perceptron")
parser.add_argument("-o", "--output", help="Where to save output data")
parser.add_argument("--epochs", help="Number of epochs to train", default=10, type=int)

args = parser.parse_args()

def load_dataset(dataset_path, batch_size=1, shuffle_buffer_size=8):
    Train_percentage = 80
    train_set = {}
    test_set = {}
    train_set["label"] = []
    test_set["label"] = []
    train_set["data"] = []
    test_set["data"] = []

    for label_index, label in enumerate(os.listdir(dataset_path)):
        for index, file in enumerate(os.listdir(os.path.join(dataset_path,label))):
            if index < len(os.listdir(os.path.join(dataset_path,label)))/100*Train_percentage:
                train_set["data"].append(np.load(os.path.join(dataset_path,label,file)))
                train_set["label"].append(label_index)
            else:
                test_set["data"].append(np.load(os.path.join(dataset_path,label,file)))
                test_set["label"].append(label_index)
    train_dataset = tf.data.Dataset.from_tensor_slices((train_set["data"], train_set["label"]))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_set["data"], test_set["label"]))
    logger.info(f"{len(train_set['data'])} data in train set and {len(test_set['data'])} data in test set")

    train_dataset = train_dataset.shuffle(shuffle_buffer_size).batch(batch_size)
    test_dataset = test_dataset.batch(batch_size)

    return train_dataset, test_dataset

def perceptron_train(train, test, output, epochs):

    data_shape = list(train.as_numpy_iterator())[0][0].shape
    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(data_shape[-3] ,data_shape[-2], data_shape[-1])),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10)
    ])

    model.compile(optimizer=tf.keras.optimizers.RMSprop(),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['sparse_categorical_accuracy'])
    
    model.fit(train, epochs=epochs, validation_data=test)
    
    model.save(output)


if __name__ == "__main__":
    train, test = load_dataset(args.data_path)
    if args.model == "perceptron":
        perceptron_train(train, test, args.output, args.epochs)