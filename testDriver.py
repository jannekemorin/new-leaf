import os
import sys
import trace
import cfg2Prolog
import datetime
import time
DEBUG = False

#-------------------------------------
# Remove all coverage reports when rerunning the program
dir = 'testCases/coverageReports'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

#-------------------------------------
# Ask user for filename/function and import the function from the file provided
filename = str(input("Enter the name of the file you would like to analyze: "))
function = input("Enter the name of the function you would like to test: ")
exec("from testFiles." + filename.split(".")[0]+ " import " + function)             # import function from file

#-------------------------------------
# Remove cfg images so they can be overwritten
if os.path.exists("cfgs/images/" + filename + ".png"):
    os.remove("cfgs/images/" + filename + ".png")

#-------------------------------------
# Create PROLOG-format control flow graph (CFG) utilizing the pycfg-0.1 package
command = "python dependencies/pycfg-0.1/pycfg/pycfg.py testFiles/" + filename + " -d 2> cfgs/text/" + filename.split(".")[0] + ".txt"
stream = os.popen(command)
output = stream.readlines()

#-------------------------------------
# Convert the CFG to a list of Prolog reachability queries
plCommandList = cfg2Prolog.convert2PL(filename)
for i in range(len(plCommandList)):
    plCommandList[i] = plCommandList[i].rstrip()
    if DEBUG:
        print("Output: %s\n", str(plCommandList[i]))

#-------------------------------------
# Move the png CFGfile generated
os.rename(("testFiles/" + filename + ".png"), ("cfgs/images/" + filename + ".png"))

#-------------------------------------
# Open the program and count the number of lines
faulty_program = open("testFiles/" + filename)
length = 0
for line in faulty_program.readlines():
    if len(line.strip()) != 0:
        if DEBUG:
            print("Line: %s\n" + line)
        length += 1

#-------------------------------------
# Helper function - convert a number to its three-digit representation
def threeDig(i):
    if i < 10:
        return "00" + str(i)
    elif i < 100:
        return "0" + str(i)
    else:
        return str(i)

#-------------------------------------
# Create a list containing the names of the test case files
dirList = os.listdir("testCases/inputs") # dir is your directory path
number_files = len(dirList)
testcaseList = []
for i in range(1, number_files + 1):
    testcaseList.append("testCases/inputs/input_" + threeDig(i) + ".txt")
    if DEBUG: 
        print(testcaseList[i - 1])

#-------------------------------------
# Run each test case on the faulty program and save the results
for i in range(len(testcaseList)): 
    in_file = open(testcaseList[i])
    function_call = in_file.read()
    out_file = open(("testCases/actualOutputs/" + "output_" + threeDig(i + 1) + ".txt"), "w")
    result = str(eval(function_call))
    out_file.write(result)

    # Create a Trace object, which will create coverage reports
    tracer = trace.Trace(
        ignoredirs=[sys.prefix, sys.exec_prefix],
        trace=0,
        count=1)

    # Run the function call from the test case using the tracer function
    tracer.run(function_call)

    # Create a coverage report, placing output in the current directory
    r = tracer.results()
    r.write_results(show_missing=True, coverdir=("."))
    os.rename("testFiles.wrong_1_001.cover", "testCases/coverageReports/output_" + threeDig(i + 1) + "_cover.txt")

    out_file.close()

#-------------------------------------
# Create a list of the coverage report filepaths for each test case
coverageFileList = []
coverageList = []
for i in range(1, number_files + 1):
    coverageFileList.append("testCases/coverageReports/output_" + threeDig(i) + "_cover.txt")
for i in range(length):
    coverageList.append([0, 0, 0])
if DEBUG:
    print(coverageFileList)
if DEBUG: 
    print(coverageList)

#-------------------------------------
# Use the diff command to get the results of each test case
passed_count = 0
failed_count = 0
testCaseResults = []
for i in range(len(testcaseList)):
    if DEBUG:
        print(len(testcaseList))
    if DEBUG: 
        print("i: " + str(i))
    actual_result_file = open("testCases/actualOutputs/output_" + threeDig(i + 1) + ".txt")
    expected_result_file = open("testCases/expectedOutputs/output_" + threeDig(i + 1) + ".txt")
    actual_result = str(actual_result_file.read().rstrip())
    expected_result = str(expected_result_file.read().rstrip())
    if actual_result == expected_result:
        if DEBUG:
            print("test case " + threeDig(i + 1) + " passed")
        testCaseResults.append(1)
        passed_count += 1
    else:
        if DEBUG:
            print("test case " + threeDig(i + 1) + " failed")
        testCaseResults.append(0)
        failed_count += 1
print("Test case results: " + str(testCaseResults))

#-------------------------------------
# See which lines were executed by each test case and build up an array (coverageList)
for i in range(len(coverageFileList)):
    curr_file = open(coverageFileList[i])
    lines = curr_file.readlines()
    lines = [x.strip() for x in lines]
    lines = [x.strip() for x in lines if x != '']
    j = 0
    for line in lines:
        if DEBUG:
            print("j: " + str(j))
        if DEBUG: 
            print("line: " + line)
        if (line != "\n") and (not ">>>>>>" in line):
            if testCaseResults[i] == 1: # passed
                coverageList[j][0] = coverageList[j][0] + 1
            else:                       # failed
                coverageList[j][1] = coverageList[j][1] + 1 
        j+=1

#-------------------------------------
# Calculate suspiciousness score and place it in the third index
suspiciousnessList = []
if DEBUG:
    print("failed count: " + str(failed_count))
if DEBUG:
    print("passed count: " + str(passed_count))
for i in range(len(coverageList)):
    if DEBUG:
        print("coverageList[i][1]:" + str(coverageList[i][1]))
    if DEBUG:
        print("failed_count:" + str(failed_count))
    num = coverageList[i][1]/failed_count
    denom = (coverageList[i][1])/(failed_count + coverageList[i][0])/(passed_count)
    if denom == 0:
        coverageList[i][2] = 0
        suspiciousnessList.append(0)
    else:
        coverageList[i][2] = num/denom
        suspiciousnessList.append(num/denom)

pythonGraph = cfg2Prolog.convert2Python(filename, suspiciousnessList)
print("Coverage list: " + str(coverageList))

#-------------------------------------
# Run Prolog queries on resulting file
reachability_list = []
from pyswip import Prolog
prolog = Prolog()
for command in plCommandList:
    print("Command: " + command)
    start = time.process_time()
    result = prolog.query(command)
    print("Time: " + str(time.process_time() - start))
    print("------------------------------------------------")
    for test in result:
        reachability_list.append(list(set(test['V'])))
print("Reachability list: " + str(reachability_list))