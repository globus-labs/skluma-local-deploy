
import os
import subprocess
import sys

#sys.path.insert(0,'/home/skluzacek/Skluma/skluma/file_sampler/FTI_Models')
#sys.path.insert(0,'/src/FTI_Models')
os.chdir('/src/')

# TODO: Will eventually be dealer's choice, but right now RF is
# TODO: ... obviously superior.
model = "rf" #os.environ["MODEL"]
features = "randhead" #os.environ["FEATURES"]

runnable = """python3 FTI_Models/main.py /src/ {0} {1}""".format(str(model), str(features))

processes = [subprocess.Popen(runnable, shell=True)]
for p in processes: p.wait()
