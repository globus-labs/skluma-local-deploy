import os
# import imghdr
import json

image_extension = ["jpg", "png", "gif", "bmp", "jpeg", "tif", "tiff", "jif", "jfif", "jp2", "jpx", "j2k", "j2c", "fpx", "pcd"]

def get_extension(i):
	ext = os.path.splitext(i)[-1].lower()
	if ext[1:len(ext)] in image_extension:
		return ext[1:len(ext)]
	else:
		return False

def image_file_in_folder(folder_path, flag):
	file_list = []
	file_name = []
	# file_extension = []
	for(dirpath, dirnames, filenames) in os.walk(folder_path):
		for i in filenames:
			try:
				# print(i + "\n")
				ext = get_extension(i)
				if ext != False:
					file_list += [dirpath + os.sep + i]
					file_name += [i]
					# file_extension += [ext]
			except:
				continue
		if flag == 0:
			break
	return [file_list, file_name] # , file_extension]


# print(image_file_in_folder("/home/ubuntu/pub8", 1))
def get_system_metadata(folder_path, flag=1):
	# [file_list, file_name, file_extension] = image_file_in_folder(folder_path, flag)
	[file_list, file_name] = image_file_in_folder(folder_path, flag)
	# f = open('/home/chaofeng/Documents/practicum/file_list.txt','w')
	f = open('file_list.txt', 'w')
	file_size = []
	for i in range(len(file_list)):
		file_size += [os.stat(file_list[i]).st_size]
		f.write(file_list[i] + '\n')
	f.close()
	return [file_list, file_name] # , file_extension, file_size]

# [file_list, file_name, file_extension, file_size] = get_system_metadata("/home/ubuntu/try", 1)
