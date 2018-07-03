FROM python:3.6.3

WORKDIR /app

RUN mkdir model
RUN mkdir data
RUN mkdir prediction

ADD requirements.txt /app
ADD main.py /app
ADD data.py /app
ADD get_file_list.py /app
ADD model.py /app
ADD label_no_wrong_file.txt /app


RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV mode=predict
ENV folder_path=data
ENV folder_mode=1
ENV label=label_no_wrong_file.txt
ENV image_path=11
#ENV model_path=model/
ENV prediction_file=prediction/predictiony.json
ENV resize_to=300
ENV pca_components=30

#CMD python3 main.py --mode $mode --folder_path $folder_path --folder_mode $folder_mode --label $label --image_path $image_path --model_path $model_path --prediction_file $prediction_file --resize_to $resize_to --pca_components $pca_components
CMD python3 main.py --mode $mode --folder_path $folder_path --folder_mode $folder_mode --label $label --image_path $image_path --prediction_file $prediction_file
