import os
import sys
import trace
import cfgConverter
import time
from pathlib import Path
'''
Driver program which (1) asks the user for input of a program file name and function name
then, (2) runs the appropriate test cases and outputs suspiciousness metrics dervied from
control flow.
'''

#--------------------------------------------------------------------
# Helper function - convert a number to its three-digit representation
def threeDig(i):
    if i < 10:
        return "00" + str(i)
    elif i < 100:
        return "0" + str(i)
    else:
        return str(i)

#--------------------------------------------------------------------
# Ask user for filename/function and import the function from the file provided
filename = str(input("Enter the name of the file you would like to analyze: "))
function = input("Enter the name of the function you would like to test: ")
exec("from testFiles." + filename.split(".")[0]+ " import " + function)   # import function from file

#--------------------------------------------------------------------
# Remove all coverage reports when rerunning the program
dir = 'testCases/coverageReports'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))
# Remove cfg images so they can be overwritten
if os.path.exists("cfgs/images/" + filename + ".png"):
    os.remove("cfgs/images/" + filename + ".png")

#--------------------------------------------------------------------
# Create PROLOG-format control flow graph (CFG) utilizing the pycfg-0.1 package
command = "python dependencies/pycfg-0.1/pycfg/pycfg.py testFiles/" + filename + " -d 2> cfgs/text/" + filename.split(".")[0] + ".txt"
stream = os.popen(command)
output = stream.readlines()

#--------------------------------------------------------------------
# Convert the CFG to a list of Prolog reachability queries
plCommandList = cfgConverter.convert2Prolog(filename)
for i in range(len(plCommandList)):
    plCommandList[i] = plCommandList[i].rstrip()

#--------------------------------------------------------------------
# Move the graphical CFG generated to the designated folder
if Path("testFiles/" + filename + ".png").is_file():
    os.rename(("testFiles/" + filename + ".png"), ("cfgs/images/" + filename + ".png"))

#--------------------------------------------------------------------
# Open the program and count the number of lines
faultyProgram = open("testFiles/" + filename)
length = 0
for line in faultyProgram.readlines():
    if len(line.strip()) != 0:
        length += 1

#--------------------------------------------------------------------
# Create a list containing the names of the test case files
dirList = os.listdir("testCases/inputs") # dir is your directory path
numOfFiles = len(dirList)
testcaseList = []
for i in range(1, numOfFiles + 1):
    testcaseList.append("testCases/inputs/input_" + threeDig(i) + ".txt")

#--------------------------------------------------------------------
# Run each test case on the faulty program and save the results
for i in range(len(testcaseList)): 
    inFile = open(testcaseList[i])
    functionCall = inFile.read()
    outFile = open(("testCases/actualOutputs/" + "output_" + threeDig(i + 1) + ".txt"), "w")
    result = str(eval(functionCall))
    outFile.write(result)
    # Create a Trace object, which will create coverage reports
    tracer = trace.Trace(
        ignoredirs=[sys.prefix, sys.exec_prefix],
        trace=0,
        count=1)
    # Run the function call from the test case using the tracer function
    tracer.run(functionCall)
    # Create a coverage report, placing output in the current directory
    r = tracer.results()
    r.write_results(show_missing=True, coverdir=("."))
    os.rename("testFiles.wrong_1_001.cover", "testCases/coverageReports/output_" + threeDig(i + 1) + "_cover.txt")
    outFile.close()

#--------------------------------------------------------------------
# Create a list of the coverage report filepaths for each test case
coverageFileList = []
coverageList = []
for i in range(1, numOfFiles + 1):
    coverageFileList.append("testCases/coverageReports/output_" + threeDig(i) + "_cover.txt")
for i in range(length):
    coverageList.append([0, 0, 0])

#--------------------------------------------------------------------
# Use the diff command to get the results of each test case
passedCount = 0
failedCount = 0
testCaseResults = []
for i in range(len(testcaseList)):
    actualResultFile = open("testCases/actualOutputs/output_" + threeDig(i + 1) + ".txt")
    expectedResultFile = open("testCases/expectedOutputs/output_" + threeDig(i + 1) + ".txt")
    actualResult = str(actualResultFile.read().rstrip())
    expectedResult = str(expectedResultFile.read().rstrip())
    if actualResult == expectedResult:
        testCaseResults.append(1)
        passedCount += 1
    else:
        testCaseResults.append(0)
        failedCount += 1
print("\nTest case results: " + str(testCaseResults) + "\n")

#--------------------------------------------------------------------
# See which lines were executed by each test case and build up an array (coverageList)
for i in range(len(coverageFileList)):
    currFile = open(coverageFileList[i])
    lines = currFile.readlines()
    lines = [x.strip() for x in lines]
    lines = [x.strip() for x in lines if x != '']
    j = 0
    for line in lines:
        if (line != "\n") and (not ">>>>>>" in line):
            if testCaseResults[i] == 1: # passed
                coverageList[j][0] = coverageList[j][0] + 1
            else:                       # failed
                coverageList[j][1] = coverageList[j][1] + 1 
        j+=1

#--------------------------------------------------------------------
# Calculate suspiciousness score based on array and place it in the third index
suspiciousnessList = []
for i in range(len(coverageList)):
    num = coverageList[i][1]/failedCount
    denom = (coverageList[i][1])/(failedCount + coverageList[i][0])/(passedCount)
    if denom == 0:
        coverageList[i][2] = 0
        suspiciousnessList.append(0)
    else:
        coverageList[i][2] = num/denom
        suspiciousnessList.append(num/denom)

pythonGraph = cfgConverter.convert2Python(filename, suspiciousnessList)
print("\nCoverage list: " + str(coverageList))

#--------------------------------------------------------------------
# Run Prolog queries on resulting file
reachabilityList = []
from pyswip import Prolog
prolog = Prolog()
for command in plCommandList:
    #print("Command: " + command)
    start = time.process_time()
    result = prolog.query(command)
    #print("Time: " + str(time.process_time() - start))     # Used to get timing metrics
    for test in result:
        reachabilityList.append(list(set(test['V'])))
print("\nReachability list: " + str(reachabilityList))