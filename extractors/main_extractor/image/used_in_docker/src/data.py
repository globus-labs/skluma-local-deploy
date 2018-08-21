import os
from PIL import Image

import numpy as np
from torchvision import transforms
import math


resize_size=224

def file_in_folder(folder_path, flag=1): 
    '''
    get files in given folder, return list of filepath and filename
    '''
    file_list = []
    file_name = []
    for(dirpath, dirnames, filenames) in os.walk(folder_path):
#         print(filenames)
        
        for i in filenames:
            try:
                # print(i + "\n")
                file_list += [dirpath + os.sep + i]
                file_name += [i]
            except:
                continue
        if flag == 0:
            break
    file_list.sort(key=path_leaf)
    file_name.sort()
    return [file_list, file_name]


def path_leaf(path): # get leaf of a path
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)


def get_continuous_image_per_folder(imas): # get continuous image, input is list of image, return a list of transformed combination of image data in tensor type
#     print('in get_continuous_image')
    res = []
#         temp = []
    count = 0
    t = 0
    for j in imas:
#         print(j)
        image = Image.open(j).convert('RGB')
        image = image.resize((resize_size, resize_size), Image.ANTIALIAS)
            
        tensor_image = transforms.ToTensor()(image)
        tensor_image = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(tensor_image)
        res.append(tensor_image)
    return res


def get_images(file_list): # get images in folder
    list_of_image = get_continuous_image_per_folder(file_list)
    res = list_of_image[0].numpy().reshape(1, 3, resize_size, resize_size)
    for i in range(1, len(list_of_image)):
        res = np.concatenate((res, list_of_image[i].numpy().reshape(1, 3, resize_size, resize_size)), 0)
    return res


def get_image_list(path, flag):
    image_list = None
    if os.path.isdir(path):
        a, b = file_in_folder(path, flag)
        image_list = a
    else:
        image_list = [path]
    return image_list


def get_batched_list(file_list, batch_size):
    cur_idx = 0
    length = len(file_list)
    batch_number = math.floor(length/batch_size)
    idx_list = np.array(list(range(batch_number*batch_size)))
    idx_list = idx_list.reshape(batch_number, batch_size)
    idx_list = idx_list.tolist()
    if batch_number*batch_size != length:
        idx_list.append(list(range(batch_number*batch_size, length)))
    res = []
    for i in idx_list:
        temp = [file_list[j] for j in i]
        res.append(temp)
    return res
