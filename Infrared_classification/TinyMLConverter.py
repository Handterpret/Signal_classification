# This code is made to try various classification techniques on Infrared datas
# Please make sure you have follow https://github.com/Handterpret/Infrared_Analysis for how to generate datas

import argparse
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

parser.add_argument("--model_path", help="Path to folder model to conver")
parser.add_argument("-o", "--output", help="Path to output folder")

args = parser.parse_args()
   
if __name__ == "__main__":
    logger.info("Converting the model ...")
    model = tf.keras.models.load_model(args.model_path)

    # Convert the model to the TensorFlow Lite format without quantization
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    # Save the model to disk
    open(os.path.join(args.output,"Tflite_exported_model.tflite"), "wb").write(tflite_model)
    
    basic_model_size = os.path.getsize(os.path.join(args.output,"Tflite_exported_model.tflite"))
    print("Model is %d bytes" % basic_model_size)