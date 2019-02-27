import model
import data
import sys
import argparse
import json
import time

parser = argparse.ArgumentParser(description='image classification: main function')
parser.add_argument('--model_path', type=str, default='model/best_model')
parser.add_argument('--mode', type=str, default='predict',
                    help='mode to run the program: test, predict')
parser.add_argument('--path', type=str, default='images',
                    help='the path of folder/image to predict')
parser.add_argument('--folder_mode', type=int, default=1,
                    help='whether looking through sub-folder, 1 is yes')
parser.add_argument('--label', type=str, default='',
                    help='if test, input the label file')
parser.add_argument('--prediction_file', type=str, default='prediction/prediction.json',
                    help='where to store the prediction')
argv = parser.parse_args()

model_path = argv.model_path
mode_flag = argv.mode
folder_path = argv.path
flag = argv.folder_mode
label_file_path = argv.label
prediction_file = argv.prediction_file
batch_size = 16

image_list = data.get_image_list(folder_path, flag)  # list of image path
batched_image_list = data.get_batched_list(image_list, batch_size)  # batched image path
model_ft = model.load_model(model_path)  # load model

if mode_flag == 'predict':

    print('start predict')
    start_time = time.time()

    prediction = model.predict(model_ft, batched_image_list)

    end_time = time.time()

    print("Prediction: " + str(prediction))
    print('finish prediction')
    print('time used to predict: ' + str(end_time - start_time))

    data = []
    for i in range(len(image_list)):
        data.append({image_list[i]: int(prediction[i])})
    with open(prediction_file, 'w') as json_file:
        json.dump(data, json_file)
        print('save to ' + prediction_file)
else:
    print('unknown mode')
