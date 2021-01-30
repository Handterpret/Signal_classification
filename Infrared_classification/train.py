# This code is made to try various classification techniques on Infrared datas
# Please make sure you have follow https://github.com/Handterpret/Infrared_Analysis for how to generate datas

import argparse
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os
import logging
from tensorflow.keras.regularizers import l2

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
parser.add_argument("--train_percentage", help="percentage of the dataset to train on i.e validate on 1-train_percentage % of the dataset", default=80, type=int)
parser.add_argument("--batch_size", help="batch size for training, can improve speed on big dataset", default=16, type=int)
parser.add_argument("--shuffle_buffer_size", help="size of buffer to shuffle", default=None, type=int)
parser.add_argument("--seq_len", help="sequence length for RNN", default=32, type=int)

args = parser.parse_args()
   
class Trainer:
    def __init__(self, batch_size, shuffle_buffer_size, model):
        self.batch_size = batch_size
        self.shuffle_buffer_size = shuffle_buffer_size
        self.model = model

    def load_RNN_dataset(self, dataset_path, train_percentage, seq_len):

        self.train_dataset = []
        self.test_dataset = []

        for label_index, label in enumerate(os.listdir(dataset_path)):
            tmp_data_train = []
            tmp_data_test = [] 
            for index, file in enumerate([file for file in os.listdir(os.path.join(dataset_path,label)) if file.endswith(".npy")]):
                if index < len(os.listdir(os.path.join(dataset_path,label)))/100*self.train_percentage:
                    for data in np.load(os.path.join(dataset_path,label,file)):
                        tmp_data_train.append(data)
                else:
                    for data in np.load(os.path.join(dataset_path,label,file)):
                        tmp_data_test.append(data)
            # finished on one label
            tmp_dataset_train = tf.data.Dataset.from_tensor_slices(tmp_data_train).window(seq_len, int(seq_len/2), drop_remainder= True)
            datas_train = [list(i.as_numpy_iterator()) for i in tmp_dataset_train]
            tmp_dataset_test = tf.data.Dataset.from_tensor_slices(tmp_data_test).window(seq_len, int(seq_len/2), drop_remainder= True)
            datas_test = [list(i.as_numpy_iterator()) for i in tmp_dataset_test]
            if not self.train_dataset:
                self.train_dataset = tf.data.Dataset.from_tensor_slices((datas_train, [tf.one_hot(label_index, len(self.labels_list)) for i in range(len([i for i in tmp_dataset_train]))]))
            else :
                self.train_dataset = self.train_dataset.concatenate(tf.data.Dataset.from_tensor_slices((datas_train, [tf.one_hot(label_index, len(self.labels_list)) for i in range(len([i for i in tmp_dataset_train]))])))
            if not self.test_dataset:
                self.test_dataset = tf.data.Dataset.from_tensor_slices((datas_test, [tf.one_hot(label_index, len(self.labels_list)) for i in range(len([i for i in tmp_dataset_test]))]))
            else :
                self.test_dataset = self.test_dataset.concatenate(tf.data.Dataset.from_tensor_slices((datas_test, [tf.one_hot(label_index, len(self.labels_list)) for i in range(len([i for i in tmp_dataset_test]))])))
        self.data_shape = self.train_dataset.as_numpy_iterator().next()[0].shape
        logger.info(f"{len([i for i in self.train_dataset.as_numpy_iterator()])} data in train set and {len([i for i in self.test_dataset.as_numpy_iterator()])} data in test set with shape : {self.data_shape}")
        logger.info(f"{len(self.labels_list)} different classes")
        self.preprocess_dataset()

    def load_dataset(self, dataset_path, train_percentage, seq_len):
        self.train_percentage = train_percentage
        self.labels_list = [i for i in os.listdir(dataset_path)]
        if self.model == "RNN":
            return self.load_RNN_dataset(dataset_path, train_percentage, seq_len)
        train_set = {}
        test_set = {}
        train_set["label"] = []
        test_set["label"] = []
        train_set["data"] = []
        test_set["data"] = []
        
        for label_index, label in enumerate(os.listdir(dataset_path)):
            for index, file in enumerate([file for file in os.listdir(os.path.join(dataset_path,label)) if file.endswith(".npy")]):
                if index < len(os.listdir(os.path.join(dataset_path,label)))/100*self.train_percentage:
                    for data in np.load(os.path.join(dataset_path,label,file)):
                        train_set["data"].append(data)
                        train_set["label"].append(label_index)
                else:
                    for data in np.load(os.path.join(dataset_path,label,file)):
                        test_set["data"].append(data)
                        test_set["label"].append(label_index)

        self.train_dataset = tf.data.Dataset.from_tensor_slices((train_set["data"], tf.one_hot(train_set["label"], len(self.labels_list))))
        self.test_dataset = tf.data.Dataset.from_tensor_slices((test_set["data"], tf.one_hot(test_set["label"], len(self.labels_list))))
        self.data_shape = train_set["data"][0].shape
        
        logger.info(f"{len(train_set['data'])} data in train set and {len(test_set['data'])} data in test set with shape : {self.data_shape}")
        logger.info(f"{len(self.labels_list)} different classes")
        self.preprocess_dataset()

    def preprocess_dataset(self):
        if not self.shuffle_buffer_size:
            self.shuffle_buffer_size = len([i for i in self.train_dataset.as_numpy_iterator()])
        self.train_dataset = self.train_dataset.shuffle(self.shuffle_buffer_size).batch(self.batch_size).prefetch(tf.data.AUTOTUNE)
        self.test_dataset = self.test_dataset.batch(self.batch_size).prefetch(tf.data.AUTOTUNE)

    
    def get_normalizer(self):
        normalizer = tf.keras.layers.experimental.preprocessing.Normalization()
        feature_ds = self.train_dataset.map(lambda x, y: x)
        normalizer.adapt(feature_ds)
        return normalizer


    def train_perceptron(self, epochs, output='./output_model'):

        normalizer = self.get_normalizer()

        model = keras.Sequential()

        model.add(layers.Input(self.data_shape))
        model.add(normalizer)

        model.add(layers.Flatten())  # this converts our 3D feature maps to 1D feature vectors
        model.add(layers.Dense(128,activation="relu"))
        model.add(layers.Dense(64,activation="relu"))
        model.add(layers.Dense(32,activation="relu"))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(len(self.labels_list), activation="softmax"))

        self.train(model, output, epochs)

    def train_CNN(self, epochs, output='./output_model'):

        normalizer = self.get_normalizer()

        model = keras.Sequential()

        model.add(layers.Input(self.data_shape))
        model.add(normalizer)
        model.add(layers.Conv1D(16, (2), padding="same"))
        model.add(layers.Activation('relu'))
        model.add(layers.Conv1D(16, (2), padding="same"))
        model.add(layers.Activation('relu'))
        #model.add(layers.AveragePooling1D())
        model.add(layers.MaxPooling1D(pool_size=(2)))

        model.add(layers.Flatten())  # this converts our 3D feature maps to 1D feature vectors
        model.add(layers.Dense(128,activation="relu"))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(len(self.labels_list), activation="softmax"))

        self.train(model, output, epochs)


    def train_RNN(self, epochs, seq_len, output='./output_model'):
        normalizer = self.get_normalizer()

        model = keras.Sequential()

        model.add(layers.Input(self.data_shape))
        model.add(normalizer)
        model.add(layers.Reshape((self.data_shape[0], self.data_shape[1]*self.data_shape[2])))
        model.add(tf.keras.layers.LSTM(64))

        model.add(layers.Flatten())  # this converts our 3D feature maps to 1D feature vectors
        model.add(layers.Dense(128,activation="relu"))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(len(self.labels_list), activation="softmax"))

        self.train(model, output, epochs)

    def train(self, model, output, epochs):
        
        model.summary()
        
        model.compile(optimizer=tf.keras.optimizers.Adam(),
                loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                metrics=['categorical_accuracy'])
        
        model.fit(self.train_dataset, epochs=epochs, validation_data=self.test_dataset)
        
        model.save(output)

if __name__ == "__main__":
    trainer = Trainer(args.batch_size, args.shuffle_buffer_size, args.model)
    trainer.load_dataset(args.data_path, args.train_percentage, args.seq_len)
    if args.model == "perceptron":
        trainer.train_perceptron(args.epochs, args.output)
    if args.model == "CNN":
        trainer.train_CNN(args.epochs, args.output)
    if args.model == "RNN":
        trainer.train_RNN(args.epochs, args.output)
    else:
        logger.error(f'{args.model} not recognized')