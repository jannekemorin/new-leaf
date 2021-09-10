import os
import importlib.util
import sys
import trace

filename = "testFiles/" + str(input("Enter the name of the file you would like to analyze: "))
mystring = "python pycfg-0.1/pycfg/pycfg.py " + filename + " -d > cfgs/" + (filename.split(".")[0]).split("/")[1] + ".txt"
print(mystring)

# Create control flow graph (CFG) utilizing the pycfg-0.1 package
command = (mystring)
stream = os.popen(command)
output = stream.readlines()
print("output: " + str(output))

'''
# Convert the CFG to a list of Prolog reachability queries
command = ("python cfg2Prolog.py cfgs/" + filename.split(".")[0] + ".txt")
stream = os.popen(command)
plCommandList = stream.readlines()
for i in range(len(plCommandList)):
    plCommandList[i] = plCommandList[i].rstrip()
print("output: " + str(plCommandList))
'''