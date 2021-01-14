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
parser.add_argument("--batch_size", help="batch size for training, can improve speed on big dataset", default=2, type=int)
parser.add_argument("--shuffle_buffer_size", help="size of buffer to shuffle", default=8, type=int)
args = parser.parse_args()
   
class Trainer:
    def __init__(self, batch_size=1, shuffle_buffer_size=8):
        self.batch_size = batch_size
        self.shuffle_buffer_size = shuffle_buffer_size

    def load_dataset(self, dataset_path):
        self.train_percentage = 80
        self.labels_list = [i for i in os.listdir(dataset_path)]

        train_set = {}
        test_set = {}
        train_set["label"] = []
        test_set["label"] = []
        train_set["data"] = []
        test_set["data"] = []

        for label_index, label in enumerate(os.listdir(dataset_path)):
            for index, file in enumerate(os.listdir(os.path.join(dataset_path,label))):
                if index < len(os.listdir(os.path.join(dataset_path,label)))/100*self.train_percentage:
                    train_set["data"].append(np.load(os.path.join(dataset_path,label,file)))
                    train_set["label"].append(label_index)
                else:
                    test_set["data"].append(np.load(os.path.join(dataset_path,label,file)))
                    test_set["label"].append(label_index)
        self.train_dataset = tf.data.Dataset.from_tensor_slices((train_set["data"], train_set["label"]))
        self.test_dataset = tf.data.Dataset.from_tensor_slices((test_set["data"], test_set["label"]))
        self.data_shape = train_set["data"][0].shape
        logger.info(f"{len(train_set['data'])} data in train set and {len(test_set['data'])} data in test set")
        self.preprocess_dataset()

    def preprocess_dataset(self):
        self.train_dataset = self.train_dataset.shuffle(self.shuffle_buffer_size).batch(self.batch_size)
        self.test_dataset = self.test_dataset.batch(self.batch_size)
    
    def train_perceptron(self, output='./output_model', epochs=10):
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(self.data_shape[-3] ,self.data_shape[-2], self.data_shape[-1])),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(len(self.labels_list))
        ])

        model.compile(optimizer=tf.keras.optimizers.RMSprop(),
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['sparse_categorical_accuracy'])
        
        model.fit(self.train_dataset, epochs=epochs, validation_data=self.test_dataset)
        
        model.save(output)

if __name__ == "__main__":
    trainer = Trainer(args.batch_size, args.shuffle_buffer_size)
    trainer.load_dataset(args.data_path)
    if args.model == "perceptron":
        trainer.train_perceptron(args.output, args.epochs)
    else:
        logger.error(f'{args.model} not recognized')