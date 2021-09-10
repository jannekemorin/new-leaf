import os
import importlib.util
import sys
import trace
import cfg2Prolog

# Create correct file name from input
filename = str(input("Enter the name of the file you would like to analyze: "))
command = "python dependencies/pycfg-0.1/pycfg/pycfg.py testFiles/" + filename + " -d 2> cfgs/text/" + filename.split(".")[0] + ".txt"

# Create control flow graph (CFG) utilizing the pycfg-0.1 package
stream = os.popen(command)
output = stream.readlines()

# Convert the CFG to a list of Prolog reachability queries
plCommandList = cfg2Prolog.convert("cfgs/text/" + filename.split(".")[0] + ".txt")
print(plCommandList)
for i in range(len(plCommandList)):
    plCommandList[i] = plCommandList[i].rstrip()
print("output: " + str(plCommandList))

# Move the png file generated
# os.rename(("testFiles/" + filename + ".png"), ("cfgs/images/" + filename))