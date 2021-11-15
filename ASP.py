
import os
import sys
from clyngor import ASP, solve
import subprocess
import re

command = "conda activate potassco && clingo crime.lp > ASPOutput.txt"
stream = os.popen(command)
output = stream.readlines()

inFile = open("ASPOutput.txt")
functionCall = inFile.readlines()[4]
reachabilityList = functionCall.split()
print(reachabilityList)

transitiveClosure=[]
for i in range(3):
    transitiveClosure.append([])

for statement in reachabilityList:
    function = statement.split("(")[0]
    args = statement.split("(")[1]
    args = args.split(",")

    if function=="reachable":
        arg1 = args[0]
        arg2 = args[1][:-1]
        (transitiveClosure[int(arg2)-1]).append(int(arg1))

    print(transitiveClosure)
