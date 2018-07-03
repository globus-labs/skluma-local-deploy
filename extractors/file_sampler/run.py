
import os
import subprocess

os.chdir('/src/')

# TODO: Will eventually be dealer's choice, but right now RF is
# TODO: ... obviously superior.
model = "rf" #os.environ["MODEL"]
features = "randhead" #os.environ["FEATURES"]

runnable = """python3 FTI_Models/main.py /src/ {0} {1}""".format(str(model), str(features))

processes = [subprocess.Popen(runnable, shell=True)]
for p in processes: p.wait()
