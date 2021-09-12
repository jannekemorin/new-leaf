import os
import importlib.util
import sys
import trace
import cfg2Prolog

# Create correct file name from input
filename = str(input("Enter the name of the file you would like to analyze: "))
function = input("Enter the name of the function you would like to test: ")
exec("from testFiles." + filename.split(".")[0]+ " import " + function)             # import function from file
command = "python dependencies/pycfg-0.1/pycfg/pycfg.py testFiles/" + filename + " -d 2> cfgs/text/" + filename.split(".")[0] + ".txt"

# Create control flow graph (CFG) utilizing the pycfg-0.1 package
stream = os.popen(command)
output = stream.readlines()

# Convert the CFG to a list of Prolog reachability queries
plCommandList = cfg2Prolog.convert("cfgs/text/" + filename.split(".")[0] + ".txt")
for i in range(len(plCommandList)):
    plCommandList[i] = plCommandList[i].rstrip()
    # print("output: " + str(plCommandList[i]))

# Move the png file generated
os.rename(("testFiles/" + filename + ".png"), ("cfgs/images/" + filename + ".png"))

# Open the program and count the number of lines
faulty_program = open("testFiles/" + filename)
length = 0
for line in faulty_program.readlines():
    if len(line.strip()) != 0:
        # print("Line: " + line)
        length += 1
# print(length)

#-------------------------------------
# A helper function to convert a number to its three-digit representation
def threeDig(i):
    if i < 10:
        return "00" + str(i)
    elif i < 100:
        return "0" + str(i)
    else:
        return str(i)
#-------------------------------------

# Create a list containing the names of the test case files
list = os.listdir("testCases/inputs") # dir is your directory path
number_files = len(list)
testcaseList = []
for i in range(1, number_files + 1):
    testcaseList.append("testCases/inputs/input_" + threeDig(i) + ".txt")
    # print(testcaseList[i - 1])

os.remove("cfgs/images/wrong_1_001.py.png")

# Run each test case on the faulty program and save results
for i in range(len(testcaseList)): 
    in_file = open(testcaseList[i])
    function_call = in_file.read()
    out_file = open(("testCases/actualOutputs/" + "output_" + threeDig(i + 1) + ".txt"), "w")
    result = str(eval(function_call))
    out_file.write(result)

    # create a Trace object, telling it what to ignore, and whether to
    # do tracing or line-counting or both.
    tracer = trace.Trace(
        ignoredirs=[sys.prefix, sys.exec_prefix],
        trace=0,
        count=1)

    # run the new command using the given tracer
    tracer.run(function_call)

    # make a report, placing output in the current directory
    r = tracer.results()
    r.write_results(show_missing=True, coverdir=("."))
    os.rename("testFiles.wrong_1_001.cover", "testCases/coverageReports/output_" + threeDig(i + 1) + "_cover.txt")

    out_file.close()

# Create coverage file list
coverageFileList = []
coverageList = []
for i in range(1, number_files + 1):
    coverageFileList.append("testCases/coverageReports/output_" + threeDig(i) + "_cover.txt")
for i in range(length):
    coverageList.append([0, 0, 0])
print(coverageFileList)
print(coverageList)

'''
# Use the diff command to get the results of each test case
passed_count = 0
failed_count = 0
testCaseResults = []
for i in range(len(testcaseList)):
    #print(len(testcaseList))
    #print("i: " + str(i))
    actual_result_file = open("data/question_1/testcase_output/wrong_1_001" + "/output_" + threeDig(i + 1) + ".txt")
    expected_result_file = open("data/question_1/ans/output_" + threeDig(i + 1) + ".txt")
    actual_result = str(actual_result_file.read().rstrip())
    expected_result = str(expected_result_file.read().rstrip())
    # lst = []
    # lst.append(actual_result)
    # lst.append(expected_result)
    # print(lst)
    if actual_result == expected_result:
        #print("test case " + threeDig(i + 1) + " passed")
        testCaseResults.append(1)
        passed_count += 1
    else:
        #print("test case " + threeDig(i + 1) + " failed")
        testCaseResults.append(0)
        failed_count += 1

# See which lines it executed and build up a list
# What happens if there are empty lines?
for i in range(len(coverageFileList)):
    curr_file = open(coverageFileList[i])
    lines = curr_file.readlines()
    lines = [x.strip() for x in lines]
    lines = [x.strip() for x in lines if x != '']
    j = 0
    while (j != length - 1):
        for line in lines:
            #print(line)
            if (line != "\n") and (not ">>>>>>" in line):
                if testCaseResults[i] == 1: # passed
                    coverageList[j][0] = coverageList[j][0] + 1
                else:                       # failed
                    coverageList[j][1] = coverageList[j][1] + 1 
                j += 1
            elif line != "\n":
                j += 1
#print(coverageList)

# Calculate suspiciousness score and place it in the third index
#print("failed count: " + str(failed_count))
#print("passed count: " + str(passed_count))
for i in range(len(coverageList)):
    #print("coverageList[i][1]:" + str(coverageList[i][1]))
    #print("failed_count:" + str(failed_count))
    num = coverageList[i][1]/failed_count
    denom = (coverageList[i][1])/(failed_count + coverageList[i][0])/(passed_count)
    #print(num)
    #print(denom)
    if denom == 0:
        coverageList[i][2] = 0
    else:
        coverageList[i][2] = num/denom
print(coverageList)

# Run Prolog queries on resulting file
reachability_list = []
from pyswip import Prolog
prolog = Prolog()
for command in plCommandList:
    #print(command)
    result = prolog.query(command)
    for test in result:
        reachability_list.append(list(set(test['V'])))
print(reachability_list)'''