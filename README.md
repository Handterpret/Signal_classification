# Signal_classification

# Infrared Classification

Code from folder :

```bash
./Infrared_classification
```

Is intended to classify signal from Infrared diodes and leds.

Please refer to : <https://github.com/Handterpret/Infrared_Analysis>

## Training

Training a model is made with file :

```bash
./Infrared_classification/train.py
```
For info on how to use, Please see:

```
python3 ./Infrared_classification/train.py --help
```


Dataset Architecture :
```
Dataset
    - Class1
        - ***.npy
        - ***.npy
        ...

    - Class2
        - ***.npy
        - ***.npy
        ...
    ...
```