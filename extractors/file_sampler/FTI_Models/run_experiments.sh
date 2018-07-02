# run experiments
# TODO: SERIOUSLY JUST DO ALL OF THIS IN A PIPE LIKE WE DO FOR DOCKER.
source bin/activate

#echo "Running svc experiments"
#python3 main.py /home/tskluzac/pub8/ svc head --split 0.5
#python3 main.py /home/tskluzac/pub8/ svc rand --split 0.5
#python3 main.py /home/tskluzac/pub8/ svc randhead --split 0.5 --head-bytes 256 --rand-bytes 256
#python3 main.py /home/tskluzac/pub8/ svc ngram --split 0.5 --ngram 1

#echo "Running logit experiments"
#python3 main.py /home/tskluzac/pub8/ logit head
#python3 main.py /home/tskluzac/pub8/ logit rand
#python3 main.py /home/tskluzac/pub8/ logit randhead --head-bytes 256 --rand-bytes 256
#python3 main.py /home/tskluzac/pub8/ logit ngram --ngram 1

echo "Running rf experiments"
python3 main.py /home/tskluzac/pub8/ rf head
python3 main.py /home/tskluzac/pub8/ rf rand
python3 main.py /home/tskluzac/pub8/ rf randhead --head-bytes 256 --rand-bytes 256
#python3 main.py /home/tskluzac/pub8/ rf ngram --ngram 1
